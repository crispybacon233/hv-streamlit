import streamlit as st
import polars as pl
from src.pipes import cast_date_to_timestamp, cast_to_boolean, check_minutes, check_unique, normalize_text



@st.cache_data
def load_data(path):
    print(f'loading state data from {path}...')
    df = (
        pl.read_csv(path)
        .pipe(cast_date_to_timestamp, 'created_at')
        .pipe(cast_to_boolean, 'revision_exists')
        .pipe(cast_to_boolean, 'lender_revision_exists')
        .pipe(check_minutes, 'minutes_cycle_time')
        .pipe(check_minutes, 'minutes_in_review_v1')
        .pipe(check_minutes, 'minutes_in_queue')
        .pipe(check_unique, 'appraisal_id')
        .pipe(normalize_text, column_name='organization_name')
        .pipe(normalize_text, column_name='loan_type')
        .filter(pl.col('minutes_in_review_v1') >= 0)
        .drop_nulls()
    )
    return df


@st.cache_data
def load_unique_organizations(df: pl.DataFrame):
    print('loading unique organization names...')
    return (
        df
        .select(pl.col('organization_name').unique())
        .sort('organization_name')
        .get_column('organization_name')
        .to_list()
    )


@st.cache_data
def load_unique_loan_types(df: pl.DataFrame):
    print('loading unique loan types...')
    return (
        df
        .select(pl.col('loan_type').unique())
        .sort('loan_type')
        .get_column('loan_type')
        .to_list()
    )


@st.cache_data
def load_unique_property_types(df: pl.DataFrame):
    print('loading unique property types...')
    return (
        df
        .select(pl.col('property_type').unique())
        .sort('property_type')
        .get_column('property_type')
        .to_list()
    )


@st.cache_data
def load_unique_qc_versions(df: pl.DataFrame):
    print('loading unique QC versions...')
    return (
        df
        .select(pl.col('qc_versions').unique())
        .sort('qc_versions')
        .get_column('qc_versions')
        .to_list()
    )


@st.cache_data
def load_unique_qc_versions(df: pl.DataFrame):
    print('loading unique QC versions...')
    return (
        df
        .select(pl.col('qc_versions').unique())
        .sort('qc_versions')
        .get_column('qc_versions')
        .to_list()
    )



def init_session_states():
    if 'organization_selection' not in st.session_state:
        st.session_state['organization_selection'] = ['Delta Appraisal', 'Forest Appraisal', 'Horizon Appraisal', 'Ocean Appraisal', 'River Appraisal']

    if 'loan_type_selection' not in st.session_state:
        st.session_state['loan_type_selection'] = '- All -'

    if 'property_type_selection' not in st.session_state:
        st.session_state['property_type_selection'] = '- All -'

    if 'qc_version_selection' not in st.session_state:
        st.session_state['qc_version_selection'] = 1


def apply_base_style():
    """Applies a consistent, dashboard-like visual style across pages."""

    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 1rem;
                max-width: 1300px;
            }
            [data-testid="stMetricValue"] {
                font-size: 1.8rem;
            }
            .dashboard-subtitle {
                color: #6b7280;
                margin-top: -0.35rem;
                margin-bottom: 1rem;
                font-size: 0.95rem;
            }
            .panel {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 0.75rem 0.9rem;
                background: #ffffff;
            }
            [data-testid="stDataFrame"] {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
            }
            [data-testid="stDataFrame"] [role="columnheader"] {
                background: #f8fafc;
                font-weight: 600;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
