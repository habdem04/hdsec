import frappe

def get_permission_query_conditions(user=None):
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)
    
    # 1. Full access for Admin/System Manager
    if user == "Administrator" or "System Manager"  or "Property Head"  in user_roles:
        return ""

    # 2. Department-based access for Material Requestor (NEW CONDITION)
    if "Material Requestor" in user_roles:
        departments = frappe.db.sql_list("""
            SELECT for_value 
            FROM `tabUser Permission`
            WHERE user=%s 
            AND allow='Department'
            AND (applicable_for IS NULL OR applicable_for='' OR applicable_for='Material Request')
        """, user)

        if departments:
            return f"`tabMaterial Request`.`custom_requested_for` IN ({','.join(frappe.db.escape(d) for d in departments)})"
        return "1=0"

    # 3. Department-based access for Material Requestor Approver
    if "Material Requestor Approver" in user_roles:
        departments = frappe.db.sql_list("""
            SELECT for_value 
            FROM `tabUser Permission`
            WHERE user=%s 
            AND allow='Department'
            AND (applicable_for IS NULL OR applicable_for='' OR applicable_for='Material Request')
        """, user)

        if departments:
            return f"`tabMaterial Request`.`custom_requested_for` IN ({','.join(frappe.db.escape(d) for d in departments)})"
        return "1=0"

    # 4. Warehouse-based access for Stock User/Material Request Issuer
    if "Stock User" in user_roles or "Material Request Issuer" or "Store Checker" in user_roles:
        warehouses = frappe.db.sql_list("""
            SELECT for_value 
            FROM `tabUser Permission`
            WHERE user=%s 
            AND allow='Warehouse'
            AND (applicable_for IS NULL OR applicable_for='' OR applicable_for='Material Request')
        """, user)

        if warehouses:
            return f"`tabMaterial Request`.`custom_request_from_warehouse` IN ({','.join(frappe.db.escape(w) for w in warehouses)})"
        return "1=0"

    # 5. Default: no access for other roles
    return "1=0"