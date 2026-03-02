import streamlit as st
import polars as pl
import plotly.express as px
import sys
sys.path.append('apps/main_dashboard')
import local_pipes
from local_pipes import filter_organization, filter_property_type, filter_loan_type
from datetime import datetime, timedelta
from src.utils import load_data


PLOT_FONT_FAMILY = "IBM Plex Sans, Avenir Next, Segoe UI, sans-serif"
PLOT_GRID_COLOR = "#e5e7eb"
PLOT_AXIS_COLOR = "#cbd5e1"
PLOT_TEXT_COLOR = "#111827"
PLOT_MUTED_TEXT = "#475569"


def apply_chart_style(fig, *, yaxis_title: str, height: int | None = None, x_grid: bool = False):
    fig.update_layout(
        template="plotly_white",
        showlegend=True,
        font=dict(family=PLOT_FONT_FAMILY, size=13, color=PLOT_TEXT_COLOR),
        title=dict(x=0.0, xanchor="left", font=dict(size=20, color=PLOT_TEXT_COLOR)),
        legend=dict(
            title_text="Organization",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor=PLOT_GRID_COLOR,
            borderwidth=1,
        ),
        margin=dict(t=74, r=24, l=56, b=56),
        hovermode="x unified",
        yaxis_title=yaxis_title,
    )

    if height is not None:
        fig.update_layout(height=height)

    fig.update_xaxes(
        showline=True,
        linecolor=PLOT_AXIS_COLOR,
        gridcolor=PLOT_GRID_COLOR,
        showgrid=x_grid,
        zeroline=False,
        tickfont=dict(color=PLOT_MUTED_TEXT),
        title_font=dict(color=PLOT_MUTED_TEXT),
    )
    fig.update_yaxes(
        showline=True,
        linecolor=PLOT_AXIS_COLOR,
        gridcolor=PLOT_GRID_COLOR,
        zeroline=False,
        tickfont=dict(color=PLOT_MUTED_TEXT),
        title_font=dict(color=PLOT_MUTED_TEXT),
    )

    return fig




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

    title = st.session_state['metric_selection'].replace('_', ' ').title()

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
        title=title
    )

    # Change "property_type=Townhouse" -> "Townhouse"
    _fig.for_each_annotation(lambda _a: _a.update(text=_a.text.split("=")[-1]))

    _fig.update_layout(bargap=0.03)
    apply_chart_style(_fig, yaxis_title="Count", height=760, x_grid=True)


    return _fig


def revision_rate():
    df = load_data('data/analyst_challenge_data.csv')
    temp_df = (
        df
        .with_columns(
            pl.col('revision_exists').cast(pl.Int64).alias('revisions')
        )
        .sort('organization_name')
    )

    fig = px.histogram(
        temp_df,
        x='organization_name',
        y='revisions',
        color='organization_name',
        facet_col=st.session_state['facet_selection_x'] if st.session_state['facet_selection_x'] else None,
        title="Revision Count by Organization",
        histfunc='sum',
        height=650
    )

    fig.for_each_annotation(lambda _a: _a.update(text=_a.text.split("=")[-1]))

    fig.update_traces(marker_line_width=0) 

    apply_chart_style(fig, yaxis_title="Revision Count")

    return fig


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
    

    def filter_property_type(df: pl.DataFrame, property_type: str) -> pl.DataFrame:
        """
        Filters the DataFrame based on the selected property type.
        Parameters:
            df (pl.DataFrame): The input DataFrame.
            property_type (str): The selected property type to filter by. If '- All -', returns the original DataFrame.
        Returns:
            pl.DataFrame: A filtered DataFrame based on the selected property type.
        """
        if property_type == '- All -':
            return df
        else:
            return df.filter(pl.col('property_type') == property_type)
        

    def filter_loan_type(df: pl.DataFrame, loan_type: str) -> pl.DataFrame:
        """
        Filters the DataFrame based on the selected loan type.
        Parameters:
            df (pl.DataFrame): The input DataFrame.
            loan_type (str): The selected loan type to filter by. If '- All -', returns the original DataFrame.
        Returns:
            pl.DataFrame: A filtered DataFrame based on the selected loan type.
        """
        if loan_type == '- All -':
            return df
        else:
            return df.filter(pl.col('loan_type') == loan_type)
    

    organization_selection = st.session_state['organization_selection']
    qc_version = st.session_state['qc_version_selection']
    property_type = st.session_state['property_type_selection']
    loan_type = st.session_state['loan_type_selection']
    metric = st.session_state['metric_selection']
    window_size = st.session_state['window_size_selection']

    _plot_df = (
        df
        .pipe(filter_property_type, property_type)
        # .pipe(filter_qc_versions, qc_version)
        .pipe(filter_loan_type, loan_type)
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
        line=dict(color="#cbd5e1", width=2),
        opacity=0.75,
    )

    apply_chart_style(_fig, yaxis_title=metric.replace('_', ' ').title())

    _fig_slope = px.line(
        slope_df, 
        x="created_at", 
        y='rolling_avg', 
        color="organization_name",
        markers=True,
        title=_title
    )

    apply_chart_style(_fig_slope, yaxis_title=metric.replace('_', ' ').title())

    if st.session_state['time_series_radio_selection'] == 'Line Chart':
        return _fig
    return _fig_slope


def display_table(time_series_chart_selection=None):
    df = load_data('data/analyst_challenge_data.csv')
    FMTS = (
        "%Y-%m-%d %H:%M:%S.%f",  # 2025-09-17 00:31:30.123456
        "%Y-%m-%d %H:%M:%S",     # 2025-09-17 00:31:30
        "%Y-%m-%d %H:%M",        # 2025-06-21 06:56
        "%Y-%m-%d",              # 2025-07-17
    )
    def parse_dt(x) -> datetime:
        # If the widget sometimes returns actual date/datetime objects, handle them too:
        if isinstance(x, datetime):
            return x
        # datetime.date (but not datetime itself)
        if hasattr(x, "year") and hasattr(x, "month") and hasattr(x, "day") and not isinstance(x, str):
            return datetime(x.year, x.month, x.day)

        s = str(x)
        for fmt in FMTS:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                pass
        raise ValueError(f"Unrecognized datetime format: {s!r}")

    def is_date_only(x) -> bool:
        # "YYYY-MM-DD"
        return isinstance(x, str) and len(x) == 10

    def filter_dates(df, time_series_chart_selection):
        if not time_series_chart_selection:
            return df

        start_raw, end_raw = time_series_chart_selection
        start_dt = parse_dt(start_raw)
        end_dt = parse_dt(end_raw)

        # If end is date-only, include the whole day
        if is_date_only(end_raw):
            end_dt = end_dt + timedelta(days=1) - timedelta(microseconds=1)

        return df.filter(pl.col("created_at").is_between(start_dt, end_dt))
    
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
            (pl.col('revision_exists').sum() / pl.len() * 100.0).round(2).alias('Revision Rate (%)'),    
            pl.len().alias('Count')
        )
        .sort(by='Avg Minutes in Review', descending=True)
    )

    if st.session_state['table_radio_selection'] == 'Raw Data':
        st.dataframe(raw_table.sort(by='created_at', descending=True))
    else:   
        st.dataframe(agg_table)
