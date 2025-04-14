import frappe

def execute():
    # Configuration for fields in the User doctype.
    # Specify the permission level and the default value you want.
    field_configurations = {
        "social_logins": {"permlevel": "2", "default": "[]"},  # Default: empty JSON array as string
        "default_app":   {"permlevel": "2", "default": "Desk"},  # Default: "Desk"
        "defaults":      {"permlevel": "2", "default": "{}"}      # For the field 'defaults', default to an empty JSON object as string
    }

    for field, configs in field_configurations.items():
        # Create a Property Setter for permissions (permlevel)
        if not frappe.db.exists("Property Setter", {
            "doc_type": "User",
            "field_name": field,
            "property": "permlevel"
        }):
            ps_permlevel = frappe.get_doc({
                "doctype": "Property Setter",
                "doc_type": "User",
                "doctype_or_field": "DocField",  # Mandatory: Indicates this is a field-level property
                "field_name": field,
                "property": "permlevel",
                "property_type": "Int",
                "value": configs["permlevel"]
            })
            ps_permlevel.insert(ignore_permissions=True)

        # Create a Property Setter for default values
        if not frappe.db.exists("Property Setter", {
            "doc_type": "User",
            "field_name": field,
            "property": "default"
        }):
            ps_default = frappe.get_doc({
                "doctype": "Property Setter",
                "doc_type": "User",
                "doctype_or_field": "DocField",  # Mandatory for field-level default value setter
                "field_name": field,
                "property": "default",
                "property_type": "Data",
                "value": configs["default"]
            })
            ps_default.insert(ignore_permissions=True)

    frappe.db.commit()