import frappe

def get_permission_query_conditions(user=None):
    if not user:
        user = frappe.session.user

    # Full access for Administrator and System Manager
    roles = frappe.get_roles(user)
    if user == "Administrator" or "System Manager" in roles:
        return ""

    # Warehouse-based access for Stock User / Material Request Issuer
    if "Stock User" in roles or "Material Request Issuer" in roles:
        # 1) Get the warehouse-types the user is allowed
        allowed_types = frappe.db.sql_list("""
            SELECT for_value
            FROM `tabUser Permission`
            WHERE user=%s
              AND allow='Warehouse Type'
        """, user)

        if not allowed_types:
            return "1=0"

        # 2) Find all Warehouses matching those types
        escaped_types = ", ".join(frappe.db.escape(val) for val in allowed_types)
        allowed_wh = frappe.db.sql_list(f"""
            SELECT name
            FROM `tabWarehouse`
            WHERE warehouse_type IN ({escaped_types})
        """)

        if not allowed_wh:
            return "1=0"

        # 3) Build an EXISTS subquery on the child table
        esc_wh_list = ", ".join(frappe.db.escape(w) for w in allowed_wh)
        return f"""
            EXISTS (
                SELECT 1
                FROM `tabStock Entry Detail` AS sed
                WHERE sed.parent = `tabStock Entry`.name
                  AND (
                    sed.s_warehouse IN ({esc_wh_list})
                    OR sed.t_warehouse IN ({esc_wh_list})
                  )
            )
        """

    # All others: no access
    return "1=0"
