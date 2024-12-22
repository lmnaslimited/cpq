import frappe
from frappe import _

@frappe.whitelist()
def get_total_cost_from_direct_material_cost(doc):
    try:
        # Ensure `doc` is a dictionary
        if not isinstance(doc, dict):
            frappe.throw(_("Invalid input: Expected a dictionary."), frappe.ValidationError)

        # Check if `direct_material_cost` is provided
        l_direct_material_cost = doc.get('direct_material_cost')
        if l_direct_material_cost is None:
            frappe.throw(_("Value doesn't exist: Param 'direct_material_cost' not found."), frappe.ValidationError)

        # Convert `direct_material_cost` to a float
        try:
            l_direct_material_cost = float(l_direct_material_cost)
        except ValueError:
            frappe.throw(_("Invalid value for 'direct_material_cost': Expected a number."), frappe.ValidationError)

        # Marginal Costs
        ld_margin = { 
            "l_labour_rate": 10,
            "l_production_rate": 10,
            "l_engineering_overhead_rate": 10,
            "l_administrative_overhead": 10,
            "l_indirect_material_cost": 10,
            "l_sales_overhead": 10
        }

        # Calculate the total cost
        l_total_cost = (l_direct_material_cost + ld_margin["l_labour_rate"] + ld_margin["l_production_rate"] +
                        ld_margin["l_engineering_overhead_rate"] + ld_margin["l_administrative_overhead"] +
                        ld_margin["l_indirect_material_cost"] + ld_margin["l_sales_overhead"])

        # Prepare the response as a JSON object
        return {
            "total_cost": l_total_cost,
            **ld_margin
        }

    except frappe.ValidationError as e:
        # Handle known validation errors with specific messages
        return {"error": str(e)}  # Frappe throws specific error message

    except Exception as e:
        # Log unexpected errors for further troubleshooting
        frappe.log_error(message=str(e), title="Unexpected Error in get_total_cost_from_direct_material_cost")
        return {"error": _("An unexpected error occurred. Please check the server logs.")}

@frappe.whitelist()
def get_selling_price_from_total_cost(doc):
    try:
        # Retrieve total cost from the document
        l_total_cost = doc.get('total_cost')
        if l_total_cost is None:
            frappe.throw(_("Value doesn't exist: Param 'l_total_cost' not found."), frappe.ValidationError)

        # Define marginal costs
        ld_margin = {
            "l_ebita": 40,  # EBITA as a percentage
            "l_transport": 10,
            "l_comission": 10,
        }

        # Calculate EBITA as a percentage of the total cost
        l_ebita = (ld_margin["l_ebita"] / 100) * l_total_cost

        # Calculate the final cost (Selling price = Total Cost + EBITA + Transport + Commission)
        l_selling = l_total_cost + l_ebita + ld_margin["l_transport"] + ld_margin["l_comission"]

        # Return the final cost along with marginal costs
        return {
            "selling": l_selling,
            **ld_margin  # Merge marginal costs into the response
        }

    except frappe.ValidationError as e:
        # Handle known validation errors with specific messages
        return {"error": str(e)}  # Frappe throws specific error message

    except Exception as e:
        # Log unexpected errors for further troubleshooting
        frappe.log_error(message=str(e), title="Unexpected Error in get_selling_price_from_total_cost")
        return {"error": _("An unexpected error occurred. Please check the server logs.")}
