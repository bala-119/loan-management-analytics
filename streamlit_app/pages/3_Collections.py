# import streamlit as st
# from snowflake.snowpark.context import get_active_session

# st.set_page_config(page_title="Collections & Delinquency", page_icon="💳", layout="wide")

# # Get active Snowpark session
# session = get_active_session()

# st.title("💳 Collections & Delinquency Signals")
# st.markdown("Analyze collection performance by payment mode, transaction success rates, and early delinquency signals[cite: 1].")

# # --- SUMMARY METRICS ---
# metrics_query = """
#     SELECT 
#         SUM(CASE WHEN TXN_TYPE = 'EMI_PAYMENT' AND TXN_STATUS = 'SUCCESS' THEN AMOUNT ELSE 0 END) AS SUCCESSFUL_COLLECTIONS,
#         SUM(CASE WHEN TXN_TYPE = 'EMI_PAYMENT' AND TXN_STATUS <> 'SUCCESS' THEN AMOUNT ELSE 0 END) AS FAILED_OR_MISSED_AMOUNT,
#         COUNT(CASE WHEN TXN_TYPE = 'EMI_PAYMENT' AND TXN_STATUS = 'SUCCESS' THEN 1 END) AS SUCCESS_COUNT,
#         COUNT(CASE WHEN TXN_TYPE = 'EMI_PAYMENT' AND TXN_STATUS <> 'SUCCESS' THEN 1 END) AS FAILED_COUNT
#     FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
# """
# res = session.sql(metrics_query).collect()[0]
# success_coll = res["SUCCESS_COLLECTIONS"] or 0
# failed_amt = res["FAILED_OR_MISSED_AMOUNT"] or 0
# success_cnt = res["SUCCESS_COUNT"] or 0
# failed_cnt = res["FAILED_COUNT"] or 0
# total_attempts = success_cnt + failed_cnt
# collection_efficiency = (success_cnt / total_attempts * 100) if total_attempts > 0 else 0

# col1, col2, col3, col4 = st.columns(4)
# col1.metric("Successful Collections", f"₹{success_coll:,.2f}")
# col2.metric("Missed/Failed Amount", f"₹{failed_amt:,.2f}")
# col3.metric("Collection Efficiency", f"{collection_efficiency:.1f}%")
# col4.metric("Failed Payment Events", f"{failed_cnt:,}")

# st.markdown("---")

# # --- CHARTS SECTION ---
# col_left, col_right = st.columns(2)

# with col_left:
#     st.subheader("📊 Collections by Payment Mode")
#     mode_query = """
#         SELECT PAYMENT_MODE, SUM(AMOUNT) AS TOTAL_AMOUNT
#         FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
#         WHERE TXN_TYPE = 'EMI_PAYMENT' AND TXN_STATUS = 'SUCCESS'
#         GROUP BY PAYMENT_MODE
#     """
#     mode_df = session.sql(mode_query).to_pandas()
#     if not mode_df.empty:
#         st.bar_chart(mode_df.set_index("PAYMENT_MODE"))
#     else:
#         st.info("No successful payment mode data available.")

# with col_right:
#     st.subheader("⚠️ Transaction Status Breakdown")
#     status_query = """
#         SELECT TXN_STATUS, COUNT(*) AS EVENT_COUNT
#         FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
#         WHERE TXN_TYPE = 'EMI_PAYMENT'
#         GROUP BY TXN_STATUS
#     """
#     status_df = session.sql(status_query).to_pandas()
#     if not status_df.empty:
#         st.bar_chart(status_df.set_index("TXN_STATUS"))
#     else:
#         st.info("No transaction status data found.")

# st.markdown("---")

# # --- DELINQUENCY / MISSED PAYMENTS TABLE ---
# st.subheader("🚨 Delinquency / Missed Payment Watchlist")
# watchlist_query = """
#     SELECT 
#         DATE_VALUE,
#         BRANCH_NAME,
#         BORROWER_NAME,
#         LOAN_ID,
#         PAYMENT_MODE,
#         AMOUNT,
#         TXN_STATUS
#     FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
#     WHERE TXN_TYPE = 'EMI_PAYMENT' AND TXN_STATUS <> 'SUCCESS'
#     ORDER BY DATE_VALUE DESC
# """
# watchlist_df = session.sql(watchlist_query).to_pandas()
# if not watchlist_df.empty:
#     st.dataframe(watchlist_df, use_container_width=True)
# else:
#     st.success("No missed or failed payments recorded. Portfolio collection health is 100%.")


import streamlit as st
from connection import get_session


st.set_page_config(
    page_title="Collections & Delinquency",
    page_icon="💰",
    layout="wide"
)

session = get_session()

st.title("💰 Collections & Delinquency")

st.markdown(
    "Analyze collection performance by payment mode, "
    "transaction success rates, and missed payment signals."
)


# ============================================================
# COLLECTION SUMMARY
# ============================================================

collection_summary_query = """
SELECT
    COALESCE(
        SUM(
            CASE
                WHEN TXN_TYPE = 'EMI_PAYMENT'
                 AND TXN_STATUS = 'SUCCESS'
                THEN AMOUNT
                ELSE 0
            END
        ),
        0
    ) AS SUCCESS_COLLECTIONS,

    COALESCE(
        SUM(
            CASE
                WHEN TXN_TYPE = 'EMI_PAYMENT'
                 AND TXN_STATUS != 'SUCCESS'
                THEN AMOUNT
                ELSE 0
            END
        ),
        0
    ) AS FAILED_COLLECTIONS,

    COUNT_IF(
        TXN_TYPE = 'EMI_PAYMENT'
        AND TXN_STATUS = 'SUCCESS'
    ) AS SUCCESSFUL_PAYMENTS,

    COUNT_IF(
        TXN_TYPE = 'EMI_PAYMENT'
        AND TXN_STATUS != 'SUCCESS'
    ) AS FAILED_PAYMENTS

FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
"""

res = session.sql(collection_summary_query).collect()[0]

success_coll = res["SUCCESS_COLLECTIONS"] or 0
failed_coll = res["FAILED_COLLECTIONS"] or 0
successful_payments = res["SUCCESSFUL_PAYMENTS"] or 0
failed_payments = res["FAILED_PAYMENTS"] or 0


# ============================================================
# COLLECTION EFFICIENCY
# ============================================================

total_payments = successful_payments + failed_payments

if total_payments > 0:
    collection_efficiency = (
        successful_payments / total_payments
    ) * 100
else:
    collection_efficiency = 0


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Successful Collections",
    f"₹{success_coll:,.2f}"
)

col2.metric(
    "Failed Collections",
    f"₹{failed_coll:,.2f}"
)

col3.metric(
    "Collection Efficiency",
    f"{collection_efficiency:.2f}%"
)

col4.metric(
    "Failed Payments",
    f"{failed_payments:,}"
)


st.markdown("---")


# ============================================================
# COLLECTIONS BY PAYMENT MODE
# ============================================================

st.subheader("💳 Collections by Payment Mode")

payment_mode_query = """
SELECT
    PAYMENT_MODE,
    SUM(AMOUNT) AS COLLECTION_AMOUNT
FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
WHERE TXN_TYPE = 'EMI_PAYMENT'
  AND TXN_STATUS = 'SUCCESS'
GROUP BY PAYMENT_MODE
ORDER BY COLLECTION_AMOUNT DESC
"""

payment_mode_df = session.sql(
    payment_mode_query
).to_pandas()

if not payment_mode_df.empty:
    st.bar_chart(
        payment_mode_df.set_index("PAYMENT_MODE")
    )
else:
    st.info("No successful collection data found.")


st.markdown("---")


# ============================================================
# PAYMENT STATUS
# ============================================================

st.subheader("📊 Payment Status")

status_query = """
SELECT
    TXN_STATUS,
    COUNT(*) AS PAYMENT_COUNT,
    SUM(AMOUNT) AS PAYMENT_AMOUNT
FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
WHERE TXN_TYPE = 'EMI_PAYMENT'
GROUP BY TXN_STATUS
ORDER BY PAYMENT_AMOUNT DESC
"""

status_df = session.sql(status_query).to_pandas()

if not status_df.empty:

    col_left, col_right = st.columns(2)

    with col_left:
        st.bar_chart(
            status_df.set_index("TXN_STATUS")["PAYMENT_COUNT"]
        )

    with col_right:
        st.bar_chart(
            status_df.set_index("TXN_STATUS")["PAYMENT_AMOUNT"]
        )

else:
    st.info("No payment status data found.")


st.markdown("---")


# ============================================================
# FAILED PAYMENT WATCHLIST
# ============================================================

st.subheader("⚠️ Failed Payment Watchlist")

failed_query = """
SELECT
    DATE_VALUE,
    BRANCH_NAME,
    BORROWER_NAME,
    LOAN_ID,
    PAYMENT_MODE,
    AMOUNT,
    TXN_STATUS
FROM LOAN_MGMT_DB.STG.SEM_FACT_LOAN_TXN
WHERE TXN_TYPE = 'EMI_PAYMENT'
  AND TXN_STATUS != 'SUCCESS'
ORDER BY DATE_VALUE DESC, AMOUNT DESC
LIMIT 100
"""

failed_df = session.sql(
    failed_query
).to_pandas()

if not failed_df.empty:

    st.dataframe(
        failed_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "No missed or failed payments recorded. "
        "Portfolio collection health is 100%."
    )

