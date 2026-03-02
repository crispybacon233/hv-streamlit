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
    

# @st.cache_data
# def load_unique_state_names():
#     print('loading unique state names...')
#     return (
#         pl.scan_parquet('data/state_data.parquet')
#         .unique('name')
#         .sort(by=['sex', 'name'])
#         .select("name")
#         .collect(engine='streaming')
#         .get_column('name')
#         .to_list()
#     )


# @st.cache_data
# def load_unique_national_names():
#     print('loading unique national names...')
#     return (
#         pl.scan_parquet('data/national_data.parquet')
#         .unique('name')
#         .sort(by=['sex', 'name'])
#         .select("name")
#         .collect(engine='streaming')
#         .get_column('name')
#         .to_list()
#     )


# def init_session_states():
#     if 'year_range' not in st.session_state:
#         st.session_state.year_range = (1910, 2024)
    
#     if 'names_filter_multi' not in st.session_state:
#         st.session_state.names_filter_multi = ['John - M', 'Mary - F']

#     if 'names_filter_single' not in st.session_state:
#         st.session_state.names_filter_single = 'Emmaline - F'

#     if 'sex' not in st.session_state:
#         st.session_state.sex = 'M'


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
