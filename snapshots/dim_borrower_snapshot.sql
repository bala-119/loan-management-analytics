{% snapshot dim_borrower_snapshot %}

{{
    config(
      target_database='LOAN_MGMT_DB',
      target_schema='EDW',
      unique_key='BORROWER_ID',
      strategy='check',
      check_cols=[
        'FIRST_NAME',
        'LAST_NAME',
        'EMAIL',
        'PHONE',
        'SEGMENT',
        'CITY',
        'STATE',
        'EMPLOYMENT_TYPE'
      ],
      invalidate_hard_deletes=True
    )
}}

SELECT
    ABS(HASH(BORROWER_ID)) AS SK_BORROWER,
    BORROWER_ID,
    FIRST_NAME,
    LAST_NAME,
    EMAIL,
    PHONE,
    SEGMENT,
    CITY,
    STATE,
    COUNTRY,
    DOB,
    EMPLOYMENT_TYPE,
    LOAD_TS
FROM {{ ref('stg_borrowers') }}

{% endsnapshot %}