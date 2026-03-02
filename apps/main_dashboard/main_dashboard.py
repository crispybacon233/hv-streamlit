import streamlit as st


import polars as pl

import sys
sys.path.append('apps/main_dashboard')

from src.utils import load_data, apply_base_style, init_session_states, reset_session_states
import widgets as widgets
from local_pipes import filter_organization, filter_property_type, filter_loan_type
from visuals import distributions, time_series, display_table

import plotly.express as px



st.set_page_config(layout="wide")
init_session_states()   
df = load_data('data/analyst_challenge_data.csv')
apply_base_style()


main_tab, dist_tab, tab3 = st.tabs(["Main", "Distribution", "Time"])

with main_tab:
    # ==============================
    # Table View
    # ==============================
    with st.container(horizontal=True):

        widgets.organization_filter()
        widgets.metric_filter('temp_line_chart')
        widgets.property_type_filter()
        widgets.loan_type_filter()
        widgets.table_view_radio()

    display_table(df)

    # ==============================
    # Time Series View
    # ==============================
    widgets.time_series_radio()
    widgets.window_size_filter()
    time_series = time_series(df)
    time_series_chart_selection = st.plotly_chart(time_series, use_container_width=True, on_select='rerun', selection_mode='box')
    if time_series_chart_selection.get('selection', {}).get('box'):
        st.session_state['time_series_chart_selection'] = time_series_chart_selection['selection']['box'][0]['x']


with dist_tab:
    widgets.qc_version_filter()
    widgets.metric_filter('temp_dist_chart')
    widgets.facet_filter_x()
    widgets.facet_filter_y()
    widgets.nbins_filter()
    fig = distributions(df)
    st.plotly_chart(fig, use_container_width=True, )




