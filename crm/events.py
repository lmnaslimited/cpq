import frappe

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
                
                selling_price = frappe.call('crm.api.pricingApi.get_selling_price_from_total_cost', doc = {"total_cost": doc.price_list_rate})
                
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