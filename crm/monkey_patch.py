# ---- Monkey Patching in Frappe ----
# 
# What is Monkey Patching?
# Monkey patching is a technique used to modify or extend existing functions 
# in a third-party module or framework without altering its original source code.
# This allows us to override built-in functions dynamically at runtime.
#
# Why are we Monkey Patching `get_linked_notes`?
# In the original function (`get_linked_notes`), only specific fields were being fetched 
# from the "FCRM Note" Doctype. However, we need **all fields** dynamically, 
# rather than specifying them explicitly. Since we cannot modify the function 
# directly in `apps/crm/crm/api/activities.py`, we use monkey patching to replace it 
# with our custom function (`get_linked_notes_all_field`).
#
# How is the Monkey Patch Executed?
# 1. We define our custom function (`get_linked_notes_all_field`) that retrieves all fields.
# 2. In `hooks.py`, we import both the original function and our new function.
# 3. We then override `get_linked_notes` by assigning it to `get_linked_notes_all_field`.
#
# This ensures that whenever `get_linked_notes` is called in the system, it will 
# execute our custom version instead of the original.
#
# --- Custom Function to Fetch All Fields ---

import frappe
def get_linked_notes_all_field(name):
	notes = frappe.db.get_all(
		"FCRM Note",
		filters={"reference_docname": name},
		fields=['*'],
	)
	return notes or []