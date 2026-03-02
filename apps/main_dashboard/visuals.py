import streamlit as st
import polars as pl
import plotly.express as px
import plotly.figure_factory as ff
from typing import List



def distributions(
    df: pl.DataFrame,
    qc_filter: List[int],
    metric_filter: str,
    facet_filter: str,
    nbins_filter: int,
):
    """
    Generates a Plotly histogram figure showing the distribution of a selected metric, 
    with options to filter by QC version, facet by a categorical variable, and adjust 
    the number of bins. Median values are overlaid as dotted vertical lines, colored by organization.
    Args:
        df (pl.DataFrame): The input DataFrame containing the data to visualize.
        qc_filter (List[int]): A list of QC versions to include in the visualization.
        metric_filter (str): The name of the metric column to visualize (e.g., 'minutes_in_review_v1').
        facet_filter (str): The name of the categorical column to facet by (e.g., 'property_type'). 
                            If None or empty, no faceting is applied.
        nbins_filter (int): The number of bins to use in the histogram.
    Returns:
        px.Figure: A Plotly Figure object containing the generated histogram.
    """
    _temp_df = (
        df
        .sort(by="organization_name")
        .filter(pl.col("qc_versions").is_in(qc_filter))
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
        x=metric_filter,
        color="organization_name",
        marginal="box",
        color_discrete_map=_color_map,
        facet_row=facet_filter,
        height=800,
        opacity=1,
        nbins=nbins_filter,
    )

    # Change "property_type=Townhouse" -> "Townhouse"
    _fig.for_each_annotation(lambda _a: _a.update(text=_a.text.split("=")[-1]))

    _fig.update_layout(
        template="simple_white",
        showlegend=True,
        bargap=0,
        margin=dict(t=60, r=20, l=60, b=60),
    )

    # --- add dotted median vlines, in matching org color, per facet ---
    if (facet_filter is None) or (facet_filter == ""):
        _med_df = (
            _temp_df
            .group_by("organization_name")
            .agg(pl.col(metric_filter).median().alias("median"))
        )

        for _row in _med_df.iter_rows(named=True):
            _fig.add_vline(
                x=_row["median"],
                line_dash="dot",
                line_width=1,
                line_color=_color_map[_row["organization_name"]],
                opacity=0.35,
            )

    else:
        _med_df = (
            _temp_df
            .group_by([facet_filter, "organization_name"])
            .agg(pl.col(metric_filter).median().alias("median"))
        )

        # build facet-value -> subplot row index map (top-to-bottom)
        _facet_vals = (
            _temp_df
            .select(facet_filter)
            .unique()
            .to_series()
            .to_list()
        )
        _facet_val_set = set(map(str, _facet_vals))

        _facet_anns = [_a for _a in _fig.layout.annotations if _a.text in _facet_val_set]
        _facet_anns = sorted(_facet_anns, key=lambda _a: -_a.y)  # top -> bottom
        _facet_to_row = {_a.text: _i + 1 for _i, _a in enumerate(_facet_anns)}

        for _row in _med_df.iter_rows(named=True):
            _facet_key = str(_row[facet_filter])
            _row_idx = _facet_to_row.get(_facet_key, 1)

            _fig.add_vline(
                x=_row["median"],
                row=_row_idx,
                col=1,
                line_dash="dot",
                line_width=1,
                line_color=_color_map[_row["organization_name"]],
                opacity=1,
            )
    
    return _fig


