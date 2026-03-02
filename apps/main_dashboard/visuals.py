import streamlit as st
import polars as pl
import plotly.express as px
import plotly.figure_factory as ff
from typing import List
import sys
sys.path.append('apps/main_dashboard')
import local_pipes
from local_pipes import filter_organization, filter_property_type, filter_loan_type
from datetime import datetime




def distributions(df):
    """
    Generates a Plotly histogram figure showing the distribution of a selected metric, 
    with options to filter by QC version, facet by a categorical variable, and adjust 
    the number of bins. Median values are overlaid as dotted vertical lines, colored by organization.

    Uses session state to get user selections for metric, QC version, facet, and number of bins.
    """
    _temp_df = (
        df
        .sort(by="organization_name")
        .pipe(local_pipes.filter_qc_version, st.session_state['qc_version_selection'])
    )

    # --- stable org color map (re-used for vlines) ---
    _orgs = (
        _temp_df
        .select("organization_name")
        .unique()
        .sort("organization_name")
        .get_column("organization_name")
        .to_list()
    )

    _palette = px.colors.qualitative.Plotly
    _color_map = { _org: _palette[_i % len(_palette)] for _i, _org in enumerate(_orgs) }

    _fig = px.histogram(
        _temp_df,
        x=st.session_state['metric_selection'],
        color="organization_name",
        marginal="box",
        color_discrete_map=_color_map,
        facet_row=st.session_state['facet_selection_y'] if st.session_state['facet_selection_y'] else None,
        facet_col=st.session_state['facet_selection_x'] if st.session_state['facet_selection_x'] else None,
        height=800,
        opacity=1,
        nbins=st.session_state['nbins_selection'],
    )

    # Change "property_type=Townhouse" -> "Townhouse"
    _fig.for_each_annotation(lambda _a: _a.update(text=_a.text.split("=")[-1]))

    _fig.update_layout(
        template="simple_white",
        showlegend=True,
        bargap=0,
        margin=dict(t=60, r=20, l=60, b=60),
    )


    return _fig


def time_series(df):
    
    def filter_qc_versions(df: pl.DataFrame, qc_version: str) -> pl.DataFrame:
        """
        Filters the DataFrame based on the selected QC version.
        Parameters:
            df (pl.DataFrame): The input DataFrame.
            qc_version (str): The selected QC version to filter by. If '- All -', returns the original DataFrame.
        Returns:
            pl.DataFrame: A filtered DataFrame based on the selected QC version.
        """

        return df.filter(pl.col('qc_versions') == qc_version)
    

    organization_selection = st.session_state['organization_selection']
    qc_version = st.session_state['qc_version_selection']
    metric = st.session_state['metric_selection']
    window_size = st.session_state['window_size_selection']

    _plot_df = (
        df
        # .pipe(filter_qc_versions, qc_version)
        .filter(pl.col('organization_name') ==organization_selection)
        .group_by('organization_name', 'created_at')
        .agg(pl.col(metric).mean())
        .sort('created_at') 
        .with_columns(
            pl.col(metric)
            .rolling_mean(window_size=window_size, min_periods=1)
            .over('organization_name') 
            .alias('rolling_avg')
        )
        .with_columns(
            pl.col(metric)
            .rolling_mean(window_size=1, min_periods=1)
            .over('organization_name') 
            .alias(metric)
        )
        .drop_nulls()
        .sort('organization_name')
    )

    slope_df = pl.concat([
        _plot_df.group_by("organization_name").head(1),
        _plot_df.group_by("organization_name").tail(1)
    ]).sort("organization_name", "created_at")


    _title_mapping = {
        'minutes_cycle_time': 'Cycle Time',
        'minutes_in_review_v1': 'Review Time',
        'minutes_in_queue': 'Queue Time',
        'rules_run': 'Rules Run'
    }

    _title = _title_mapping.get(metric, metric.replace('_', ' ').title())

    # if st.session_state['qc_version_selection'] != '- All -':
    #     _title += f" - QC Version {str(st.session_state['qc_version_selection'])}"
    # else:
    #     _title += " - All QC Versions"

    _fig = px.line(
        _plot_df,
        x='created_at',
        y='rolling_avg',
        color='organization_name',
        title=_title,
    )

    # Add raw metric as a light gray line in the background
    _fig.add_scatter(
        x=_plot_df['created_at'],
        y=_plot_df[metric],
        mode="lines",
        name="Raw",
        line=dict(color="lightgray", width=2),
        opacity=0.75,
    )

    _fig.update_layout(
        template="plotly",
        showlegend=True,
        bargap=0.2,
        margin=dict(t=60, r=20, l=60, b=60),
        yaxis_title=metric.replace('_', ' ').title(),
    )

    _fig_slope = px.line(
        slope_df, 
        x="created_at", 
        y='rolling_avg', 
        color="organization_name",
        markers=True,
        title=_title
    )

    _fig_slope.update_layout(
        template="plotly",
        showlegend=True,
        bargap=0.2,
        margin=dict(t=60, r=20, l=60, b=60),
        yaxis_title=metric.replace('_', ' ').title(),
    )

    if st.session_state['time_series_radio_selection'] == 'Line Chart':
        return _fig
    return _fig_slope


def display_table(df, time_series_chart_selection=None):

    def filter_dates(df, time_series_chart_selection):
        if time_series_chart_selection is not None:
            start_date, end_date = time_series_chart_selection
            start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S.%f").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S.%f").date()
            return df.filter(pl.col('created_at').is_between(start_date, end_date))
        else:
            return df
    
    raw_table = (
        df
        .pipe(filter_organization, st.session_state['organization_selection'])
        .pipe(filter_property_type, st.session_state['property_type_selection'])
        .pipe(filter_loan_type, st.session_state['loan_type_selection'])
        .pipe(filter_dates, st.session_state['time_series_chart_selection'])
        .drop('organization_name')
    )

    agg_table = (
        df
        .pipe(filter_organization, st.session_state['organization_selection'])
        .pipe(filter_property_type, st.session_state['property_type_selection'])
        .pipe(filter_loan_type, st.session_state['loan_type_selection'])
        .pipe(filter_dates, st.session_state['time_series_chart_selection'])
        .group_by('loan_type', 'property_type', 'qc_versions')
        .agg(
            pl.col('minutes_in_review_v1').mean().round(2).alias('Avg Minutes in Review'),
            pl.col('minutes_in_queue').mean().round(2).alias('Avg Minutes in Queue'),
            pl.col('minutes_cycle_time').mean().round(2).alias('Avg Minutes Cycle Time'),
            pl.col('rules_run').mean().round(2).alias('Avg Rules Run'),
            pl.len().alias('Count')
        )
        .sort(by='Avg Minutes in Review', descending=True)
    )

    if st.session_state['table_radio_selection'] == 'Raw Data':
        st.dataframe(raw_table.sort(by='created_at', descending=True))
    else:   
        st.dataframe(agg_table)
