# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
import click
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from crm.fcrm.doctype.crm_products.crm_products import create_product_details_script


def before_install():
	pass


def after_install(force=False):
	add_default_lead_statuses()
	add_default_deal_statuses()
	add_default_communication_statuses()
	add_default_fields_layout(force)
	add_property_setter()
	add_email_template_custom_fields()
	add_default_industries()
	add_default_lead_sources()
	add_standard_dropdown_items()
	add_default_scripts()
	frappe.db.commit()


def add_default_lead_statuses():
	statuses = {
		"New": {
			"color": "gray",
			"position": 1,
		},
		"Contacted": {
			"color": "orange",
			"position": 2,
		},
		"Nurture": {
			"color": "blue",
			"position": 3,
		},
		"Qualified": {
			"color": "green",
			"position": 4,
		},
		"Unqualified": {
			"color": "red",
			"position": 5,
		},
		"Junk": {
			"color": "purple",
			"position": 6,
		},
	}

	for status in statuses:
		if frappe.db.exists("CRM Lead Status", status):
			continue

		doc = frappe.new_doc("CRM Lead Status")
		doc.lead_status = status
		doc.color = statuses[status]["color"]
		doc.position = statuses[status]["position"]
		doc.insert()


def add_default_deal_statuses():
	statuses = {
		"Qualification": {
			"color": "gray",
			"position": 1,
		},
		"Demo/Making": {
			"color": "orange",
			"position": 2,
		},
		"Proposal/Quotation": {
			"color": "blue",
			"position": 3,
		},
		"Negotiation": {
			"color": "yellow",
			"position": 4,
		},
		"Ready to Close": {
			"color": "purple",
			"position": 5,
		},
		"Won": {
			"color": "green",
			"position": 6,
		},
		"Lost": {
			"color": "red",
			"position": 7,
		},
	}

	for status in statuses:
		if frappe.db.exists("CRM Deal Status", status):
			continue

		doc = frappe.new_doc("CRM Deal Status")
		doc.deal_status = status
		doc.color = statuses[status]["color"]
		doc.position = statuses[status]["position"]
		doc.insert()


def add_default_communication_statuses():
	statuses = ["Open", "Replied"]

	for status in statuses:
		if frappe.db.exists("CRM Communication Status", status):
			continue

		doc = frappe.new_doc("CRM Communication Status")
		doc.status = status
		doc.insert()


def add_default_fields_layout(force=False):
	quick_entry_layouts = {
		"CRM Lead-Quick Entry": {
			"doctype": "CRM Lead",
			"layout": '[{"name": "person_section", "columns": [{"name": "column_5jrk", "fields": ["salutation", "email"]}, {"name": "column_5CPV", "fields": ["first_name", "mobile_no"]}, {"name": "column_gXOy", "fields": ["last_name", "gender"]}]}, {"name": "organization_section", "columns": [{"name": "column_GHfX", "fields": ["organization", "territory"]}, {"name": "column_hXjS", "fields": ["website", "annual_revenue"]}, {"name": "column_RDNA", "fields": ["no_of_employees", "industry"]}]}, {"name": "lead_section", "columns": [{"name": "column_EO1H", "fields": ["status"]}, {"name": "column_RWBe", "fields": ["lead_owner"]}]}]',
		},
		"CRM Deal-Quick Entry": {
			"doctype": "CRM Deal",
			"layout": '[{"name": "organization_section", "hidden": true, "editable": false, "columns": [{"name": "column_GpMP", "fields": ["organization"]}, {"name": "column_FPTn", "fields": []}]}, {"name": "organization_details_section", "editable": false, "columns": [{"name": "column_S3tQ", "fields": ["organization_name", "territory"]}, {"name": "column_KqV1", "fields": ["website", "annual_revenue"]}, {"name": "column_1r67", "fields": ["no_of_employees", "industry"]}]}, {"name": "contact_section", "hidden": true, "editable": false, "columns": [{"name": "column_CeXr", "fields": ["contact"]}, {"name": "column_yHbk", "fields": []}]}, {"name": "contact_details_section", "editable": false, "columns": [{"name": "column_ZTWr", "fields": ["salutation", "email"]}, {"name": "column_tabr", "fields": ["first_name", "mobile_no"]}, {"name": "column_Qjdx", "fields": ["last_name", "gender"]}]}, {"name": "deal_section", "columns": [{"name": "column_mdps", "fields": ["status"]}, {"name": "column_H40H", "fields": ["deal_owner"]}]}]',
		},
		"Contact-Quick Entry": {
			"doctype": "Contact",
			"layout": '[{"name": "salutation_section", "columns": [{"name": "column_eXks", "fields": ["salutation"]}]}, {"name": "full_name_section", "hideBorder": true, "columns": [{"name": "column_cSxf", "fields": ["first_name"]}, {"name": "column_yBc7", "fields": ["last_name"]}]}, {"name": "email_section", "hideBorder": true, "columns": [{"name": "column_tH3L", "fields": ["email_id"]}]}, {"name": "mobile_gender_section", "hideBorder": true, "columns": [{"name": "column_lrfI", "fields": ["mobile_no"]}, {"name": "column_Tx3n", "fields": ["gender"]}]}, {"name": "organization_section", "hideBorder": true, "columns": [{"name": "column_S0J8", "fields": ["company_name"]}]}, {"name": "designation_section", "hideBorder": true, "columns": [{"name": "column_bsO8", "fields": ["designation"]}]}, {"name": "address_section", "hideBorder": true, "columns": [{"name": "column_W3VY", "fields": ["address"]}]}]',
		},
		"CRM Organization-Quick Entry": {
			"doctype": "CRM Organization",
			"layout": '[{"name": "organization_section", "columns": [{"name": "column_zOuv", "fields": ["organization_name"]}]}, {"name": "website_revenue_section", "hideBorder": true, "columns": [{"name": "column_I5Dy", "fields": ["website"]}, {"name": "column_Rgss", "fields": ["annual_revenue"]}]}, {"name": "territory_section", "hideBorder": true, "columns": [{"name": "column_w6ap", "fields": ["territory"]}]}, {"name": "employee_industry_section", "hideBorder": true, "columns": [{"name": "column_u5tZ", "fields": ["no_of_employees"]}, {"name": "column_FFrT", "fields": ["industry"]}]}, {"name": "address_section", "hideBorder": true, "columns": [{"name": "column_O2dk", "fields": ["address"]}]}]',
		},
		"Address-Quick Entry": {
			"doctype": "Address",
			"layout": '[{"name": "details_section", "columns": [{"name": "column_uSSG", "fields": ["address_title", "address_type", "address_line1", "address_line2", "city", "state", "country", "pincode"]}]}]',
		},
		"CRM Call Log-Quick Entry": {
			"doctype": "CRM Call Log",
			"layout": '[{"name":"details_section","columns":[{"name":"column_uMSG","fields":["type","from","duration"]},{"name":"column_wiZT","fields":["to","status","caller","receiver"]}]}]',
		},
		"Item-Quick Entry": {
			"doctype": "Item",
			"layout": '[{"name":"first_tab","sections":[{"name":"item_section","columns":[{"name":"column_5jrk","fields":["item_code","item_name"]},{"name":"column_5CPV","fields":["item_group","stock_uom"]}]},{"name":"item_attribute","columns":[{"name":"column_5jrk","fields":["attributes"]}]}]}]',
		},
		"Quotation-Quick Entry": {
			"doctype": "Quotation",
			"layout": '[{"name":"first_tab","sections":[{"name":"quotation_section","columns":[{"name":"column_5jrk","fields":["quotation_to","party_name"]},{"name":"column_5CPV","fields":["transaction_date"]}]},{"name":"currency_and_price List","columns":[{"name":"column_5jrk","fields":["currency"]},{"name":"column_5jrk","fields":["selling_price_list"]}]},{"label":"New Section","name":"section_JwOX","opened":true,"columns":[{"name":"column_cTLW","fields":["items"]}]}]}]',
		}
	}

	sidebar_fields_layouts = {
		"CRM Lead-Side Panel": {
			"doctype": "CRM Lead",
			"layout": '[{"label":"Details","name":"details_section","opened":true,"columns":[{"name":"column_kl92","fields":["organization","website","territory","industry","job_title","source","lead_owner","no_of_employees"]}]},{"label":"Person","name":"person_section","opened":true,"columns":[{"name":"column_XmW2","fields":["salutation","first_name","last_name","email","mobile_no"]}]}]',
		},
		"CRM Deal-Side Panel": {
			"doctype": "CRM Deal",
			"layout": '[{"label":"Contacts","name":"contacts_section","opened":true,"editable":false,"contacts":[]},{"label":"Organization Details","name":"organization_section","opened":true,"columns":[{"name":"column_na2Q","fields":["organization","website","territory","annual_revenue","close_date","probability","next_step","deal_owner"]}]}]',
		},
		"Contact-Side Panel": {
			"doctype": "Contact",
			"layout": '[{"label": "Details", "name": "details_section", "opened": true, "columns": [{"name": "column_eIWl", "fields": ["salutation", "first_name", "last_name", "email_id", "mobile_no", "gender", "company_name", "designation", "address"]}]}]',
		},
		"CRM Organization-Side Panel": {
			"doctype": "CRM Organization",
			"layout": '[{"label": "Details", "name": "details_section", "opened": true, "columns": [{"name": "column_IJOV", "fields": ["organization_name", "website", "territory", "industry", "no_of_employees", "address"]}]}]',
		},
		"Design-Side Panel": {
			"doctype": "Design",
			"layout": '[{"label":"Design Information","name":"design_information","opened":true,"columns":[{"name":"column1","fields":["design_template","status","item"]}]},{"label":"Price List","name":"price_list","opened":true,"columns":[{"name":"column1","fields":["direct_material_cost","total_cost"]}]},{"label":"Ownership","name":"ownership_tab","opened":true,"columns":[{"name":"column1","fields":["created_by"]}]}]',
		},
		"Item-Side Panel": {
			"doctype": "Item",
			"layout": '[{"label":"Item Details","name":"item_details","opened":true,"columns":[{"name":"column1","fields":["item_code","item_name","item_group","stock_uom"]}],"showEditButton":true,"visible":4}]',
		},
		"Quotation-Side Panel": {
			"doctype": "Quotation",
			"layout": '[{"label":"Quotation Details","name":"quotation_details","opened":true,"columns":[{"name":"column1","fields":["quotation_to","party_name","customer_name","transaction_date","valid_till","order_type"]}],"showEditButton":true,"visible":6},{"label":"Currency and Price List","name":"currency_and_pricelist","opened":true,"columns":[{"name":"column1","fields":["currency","selling_price_list"]}],"showEditButton":true,"visible":2},{"label":"Total","name":"total","opened":true,"columns":[{"name":"column1","fields":["total_qty","total","net_total","grand_total"]}],"showEditButton":true,"visible":2},{"label":"Additional Discount","name":"additional_discount","opened":true,"columns":[{"name":"column1","fields":["total_qty","total","apply_discount_on","additional_discount_percentage","discount_amount"]}],"showEditButton":true,"visible":2}]',
		},
	}

	data_fields_layouts = {
		"CRM Lead-Data Fields": {
			"doctype": "CRM Lead",
			"layout": '[{"name":"first_tab","sections":[{"label":"Tracker","name":"section_DdiP","opened":true,"columns":[{"name":"column_FScX","fields":["custom_question_type"]},{"label":"","name":"column_Gwah","fields":["custom_prompt"]}],"editingLabel":false},{"label":"New Section","name":"section_AKZz","opened":true,"columns":[{"name":"column_iicT","fields":["custom_lead_questionnaire"]}]},{"label":"New Section","name":"section_Zilu","opened":true,"columns":[{"name":"column_tsAe","fields":["products"]}]}]}]',
		},
		"CRM Deal-Data Fields": {
			"doctype": "CRM Deal",
			"layout": '[{"name":"first_tab","sections":[{"label":"Details","name":"details_section","opened":true,"columns":[{"name":"column_z9XL","fields":["organization","annual_revenue","next_step"]},{"name":"column_gM4w","fields":["website","close_date","deal_owner"]},{"name":"column_gWmE","fields":["territory","probability"]}]},{"label":"New Section","name":"section_ndrr","opened":true,"columns":[{"name":"column_hmVA","fields":["products"]}]}]}]',
		},
		"Design-Data Fields": {
			"doctype": "Design",
			"layout": '[{"name":"tab_DoQF","sections":[{"name":"section_hWFE","columns":[{"name":"column_OOsl","fields":["design_attributes"]}]}]}]',
		},
		"Item-Data Fields": {
			"doctype": "Item",
			"layout": '[{"name":"tab_5if5","sections":[{"name":"section_Axge","columns":[{"name":"column_PSU4","fields":["is_stock_item","auto_create_assets"]}]},{"name":"section_6cua","columns":[{"name":"column_ihfy","fields":["description","brand"]}]},{"name":"section_kqgy","columns":[{"name":"column_sSU8","fields":["attributes"]}]}]},{"name":"tab_8dGd","sections":[{"name":"section_LLTT","columns":[{"name":"column_jmkI","fields":[]}]}]},{"name":"tab_AJXj","sections":[{"name":"section_85JY","columns":[{"name":"column_X0ZV","fields":[]}]},{"name":"section_tKW5","columns":[{"name":"column_6Vvf","fields":["shelf_life_in_days","end_of_life","default_material_request_type","valuation_method"]},{"name":"column_hRdb","fields":["warranty_period","weight_per_unit","weight_uom","allow_negative_stock"]}]},{"name":"section_Kvoo","columns":[{"name":"column_HJ8K","fields":["barcodes"]}]},{"name":"section_cuQr","columns":[{"name":"column_Tpyi","fields":["reorder_levels"]}]},{"name":"section_vw9l","columns":[{"name":"column_KSLH","fields":["has_batch_no","create_new_batch","batch_number_series","has_expiry_date","retain_sample","sample_quantity"]},{"name":"column_hSXd","fields":["has_serial_no","serial_no_series"]}]}]},{"name":"tab_VTDJ","sections":[{"name":"section_2hXV","columns":[{"name":"column_Zip6","fields":["variant_of","variant_based_on","attributes"]}]}]},{"name":"tab_8fUi","sections":[{"name":"section_wjvU","columns":[{"name":"column_3Yp0","fields":[]}]},{"name":"section_QsAS","columns":[{"name":"column_MC8G","fields":["enable_deferred_expense","no_of_months_exp"]},{"name":"column_IQkw","fields":["enable_deferred_revenue","no_of_months"]}]},{"name":"section_o0il","columns":[{"name":"column_b9KF","fields":["item_defaults"]}]}]},{"name":"tab_kOJN","sections":[{"name":"section_fusT","columns":[{"name":"column_rfXP","fields":["purchase_uom","min_order_qty","safety_stock","is_purchase_item"]},{"name":"column_ejAq","fields":["lead_time_days","last_purchase_rate","is_customer_provided_item","customer"]}]},{"name":"section_Il6x","columns":[{"name":"column_3j9I","fields":["delivered_by_supplier"]},{"name":"column_0nbt","fields":["supplier_items"]}]},{"name":"section_98hN","columns":[{"name":"column_qRvQ","fields":["country_of_origin"]},{"name":"column_GW07","fields":["customs_tariff_number"]}]}]},{"name":"tab_gI4T","sections":[{"name":"section_MMI5","columns":[{"name":"column_AwYD","fields":["sales_uom","grant_commission","is_sales_item"]},{"name":"column_6Wkp","fields":["max_discount"]}]},{"name":"section_OJQm","columns":[{"name":"column_IsdN","fields":["customer_items"]}]}]},{"name":"tab_826a","sections":[{"name":"section_luT4","columns":[{"name":"column_KnH5","fields":["taxes"]}]}]},{"name":"tab_D32F","sections":[{"name":"section_D5xH","columns":[{"name":"column_B0oD","fields":["inspection_required_before_purchase","quality_inspection_template","inspection_required_before_delivery"]}]}]},{"name":"tab_kBgD","sections":[{"name":"section_DVUf","columns":[{"name":"column_eRTP","fields":["include_item_in_manufacturing","is_sub_contracted_item","default_bom"]},{"name":"column_XQcC","fields":["customer_code","default_item_manufacturer","default_manufacturer_part_no","total_projected_qty"]}]}]}]',
		},
		"Quotation-Data Fields": {
			"doctype": "Quotation",
			"layout": '[{"name":"tab_ugJ4","sections":[{"name":"section_418P","columns":[{"name":"column_rTsE","fields":["items"]}]},{"name":"section_ZICI","columns":[{"name":"column_X1bf","fields":["total_qty","total_net_weight"]},{"name":"column_j5zc","fields":["base_total","base_net_total"]},{"name":"column_Oxup","fields":["total","net_total"]}]},{"name":"section_peH8","columns":[{"name":"column_KNVq","fields":["tax_category","taxes_and_charges"]},{"name":"column_n1vF","fields":["shipping_rule"]},{"name":"column_gu3c","fields":["incoterm","named_place"]}]},{"name":"section_SjBn","columns":[{"name":"column_4ZKG","fields":["taxes"]}]},{"name":"section_4NH9","columns":[{"name":"column_pQbh","fields":["base_total_taxes_and_charges"]},{"name":"column_9VoF","fields":["total_taxes_and_charges"]}]},{"name":"section_R7dN","columns":[{"name":"column_reVM","fields":["base_grand_total","base_rounding_adjustment","base_rounded_total","base_in_words"]},{"name":"column_2azM","fields":["grand_total","rounding_adjustment","rounded_total","disable_rounded_total","in_words"]}]},{"name":"section_ZScr","columns":[{"name":"column_Uco4","fields":["apply_discount_on","base_discount_amount","coupon_code"]},{"name":"column_HZz0","fields":["additional_discount_percentage","discount_amount","referral_sales_partner"]}]},{"name":"section_eEyy","columns":[{"name":"column_duaO","fields":["other_charges_calculation"]}]},{"name":"section_NaWc","columns":[{"name":"column_Iz3X","fields":["pricing_rules"]}]}]},{"name":"tab_ywjG","sections":[{"name":"section_uw2V","columns":[{"name":"column_esBB","fields":[]}]},{"name":"section_felE","columns":[{"name":"column_8zo2","fields":["customer_address","address_display"]},{"name":"column_BDRr","fields":["contact_person","contact_display","contact_mobile","contact_email"]}]},{"name":"section_M6So","columns":[{"name":"column_f4wz","fields":["shipping_address_name"]},{"name":"column_br9o","fields":["shipping_address"]}]},{"name":"section_frkQ","columns":[{"name":"column_tKI8","fields":["company_address","company_address_display"]},{"name":"column_aAw9","fields":["company_contact_person"]}]}]},{"name":"tab_GTLN","sections":[{"name":"section_1j2D","columns":[{"name":"column_0iKs","fields":[]}]},{"name":"section_uTN6","columns":[{"name":"column_LWPZ","fields":["payment_terms_template","payment_schedule"]}]},{"name":"section_3PC4","columns":[{"name":"column_O0nu","fields":["tc_name","terms"]}]}]},{"name":"tab_sXpK","sections":[{"name":"section_bct8","columns":[{"name":"column_LeTn","fields":[]}]},{"name":"section_9vZe","columns":[{"name":"column_8zAo","fields":["auto_repeat","update_auto_repeat_reference"]}]},{"name":"section_wnPf","columns":[{"name":"column_t4yN","fields":["letter_head","group_same_items"]},{"name":"column_wr3z","fields":["select_print_heading","language"]}]},{"name":"section_G3gZ","columns":[{"name":"column_I3nt","fields":["lost_reasons","competitors"]},{"name":"column_W4ol","fields":["order_lost_reason"]}]},{"name":"section_VzKQ","columns":[{"name":"column_PAwk","fields":["status","customer_group","territory"]},{"name":"column_oBEV","fields":["campaign","source"]},{"name":"column_TRib","fields":["opportunity","supplier_quotation","enq_det"]}]}]},{"name":"tab_2mVR","sections":[{"name":"section_kt06","columns":[{"name":"column_aEA6","fields":[]}]}]}]'
		}
	}

	for layout in quick_entry_layouts:
		if frappe.db.exists("CRM Fields Layout", layout):
			if force:
				frappe.delete_doc("CRM Fields Layout", layout)
			else:
				continue

		doc = frappe.new_doc("CRM Fields Layout")
		doc.type = "Quick Entry"
		doc.dt = quick_entry_layouts[layout]["doctype"]
		doc.layout = quick_entry_layouts[layout]["layout"]
		doc.insert()

	for layout in sidebar_fields_layouts:
		if frappe.db.exists("CRM Fields Layout", layout):
			if force:
				frappe.delete_doc("CRM Fields Layout", layout)
			else:
				continue

		doc = frappe.new_doc("CRM Fields Layout")
		doc.type = "Side Panel"
		doc.dt = sidebar_fields_layouts[layout]["doctype"]
		doc.layout = sidebar_fields_layouts[layout]["layout"]
		doc.insert()

	for layout in data_fields_layouts:
		if frappe.db.exists("CRM Fields Layout", layout):
			if force:
				frappe.delete_doc("CRM Fields Layout", layout)
			else:
				continue

		doc = frappe.new_doc("CRM Fields Layout")
		doc.type = "Data Fields"
		doc.dt = data_fields_layouts[layout]["doctype"]
		doc.layout = data_fields_layouts[layout]["layout"]
		doc.insert()


def add_property_setter():
	if not frappe.db.exists("Property Setter", {"name": "Contact-main-search_fields"}):
		doc = frappe.new_doc("Property Setter")
		doc.doctype_or_field = "DocType"
		doc.doc_type = "Contact"
		doc.property = "search_fields"
		doc.property_type = "Data"
		doc.value = "email_id"
		doc.insert()


def add_email_template_custom_fields():
	if not frappe.get_meta("Email Template").has_field("enabled"):
		click.secho("* Installing Custom Fields in Email Template")

		create_custom_fields(
			{
				"Email Template": [
					{
						"default": "0",
						"fieldname": "enabled",
						"fieldtype": "Check",
						"label": "Enabled",
						"insert_after": "",
					},
					{
						"fieldname": "reference_doctype",
						"fieldtype": "Link",
						"label": "Doctype",
						"options": "DocType",
						"insert_after": "enabled",
					},
				]
			}
		)

		frappe.clear_cache(doctype="Email Template")


def add_default_industries():
	industries = [
		"Accounting",
		"Advertising",
		"Aerospace",
		"Agriculture",
		"Airline",
		"Apparel & Accessories",
		"Automotive",
		"Banking",
		"Biotechnology",
		"Broadcasting",
		"Brokerage",
		"Chemical",
		"Computer",
		"Consulting",
		"Consumer Products",
		"Cosmetics",
		"Defense",
		"Department Stores",
		"Education",
		"Electronics",
		"Energy",
		"Entertainment & Leisure, Executive Search",
		"Financial Services",
		"Food",
		"Beverage & Tobacco",
		"Grocery",
		"Health Care",
		"Internet Publishing",
		"Investment Banking",
		"Legal",
		"Manufacturing",
		"Motion Picture & Video",
		"Music",
		"Newspaper Publishers",
		"Online Auctions",
		"Pension Funds",
		"Pharmaceuticals",
		"Private Equity",
		"Publishing",
		"Real Estate",
		"Retail & Wholesale",
		"Securities & Commodity Exchanges",
		"Service",
		"Soap & Detergent",
		"Software",
		"Sports",
		"Technology",
		"Telecommunications",
		"Television",
		"Transportation",
		"Venture Capital",
	]

	for industry in industries:
		if frappe.db.exists("CRM Industry", industry):
			continue

		doc = frappe.new_doc("CRM Industry")
		doc.industry = industry
		doc.insert()


def add_default_lead_sources():
	lead_sources = [
		"Existing Customer",
		"Reference",
		"Advertisement",
		"Cold Calling",
		"Exhibition",
		"Supplier Reference",
		"Mass Mailing",
		"Customer's Vendor",
		"Campaign",
		"Walk In",
	]

	for source in lead_sources:
		if frappe.db.exists("CRM Lead Source", source):
			continue

		doc = frappe.new_doc("CRM Lead Source")
		doc.source_name = source
		doc.insert()


def add_standard_dropdown_items():
	crm_settings = frappe.get_single("FCRM Settings")

	# don't add dropdown items if they're already present
	if crm_settings.dropdown_items:
		return

	crm_settings.dropdown_items = []

	for item in frappe.get_hooks("standard_dropdown_items"):
		crm_settings.append("dropdown_items", item)

	crm_settings.save()


def add_default_scripts():
	for doctype in ["CRM Lead", "CRM Deal"]:
		create_product_details_script(doctype)
