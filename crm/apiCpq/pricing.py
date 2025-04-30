import frappe
from frappe import _

@frappe.whitelist()
def get_total_cost_from_direct_material_cost(i_direct_material_cost):
    """
    API to calculate the total cost based on direct material cost and fixed margin rates.

    Args:
        i_direct_material_cost (str): A string containing'direct_material_cost'.

    Returns:
        dict: A dictionary with the total cost and individual margin rates.
            Example:
            {
                "total_cost": <calculated_total_cost>,
                "l_labour_rate": 10,
                "l_production_rate": 10,
                "l_engineering_overhead_rate": 10,
                "l_administrative_overhead": 10,
                "l_indirect_material_cost": 10,
                "l_sales_overhead": 10
            }
    """

    try:        
        
        l_direct_material_cost = float(i_direct_material_cost)
        
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

        return {
            "total_cost": l_total_cost,
            **ld_margin
        }

    except ValueError:
        # Handle the case where the input can't be converted to float
        frappe.throw(_("Invalid value for 'direct_material_cost': Expected a valid numeric value."), frappe.ValidationError)


    except Exception as e:
        frappe.log_error(message=str(e), title="Unexpected Error in get_total_cost_from_direct_material_cost")
        return {"error": _("An unexpected error occurred. Please check the server logs.")}


@frappe.whitelist()
def get_selling_price_from_total_cost(i_total_cost):
    """
    API to calculate the selling price based on the total cost and fixed margin rates.

    Args:
        i_total_cost (float): A float containing 'total_cost'.

    Returns:
        dict: A dictionary with the calculated selling price and margin details.
            Example:
            {
                "selling": <calculated_selling_price>,
                "l_ebita": 40,
                "l_transport": 10,
                "l_comission": 10
            }
    """

    try:
       
        # Define marginal costs
        ld_margin = {
            "l_ebita": 40,  # EBITA as a percentage
            "l_transport": 10,
            "l_comission": 10, # comission as a percentage
        }

        # Calculation for the final cost
        l_selling = (i_total_cost + ((ld_margin["l_transport"] / 100 ) * i_total_cost)) / (1 - (ld_margin["l_ebita"] + ld_margin["l_comission"]) / 100 )

        return {
            "selling": l_selling,
            **ld_margin
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="Unexpected Error in get_selling_price_from_total_cost")
        return {"error": _("An unexpected error occurred. Please check the server logs.")}