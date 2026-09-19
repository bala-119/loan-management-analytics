# import streamlit as st


# st.set_page_config(page_title="Loan Management Analytics", page_icon="🏦", layout="wide")

# # Get Snowpark active session
# from connection import get_session

# session = get_session()

# st.title("🏦 Loan Management Analytics Platform")
# st.markdown("Welcome to the executive command center. Use the sidebar to navigate through portfolio performance, collections, and granular drilldowns[cite: 1].")

# # High-level metrics quick view
# total_disb_query = """
#     SELECT SUM(AMOUNT) AS VAL FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN WHERE TXN_TYPE = 'DISBURSEMENT'
# """
# total_coll_query = """
#     SELECT SUM(AMOUNT) AS VAL FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN WHERE TXN_TYPE = 'EMI_PAYMENT' AND TXN_STATUS = 'SUCCESS'
# """

# disb_val = session.sql(total_disb_query).collect()[0]['VAL'] or 0
# coll_val = session.sql(total_coll_query).collect()[0]['VAL'] or 0

# col1, col2, col3 = st.columns(3)
# col1.metric("Total Disbursements", f"₹{disb_val:,.2f}")
# col2.metric("Total Collections", f"${coll_val:,.2f}")
# col3.metric("Net Cashflow", f"${(coll_val - disb_val):,.2f}")



import streamlit as st
from connection import get_session


st.set_page_config(
    page_title="Loan Management Analytics",
    page_icon="🏦",
    layout="wide"
)

# Get Snowpark session
session = get_session()

st.title("🏦 Loan Management Analytics Platform")

st.markdown(
    "Welcome to the executive command center. "
    "Use the sidebar to navigate through portfolio performance, "
    "collections, and granular drilldowns."
)

# High-level metrics
total_disb_query = """
    SELECT SUM(AMOUNT) AS VAL
    FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
    WHERE TXN_TYPE = 'DISBURSEMENT'
"""

total_coll_query = """
    SELECT SUM(AMOUNT) AS VAL
    FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
    WHERE TXN_TYPE = 'EMI_PAYMENT'
      AND TXN_STATUS = 'SUCCESS'
"""

disb_val = session.sql(total_disb_query).collect()[0]["VAL"] or 0
coll_val = session.sql(total_coll_query).collect()[0]["VAL"] or 0

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Disbursements",
    f"₹{disb_val:,.2f}"
)

col2.metric(
    "Total Collections",
    f"₹{coll_val:,.2f}"
)

col3.metric(
    "Net Cashflow",
    f"₹{(coll_val - disb_val):,.2f}"
)

