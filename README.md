# Loan Management Analytics Platform

A modern data engineering and analytics project built using **Snowflake, dbt, Snowpipe, and Streamlit** to transform raw loan-management data into analytics-ready data models.

## 📌 Project Overview

The **Loan Management Analytics Platform** processes data related to:

* Borrowers
* Branches
* Loans
* Loan transactions / EMI payments

The project follows a layered data architecture where raw data is ingested into Snowflake, transformed using dbt, and exposed through analytics-ready fact and dimension models.

The final data can be consumed through a **Streamlit dashboard** for business analysis.

---

## 🏗️ Architecture

```text
Source CSV Files
       │
       ▼
   Landing Zone
       │
       ▼
    Snowpipe
       │
       ▼
 Raw Snowflake Tables
       │
       ▼
   dbt Staging
       │
       ▼
 Dimensions + Fact Models
       │
       ▼
 Semantic / Analytics Layer
       │
       ▼
    Streamlit
    Dashboard
```

---

## 🛠️ Technology Stack

| Technology        | Purpose                                    |
| ----------------- | ------------------------------------------ |
| **Snowflake**     | Cloud data warehouse                       |
| **Snowpipe**      | Automated data ingestion                   |
| **dbt**           | Data transformation and testing            |
| **Snowflake SQL** | Data processing and modeling               |
| **Streamlit**     | Analytics dashboard                        |
| **Git/GitHub**    | Version control                            |
| **Python**        | Streamlit application and supporting logic |

---

## 📂 Project Structure

```text
loan_mgmt_transformation/
│
├── analyses/
│
├── macros/
│
├── models/
│   ├── staging/
│   │   ├── stg_borrowers.sql
│   │   ├── stg_branches.sql
│   │   ├── stg_loans.sql
│   │   └── stg_loan_txn.sql
│   │
│   ├── dimensions/
│   │   ├── dim_date.sql
│   │   ├── dim_branch.sql
│   │   └── ...
│   │
│   └── facts/
│       ├── fact_loan_txn.sql
│       └── ...
│
├── snapshots/
│   ├── dim_borrower_snapshot.sql
│   └── dim_loan_snapshot.sql
│
├── seeds/
├── tests/
│
├── streamlit_app/
│   └── app.py
│
├── dbt_project.yml
├── .gitignore
└── README.md
```

---

## 🔄 Data Pipeline

### 1. Data Ingestion

Source files containing borrower, branch, loan, and transaction information are placed in the landing layer.

Snowpipe loads the files into Snowflake raw tables.

The ingestion process captures metadata such as:

* `LOAD_TS`
* `FILE_NAME`
* `ROW_NUMBER`

Invalid records can be redirected to a rejection/quarantine area.

---

### 2. Staging Layer

dbt staging models standardize and clean the raw data.

Examples:

```text
stg_borrowers
stg_branches
stg_loans
stg_loan_txn
```

Typical transformations include:

* Data type standardization
* Column renaming
* Null handling
* Data cleansing
* Source-level filtering

---

### 3. Dimension Models

The project creates reusable analytical dimensions such as:

```text
dim_date
dim_branch
dim_borrower
dim_loan
```

Historical changes to important entities are handled using **Slowly Changing Dimension (SCD) Type 2** snapshots where required.

This allows historical versions of borrower and loan information to be preserved.

---

### 4. Fact Model

The central transactional model is:

```text
FACT_LOAN_TXN
```

The grain of the fact table is:

```text
TXN_ID + TXN_LINE_ID
```

This represents an individual transaction line and prevents duplicate transaction-level records.

The fact model supports analysis such as:

* Loan disbursement analysis
* EMI/payment analysis
* Outstanding amounts
* Branch-level performance
* Loan-type analysis
* Borrower-segment analysis

---

## 🔁 Incremental Processing

The transaction fact model is implemented using dbt incremental processing.

Instead of rebuilding the complete fact table every time, new or changed records can be processed incrementally.

The model uses:

```text
TXN_ID + TXN_LINE_ID
```

as the unique business key.

This reduces unnecessary processing as transaction volume increases.

---

## 📸 Historical Data with SCD Type 2

The project uses dbt snapshots to maintain historical versions of selected entities.

Example:

```text
dim_borrower_snapshot
dim_loan_snapshot
```

Historical records can be tracked using fields such as:

```text
DBT_VALID_FROM
DBT_VALID_TO
DBT_SCD_ID
```

This allows analysts to understand how borrower or loan attributes changed over time.

---

## 🧪 Data Quality

dbt tests are used to validate the transformed data.

Examples include:

* `not_null`
* `unique`
* `relationships`
* Accepted-value validations

These tests help detect issues before data reaches the analytics layer.

Run tests with:

```bash
dbt test
```

Run the complete transformation pipeline with:

```bash
dbt build
```

---

## 📊 Streamlit Dashboard

The project includes a Streamlit application for exploring the transformed loan data.

The dashboard can be used to analyze metrics across dimensions such as:

* Region
* Loan type
* Borrower segment
* Branch
* Transaction information

Run the application locally with:

```bash
streamlit run streamlit_app/app.py
```

> The Streamlit application requires a valid Snowflake connection. Credentials should be supplied through environment variables or Streamlit secrets and must not be committed to GitHub.

---

## ⚙️ Setup

### Prerequisites

Install:

* Python
* dbt
* dbt-snowflake
* Snowflake account
* Streamlit

Install required Python packages:

```bash
pip install dbt-snowflake streamlit snowflake-snowpark-python
```

### Configure dbt

Create your local dbt profile:

```text
~/.dbt/profiles.yml
```

The profile should contain your Snowflake connection details.

**Do not commit `profiles.yml` to GitHub.**

---

## ▶️ Running the Project

From the project directory:

### Check dbt configuration

```bash
dbt debug
```

### Install dependencies

```bash
dbt deps
```

### Run models

```bash
dbt run
```

### Run tests

```bash
dbt test
```

### Build models and run tests

```bash
dbt build
```

### Run Streamlit

```bash
streamlit run streamlit_app/app.py
```

---

## 🔐 Security

Credentials and secrets are intentionally excluded from this repository.

The following files should **never** be committed:

```text
profiles.yml
.env
.streamlit/secrets.toml
```

Use `.gitignore`, environment variables, or Streamlit secrets to manage credentials.

---

## 🎯 Key Data Engineering Concepts Demonstrated

This project demonstrates practical implementation of:

* Cloud data warehousing
* Snowflake
* Snowpipe
* dbt transformations
* dbt incremental models
* dbt snapshots
* SCD Type 2
* Fact and dimension modeling
* Data quality testing
* SQL transformations
* Data ingestion metadata
* Data validation and rejected-record handling
* Analytics/semantic layer
* Streamlit data applications
* Git/GitHub version control

---

## 👥 Project Team

| Member   | Responsibility                      |
| -------- | ----------------------------------- |
| Member 1 | Data ingestion & Snowflake          |
| Member 2 | dbt transformations & data modeling |
| Member 3 | Analytics & Streamlit               |

---

## 📌 Project Status

The core data pipeline, dbt transformation layer, historical tracking, analytical models, and Streamlit analytics layer have been developed as part of the project.

Further enhancements can include automated orchestration, CI/CD, monitoring, and additional analytical dashboards.

---

## 📚 Resources

* [dbt Documentation](https://docs.getdbt.com/)
* [Snowflake Documentation](https://docs.snowflake.com/)
* [Streamlit Documentation](https://docs.streamlit.io/)
