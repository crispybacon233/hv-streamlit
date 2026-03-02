import streamlit as st
import polars as pl

import sys
sys.path.append('apps/main_dashboard')

from src.utils import load_data, apply_base_style, init_session_states
import widgets as widgets
from local_pipes import filter_organization, filter_property_type, filter_loan_type
from visuals import distributions

import plotly.express as px


init_session_states()
df = load_data('data/analyst_challenge_data.csv')
apply_base_style()



main_tab, dist_tab, tab3 = st.tabs(["Main", "Distribution", "Time"])

with main_tab:



    # ==============================
    # Filters
    # ==============================
    widgets.organization_filter()
    widgets.property_type_filter()
    widgets.loan_type_filter()
    table_radio = st.radio(
        'Select Table View',
        options=['Aggregated Metrics', 'Raw Data'],
        index=0,
        horizontal=True,
    )


    raw_table = (
        df
        .pipe(filter_organization, st.session_state['organization_selection'])
        .pipe(filter_property_type, st.session_state['property_type_selection'])
        .pipe(filter_loan_type, st.session_state['loan_type_selection'])
    )

    agg_table = (
        df
        .pipe(filter_organization, st.session_state['organization_selection'])
        .pipe(filter_property_type, st.session_state['property_type_selection'])
        .pipe(filter_loan_type, st.session_state['loan_type_selection'])
        .group_by('organization_name', 'loan_type', 'property_type', 'qc_versions')
        .agg(
            pl.col('minutes_in_review_v1').mean().round(2).alias('Avg Minutes in Review'),
            pl.col('minutes_in_queue').mean().round(2).alias('Avg Minutes in Queue'),
            pl.col('minutes_cycle_time').mean().round(2).alias('Avg Minutes Cycle Time'),
            pl.col('rules_run').mean().round(2).alias('Avg Rules Run'),
            pl.len().alias('Count')
        )
        .sort(by='Avg Minutes in Review', descending=True)
    )

    if table_radio == 'Raw Data':
        st.dataframe(raw_table.sort(by='created_at', descending=True))
    else:   
        st.dataframe(agg_table)



with dist_tab:
    widgets.qc_version_filter()
    widgets.metric_filter()
    widgets.facet_filter()
    widgets.nbins_filter()


    fig = distributions(df)


    st.plotly_chart(fig, use_container_width=True, )




