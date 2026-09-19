import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Transaction Explorer", page_icon="🔍", layout="wide")

# Get active Snowpark session
session = get_active_session()

st.title("🔍 Transaction Explorer & Drilldown")
st.markdown("Search, filter, and export granular loan transaction records.")

# --- SEARCH & FILTER CONTROLS ---
col1, col2, col3 = st.columns(3)

with col1:
    search_borrower = st.text_input("Filter by Borrower Name")
with col2:
    search_loan_id = st.text_input("Filter by Loan ID")
with col3:
    txn_type_filter = st.selectbox("Transaction Type", ["All", "DISBURSEMENT", "EMI_PAYMENT"])

# Build query dynamically based on search inputs
query = """
    SELECT 
        TXN_ID, TXN_LINE_ID, DATE_VALUE, BRANCH_NAME, 
        BORROWER_NAME, LOAN_ID, LOAN_TYPE, TXN_TYPE, 
        AMOUNT, INTEREST_COMPONENT, FEE_COMPONENT, 
        PAYMENT_MODE, TXN_STATUS
    FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
    WHERE 1=1
"""

if search_borrower:
    query += f" AND ILIKE(BORROWER_NAME, '%{search_borrower}%')"
if search_loan_id:
    query += f" AND ILIKE(LOAN_ID, '%{search_loan_id}%')"
if txn_type_filter != "All":
    query += f" and TXN_TYPE = '{txn_type_filter}'"

query += " ORDER BY DATE_VALUE DESC LIMIT 1000"

# Fetch data as pandas dataframe
df = session.sql(query).to_pandas()

# --- DISPLAY RESULTS & EXPORT ---
st.markdown(f"**Showing {len(df)} matching transactions (capped at 1,000)**")
st.dataframe(df, use_container_width=True)



if not df.empty:
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Transactions as CSV",
        data=csv_data,
        file_name="loan_transactions_export.csv",
        mime="text/csv"
    )

