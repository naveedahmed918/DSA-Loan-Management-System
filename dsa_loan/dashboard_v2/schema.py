"""Single place that names the DocTypes and status values the Admin dashboard reads.

Everything here comes from the live schema dump of this site (dsa_schema.json). If a DocType or
field is renamed, change it here and nowhere else. Other dashboards (DSA, Lender, Franchise,
Accounts) can import the same constants.
"""

CUSTOMER = "Loan Customer"
LOAN_APP = "Customer Loan Application"
LENDER = "Lender"
LENDER_TYPE = "Lender Type"
PRODUCT = "Lender Loan Product"
LENDER_APP = "Lender Application"
DISB = "Lender Disbursement"
COMM = "Lender Commission Record"
AGREEMENT = "Lender Agreement"

SALES_INVOICE = "Sales Invoice"
PAYMENT_ENTRY = "Payment Entry"
PURCHASE_INVOICE = "Purchase Invoice"

# ---- Loan Application.application_status
LOAN_STATUS_ORDER = ["Draft", "Submitted", "Under Review", "Approved", "Rejected", "Disbursed"]
LOAN_PENDING = ["Draft", "Submitted", "Under Review"]
LOAN_APPROVED = ["Approved", "Disbursed"]  # "approved" includes loans already disbursed

# ---- Lender Application.application_status
LAPP_NOT_SUBMITTED = ["Draft", "Withdrawn"]
LAPP_AWAITING = ["Submitted", "Under Review"]
LAPP_APPROVED = ["Approved", "Sanctioned", "Disbursed"]  # "approved or beyond"
LAPP_REVIEW = ["Submitted", "Under Review", "Documents Required"]

# ---- Lender Disbursement.disbursement_status
DISB_DONE = "Processed"

# ---- Lender Commission Record.commission_status
COMM_CANCELLED = "Cancelled"
COMM_OPEN = ["Pending", "Invoiced", "Partially Paid"]
COMM_INVOICED = ["Invoiced", "Partially Paid"]

# ---- Lender.lender_status (a Link to Lender Status)
LENDER_ACTIVE = "Active"

DEFAULT_COMPANY = "DSA Loan Services"
PAGE = "dsa-admin-dashboard-v2"
