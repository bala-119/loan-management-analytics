{{ config(materialized='view') }}

SELECT 
    t.TXN_ID,
    t.TXN_LINE_ID,
    d.DATE_VALUE,
    d.YEAR,
    d.QUARTER,
    d.MONTH,
    b.BRANCH_ID,
    b.BRANCH_NAME,
    b.REGION,
    b.CITY AS BRANCH_CITY,
    b.STATE AS BRANCH_STATE,
    br.BORROWER_ID,
    br.FIRST_NAME || ' ' || br.LAST_NAME AS BORROWER_NAME,
    br.SEGMENT AS BORROWER_SEGMENT,
    br.EMPLOYMENT_TYPE,
    l.LOAN_ID,
    l.LOAN_TYPE,
    l.PRINCIPAL_AMOUNT,
    l.INTEREST_RATE,
    l.TENURE_MONTHS,
    l.LOAN_STATUS,
    l.SECURITY_TYPE,
    t.TXN_TYPE,
    t.AMOUNT,
    t.INTEREST_COMPONENT,
    t.FEE_COMPONENT,
    t.PAYMENT_MODE,
    t.TXN_STATUS
FROM {{ ref('fact_loan_txn') }} t
LEFT JOIN {{ ref('dim_date') }} d ON t.SK_DATE = d.SK_DATE
LEFT JOIN {{ ref('dim_branch') }} b ON t.SK_BRANCH = b.SK_BRANCH
LEFT JOIN {{ ref('dim_borrower_snapshot') }} br ON t.SK_BORROWER = br.SK_BORROWER AND br.dbt_valid_to IS NULL
LEFT JOIN {{ ref('dim_loan_snapshot') }} l ON t.SK_LOAN = l.SK_LOAN AND l.dbt_valid_to IS NULL