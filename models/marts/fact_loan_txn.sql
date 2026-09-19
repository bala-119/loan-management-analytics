    {{
        config(
            materialized='incremental',
            unique_key=['TXN_ID', 'TXN_LINE_ID']
        )
    }}

    SELECT 
        t.TXN_ID,
        t.TXN_LINE_ID,
        COALESCE(d.SK_DATE, 19700101) AS SK_DATE,
        COALESCE(b.SK_BORROWER, -1) AS SK_BORROWER,
        COALESCE(l.SK_LOAN, -1) AS SK_LOAN,
        COALESCE(br.SK_BRANCH, -1) AS SK_BRANCH,
        t.TXN_DATE,
        t.TXN_TYPE,
        t.AMOUNT,
        t.INTEREST_COMPONENT,
        t.FEE_COMPONENT,
        t.PAYMENT_MODE,
        t.TXN_STATUS,
        t.LOAD_TS
    FROM {{ ref('stg_loan_txn') }} t
    LEFT JOIN {{ ref('dim_date') }} d ON t.TXN_DATE = d.DATE_VALUE
    LEFT JOIN {{ ref('dim_borrower_snapshot') }} b 
        ON t.BORROWER_ID = b.BORROWER_ID AND b.dbt_valid_to IS NULL -- Active record
    LEFT JOIN {{ ref('dim_loan_snapshot') }} l 
        ON t.LOAN_ID = l.LOAN_ID AND l.dbt_valid_to IS NULL
    LEFT JOIN {{ ref('dim_branch') }} br 
        ON t.BRANCH_ID = br.BRANCH_ID

    {% if is_incremental() %}
    WHERE t.LOAD_TS > (SELECT MAX(LOAD_TS) FROM {{ this }})
    {% endif %}