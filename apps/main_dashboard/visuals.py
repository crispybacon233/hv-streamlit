import streamlit as st
import polars as pl
import plotly.express as px
import plotly.figure_factory as ff
from typing import List
import sys
sys.path.append('apps/main_dashboard')
import local_pipes 




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
        facet_row=st.session_state['facet_selection'] if st.session_state['facet_selection'] else None,
        facet_col='loan_type',
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


