import frappe

def get_warehouse_based_material_request_conditions(user=None):

    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)
    
    # 1. Full access for Admin/System Manager/Purchase Manager/GM
    if (user == "Administrator" or 
        "System Manager" in user_roles or
        "Purchase Manager" in user_roles or
        "GM" in user_roles):
        return ""

    # 2. Material Requestor Approver - Department-based access (priority access)
    if "Material Requestor Approver" in user_roles:
        departments = frappe.db.sql_list("""
            SELECT for_value 
            FROM `tabUser Permission`
            WHERE user=%s 
            AND allow='Department'
            AND (applicable_for IS NULL OR applicable_for='' OR applicable_for='Material Request')
        """, user)

        if departments:
            # Can always see their department's requests regardless of status
            return f"`tabMaterial Request`.`custom_requested_for` IN ({','.join(frappe.db.escape(d) for d in departments)})"

    # 3. Property Head/Stock Manager access (only approved/verified)
    if "Property Head" in user_roles or "Stock Manager" in user_roles:
        return """(`tabMaterial Request`.`custom_mr_request_approval_status` = 'Material Request Approved'
                 OR `tabMaterial Request`.`workflow_state` = 'Stock Balance Verified')"""

    # 4. Stock User/Material Request Issuer (warehouse-based, no drafts)
    if "Stock User" in user_roles or "Material Request Issuer" in user_roles:
        warehouses = frappe.db.sql_list("""
            SELECT for_value 
            FROM `tabUser Permission`
            WHERE user=%s 
            AND allow='Warehouse'
            AND (applicable_for IS NULL OR applicable_for='' OR applicable_for='Material Request')
        """, user)

        if warehouses:
            return f"""
                (`tabMaterial Request`.`custom_request_from_warehouse` IN ({','.join(frappe.db.escape(w) for w in warehouses)})
                AND `tabMaterial Request`.`workflow_state` != 'Draft')
            """
    
    # 5. Default: no access
    return "1=0"