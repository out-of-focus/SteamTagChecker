import streamlit as st
import math
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import scipy
import numpy as np
from plotly.subplots import make_subplots
import plotnine
from plotnine import ggplot, aes, geom_histogram, scale_x_log10, scale_color_manual, scale_fill_manual

def filter_data(df, fallbck, incl_tags, excl_tags):
    ''' Applies filters stored in session to selected dataframe and returns a filtered dataframe.
     Additionally, checks the revenue estimate method and adjusts estimates accordingly.'''

    if 'yr_from' in st.session_state:
        new_df = df[(df["release_year"]>=int(st.session_state["yr_from"])) &
                    (df["release_year"]<= int(st.session_state["yr_to"])) &
                    (df["review_count"]>=st.session_state["min_reviews"])]
    else:
        new_df = df[(df["release_year"] >= fallbck["yrFrom"]) & (df["release_year"] <= fallbck["yrTo"]) &
                    (df["review_count"]>=fallbck["minReviews"])]

    if ("method_check" in st.session_state and
        st.session_state["method_check"] == "Reviews"):
        if "sales_per_review" in st.session_state:
            sales_per_review = st.session_state["sales_per_review"]
        else:
            sales_per_review = fallbck["sales_per_review"]
        new_df["copies_sold_est"] = round(new_df["review_count"] * sales_per_review,0)
        new_df["revenue_est"] = new_df["copies_sold_est"] * new_df["price_USD"]
    else:
        sales_per_review = fallbck["sales_per_review"]
        new_df["copies_sold_est"] = round(new_df["review_count"] * sales_per_review,0)
        new_df["revenue_est"] = new_df["copies_sold_est"] * new_df["price_USD"]

    if "min_rating" in st.session_state:
        match st.session_state["min_rating"]:
            case "Very Negative":
                new_df = new_df[new_df["user_rating_int"] > 1]
            case "Negative":
                new_df = new_df[new_df["user_rating_int"] > 2]
            case "Mostly Negative":
                new_df = new_df[new_df["user_rating_int"] > 3]
            case "Mixed":
                new_df = new_df[new_df["user_rating_int"] > 4]
            case "Mostly Positive":
                new_df = new_df[new_df["user_rating_int"] > 5]
            case "Positive":
                new_df = new_df[new_df["user_rating_int"] > 6]
            case "Very Positive":
                new_df = new_df[new_df["user_rating_int"] > 7]
            case "Overwhelmingly Positive":
                new_df = new_df[new_df["user_rating_int"] > 8]

    for tag in incl_tags:
        new_df = new_df[new_df.apply(lambda row: tag in row["tags"], axis=1)]
    for tag in excl_tags:
        new_df = new_df[new_df.apply(lambda row: tag not in row["tags"], axis=1)]
    return new_df

def make_tag_cols(no_of_cols, tag_list, incl_tags):
    ''' Creates columns of checkboxes with given tags'''
    tagCols = st.columns(no_of_cols)
    for num, col in enumerate(tagCols):
        items_per_col = math.ceil(len(tag_list) / len(tagCols))
        for i in range(0, items_per_col):
            itemNo = items_per_col * num + i
            try:
                val = tag_list[itemNo] in incl_tags
                col.checkbox(label=tag_list[itemNo], key="tag_" + tag_list[itemNo].replace(" ", "_"), value=val)
            except IndexError:
                pass
def make_extag_cols(no_of_cols, tag_list, excl_tags):
    tagCols = st.columns(no_of_cols)
    for num, col in enumerate(tagCols):
        items_per_col = math.ceil(len(tag_list) / len(tagCols))
        for i in range(0, items_per_col):
            itemNo = items_per_col * num + i
            try:
                val = tag_list[itemNo] in excl_tags
                col.checkbox(label=tag_list[itemNo], key="excl_" + tag_list[itemNo].replace(" ", "_"), value=val)
            except IndexError:
                pass

def find_other_tags(data, taglist):
    ''' Checks for tags in the database that were omitted in the current tag list - and returns the omitted tags '''
    all_tags_rows = data["tags"].to_list()
    all_tags = []
    for list in all_tags_rows:
        for item in list.split(", "):
            all_tags.append(item)
    all_tags = set(all_tags)
    new_tags = []
    for tag in all_tags:
        if tag not in taglist:
            new_tags.append(tag)
    return new_tags



def plot_releases_per_year(df, fallbck):
    plot_df = df[(df["release_year"] < 2025) & (df["release_year"] >= 2010)]
    plot_df = plot_df[["game_id", "release_year"]].groupby("release_year").count().reset_index()
    #years = plot_df["release_year"].unique()
    fig = go.Figure([go.Bar(x=plot_df["release_year"], y=plot_df["game_id"], text=plot_df["game_id"],
                            hovertemplate='%{y} games published in %{x}<extra></extra>',
                            width=.8,
                            marker_color='steelblue',
                            textfont_size=16) ])
    fig.update_layout(hovermode='closest',
                      title_text="Number of Games Released per Year",
                      #title_subtitle_text="*Games with the selected filters",
                      title_x=0.5,
                      title_xanchor="center",
                      title_font_size=20,
                      # Axis labels and ticks font sizes
                      xaxis=dict(
                          title_font_size=18,  # X-axis label font size
                          tickfont_size=16  # X-axis tick font size
                      ),
                      yaxis=dict(
                          title=dict(
                              text="No. of Games",
                              font=dict(size=18)
                          ),

                          title_font_size=18,  # Y-axis label font size
                          tickfont_size=16  # Y-axis tick font size
                      ),
                      # Hover text font size
                      hoverlabel=dict(
                          font_size=16
                      )
                      )
    if "yr_from" in st.session_state.keys():
        fro = st.session_state["yr_from"]
    else:
        fro = fallbck["yrFrom"]
    if "yr_to" in st.session_state.keys():
        to = st.session_state["yr_to"]
    else:
        to = fallbck["yrTo"]
    if int(to)==2025:
        to=2024
    fig.update_xaxes(tickmode="array", tickvals=list(range(2010, 2025, 1)), range=[int(fro)-0.5, int(to)+0.5])
    return fig

def format_currency_short(value):
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:,.0f}"

def plot_rev_per_year(df, selectedFilters):
    grouped = df.groupby("release_year")["revenue_est"].median()
    grouped_df = grouped.reset_index()
    grouped_df = grouped_df[grouped_df["release_year"]<2025]

    grouped_df['formatted_text'] = grouped_df['revenue_est'].apply(format_currency_short)

    fig = px.bar(grouped_df, x="release_year", y="revenue_est",
                 text="formatted_text")  # Use the formatted text

    fig.update_layout(
        # Chart title
        title=dict(
            text="Median Revenue by Release Year",
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        # Background colors
        plot_bgcolor='white',
        paper_bgcolor='white',
        # Axis labels and font sizes
        xaxis=dict(
            title="",
            title_font_size=16,
            tickfont_size=16,
            gridcolor='lightgray',
            gridwidth=1,
            tickmode='linear',
            dtick=1,
            range=[int(selectedFilters["yrFrom"])-0.5, min(int(selectedFilters["yrTo"]),2024)+0.5]
        ),
        yaxis=dict(
            title="Median Revenue per Year ($)",
            title_font_size=16,
            tickfont_size=16,
            gridcolor='lightgray',
            gridwidth=1
        )
    )
    # Bar colors, text formatting, and hover styling
    fig.update_traces(
        marker_color='steelblue',
        textfont_size=14,
        hovertemplate='<b>Year: %{x}</b><br>Median Revenue: $%{y:,.0f}<extra></extra>',
        hoverlabel=dict(
            font=dict(size=16),
            bgcolor='white',
            bordercolor='gray'
        )
    )
    return fig

def plot_histogram(df, type):

    # make sure plotted column has all positive, non-null values
    if type=="revenue":
        plot_df = df.dropna(subset="revenue_est")
        plot_df = plot_df[plot_df["revenue_est"] > 0]
    elif type=="sales":
        plot_df = df.dropna(subset="copies_sold_est")
        plot_df = plot_df[plot_df["copies_sold_est"] > 0]

    # determine the number of bins:
    min_bins = 10
    max_bins = 30+1
    n = len(plot_df)
    if n<2:
        n_bins=2
    elif n<4:
        n_bins=3
    elif n<10:
        n_bins=4
    elif n < 20:
        n_bins = n//3 +1
    elif n<31:
        n_bins = n // 4 + 1
    elif n > 80000:
        n_bins = max_bins
    else:
        # Scale bins with sample size
        n_bins = int(min_bins + (max_bins - min_bins) * np.log10(n / 100) / 2.9)

    if type=="revenue":
        skew = scipy.stats.skew(plot_df["revenue_est"])
    elif type=="sales":
        skew = scipy.stats.skew(plot_df["copies_sold_est"])
    is_skewed = False
    if abs(skew)>1.4:
        if type=="revenue":
            fig = plot_hist_log(plot_df, n_bins)
        elif type=="sales":
            fig = plot_hist_log_sales(plot_df, n_bins)
        is_skewed = True
    else:
        if type == "revenue":
            fig = plot_hist_lin(plot_df, n_bins)
        elif type == "sales":
            fig = plot_hist_lin_sales(plot_df, n_bins)
    #fig = plot_hist_lin(plot_df, n_bins)

    return fig, skew, is_skewed



def plot_hist_log(df, bins):

    #print("Log scale used!")

    # Calculate logarithmic bins (same as your matplotlib/bokeh version)
    log_min = np.log10(df["revenue_est"].min() + 0.1)
    log_max = np.log10(df["revenue_est"].max())
    binlist = np.logspace(log_min, log_max, bins)

    # Create histogram data
    hist, edges = np.histogram(df["revenue_est"], bins=binlist)

    # Calculate percentages
    total_count = np.sum(hist)
    percentages = (hist / total_count) * 100

    # Prepare data for Plotly
    left_edges = edges[:-1]
    right_edges = edges[1:]
    widths = right_edges - left_edges
    centers = (left_edges + right_edges) / 2

    # Create custom hover text with count and percentage
    hover_text = [
        f"Range: ${left:,.0f} - ${right:,.0f}<br>" +
        f"No. of Games: {count:,} ({pct:.1f}%)<br>" +
        f"Center: ${center:,.0f}"
        for left, right, count, pct, center in zip(left_edges, right_edges, hist, percentages, centers)
    ]

    # Create the main histogram
    fig = go.Figure()

    # Add histogram bars
    fig.add_trace(go.Bar(
        x=centers,
        y=hist,
        width=widths,
        name="Revenue Distribution",
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_text,
        marker=dict(
            color='steelblue',
            opacity=0.8,
            line=dict(color='white', width=1)
        ),
        showlegend=False
    ))
    fig.update_traces(hoverlabel=dict(font=dict(size=16)))


    # Calculate percentiles for vertical lines
    percentiles = np.percentile(df["revenue_est"], [25, 50, 75])

    # Add vertical lines for percentiles with different line styles and colors
    line_styles = ["dot", "dash", "dashdot"]
    hex_colors = ["#FF6B35", "#004E89", "#7209B7"]  # Orange, Navy Blue, Purple
    labels = ["25% games below", "50% (median)", "75% games below"]

    max_height = max(hist)

    for percentile, line_style, color, label in zip(percentiles, line_styles, hex_colors, labels):
        fig.add_trace(go.Scatter(
            x=[percentile, percentile],
            y=[0, max_height * 1.1],
            mode='lines',
            line=dict(color="#004E89", width=1.5, dash=line_style),
            name=label,
            hoverinfo='skip',  # Remove hover info for percentile lines
            showlegend=True
        ))

    # Add percentile value annotations at the top - not working
    for i, (percentile, color) in enumerate(zip(percentiles, hex_colors)):
        fig.add_annotation(
            x=percentile,
            y=max_height * 1.08,  # Slightly higher position
            text=f"${percentile:,.0f}",
            showarrow=False,
            font=dict(size=14, color=color),
            xanchor="left",
            yanchor="bottom",
            xshift=5,  # Offset to the right of the line
            bgcolor="white",  # White background to make text more visible
            bordercolor=color,
            borderwidth=1
        )
    # Alternative approach using text shapes
    fig.add_trace(go.Scatter(
        x=percentiles,
        y=[max_height * 1.08] * len(percentiles),
        mode='text',
        text=[f" ${p:,.0f}" for p in percentiles],
        textposition="middle right",
        showlegend=False,
        hoverinfo='skip',
        textfont_size=16
    ))

    # Update layout with all customizations
    fig.update_layout(
        title=dict(
        text="Revenue Distribution<br><sub style='color: gray; font-weight: 400'>Hover over the chart for more info. Note the logarithmic scale.</sub>",
        x=0.5,  # Slightly left of center for Streamlit
        xanchor='center',
        font=dict(size=20)
        ),
        xaxis=dict(
            type="log",
            title=dict(
                text="Revenue Estimate",
                font=dict(size=20)
            ),
            tickfont=dict(size=16),
            tickformat="$,.0f",
            tickangle=45  # 45 degree rotation for tick labels
        ),
        yaxis=dict(
            title=dict(
                text="No. of Games",
                font=dict(size=18)
            ),
            tickfont=dict(size=16)
        ),
        width=800,
        height=500,
        plot_bgcolor='white',
        legend=dict(
            x=1,
            y=1,
            xanchor='right',
            yanchor='top',
            font=dict(size=16)
        ),
        hovermode='closest'
    )

    # Update grid and styling
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', type="log", range=[np.log10(df["revenue_est"].min()), np.log10(df["revenue_est"].max())])
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

    return fig

def plot_hist_lin(df, bins):
    #print("Linear!")

    # Calculate LINEAR bins (changed from logarithmic)
    min_val = df["revenue_est"].min()
    max_val = df["revenue_est"].max()
    binlist = np.linspace(min_val, max_val, bins)

    # Create histogram data
    hist, edges = np.histogram(df["revenue_est"], bins=binlist)

    # Calculate percentages
    total_count = np.sum(hist)
    percentages = (hist / total_count) * 100

    # Prepare data for Plotly
    left_edges = edges[:-1]
    right_edges = edges[1:]
    widths = right_edges - left_edges
    centers = (left_edges + right_edges) / 2

    # Create custom hover text with count and percentage
    hover_text = [
        f"Range: ${left:,.0f} - ${right:,.0f}<br>" +
        f"No. of Games: {count:,} ({pct:.1f}%)<br>" +
        f"Center: ${center:,.0f}"
        for left, right, count, pct, center in zip(left_edges, right_edges, hist, percentages, centers)
    ]

    # Create the main histogram
    fig = go.Figure()

    # Add histogram bars
    fig.add_trace(go.Bar(
        x=centers,
        y=hist,
        width=widths,
        name="Revenue Distribution",
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_text,
        marker=dict(
            color='steelblue',
            opacity=0.8,
            line=dict(color='white', width=1)
        ),
        showlegend=False
    ))
    fig.update_traces(hoverlabel=dict(font=dict(size=16)))

    # Calculate percentiles for vertical lines
    percentiles = np.percentile(df["revenue_est"], [25, 50, 75])

    # Add vertical lines for percentiles with different line styles and colors
    line_styles = ["dot", "dash", "dashdot"]
    hex_colors = ["#FF6B35", "#004E89", "#7209B7"]  # Orange, Navy Blue, Purple
    labels = ["25% games below", "50% (median)", "75% games below"]

    max_height = max(hist)

    for percentile, line_style, color, label in zip(percentiles, line_styles, hex_colors, labels):
        fig.add_trace(go.Scatter(
            x=[percentile, percentile],
            y=[0, max_height * 1.1],
            mode='lines',
            line=dict(color="#004E89", width=1.5, dash=line_style),
            name=label,
            hoverinfo='skip',  # Remove hover info for percentile lines
            showlegend=True
        ))

    # Add percentile value annotations at the top
    for i, (percentile, color) in enumerate(zip(percentiles, hex_colors)):
        fig.add_annotation(
            x=percentile,
            y=max_height * 1.08,
            text=f"${percentile:,.0f}",
            showarrow=False,
            font=dict(size=16, color="#004E89"),
            xanchor="left",
            yanchor="bottom",
            xshift=5,  # Offset to the right of the line
            bgcolor="white",
            # bordercolor=color,
            borderwidth=0
        )

    # Update layout with all customizations
    fig.update_layout(
        title=dict(
            text="Revenue Distribution<br><sub style='color: gray; font-weight: 400'>Hover over the chart for more information</sub>",
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        xaxis=dict(
            type="linear",
            title=dict(
                text="Revenue Estimate",
                font=dict(size=18)
            ),
            tickfont=dict(size=16),
            tickformat="$,.0f",
            tickangle=45,
            range=[min_val, max_val]
        ),
        yaxis=dict(
            title=dict(
                text="No. of Games",
                font=dict(size=18)
            ),
            tickfont=dict(size=16)
        ),
        width=800,
        height=500,
        plot_bgcolor='white',
        legend=dict(
            x=1,
            y=1,
            xanchor='right',
            yanchor='top',
            font=dict(size=16)
        ),
        hovermode='closest'
    )

    # Update grid and styling
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

    return fig

def plot_distribution(df):
    temp_df = df[["name", "revenue_est"]]
    temp_df.columns = ["Title", "Revenue"]
    fig = px.strip(temp_df, x="Revenue", hover_data=temp_df.columns, height=300)

    # Increase marker size
    fig.update_traces(marker=dict(size=12))

    fig.update_layout(
        title=dict(
            text="Revenue Distribution (Linear Scale)",
            x=0.5,  # Center the title
            xanchor='center',
            font=dict(size=18)  # Title font size
        )
    )

    fig.update_xaxes(range=[-100, temp_df['Revenue'].max()+1000],
                     type="linear",
                     title="Revenue Estimate",
                     showgrid=True,
                     title_font_size=16,
                     tickfont_size=16)
    fig.update_yaxes(
        showticklabels=False,  # Hide tick labels
        title="",  # Remove axis title
        showgrid=False,  # Remove grid lines
        zeroline=False  # Remove zero line
    )
    return fig




def plot_hist_lin_sales(df, bins):
    #print("Linear!")

    # Calculate LINEAR bins (changed from logarithmic)
    min_val = df["copies_sold_est"].min()
    max_val = df["copies_sold_est"].max()
    binlist = np.linspace(min_val, max_val, bins)

    # Create histogram data
    hist, edges = np.histogram(df["copies_sold_est"], bins=binlist)

    # Calculate percentages
    total_count = np.sum(hist)
    percentages = (hist / total_count) * 100

    # Prepare data for Plotly
    left_edges = edges[:-1]
    right_edges = edges[1:]
    widths = right_edges - left_edges
    centers = (left_edges + right_edges) / 2

    # Create custom hover text with count and percentage
    hover_text = [
        f"Range: ${left:,.0f} - ${right:,.0f}<br>" +
        f"No. of Games: {count:,} ({pct:.1f}%)<br>" +
        f"Center: ${center:,.0f}"
        for left, right, count, pct, center in zip(left_edges, right_edges, hist, percentages, centers)
    ]

    # Create the main histogram
    fig = go.Figure()

    # Add histogram bars
    fig.add_trace(go.Bar(
        x=centers,
        y=hist,
        width=widths,
        name="Sales Distribution",
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_text,
        marker=dict(
            color='steelblue',
            opacity=0.8,
            line=dict(color='white', width=1)
        ),
        showlegend=False
    ))
    fig.update_traces(hoverlabel=dict(font=dict(size=16)))

    # Calculate percentiles for vertical lines
    percentiles = np.percentile(df["copies_sold_est"], [25, 50, 75])

    # Add vertical lines for percentiles with different line styles and colors
    line_styles = ["dot", "dash", "dashdot"]
    hex_colors = ["#FF6B35", "#004E89", "#7209B7"]  # Orange, Navy Blue, Purple
    labels = ["25% games below", "50% (median)", "75% games below"]

    max_height = max(hist)

    for percentile, line_style, color, label in zip(percentiles, line_styles, hex_colors, labels):
        fig.add_trace(go.Scatter(
            x=[percentile, percentile],
            y=[0, max_height * 1.1],
            mode='lines',
            line=dict(color="#004E89", width=1.5, dash=line_style),
            name=label,
            hoverinfo='skip',  # Remove hover info for percentile lines
            showlegend=True
        ))

    # Add percentile value annotations at the top
    for i, (percentile, color) in enumerate(zip(percentiles, hex_colors)):
        fig.add_annotation(
            x=percentile,
            y=max_height * 1.08,
            text=f"${percentile:,.0f}",
            showarrow=False,
            font=dict(size=16, color="#004E89"),
            xanchor="left",
            yanchor="bottom",
            xshift=5,  # Offset to the right of the line
            bgcolor="white",
            # bordercolor=color,
            borderwidth=0
        )

    # Update layout with all customizations
    fig.update_layout(
        title=dict(
            text="Sales Distribution<br><sub style='color: gray; font-weight: 400'>Hover over the chart for more information</sub>",
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        xaxis=dict(
            type="linear",
            title=dict(
                text="Sales Estimate (copies sold)",
                font=dict(size=18)
            ),
            tickfont=dict(size=16),
            tickformat=".0f",
            tickangle=45,
            range=[min_val, max_val]
        ),
        yaxis=dict(
            title=dict(
                text="No. of Games",
                font=dict(size=18)
            ),
            tickfont=dict(size=16)
        ),
        width=800,
        height=500,
        plot_bgcolor='white',
        legend=dict(
            x=1,
            y=1,
            xanchor='right',
            yanchor='top',
            font=dict(size=16)
        ),
        hovermode='closest'
    )

    # Update grid and styling
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

    return fig


def plot_hist_log_sales(df, bins):

    #print("Log scale used!")

    # Calculate logarithmic bins (same as your matplotlib/bokeh version)
    log_min = np.log10(df["copies_sold_est"].min() + 0.1)
    log_max = np.log10(df["copies_sold_est"].max())
    binlist = np.logspace(log_min, log_max, bins)

    # Create histogram data
    hist, edges = np.histogram(df["copies_sold_est"], bins=binlist)

    # Calculate percentages
    total_count = np.sum(hist)
    percentages = (hist / total_count) * 100

    # Prepare data for Plotly
    left_edges = edges[:-1]
    right_edges = edges[1:]
    widths = right_edges - left_edges
    centers = (left_edges + right_edges) / 2

    # Create custom hover text with count and percentage
    hover_text = [
        f"Range: {left:,.0f} - {right:,.0f}<br>" +
        f"No. of Games: {count:,} ({pct:.1f}%)<br>" +
        f"Center: Sold copies:{center:,.0f}"
        for left, right, count, pct, center in zip(left_edges, right_edges, hist, percentages, centers)
    ]

    # Create the main histogram
    fig = go.Figure()

    # Add histogram bars
    fig.add_trace(go.Bar(
        x=centers,
        y=hist,
        width=widths,
        name="Sales Distribution",
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_text,
        marker=dict(
            color='steelblue',
            opacity=0.8,
            line=dict(color='white', width=1)
        ),
        showlegend=False
    ))
    fig.update_traces(hoverlabel=dict(font=dict(size=16)))


    # Calculate percentiles for vertical lines
    percentiles = np.percentile(df["copies_sold_est"], [25, 50, 75])

    # Add vertical lines for percentiles with different line styles and colors
    line_styles = ["dot", "dash", "dashdot"]
    hex_colors = ["#FF6B35", "#004E89", "#7209B7"]  # Orange, Navy Blue, Purple
    labels = ["25% games below", "50% (median)", "75% games below"]

    max_height = max(hist)

    for percentile, line_style, color, label in zip(percentiles, line_styles, hex_colors, labels):
        fig.add_trace(go.Scatter(
            x=[percentile, percentile],
            y=[0, max_height * 1.1],
            mode='lines',
            line=dict(color="#004E89", width=1.5, dash=line_style),
            name=label,
            hoverinfo='skip',  # Remove hover info for percentile lines
            showlegend=True
        ))

    # Add percentile value annotations at the top - not working
    for i, (percentile, color) in enumerate(zip(percentiles, hex_colors)):
        fig.add_annotation(
            x=percentile,
            y=max_height * 1.08,  # Slightly higher position
            text=f"{percentile:,.0f}",
            showarrow=False,
            font=dict(size=14, color=color),
            xanchor="left",
            yanchor="bottom",
            xshift=5,  # Offset to the right of the line
            bgcolor="white",  # White background to make text more visible
            bordercolor=color,
            borderwidth=1
        )
    # Alternative approach using text shapes
    fig.add_trace(go.Scatter(
        x=percentiles,
        y=[max_height * 1.08] * len(percentiles),
        mode='text',
        text=[f" {p:,.0f}" for p in percentiles],
        textposition="middle right",
        showlegend=False,
        hoverinfo='skip',
        textfont_size=16
    ))

    # Update layout with all customizations
    fig.update_layout(
        title=dict(
        text="Sales Distribution<br><sub style='color: gray; font-weight: 400'>Hover over the chart for more info. Note the logarithmic scale.</sub>",
        x=0.5,  # Slightly left of center for Streamlit
        xanchor='center',
        font=dict(size=20)
        ),
        xaxis=dict(
            type="log",
            title=dict(
                text="Sales Estimate (copies sold)",
                font=dict(size=20)
            ),
            tickfont=dict(size=16),
            tickformat=".0f",
            tickangle=45  # 45 degree rotation for tick labels
        ),
        yaxis=dict(
            title=dict(
                text="No. of Games",
                font=dict(size=18)
            ),
            tickfont=dict(size=16)
        ),
        width=800,
        height=500,
        plot_bgcolor='white',
        legend=dict(
            x=1,
            y=1,
            xanchor='right',
            yanchor='top',
            font=dict(size=16)
        ),
        hovermode='closest'
    )

    # Update grid and styling
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', type="log", range=[np.log10(df["copies_sold_est"].min()), np.log10(df["copies_sold_est"].max())])
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

    return fig

if __name__ == "__main__":
    data_df = pd.read_csv("files/steam_show_df.csv")
    fig = plot_histogram(data_df)
    fig.show()