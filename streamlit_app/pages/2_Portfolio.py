# import streamlit as st
# from snowflake.snowpark.context import get_active_session

# st.set_page_config(page_title="Portfolio Analysis", page_icon="📁", layout="wide")

# # Get active Snowpark session
# session = get_active_session()

# st.title("📁 Loan Portfolio & Mix Analysis")
# st.markdown("Analyze outstanding loan principal, product distributions, security types, and portfolio health[cite: 1].")

# # --- HIGH-LEVEL METRICS ---
# portfolio_summary_query = """
#     SELECT 
#         COUNT(DISTINCT LOAN_ID) AS ACTIVE_LOANS,
#         SUM(PRINCIPAL_AMOUNT) AS TOTAL_PRINCIPAL,
#         AVG(INTEREST_RATE) AS AVG_RATE,
#         AVG(TENURE_MONTHS) AS AVG_TENURE
#     FROM LOAN_MGMT_DB.SEM.V_PORTFOLIO_SUMMARY
# """
# summary_res = session.sql(portfolio_summary_query).collect()[0]
# active_loans = summary_res["ACTIVE_LOANS"] or 0
# total_principal = summary_res["TOTAL_PRINCIPAL"] or 0
# avg_rate = summary_res["AVG_RATE"] or 0
# avg_tenure = summary_res["AVG_TENURE"] or 0

# col1, col2, col3, col4 = st.columns(4)
# col1.metric("Active Loans", f"{active_loans:,}")
# col2.metric("Total Principal Portfolio", f"₹{total_principal:,.2f}")
# col3.metric("Avg Interest Rate", f"{avg_rate:.2f}%")
# col4.metric("Avg Tenure (Months)", f"{avg_tenure:.1f}")

# st.markdown("---")

# # --- CHARTS SECTION ---
# col_left, col_right = st.columns(2)

# with col_left:
#     st.subheader("📊 Portfolio Mix by Loan Type")
#     loan_type_query = """
#         SELECT LOAN_TYPE, SUM(PRINCIPAL_AMOUNT) AS PRINCIPAL_SUM
#         FROM LOAN_MGMT_DB.SEM.V_PORTFOLIO_SUMMARY
#         GROUP BY LOAN_TYPE
#     """
#     loan_type_df = session.sql(loan_type_query).to_pandas()
#     if not loan_type_df.empty:
#         st.bar_chart(loan_type_df.set_index("LOAN_TYPE"))
#     else:
#         st.info("No loan type data found.")

# with col_right:
#     st.subheader("🛡️ Portfolio Mix by Security Type")
#     security_query = """
#         SELECT SECURITY_TYPE, SUM(PRINCIPAL_AMOUNT) AS PRINCIPAL_SUM
#         FROM LOAN_MGMT_DB.SEM.V_PORTFOLIO_SUMMARY
#         GROUP BY SECURITY_TYPE
#     """
#     security_df = session.sql(security_query).to_pandas()
#     if not security_df.empty:
#         st.bar_chart(security_df.set_index("SECURITY_TYPE"))
#     else:
#         st.info("No security type data found.")

# st.markdown("---")

# # --- GRANULAR PORTFOLIO TABLE ---
# st.subheader("📋 Detailed Portfolio Breakdown")
# detail_query = """
#     SELECT * 
#     FROM LOAN_MGMT_DB.SEM.V_PORTFOLIO_SUMMARY
# """
# detail_df = session.sql(detail_query).to_pandas()
# st.dataframe(detail_df, use_container_width=True)



import streamlit as st
from connection import get_session


st.set_page_config(
    page_title="Portfolio Analysis",
    page_icon="📁",
    layout="wide"
)

# Get local Snowpark session
session = get_session()


st.title("📁 Loan Portfolio & Mix Analysis")

st.markdown(
    "Analyze outstanding loan principal, product distributions, "
    "security types, and portfolio health."
)


# ============================================================
# Create one row per loan
# ============================================================

loan_level_cte = """
WITH loan_level AS (
    SELECT
        LOAN_ID,
        LOAN_TYPE,
        SECURITY_TYPE,
        LOAN_STATUS,
        PRINCIPAL_AMOUNT,
        INTEREST_RATE,
        TENURE_MONTHS,
        DATE_VALUE
    FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
    WHERE LOAN_ID IS NOT NULL
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY LOAN_ID
        ORDER BY DATE_VALUE DESC, TXN_ID DESC, TXN_LINE_ID DESC
    ) = 1
)
"""


# ============================================================
# HIGH-LEVEL METRICS
# ============================================================

portfolio_summary_query = loan_level_cte + """
SELECT
    COUNT(DISTINCT CASE
        WHEN LOAN_STATUS = 'ACTIVE' THEN LOAN_ID
    END) AS ACTIVE_LOANS,

    COALESCE(
        SUM(CASE
            WHEN LOAN_STATUS = 'ACTIVE' THEN PRINCIPAL_AMOUNT
        END),
        0
    ) AS TOTAL_PRINCIPAL,

    COALESCE(
        AVG(CASE
            WHEN LOAN_STATUS = 'ACTIVE' THEN INTEREST_RATE
        END),
        0
    ) AS AVG_RATE,

    COALESCE(
        AVG(CASE
            WHEN LOAN_STATUS = 'ACTIVE' THEN TENURE_MONTHS
        END),
        0
    ) AS AVG_TENURE

FROM loan_level
"""

summary_res = session.sql(portfolio_summary_query).collect()[0]

active_loans = summary_res["ACTIVE_LOANS"] or 0
total_principal = summary_res["TOTAL_PRINCIPAL"] or 0
avg_rate = summary_res["AVG_RATE"] or 0
avg_tenure = summary_res["AVG_TENURE"] or 0


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Active Loans",
    f"{active_loans:,}"
)

col2.metric(
    "Total Principal Portfolio",
    f"₹{total_principal:,.2f}"
)

col3.metric(
    "Avg Interest Rate",
    f"{avg_rate:.2f}%"
)

col4.metric(
    "Avg Tenure (Months)",
    f"{avg_tenure:.1f}"
)


st.markdown("---")


# ============================================================
# CHARTS
# ============================================================

col_left, col_right = st.columns(2)


# ------------------------------------------------------------
# Portfolio Mix by Loan Type
# ------------------------------------------------------------

with col_left:

    st.subheader("📊 Portfolio Mix by Loan Type")

    loan_type_query = loan_level_cte + """
    SELECT
        LOAN_TYPE,
        SUM(PRINCIPAL_AMOUNT) AS PRINCIPAL_SUM
    FROM loan_level
    WHERE LOAN_STATUS = 'ACTIVE'
    GROUP BY LOAN_TYPE
    ORDER BY PRINCIPAL_SUM DESC
    """

    loan_type_df = session.sql(loan_type_query).to_pandas()

    if not loan_type_df.empty:
        st.bar_chart(
            loan_type_df.set_index("LOAN_TYPE")
        )
    else:
        st.info("No loan type data found.")


# ------------------------------------------------------------
# Portfolio Mix by Security Type
# ------------------------------------------------------------

with col_right:

    st.subheader("🛡️ Portfolio Mix by Security Type")

    security_query = loan_level_cte + """
    SELECT
        SECURITY_TYPE,
        SUM(PRINCIPAL_AMOUNT) AS PRINCIPAL_SUM
    FROM loan_level
    WHERE LOAN_STATUS = 'ACTIVE'
    GROUP BY SECURITY_TYPE
    ORDER BY PRINCIPAL_SUM DESC
    """

    security_df = session.sql(security_query).to_pandas()

    if not security_df.empty:
        st.bar_chart(
            security_df.set_index("SECURITY_TYPE")
        )
    else:
        st.info("No security type data found.")


st.markdown("---")


# ============================================================
# LOAN STATUS DISTRIBUTION
# ============================================================

st.subheader("📈 Portfolio Health by Loan Status")

status_query = loan_level_cte + """
SELECT
    LOAN_STATUS,
    COUNT(*) AS LOAN_COUNT,
    SUM(PRINCIPAL_AMOUNT) AS PRINCIPAL_AMOUNT
FROM loan_level
GROUP BY LOAN_STATUS
ORDER BY PRINCIPAL_AMOUNT DESC
"""

status_df = session.sql(status_query).to_pandas()

if not status_df.empty:

    col_status1, col_status2 = st.columns(2)

    with col_status1:
        st.bar_chart(
            status_df.set_index("LOAN_STATUS")["LOAN_COUNT"]
        )

    with col_status2:
        st.bar_chart(
            status_df.set_index("LOAN_STATUS")["PRINCIPAL_AMOUNT"]
        )

else:
    st.info("No loan status data found.")


st.markdown("---")


# ============================================================
# DETAILED PORTFOLIO TABLE
# ============================================================

st.subheader("📋 Detailed Portfolio Breakdown")

detail_query = loan_level_cte + """
SELECT
    LOAN_ID,
    LOAN_TYPE,
    SECURITY_TYPE,
    LOAN_STATUS,
    PRINCIPAL_AMOUNT,
    INTEREST_RATE,
    TENURE_MONTHS,
    DATE_VALUE AS LATEST_TRANSACTION_DATE
FROM loan_level
ORDER BY PRINCIPAL_AMOUNT DESC
"""

detail_df = session.sql(detail_query).to_pandas()

if not detail_df.empty:
    st.dataframe(
        detail_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No portfolio data found.")
