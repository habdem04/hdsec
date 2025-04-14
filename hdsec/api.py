import frappe

@frappe.whitelist()
def get_default_letterhead(company=None):
    """
    Returns the default Letter Head.
    For your configuration, it always returns 'MR'.
    """
    return "MR"

@frappe.whitelist()
def get_default_print_format(company=None):
    """
    Returns the default Print Format.
    For your configuration, it always returns 'MR'.
    """
    return "MR"