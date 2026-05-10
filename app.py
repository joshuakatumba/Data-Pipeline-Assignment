import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# == Page Config ==
st.set_page_config(
    page_title="Patent Intelligence Dashboard",
    page_icon=".",
    layout="wide",
    initial_sidebar_state="expanded",
)

# == Custom CSS ==
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hero header */
.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF 0%, #48C6EF 50%, #A855F7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
    letter-spacing: -1px;
}
.hero-sub {
    font-size: 1.05rem;
    color: #8B949E;
    margin-top: 4px;
    margin-bottom: 28px;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(145deg, #161B22 0%, #1C2333 100%);
    border: 1px solid rgba(108,99,255,0.15);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(108,99,255,0.18);
}
.metric-icon { margin-bottom: 8px; display: flex; justify-content: center; }
.metric-icon svg { width: 28px; height: 28px; }
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6C63FF, #48C6EF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-label { font-size: 0.82rem; color: #8B949E; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }

/* Section headers */
.section-header {
    font-size: 1.35rem;
    font-weight: 700;
    color: #E6EDF3;
    margin: 32px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(108,99,255,0.3);
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1117 0%, #161B22 100%);
    border-right: 1px solid rgba(108,99,255,0.12);
}
section[data-testid="stSidebar"] .stMarkdown h1 {
    font-size: 1.3rem;
    background: linear-gradient(135deg, #6C63FF, #A855F7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Dataframe */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Hide Streamlit branding */
footer {visibility: hidden;}

/* Slider label */
.stSlider label { font-weight: 600; color: #C9D1D9 !important; }
</style>
""", unsafe_allow_html=True)

# == Plotly Theme ==
COLORS = ["#6C63FF","#48C6EF","#A855F7","#F472B6","#34D399","#FBBF24","#FB923C","#F87171"]

def styled_bar(df, x, y, title, horizontal=False):
    if horizontal:
        fig = px.bar(df, x=y, y=x, orientation='h', color=y,
                     color_continuous_scale=["#161B22","#6C63FF"], title=title)
    else:
        fig = px.bar(df, x=x, y=y, color=y,
                     color_continuous_scale=["#161B22","#6C63FF"], title=title)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#C9D1D9"),
        title=dict(font=dict(size=16, color="#E6EDF3")),
        coloraxis_showscale=False, showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(gridcolor="rgba(108,99,255,0.08)"),
        yaxis=dict(gridcolor="rgba(108,99,255,0.08)"),
    )
    fig.update_traces(marker_line_width=0, marker_cornerradius=6)
    return fig

def styled_line(df, x, y_cols, title, colors=None):
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        c = (colors or COLORS)[i % len(colors or COLORS)]
        dash = "solid" if i == 0 else "dash"
        fig.add_trace(go.Scatter(x=df[x], y=df[col], name=col, mode="lines+markers",
                                 line=dict(color=c, width=3, dash=dash),
                                 marker=dict(size=6)))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#C9D1D9"),
        title=dict(text=title, font=dict(size=16, color="#E6EDF3")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11)),
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(gridcolor="rgba(108,99,255,0.08)"),
        yaxis=dict(gridcolor="rgba(108,99,255,0.08)"),
    )
    return fig

def styled_pie(df, names, values, title):
    fig = px.pie(df, names=names, values=values, title=title, color_discrete_sequence=COLORS,
                 hole=0.55)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#C9D1D9"),
        title=dict(font=dict(size=16, color="#E6EDF3")),
        legend=dict(font=dict(size=11)),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_traces(textinfo="percent+label", textfont_size=11)
    return fig

# == Data Loading ==
@st.cache_data
def load_full_data():
    conn = sqlite3.connect("patents.db")
    df_patents = pd.read_sql_query("SELECT * FROM patents", conn)
    df_inventors = pd.read_sql_query("SELECT * FROM inventors", conn)
    df_companies = pd.read_sql_query("SELECT * FROM companies", conn)
    df_rels = pd.read_sql_query("SELECT * FROM relationships", conn)
    conn.close()
    return df_patents, df_inventors, df_companies, df_rels

try:
    df_patents, df_inventors, df_companies, df_rels = load_full_data()

    # == Sidebar Filters ==
    with st.sidebar:
        st.markdown("# Patent Explorer")
        st.markdown("---")

        st.markdown("### Year Range")
        min_yr, max_yr = int(df_patents["year"].min()), int(df_patents["year"].max())
        year_range = st.slider("Select year range", min_yr, max_yr, (min_yr, max_yr), key="year_slider")

        st.markdown("### Classification")
        all_classes = sorted(df_patents["classification"].dropna().unique().tolist())
        selected_classes = st.multiselect("Filter by category", all_classes, default=all_classes)

        st.markdown("### Country")
        all_countries = sorted(df_inventors["country"].dropna().unique().tolist())
        selected_countries = st.multiselect("Filter by country", all_countries, default=all_countries)

        st.markdown("### Display Controls")
        top_n = st.slider("Top N results to show", 3, 25, 10, key="topn_slider")
        show_projections = st.toggle("Show Trend Projections", value=True)
        projection_years = st.slider("Projection years ahead", 1, 10, 5, key="proj_slider") if show_projections else 0

        st.markdown("---")
        st.markdown("### Patent Search")
        search_query = st.text_input("Search titles & abstracts", placeholder="e.g. semiconductor")

    # == Apply Filters ==
    filtered_patents = df_patents[
        (df_patents["year"] >= year_range[0]) &
        (df_patents["year"] <= year_range[1]) &
        (df_patents["classification"].isin(selected_classes))
    ]

    # Filter by country via inventors
    country_inventor_ids = df_inventors[df_inventors["country"].isin(selected_countries)]["inventor_id"]
    country_patent_ids = df_rels[df_rels["inventor_id"].isin(country_inventor_ids)]["patent_id"].unique()
    filtered_patents = filtered_patents[filtered_patents["patent_id"].isin(country_patent_ids)]

    # Search
    if search_query:
        mask = (
            filtered_patents["title"].str.contains(search_query, case=False, na=False) |
            filtered_patents["abstract"].str.contains(search_query, case=False, na=False)
        )
        filtered_patents = filtered_patents[mask]

    filtered_rels = df_rels[df_rels["patent_id"].isin(filtered_patents["patent_id"])]

    # == Hero Header ==
    st.markdown('<p class="hero-title">Global Patent Intelligence</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Interactive analytics dashboard - adjust sliders in the sidebar to explore custom data views</p>', unsafe_allow_html=True)

    # == KPI Metrics ==
    total = len(filtered_patents)
    n_inventors = filtered_rels["inventor_id"].nunique()
    n_companies = filtered_rels["company_id"].nunique()
    n_categories = filtered_patents["classification"].nunique()
    yr_span = f"{year_range[0]} - {year_range[1]}"

    cols = st.columns(5)
    svg_icons = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#6C63FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#48C6EF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#A855F7" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 7V5a4 4 0 0 0-8 0v2"/></svg>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#F472B6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    ]
    labels = ["Patents","Inventors","Companies","Categories","Year Span"]
    values = [f"{total:,}", f"{n_inventors:,}", f"{n_companies:,}", str(n_categories), yr_span]
    for col, svg, label, val in zip(cols, svg_icons, labels, values):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{svg}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # == Row 1: Top Inventors and Companies ==
    st.markdown('<div class="section-header"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FBBF24" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg> Top Performers</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        inv_counts = (filtered_rels.merge(df_inventors, on="inventor_id")
                      .groupby("name")["patent_id"].count()
                      .nlargest(top_n).reset_index(name="patents"))
        if not inv_counts.empty:
            st.plotly_chart(styled_bar(inv_counts, "name", "patents", f"Top {top_n} Inventors", horizontal=True),
                           use_container_width=True)
        else:
            st.info("No inventor data matches your filters.")

    with c2:
        comp_counts = (filtered_rels.merge(df_companies, on="company_id")
                       .groupby("name")["patent_id"].count()
                       .nlargest(top_n).reset_index(name="patents"))
        if not comp_counts.empty:
            st.plotly_chart(styled_bar(comp_counts, "name", "patents", f"Top {top_n} Companies", horizontal=True),
                           use_container_width=True)
        else:
            st.info("No company data matches your filters.")

    # == Row 2: Trends and Categories ==
    st.markdown('<div class="section-header"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#48C6EF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg> Trends & Classification</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        trends = (filtered_patents.groupby("year")["patent_id"].count()
                  .reset_index(name="Historical"))
        if not trends.empty and len(trends) >= 2:
            if show_projections and projection_years > 0:
                x_h = trends["year"].values
                y_h = trends["Historical"].values
                z = np.polyfit(x_h, y_h, 1)
                p = np.poly1d(z)
                last = int(x_h[-1])
                x_f = np.arange(last + 1, last + 1 + projection_years)
                y_f = np.maximum(0, p(x_f))
                proj_df = pd.DataFrame({"year": x_f, "Projected": y_f})
                combined = trends.merge(proj_df, on="year", how="outer").sort_values("year")
            else:
                combined = trends.copy()
                combined["Projected"] = np.nan
            y_cols = ["Historical"] + (["Projected"] if combined["Projected"].notna().any() else [])
            st.plotly_chart(styled_line(combined, "year", y_cols,
                           "Patent Filing Trends & Projections", ["#6C63FF","#F472B6"]),
                           use_container_width=True)
        else:
            st.info("Not enough trend data for the selected filters.")

    with c4:
        cat_counts = (filtered_patents.groupby("classification")["patent_id"].count()
                      .nlargest(top_n).reset_index(name="patents"))
        if not cat_counts.empty:
            st.plotly_chart(styled_pie(cat_counts, "classification", "patents",
                           "Patent Categories Distribution"), use_container_width=True)
        else:
            st.info("No category data matches your filters.")

    # == Row 3: Country and Heatmap ==
    st.markdown('<div class="section-header"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg> Geographic & Temporal Analysis</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)

    with c5:
        country_counts = (filtered_rels.merge(df_inventors, on="inventor_id")
                          .groupby("country")["patent_id"].nunique()
                          .nlargest(top_n).reset_index(name="patents"))
        if not country_counts.empty:
            st.plotly_chart(styled_bar(country_counts, "country", "patents",
                           f"Top {top_n} Countries by Patent Count"), use_container_width=True)
        else:
            st.info("No country data matches your filters.")

    with c6:
        heat_data = (filtered_patents.groupby(["year","classification"])["patent_id"]
                     .count().reset_index(name="count"))
        if not heat_data.empty:
            pivot = heat_data.pivot(index="classification", columns="year", values="count").fillna(0)
            fig_heat = px.imshow(pivot, aspect="auto", color_continuous_scale=["#0D1117","#6C63FF","#A855F7"],
                                 title="Classification x Year Heatmap")
            fig_heat.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#C9D1D9"),
                title=dict(font=dict(size=16, color="#E6EDF3")),
                margin=dict(l=20, r=20, t=50, b=20),
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Not enough data for heatmap.")

    # == Qualitative Data Table ==
    st.markdown('<div class="section-header"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#A855F7" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg> Patent Records Explorer</div>', unsafe_allow_html=True)
    display_df = filtered_patents[["title","abstract","classification","year"]].copy()
    display_df.columns = ["Title","Abstract","Classification","Year"]
    display_df = display_df.sort_values("Year", ascending=False).head(100)
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=420)

    # == Footer ==
    st.markdown("---")
    st.markdown(
        '<p style="text-align:center;color:#484F58;font-size:0.8rem;">'
        'Global Patent Intelligence Dashboard &middot; Built with Streamlit & Plotly'
        '</p>', unsafe_allow_html=True
    )

except sqlite3.OperationalError:
    st.error("Database not found! Please run the data pipeline scripts first.")
    st.code("python scripts/1_extract_data.py\npython scripts/2_clean_data.py\npython scripts/3_load_to_sql.py\npython scripts/4_analyze_and_report.py")
