import streamlit as st

import sys
sys.path.append('apps/main_dashboard')

from src.utils import load_data, apply_base_style, init_session_states
import widgets as widgets
from visuals import distributions, time_series, display_table, revision_rate



st.set_page_config(layout="wide")
init_session_states()   
df = load_data('data/analyst_challenge_data.csv')
apply_base_style()


main_tab, dist_tab = st.tabs(["Main", "Distribution"])

with main_tab:
    st.markdown("### Quality Control Overview")
    st.markdown(
        "<p class='dashboard-subtitle'>Track operational performance, inspect records, and monitor trend movement in one workspace.</p>",
        unsafe_allow_html=True,
    )

    with st.container(key="main_toolbar"):
        org_col, metric_col, property_col, loan_col = st.columns([1.5, 1.25, 1.0, 1.0], gap="small")
        with org_col:
            widgets.organization_filter()
        with metric_col:
            widgets.metric_filter('temp_line_chart')
        with property_col:
            widgets.property_type_filter()
        with loan_col:
            widgets.loan_type_filter()

    with st.container(key="table_section"):
        title_col, view_col = st.columns([2.6, 1.4], vertical_alignment="center")
        with title_col:
            st.markdown("#### Table View")
            st.caption("Switch between summarized metrics and full record detail.")
        with view_col:
            widgets.table_view_radio()
        display_table()

    with st.container(key="timeseries_section"):
        st.markdown("#### Time Series")
        st.caption("Use chart mode and rolling window controls to compare trend behavior.")
        mode_col, window_col, _ = st.columns([1.6, 1.2, 2.4], vertical_alignment="center")
        with mode_col:
            widgets.time_series_radio()
        with window_col:
            widgets.window_size_filter()

        time_series_fig = time_series(df)
        time_series_chart_selection = st.plotly_chart(
            time_series_fig,
            use_container_width=True,
            on_select='rerun',
            selection_mode='box',
        )
        try:
            st.session_state['time_series_chart_selection'] = time_series_chart_selection['selection']['box'][0]['x']
        except:
            st.session_state['time_series_chart_selection'] = None


with dist_tab:

    st.markdown("### Distribution Analysis")
    st.markdown(
        "<p class='dashboard-subtitle'>Review metric spread by organization and segment the distributions with facet controls.</p>",
        unsafe_allow_html=True,
    )

    with st.container(key="dist_toolbar"):
        qc_col, metric_col, facet_x_col, facet_y_col, bins_col = st.columns([1.0, 1.1, 1.0, 1.0, 1.3], gap="small")
        with qc_col:
            widgets.qc_version_filter()
        with metric_col:
            widgets.metric_filter('temp_dist_chart')
        with facet_x_col:
            widgets.facet_filter_x()
        with facet_y_col:
            widgets.facet_filter_y()
        with bins_col:
            widgets.nbins_filter()

    with st.container(key="distribution_section"):
        st.markdown("#### Metric Distribution")
        st.caption("Histogram and box summary update live from the selected controls.")
        fig = distributions(df)
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container(key="revision_rate_section"):
        st.markdown("#### Revision Rate")
        st.caption("Count of QC revisions by organization. Facet by loan or property type to find patterns in revision occurrence.")
        revision_rate_fig = revision_rate()
        st.plotly_chart(revision_rate_fig, use_container_width=True)


