{{ config(materialized='table') }}

SELECT
    ROW_NUMBER() OVER (ORDER BY BRANCH_ID) AS SK_BRANCH,
    BRANCH_ID,
    BRANCH_NAME,
    REGION,
    CITY,
    STATE,
    COUNTRY,
    OPEN_DATE,
    STATUS
FROM {{ ref('stg_branches') }}