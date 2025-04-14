import frappe
from frappe.utils import now

def update_workflow_fields(doc, method):
    """
    Update Material Request custom fields based on the current workflow state.
    All status fields are derived from doc.workflow_state.
    The currently logged-in employee is loaded from the Employee Signature doctype,
    and both the full name and signature are used to update the document.
    """
    current_user = frappe.session.user
    current_datetime = now()

    # Load the Employee Signature record for the current user.
    try:
        employee_signature = frappe.get_doc("Employee Signature", {"user": current_user})
    except Exception as e:
        frappe.throw("Employee Signature record not found for the current user.")

    # Retrieve employee details
    employee_full_name = employee_signature.get("full_name") or current_user
    employee_user_signature = employee_signature.get("signature")  # Ensure this field exists in your Employee Signature doctype

    user_roles = frappe.get_roles(current_user)

    # Helper function to check if the current user has one of the required roles
    def has_role(required_roles):
        return any(role in user_roles for role in required_roles)

    # 1. Draft – require "Material Requestor"
    if doc.workflow_state == "Draft":
        if has_role(["Material Requestor"]):
            doc.set("custom_mr_prepared_by_status", doc.workflow_state)
            doc.set("custom_mr_prepared_date", current_datetime)
            doc.set("custom_mr_requested_by", employee_full_name)
            doc.set("custom_mr_requested_by_signature", employee_user_signature)
        else:
            frappe.msgprint("Draft state update skipped: You must have the 'Material Requestor' role.")
            return

    # 2. Material Request Approved – require "Material Requestor Approver"
    elif doc.workflow_state == "Material Request Approved":
        if has_role(["Material Requestor Approver"]):
            doc.set("custom_mr_request_approval_status", doc.workflow_state)
            doc.set("custom_mr_request_approval_date", current_datetime)
            doc.set("custom_mr_request_approved_by_", employee_full_name)
            doc.set("custom_mr_request_approved_by_signature", employee_user_signature)
            if not doc.get("custom_mr_requested_by"):
                doc.set("custom_mr_requested_by", employee_full_name)
                doc.set("custom_mr_requested_by_signature", employee_user_signature)
        else:
            frappe.msgprint("Update skipped for 'Material Request Approved': Insufficient role (requires Material Requestor Approver).")
            return

    # 3. Material Request Rejected – require "Material Requestor Approver"
    elif doc.workflow_state == "Material Request Rejected":
        if has_role(["Material Requestor Approver"]):
            doc.set("custom_mr_request_approval_status", doc.workflow_state)
            doc.set("custom_mr_request_approval_date", current_datetime)
            doc.set("custom_mr_request_approved_by_", employee_full_name)
            doc.set("custom_mr_request_approved_by_signature", employee_user_signature)
        else:
            frappe.msgprint("Update skipped for 'Material Request Rejected': Insufficient role.")
            return

    # 4. MR Reviewed by Requestor – require "Material Requestor"
    elif doc.workflow_state == "MR Reviewed by Requestor":
        if has_role(["Material Requestor"]):
            doc.set("custom_mr_prepared_by_status", doc.workflow_state)
            doc.set("custom_mr_prepared_date", current_datetime)
            doc.set("custom_mr_requested_by", employee_full_name)
            doc.set("custom_mr_requested_by_signature", employee_user_signature)
        else:
            frappe.msgprint("Update skipped for 'MR Reviewed by Requestor': Insufficient role.")
            return

    # 5. Stock Verification – require ("Stock User" or "Store Checker")
    elif doc.workflow_state in ["MR Request Verified and Accepted", "MR Request Verified and Not Accepted", "MR Reviewed By Stock Cheker"]:
        if has_role(["Stock User", "Store Checker"]):
            doc.set("custom_mr_stock_verification_status", doc.workflow_state)
            doc.set("custom_mr_stock_verification_date", current_datetime)
            doc.set("custom_mr_stock_verified_by", employee_full_name)
            doc.set("custom_mr_stock_verified_by_signature", employee_user_signature)
        else:
            frappe.msgprint("Update skipped for stock verification: Insufficient role (requires Stock User or Store Checker).")
            return

    # 6. Stock Approval – require ("Property Head" or "Stock Manager")
    elif doc.workflow_state in ["MR Approved By Property Head", "PR Approved By Property Head"]:
        if has_role(["Property Head", "Stock Manager"]):
            doc.set("custom_mr_stock_approval_status", doc.workflow_state)
            doc.set("custom_mr_stock_approval_date", current_datetime)
            doc.set("custom_mr_stock_approved_by", employee_full_name)
            doc.set("custom_mr_stock_approved_by_signature", employee_user_signature)
        else:
            frappe.msgprint("Update skipped for stock approval: Insufficient role (requires Property Head or Stock Manager).")
            return

    # 7. Stock Rejection – require ("Property Head" or "Stock Manager")
    elif doc.workflow_state in ["MR Rejected By Property Head", "PR Rejected By Property Head"]:
        if has_role(["Property Head", "Stock Manager"]):
            doc.set("custom_mr_stock_approval_status", doc.workflow_state)
            doc.set("custom_mr_stock_approval_date", current_datetime)
            doc.set("custom_mr_stock_approved_by", employee_full_name)
            doc.set("custom_mr_stock_approved_by_signature", employee_user_signature)
        else:
            frappe.msgprint("Update skipped for stock rejection: Insufficient role.")
            return

    # 8. Approved/Rejected PR – require "Purchase Manager"
    elif doc.workflow_state in ["Approved PR", "Rejected PR"]:
        if has_role(["Purchase Manager"]):
            doc.set("custom_pr_approval_status", doc.workflow_state)
            doc.set("custom_pr_approval_date", current_datetime)
            doc.set("custom_pr_approved_by", employee_full_name)
            doc.set("custom_pr_approved_by_signature", employee_user_signature)
        else:
            frappe.msgprint("Update skipped for PR approval/rejection: Insufficient role (requires Purchase Manager).")
            return

    # 9. Authorized/Unauthorized PR – require "GM"
    elif doc.workflow_state in ["Authorized PR", "Unauthorized PR"]:
        if has_role(["GM"]):
            doc.set("custom_authorization_status", doc.workflow_state)
            doc.set("custom_pr_authorization_date", current_datetime)
            doc.set("custom_pr_authorized_by", employee_full_name)
            doc.set("custom_pr_authorized_by_signature", employee_user_signature)
        else:
            frappe.msgprint("Update skipped for PR authorization: Insufficient role (requires GM).")
            return

    frappe.logger().info(
        f"[Workflow Update] Document '{doc.name}' updated to state '{doc.workflow_state}' by employee {employee_full_name}"
    )