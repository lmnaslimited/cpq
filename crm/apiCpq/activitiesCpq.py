import frappe
from frappe import _
from frappe.utils.caching import redis_cache
from frappe.desk.form.load import get_docinfo
import json

# Import the original get_activities function
from crm.api.activities import (
    get_activities as original_get_activities,
    get_linked_calls,
    get_linked_notes,
    get_linked_tasks,
    get_attachments,
    handle_multiple_versions,
	parse_attachment_log
)

@frappe.whitelist()
def get_activities_cpq(name):
	if frappe.db.exists("CRM Deal", name):
		return original_get_activities(name)
	elif frappe.db.exists("CRM Lead", name):
		return original_get_activities(name)
	elif frappe.db.exists("Design", name):
		return get_doctype_activities("Design",name)
	elif frappe.db.exists("Item", name):
		return get_doctype_activities("Item",name)
	elif frappe.db.exists("Quotation", name):
		return get_doctype_activities("Quotation",name)
	elif frappe.db.exists("Condition Type", name):
		return get_doctype_activities("Condition Type", name)
	else:
		frappe.throw(_("Document not found"), frappe.DoesNotExistError)

def get_doctype_activities(doctype, name):
	get_docinfo('', doctype, name)
	docinfo = frappe.response["docinfo"]
	doctype_meta = frappe.get_meta(doctype)
	doctype_fields = {field.fieldname: {"label": field.label, "options": field.options} for field in doctype_meta.fields}
	avoid_fields = [
		"converted",
		"response_by",
		"sla_creation",
		"sla",
		"first_response_time",
		"first_responded_on",
	]

	doc = frappe.db.get_values(doctype, name, ["creation", "owner"])[0]
	activities = [{
		"activity_type": "creation",
		"creation": doc[0],
		"owner": doc[1],
		"data": "created this document",
		"is_lead": True,
	}]

	docinfo.versions.reverse()

	for version in docinfo.versions:
		data = json.loads(version.data)
		if not data.get("changed"):
			continue

		if change := data.get("changed")[0]:
			field = doctype_fields.get(change[0], None)

			if not field or change[0] in avoid_fields or (not change[1] and not change[2]):
				continue

			field_label = field.get("label") or change[0]
			field_option = field.get("options") or None

			activity_type = "changed"
			data = {
				"field": change[0],
				"field_label": field_label,
				"old_value": change[1],
				"value": change[2],
			}

			if not change[1] and change[2]:
				activity_type = "added"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[2],
				}
			elif change[1] and not change[2]:
				activity_type = "removed"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[1],
				}

		activity = {
			"activity_type": activity_type,
			"creation": version.creation,
			"owner": version.owner,
			"data": data,
			"is_lead": True,
			"options": field_option,
		}
		activities.append(activity)

	for comment in docinfo.comments:
		activity = {
			"name": comment.name,
			"activity_type": "comment",
			"creation": comment.creation,
			"owner": comment.owner,
			"content": comment.content,
			"attachments": get_attachments('Comment', comment.name),
			"is_lead": True,
		}
		activities.append(activity)

	for communication in docinfo.communications + docinfo.automated_messages:
		activity = {
			"activity_type": "communication",
			"communication_type": communication.communication_type,
			"creation": communication.creation,
			"data": {
				"subject": communication.subject,
				"content": communication.content,
				"sender_full_name": communication.sender_full_name,
				"sender": communication.sender,
				"recipients": communication.recipients,
				"cc": communication.cc,
				"bcc": communication.bcc,
				"attachments": get_attachments('Communication', communication.name),
				"read_by_recipient": communication.read_by_recipient,
			},
			"is_lead": True,
		}
		activities.append(activity)
	for attachment_log in docinfo.attachment_logs:
		activity = {
			"name": attachment_log.name,
			"activity_type": "attachment_log",
			"creation": attachment_log.creation,
			"owner": attachment_log.owner,
			"data": parse_attachment_log(attachment_log.content, attachment_log.comment_type),
			"is_lead": True,
		}
		activities.append(activity)

	calls = get_linked_calls(name)
	notes = get_linked_notes(name)
	tasks = get_linked_tasks(name)
	attachments = get_attachments(doctype, name)

	activities.sort(key=lambda x: x["creation"], reverse=True)
	activities = handle_multiple_versions(activities)

	return activities, calls, notes, tasks, attachments