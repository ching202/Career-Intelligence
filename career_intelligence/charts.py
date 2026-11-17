"""Small Plotly presentation helpers; numbers come from analytics.py."""

import plotly.express as px

PALETTE = ["#0D9488", "#5063C7", "#D68C24", "#AA5B90", "#357DB0"]


def style(figure):
    figure.update_layout(
        template="plotly_white", colorway=PALETTE, font={"family": "Arial", "color": "#182B43", "size": 13},
        margin={"l": 12, "r": 16, "t": 24, "b": 16}, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=380,
    )
    return figure


def horizontal_bar(frame, label, value, axis_title, hover=None):
    figure = px.bar(frame.sort_values(value), x=value, y=label, orientation="h",
                    color_discrete_sequence=PALETTE, hover_data=hover)
    figure.update_layout(xaxis_title=axis_title, yaxis_title=None)
    figure.update_xaxes(rangemode="tozero")
    return style(figure)


def salary_histogram(jobs):
    figure = px.histogram(jobs.dropna(subset=["salary_mid_usd"]), x="salary_mid_usd",
                          nbins=18, color_discrete_sequence=PALETTE)
    figure.update_layout(xaxis_title="Annualized salary midpoint (USD)", yaxis_title="Job records", bargap=0.07)
    figure.update_xaxes(tickprefix="$", separatethousands=True)
    return style(figure)
