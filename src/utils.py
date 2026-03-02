import streamlit as st
import polars as pl
from src.pipes import cast_date_to_timestamp, cast_to_boolean, check_minutes, check_unique, normalize_text



@st.cache_data
def load_data(path):
    print(f'loading state data from {path}...')
    df = (
        pl.read_csv(path)
        .pipe(cast_date_to_timestamp, 'created_at')
        .with_columns(pl.col("created_at").cast(pl.Date))
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


DEFAULTS = {
    "organization_selection": 'Delta Appraisal',
    "loan_type_selection": "- All -",
    "property_type_selection": "- All -",
    "qc_version_selection": 1,
    "facet_selection_x": None,
    "facet_selection_y": None,
    "table_view_selection": "Aggregated Metrics",
    "metric_selection": "minutes_in_review_v1",
    'time_series_radio_selection': 'Line Chart',
    'time_series_chart_selection': None,
}

def init_session_states():
    for k, v in DEFAULTS.items():
        st.session_state.setdefault(k, v)

def reset_session_states():
    _ = [
        st.session_state.pop(k, None)
        for k in list(st.session_state.keys())
    ]
    st.rerun()



def apply_base_style():
    """Applies a consistent, dashboard-like visual style across pages."""

    st.markdown(
        """
        <style>
            :root {
                --hv-page-bg: #f4f7fb;
                --hv-panel-bg: #ffffff;
                --hv-border: #e2e8f0;
                --hv-border-strong: #cbd5e1;
                --hv-text: #0f172a;
                --hv-text-muted: #64748b;
                --hv-accent: #0f766e;
                --hv-shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.05);
                --hv-shadow-md: 0 10px 24px rgba(15, 23, 42, 0.06);
                --hv-radius-sm: 10px;
                --hv-radius-md: 14px;
                --hv-space-1: 0.25rem;
                --hv-space-2: 0.5rem;
                --hv-space-3: 0.75rem;
                --hv-space-4: 1rem;
                --hv-space-5: 1.5rem;
            }

            [data-testid="stAppViewContainer"] {
                background: var(--hv-page-bg);
            }

            .block-container {
                max-width: 1360px;
                padding-top: 1.1rem;
                padding-bottom: 1.25rem;
            }

            h1, h2, h3, h4, h5, h6 {
                color: var(--hv-text);
                font-family: "IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif;
                letter-spacing: -0.01em;
            }

            .dashboard-subtitle {
                color: var(--hv-text-muted);
                margin-top: -0.4rem;
                margin-bottom: var(--hv-space-4);
                font-size: 0.94rem;
            }

            div[data-testid="stTabs"] [role="tablist"] {
                gap: var(--hv-space-2);
                border-bottom: 1px solid var(--hv-border);
                padding-bottom: var(--hv-space-2);
            }

            div[data-testid="stTabs"] [role="tab"] {
                border: 1px solid transparent;
                border-radius: 999px;
                color: var(--hv-text-muted);
                font-weight: 600;
                padding: 0.38rem 0.9rem;
                margin: 0;
            }

            div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
                color: var(--hv-text);
                background: var(--hv-panel-bg);
                border-color: var(--hv-border);
                box-shadow: var(--hv-shadow-sm);
            }

            div[data-testid="stWidgetLabel"] p {
                font-size: 0.84rem;
                font-weight: 600;
                color: var(--hv-text);
                letter-spacing: 0.01em;
                margin-bottom: 0.3rem;
            }

            div[data-baseweb="select"] > div {
                min-height: 2.25rem;
                border: 1px solid var(--hv-border-strong);
                border-radius: var(--hv-radius-sm);
                background: #ffffff;
                box-shadow: none;
            }

            div[data-baseweb="select"] > div:hover {
                border-color: #94a3b8;
            }

            div[data-baseweb="slider"] [role="slider"] {
                border-color: var(--hv-accent);
            }

            div[role="radiogroup"] {
                gap: var(--hv-space-1);
            }

            .st-key-main_toolbar,
            .st-key-dist_toolbar {
                position: sticky;
                top: 0.6rem;
                z-index: 30;
                background: rgba(244, 247, 251, 0.92);
                backdrop-filter: blur(6px);
                border: 1px solid var(--hv-border);
                border-radius: var(--hv-radius-md);
                padding: var(--hv-space-3) var(--hv-space-4);
                margin-bottom: var(--hv-space-4);
                box-shadow: var(--hv-shadow-sm);
            }

            .st-key-table_section,
            .st-key-timeseries_section,
            .st-key-distribution_section {
                background: var(--hv-panel-bg);
                border: 1px solid var(--hv-border);
                border-radius: var(--hv-radius-md);
                padding: 0.9rem 1rem 0.7rem 1rem;
                margin-bottom: var(--hv-space-4);
                box-shadow: var(--hv-shadow-sm);
            }

            [data-testid="stDataFrame"] {
                border: 1px solid var(--hv-border);
                border-radius: var(--hv-radius-md);
                overflow: hidden;
                box-shadow: var(--hv-shadow-sm);
            }

            [data-testid="stDataFrame"] [role="columnheader"] {
                background: #f8fafc;
                font-weight: 600;
                border-bottom: 1px solid var(--hv-border);
            }

            [data-testid="stPlotlyChart"] {
                border: 1px solid var(--hv-border);
                border-radius: var(--hv-radius-md);
                background: #ffffff;
                padding: 0.2rem 0.3rem;
                box-shadow: var(--hv-shadow-sm);
            }

            @media (max-width: 960px) {
                .st-key-main_toolbar,
                .st-key-dist_toolbar {
                    position: static;
                    backdrop-filter: none;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
