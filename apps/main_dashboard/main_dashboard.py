import streamlit as st
import polars as pl
from src.utils import load_data, apply_base_style
from apps.main_dashboard.visuals import distributions

import plotly.express as px


df = load_data('data/analyst_challenge_data.csv')
apply_base_style()




main_tab, table_tab, tab3 = st.tabs(["Main", "Table", "Time"])

# date_filter = st.slider(
#     "Select date range",
#     value=(df.select(pl.col('created_at').min()).to_series()[0], df.select(pl.col('created_at').max()).to_series()[0]),
#     min_value=df.select(pl.col('created_at').min()).to_series()[0],
#     max_value=df.select(pl.col('created_at').max()).to_series()[0],
# )

with main_tab:
    qc_filter = st.selectbox(
        'Select QC Versions',
        options=df.select(pl.col('qc_versions').unique()).to_series().to_list(),
        index=0,
    )

    metric_options = ['minutes_in_review_v1', 'minutes_in_queue', 'minutes_cycle_time', 'rules_run']
    metric_filter = st.selectbox('Select Metric', options=metric_options, index=0)

    facets_options = ['property_type', 'loan_type']
    facet_filter = st.selectbox('Facet by', options=facets_options, index=0)

    nbins_filter = st.slider('Number of bins', min_value=1, max_value=200, value=30, step=1)


    fig = distributions(
        df=df,
        qc_filter=qc_filter,
        metric_filter=metric_filter,
        facet_filter=facet_filter,
        nbins_filter=nbins_filter,
    )


    st.plotly_chart(fig, use_container_width=True, )



with table_tab:
    table = (
        df
        .group_by('organization_name', 'loan_type', 'property_type', 'qc_versions')
        .agg(
            pl.col('minutes_in_review_v1').mean(),
            pl.col('minutes_in_queue').mean(),
            pl.col('minutes_cycle_time').mean(),
            pl.col('rules_run').mean(),
            pl.len().alias('count')
        )
        .sort(by='minutes_in_review_v1', descending=True)
    )
    st.dataframe(table)

