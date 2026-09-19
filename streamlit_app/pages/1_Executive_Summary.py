import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Executive Summary", page_icon="📊", layout="wide")

# Get Snowpark active session
session = get_active_session()

st.title("📊 Executive Summary")
st.markdown("High-level portfolio performance, cashflows, and disbursements breakdown[cite: 1].")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Global Filters")

# Fetch filter options from semantic view
regions_df = session.sql("SELECT DISTINCT REGION FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN WHERE REGION IS NOT NULL").collect()
regions = [row["REGION"] for row in regions_df]
selected_region = st.sidebar.selectbox("Region/Branch", ["All"] + regions)

loan_types_df = session.sql("SELECT DISTINCT LOAN_TYPE FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN WHERE LOAN_TYPE IS NOT NULL").collect()
loan_types = [row["LOAN_TYPE"] for row in loan_types_df]
selected_loan_type = st.sidebar.selectbox("Loan Type", ["All"] + loan_types)

segments_df = session.sql("SELECT DISTINCT BORROWER_SEGMENT FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN WHERE BORROWER_SEGMENT IS NOT NULL").collect()
segments = [row["BORROWER_SEGMENT"] for row in segments_df]
selected_segment = st.sidebar.selectbox("Borrower Segment", ["All"] + segments)

# --- BUILD DYNAMIC WHERE CLAUSE ---
where_clauses = ["1=1"]
if selected_region != "All":
    where_clauses.append(f"REGION = '{selected_region}'")
if selected_loan_type != "All":
    where_clauses.append(f"LOAN_TYPE = '{selected_loan_type}'")
if selected_segment != "All":
    where_clauses.append(f"BORROWER_SEGMENT = '{selected_segment}'")

where_sql = " AND ".join(where_clauses)

# --- KPI QUERIES ---
kpi_query = f"""
    SELECT 
        SUM(CASE WHEN TXN_TYPE = 'DISBURSEMENT' THEN AMOUNT ELSE 0 END) AS TOTAL_DISB,
        SUM(CASE WHEN TXN_TYPE = 'EMI_PAYMENT' AND TXN_STATUS = 'SUCCESS' THEN AMOUNT ELSE 0 END) AS TOTAL_COLL,
        COUNT(DISTINCT CASE WHEN TXN_TYPE = 'EMI_PAYMENT' AND TXN_STATUS = 'SUCCESS' THEN TXN_ID END) AS EMI_COUNT
    FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
    WHERE {where_sql}
"""

kpi_res = session.sql(kpi_query).collect()[0]
total_disb = kpi_res["TOTAL_DISB"] or 0
total_coll = kpi_res["TOTAL_COLL"] or 0
emi_count = kpi_res["EMI_COUNT"] or 0
net_cashflow = total_coll - total_disb
avg_emi = (total_coll / emi_count) if emi_count > 0 else 0

# --- DISPLAY METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Disbursements", f"₹{total_disb:,.2f}")
col2.metric("Collections", f"₹{total_coll:,.2f}")
col3.metric("Net Cashflow", f"₹{net_cashflow:,.2f}", delta=f"{net_cashflow:,.2f}")
col4.metric("Average EMI", f"₹{avg_emi:,.2f}")

st.markdown("---")

# --- TRENDS CHART ---
st.subheader("📈 Cashflow Trend Over Time")
trend_query = f"""
    SELECT 
        DATE_VALUE,
        SUM(CASE WHEN TXN_TYPE = 'DISBURSEMENT' THEN AMOUNT ELSE 0 END) AS DISBURSEMENTS,
        SUM(CASE WHEN TXN_TYPE = 'EMI_PAYMENT' AND TXN_STATUS = 'SUCCESS' THEN AMOUNT ELSE 0 END) AS COLLECTIONS
    FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
    WHERE {where_sql}
    GROUP BY DATE_VALUE
    ORDER BY DATE_VALUE
"""
trend_df = session.sql(trend_query).to_pandas()

if not trend_df.empty:
    st.line_chart(trend_df.set_index("DATE_VALUE"))
else:
    st.info("No transaction data available for the selected filters.")
