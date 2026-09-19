
import streamlit as st
from snowflake.snowpark import Session


@st.cache_resource
def get_session():

    connection_parameters = {
        "account": "XYPMRDB-UZ40819",
        "user": "BALA119",
        "password": "Balasubramaniyan@22369",
        "warehouse": "COMPUTE_WH",
        "database": "LOAN_MGMT_DB",
        "schema": "SEM",
        "role": "ACCOUNTADMIN",
    }

    return Session.builder.configs(connection_parameters).create()

