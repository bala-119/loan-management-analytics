{% snapshot dim_loan_snapshot %}

{{
    config(
      target_database='LOAN_MGMT_DB',
      target_schema='EDW',
      unique_key='LOAN_ID',
      strategy='check',
      check_cols=[
        'LOAN_TYPE',
        'PRINCIPAL_AMOUNT',
        'INTEREST_RATE',
        'TENURE_MONTHS',
        'LOAN_STATUS',
        'SECURITY_TYPE'
      ],
      invalidate_hard_deletes=True
    )
}}

SELECT
    ABS(HASH(LOAN_ID)) AS SK_LOAN,
    LOAN_ID,
    BORROWER_ID,
    BRANCH_ID,
    LOAN_TYPE,
    PRINCIPAL_AMOUNT,
    INTEREST_RATE,
    TENURE_MONTHS,
    DISBURSE_DATE,
    LOAN_STATUS,
    SECURITY_TYPE,
    UPDATED_AT,
    LOAD_TS
FROM {{ ref('stg_loans') }}

{% endsnapshot %}