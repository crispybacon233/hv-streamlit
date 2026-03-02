import streamlit as st
import polars as pl
from src.utils import load_unique_organizations, load_unique_loan_types, load_unique_property_types, load_data, load_unique_qc_versions

# ==============================
# Load Data and Unique Values for Filters
# ==============================
df = load_data('data/analyst_challenge_data.csv')
ORGANIZATION_OPTIONS = load_unique_organizations(df)
PROPERTY_TYPE_OPTIONS = load_unique_property_types(df)
LOAN_TYPE_OPTIONS = load_unique_loan_types(df)


# ==============================
# Widget Functions
# ==============================
def organization_filter():

    if 'organization_selection' not in st.session_state:
        st.session_state['organization_selection'] = ['Delta Appraisal', 'Forest Appraisal', 'Horizon Appraisal', 'Ocean Appraisal', 'River Appraisal']

    def update_organization_selection():
        st.session_state['organization_selection'] = st.session_state._temp_organization_filter

    st.multiselect(
        'Select Organization',
        options=ORGANIZATION_OPTIONS,
        default=ORGANIZATION_OPTIONS,
        key='_temp_organization_filter',
        on_change=update_organization_selection,
    )


def checkbox_all_organizations():
    if 'organization_selection' not in st.session_state:
        st.session_state['organization_selection'] = ['Delta Appraisal', 'Forest Appraisal', 'Horizon Appraisal', 'Ocean Appraisal', 'River Appraisal']

    def toggle_all_organizations():
        if st.session_state['select_all_organizations']:
            st.session_state['organization_selection'] = ['Delta Appraisal', 'Forest Appraisal', 'Horizon Appraisal', 'Ocean Appraisal', 'River Appraisal']
        else:
            st.session_state['organization_selection'] = []

    st.checkbox(
        'Select All Organizations',
        key='select_all_organizations',
        on_change=toggle_all_organizations,
    )


def property_type_filter():

    PROPERTY_TYPE_OPTIONS = load_unique_property_types(df)

    if 'property_type_selection' not in st.session_state:
        st.session_state['property_type_selection'] = None

    def update_property_type_selection():
        st.session_state['property_type_selection'] = st.session_state._temp_property_type_filter

    st.selectbox(
        'Select Property Type',
        options= ['- All -'] + PROPERTY_TYPE_OPTIONS,
        index=0,
        key='_temp_property_type_filter',
        on_change=update_property_type_selection,
    )


def loan_type_filter():

    LOAN_TYPE_OPTIONS = load_unique_loan_types(df)

    if 'loan_type_selection' not in st.session_state:
        st.session_state['loan_type_selection'] = None

    def update_loan_type_selection():
        st.session_state['loan_type_selection'] = st.session_state._temp_loan_type_filter

    st.selectbox(
        'Select Loan Type',
        options= ['- All -'] + LOAN_TYPE_OPTIONS,
        index=0,
        key='_temp_loan_type_filter',
        on_change=update_loan_type_selection,
    )


def qc_version_filter():

    QC_VERSION_OPTIONS = load_unique_qc_versions(df)

    if 'qc_version_selection' not in st.session_state:
        st.session_state['qc_version_selection'] = None

    def update_qc_version_selection():
        st.session_state['qc_version_selection'] = st.session_state._temp_qc_version_filter

    st.selectbox(
        'Select QC Version',
        options= QC_VERSION_OPTIONS,
        index=0,
        key='_temp_qc_version_filter',
        on_change=update_qc_version_selection,
    )


def metric_filter():

    metric_options = ['minutes_in_review_v1', 'minutes_in_queue', 'minutes_cycle_time', 'rules_run']

    if 'metric_selection' not in st.session_state:
        st.session_state['metric_selection'] = metric_options[0]

    def update_metric_selection():
        st.session_state['metric_selection'] = st.session_state._temp_metric_filter

    st.selectbox(
        'Select Metric',
        options= metric_options,
        index=0,
        key='_temp_metric_filter',
        on_change=update_metric_selection,
    )


def facet_filter():

    facets_options = ['property_type', 'loan_type']

    if 'facet_selection' not in st.session_state:
        st.session_state['facet_selection'] = facets_options[0]

    def update_facet_selection():
        st.session_state['facet_selection'] = st.session_state._temp_facet_filter

    st.selectbox(
        'Facet by',
        options= facets_options,
        index=0,
        key='_temp_facet_filter',
        on_change=update_facet_selection,
    )


def nbins_filter():

    if 'nbins_selection' not in st.session_state:
        st.session_state['nbins_selection'] = 30

    def update_nbins_selection():
        st.session_state['nbins_selection'] = st.session_state._temp_nbins_filter

    st.slider(
        'Number of bins',
        min_value=1,
        max_value=100,
        value=50,
        step=1,
        key='_temp_nbins_filter',
        on_change=update_nbins_selection,
    )