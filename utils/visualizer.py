"""
utils/visualizer.py
Plotly chart builders for the Electoral Analytics Matrix.
"""

import logging
import pandas as pd
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

PLOT_BG    = "#08080f"
GRID_COLOR = "#1a1a3a"
TEXT_COLOR = "#d0d0e8"


def render_pow_bar(
    pow_map: dict[str, float],
    colors: list[str],
) -> go.Figure:
    """
    Horizontal bar chart showing Probability of Win for each candidate.

    Args:
        pow_map: {candidate_name: pow_percentage}
        colors:  List of hex color strings per candidate

    Returns:
        Plotly Figure
    """
    names  = list(pow_map.keys())
    values = list(pow_map.values())
    bars_colors = [colors[i % len(colors)] for i in range(len(names))]

    fig = go.Figure(go.Bar(
        x=values,
        y=names,
        orientation="h",
        marker=dict(
            color=bars_colors,
            opacity=0.85,
            line=dict(color=bars_colors, width=1),
        ),
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=13),
    ))

    fig.update_layout(
        title=dict(text="Probability of Win (%)", font=dict(color=TEXT_COLOR, size=14), x=0.01),
        xaxis=dict(
            range=[0, max(values) * 1.2],
            title="PoW (%)",
            gridcolor=GRID_COLOR,
            color=TEXT_COLOR,
            tickfont=dict(color=TEXT_COLOR),
        ),
        yaxis=dict(
            autorange="reversed",
            gridcolor=GRID_COLOR,
            color=TEXT_COLOR,
            tickfont=dict(color=TEXT_COLOR, size=12),
        ),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PLOT_BG,
        margin=dict(l=20, r=60, t=40, b=20),
        height=300,
        showlegend=False,
    )
    return fig


def render_radar_chart(
    candidates: list[dict],
    factors: list[str],
    factor_labels: dict[str, str],
    colors: list[str],
) -> go.Figure:
    """
    Spider/radar chart comparing all candidates across all factors.

    Args:
        candidates:    List of candidate dicts
        factors:       List of factor keys
        factor_labels: Human-readable factor names
        colors:        Hex color list

    Returns:
        Plotly Figure
    """
    labels = [factor_labels[f] for f in factors] + [factor_labels[factors[0]]]  # close polygon

    fig = go.Figure()

    for i, cand in enumerate(candidates):
        values = [cand.get(f, 0) for f in factors]
        values += [values[0]]  # close the polygon

        color = colors[i % len(colors)]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            fill="toself",
            name=cand["name"],
            line=dict(color=color, width=2),
            fillcolor=color.replace("#", "rgba(").replace(")", ",0.12)") if color.startswith("#") else color,
            opacity=0.9,
        ))

    fig.update_layout(
        polar=dict(
            bgcolor=PLOT_BG,
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                gridcolor=GRID_COLOR,
                color=TEXT_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            angularaxis=dict(
                gridcolor=GRID_COLOR,
                color=TEXT_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=10),
            ),
        ),
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        legend=dict(
            font=dict(color=TEXT_COLOR),
            bgcolor=PLOT_BG,
            bordercolor=GRID_COLOR,
        ),
        title=dict(text="Factor Comparison (Raw Scores)", font=dict(color=TEXT_COLOR, size=14), x=0.01),
        height=420,
        margin=dict(l=40, r=40, t=50, b=20),
    )
    return fig


def render_matrix_table(
    candidates: list[dict],
    scores: dict[str, dict[str, float]],
    pow_map: dict[str, float],
    factors: list[str],
    factor_labels: dict[str, str],
    weights: dict[str, float],
) -> pd.DataFrame:
    """
    Build a structured comparison DataFrame for display.

    Args:
        candidates:    Raw candidate data
        scores:        Weighted scores from compute_scores()
        pow_map:       PoW percentages from compute_pow()
        factors:       List of factor keys
        factor_labels: Human-readable labels
        weights:       Analyst-defined factor weights

    Returns:
        Pandas DataFrame ready for st.dataframe()
    """
    rows = []

    for factor in factors:
        row = {
            "Factor":  factor_labels[factor],
            "Weight": f"{weights.get(factor, 1.0):.1f}×",
        }
        for cand in candidates:
            name = cand["name"]
            raw  = cand.get(factor, 0)
            ws   = scores[name].get(factor, 0)
            row[name] = f"{raw}/10  (→{ws:.1f})"
        rows.append(row)

    # Totals row
    total_row = {"Factor": "━━ TOTAL WEIGHTED SCORE ━━", "Weight": ""}
    for cand in candidates:
        name = cand["name"]
        total_row[name] = f"{scores[name]['total']:.1f}"
    rows.append(total_row)

    # PoW row
    pow_row = {"Factor": "◈ PROBABILITY OF WIN", "Weight": ""}
    for cand in candidates:
        pow_row[cand["name"]] = f"{pow_map[cand['name']]:.1f}%"
    rows.append(pow_row)

    return pd.DataFrame(rows)
