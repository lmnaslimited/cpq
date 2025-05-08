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
    

# Function to fetch the existing item price document
def fn_get_item_price_document(i_item_code, i_price_list):
    la_item_price = frappe.get_all(
        "Item Price",
        filters={
            "item_code": i_item_code,
            "price_list": i_price_list
        },
        fields=["name"],
        order_by="valid_from desc",
        limit=1
    )
    return la_item_price[0] if la_item_price else None


# Event handler for Item Price on after_save
def create_or_update_item_prices(doc, event):
    """
    Event handler to create or update item prices for all selling price lists 
    (excluding "Standard Selling") whenever an Item Price document is saved.

    Args:
        doc (object): The Item Price document that triggered the event.
        event (str): The event name (e.g., 'after_save').

    Functionality:
        - Checks if the price list of the current Item Price document is "Standard Selling".
        - Retrieves all other selling price lists from the database.
        - For each selling price list:
            - Calls an external API to calculate the selling price based on the total cost.
            - Updates the existing Item Price document for the price list if it exists.
            - Creates a new Item Price document for the price list if it does not exist.

    Dependencies:
        - `crm.api.pricingApi.get_selling_price_from_total_cost`: External API used to calculate the selling price.
        - `fn_get_item_price_document`: Helper function to fetch the existing Item Price for a given item code and price list.

    Returns:
        None
    """

    # Only proceed if the price list is "Standard Selling"
    if doc.price_list == 'Standard Selling':
        # Fetch all price lists except "Standard Selling"
        ld_price_lists = frappe.get_all(
            'Price List',
            fields=['name', 'selling'],
            filters={'name': ['!=', 'Standard Selling']}
        )
        
        # Iterate through each price list
        for ld_price_list in ld_price_lists:
            if ld_price_list.selling == 1:
                
                selling_price = frappe.call('crm.apiCpq.pricing.get_selling_price_from_total_cost', i_total_cost =  doc.price_list_rate)
                
                # Fetch the existing item price for the current price list
                l_item_price_doc = fn_get_item_price_document(doc.item_code, ld_price_list.name)
                
                # If an existing Item Price is found, update it
                if l_item_price_doc:
                    ld_price_list_item_price = frappe.get_doc('Item Price', l_item_price_doc.name)
                    ld_price_list_item_price.price_list_rate = selling_price.get("selling")
                    ld_price_list_item_price.save()
                
                # Otherwise, create a new Item Price
                else:
                    ld_target_item_price = frappe.copy_doc(doc)
                    ld_target_item_price.price_list = ld_price_list.name
                    ld_target_item_price.price_list_rate = selling_price.get("selling")
                    ld_target_item_price.insert()