# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import base64
from PIL import Image
import io

# ---------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & BACKGROUND
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Lines Drawn, Lives Lost",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Function to embed background image (bg.png) via base64
def set_background(png_path: str):
    """
    Load image from assets/bg.png and embed it as CSS background full-screen.
    """
    with open(png_path, "rb") as file:
        data = file.read()
    b64 = base64.b64encode(data).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{b64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_background("assets/bg.png")

# ---------------------------------------------------------------------------
# 2. CUSTOM FONTS & GLOBAL COLORS
# ---------------------------------------------------------------------------

FONT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');

/* Application-wide styling */
body, * {
    font-family: 'Poppins', sans-serif !important;
    color: #FFFFFF;
}

/* Main titles & subtitles using Bernard MT Condensed */
h1 {
    font-family: 'Bernard MT Condensed', serif !important;
    color: #FFFFF;
    margin-bottom: 0.25rem;
}
h1 .highlight {
    font-family: 'Bernard MT Condensed', serif !important; 
    color: #E5C056;
}

h2 {
    font-family: 'Bernard MT Condensed', serif !important;
    color: #E5C056;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}

/* For subtitle/h3 we use Poppins Bold */
h3 {
    font-family: 'Poppins', sans-serif !important;
    color: #E5C056;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

/* Box and card colors */
.div-box {
    background-color: rgba(43, 45, 66, 0.8);
    padding: 1rem;
    border-radius: 8px;
}

/* Custom Footer */
.custom-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: rgba(43, 45, 66, 0.9);
    color: #E5C056;
    text-align: center;
    padding: 10px 0;
    font-family: 'Poppins', sans-serif !important;
    font-size: 14px;
    z-index: 999;
    border-top: 1px solid rgba(229, 192, 86, 0.3);
}

/* Hide default Streamlit menu & footer if desired */
# MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(FONT_CSS, unsafe_allow_html=True)

# Global color palette
COLOR_PRIMARY = "#2B2D42"   # dark navy
COLOR_ACCENT  = "#E5C056"   # golden yellow
COLOR_WHITE   = "#FFFFFF"

# ---------------------------------------------------------------------------
# 3. HORIZONTAL NAVIGATION (top menu bar)
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* Override Streamlit's container width */
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: none !important;
    }
    
    .navbar-container {
        background: linear-gradient(135deg, rgba(43, 45, 66, 0.95), rgba(43, 45, 66, 0.85));
        padding: 20px 30px;
        border-radius: 15px;
        margin: 0 calc(-50vw + 50%) 30px calc(-50vw + 50%);
        width: 100vw;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(229, 192, 86, 0.2);
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        margin-top: -70px;
    }
    
    .navbar-title {
        font-family: 'Bernard MT Condensed', serif !important;
        font-size: 3.2rem;
        color: #FFFFFF;
        margin: 0 0 15px 0;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    
    .navbar-title .highlight {
        font-family: 'Bernard MT Condensed', serif !important;
        color: #E5C056;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    
    .navbar-menu {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    /* Custom radio button styling */
    .stRadio > div {
        display: flex;
        justify-content: center;
        gap: 10px;
    }
    
    .stRadio > div > label {
        background: linear-gradient(145deg, rgba(229, 192, 86, 0.1), rgba(229, 192, 86, 0.05));
        color: #FFFFFF !important;
        padding: 12px 24px !important;
        border-radius: 25px !important;
        border: 2px solid rgba(229, 192, 86, 0.3) !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        font-weight: 500 !important;
        font-size: 16px !important;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stRadio > div > label:hover {
        background: linear-gradient(145deg, rgba(229, 192, 86, 0.2), rgba(229, 192, 86, 0.1)) !important;
        border-color: rgba(229, 192, 86, 0.6) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(229, 192, 86, 0.2) !important;
    }
    
    .stRadio > div > label[data-checked="true"] {
        background: linear-gradient(145deg, #E5C056, #d4af4a) !important;
        color: #2B2D42 !important;
        border-color: #E5C056 !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 25px rgba(229, 192, 86, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Hide radio button circles */
    .stRadio > div > label > div:first-child {
        display: none !important;
    }
    
    /* Style the text container */
    .stRadio > div > label > div:last-child {
        padding-left: 0 !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .navbar-title {
            font-size: 2.5rem;
        }
        
        .stRadio > div {
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .stRadio > div > label {
            padding: 10px 18px !important;
            font-size: 14px !important;
        }
        
        .navbar-container {
            padding: 15px 20px;
        }
    }
    </style>

    <div class="navbar-container">
      <div class="navbar-title">Lines Drawn <span class="highlight">Lives Lost</span></div>
      <div class="navbar-menu">
    """,
    unsafe_allow_html=True
)

menu = st.radio(
    "",
    ("Changing Borders", "The Population", "The Cost", "Data Sources"),
    horizontal=True,
    index=0,
    label_visibility="collapsed",
    key="main_navigation"
)

st.markdown(
    """
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------------
# 4. FUNCTIONALITY FOR EACH PAGE BASED ON MENU
# ---------------------------------------------------------------

# 4.1 "Changing Borders" Page
def show_changing_borders():
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("<h1>Changing <span class='highlight'>Borders</span></h1>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="div-box" style="margin-bottom:1.5rem;">
              <p>
                This interactive map traces the shifting borders between Israel and Palestine over time, 
                visualizing the transformation of territorial control from 1918, 1947, 1960, to 2015. 
                Each year reflects major geopolitical events that reshaped land and lives.
              </p>
              <p style="font-size:0.9rem; color:#FFFFFF;">
                *Use the slider below to select a year and view the interactive map.*
              </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # slider
        years = [1918, 1947, 1960, 2015]
        selected_year = st.select_slider(
            label="Select Year:",
            options=years,
            value=1918,             # default value
            format_func=lambda x: str(x),
            key="border_year_slider"
        )

        st.markdown(
            """
            <div style="
                display: flex; 
                justify-content: space-between; 
                padding: 0 0.5rem; 
                margin-top: -0.5rem; 
                font-size: 0.9rem; 
                color: #FFFFFF;">
              <span>1918</span>
              <span>1947</span>
              <span>1960</span>
              <span>2015</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div style="margin-top: 0.5rem; color: #FFFFFF;">
                <strong>Selected Year:</strong> 
                <span style="color:{COLOR_ACCENT}; font-size:1.2rem;">{selected_year}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        # # color legend for map
        # st.markdown(
        #     f"""
        #     <div style="
        #         display: flex; 
        #         align-items: center; 
        #         gap: 1rem; 
        #         margin-top: 0.5rem;
        #     ">
        #       <div style="
        #           width:20px; 
        #           height:20px; 
        #           background-color:#020404; 
        #           border-radius:3px;
        #           border:1px solid #FFFFFF;
        #           ">
        #       </div>
        #       <span style="color:#FFFFFF; font-size:0.95rem;">Israel</span>
        #       <div style="
        #           width:20px; 
        #           height:20px; 
        #           background-color:{COLOR_ACCENT}; 
        #           border-radius:3px;
        #           border:1px solid #FFFFFF;
        #           ">
        #       </div>
        #       <span style="color:#FFFFFF; font-size:0.95rem;">Palestine</span>
        #     </div>
        #     """,
        #     unsafe_allow_html=True
        # )

    with col_right:
        if   selected_year == 1918: img_path = "assets/1918.png"
        elif selected_year == 1947: img_path = "assets/1947.png"
        elif selected_year == 1960: img_path = "assets/1960.png"
        elif selected_year == 2015: img_path = "assets/2015.png"
        else:                       img_path = None

        if img_path:
            try:
                image = Image.open(img_path)
                st.image(
                    image,
                    use_container_width=False,
                    width=400
                )
                st.markdown(
                    f"""
                    <p style="color: #FFFFFF; font-weight: bold; 
                              margin-top: 0.5rem; font-size: 0.95rem; margin-left: 11.5rem;">
                      Map year {selected_year}
                    </p>
                    """,
                    unsafe_allow_html=True
                )
            except FileNotFoundError:
                st.error("Failed to load image: file not found in assets/ folder.")
        else:
            st.error("Invalid year or image file not yet available.")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# 4.2 "The Population" Page
def show_population():
    st.markdown("<h1>The <span class='highlight'>Population</span></h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="div-box">
        <p>
        War leaves its mark not just in loss, but in survival. This section tracks population changes 
        in Israel and Palestinian territories over time, showing resilience, displacement, 
        and demographic trends shaped by conflict and migration.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------
    # 4.2.1 Load Population Dataset
    # ------------------------------
    url_palestine = "https://drive.google.com/uc?id=1Kr3mWDhTErT9OlibX_aBaHVtNvRTlZhx"
    url_israel    = "https://drive.google.com/uc?id=1pfdUGsK4uKs-c7KUQ_zsnKVOkWadu0cw"

    @st.cache_data(show_spinner=False)
    def load_population_data():
        df_p = pd.read_csv(url_palestine)
        df_i = pd.read_csv(url_israel)
        # Clean string columns (remove ',' and '%')
        for df in (df_p, df_i):
            df["Population"]       = pd.to_numeric(df["Population"].str.replace(",", ""), errors="coerce")
            df["Yearly % Change"]  = pd.to_numeric(df["Yearly % Change"].str.replace("%", ""), errors="coerce")
            df["Yearly Change"]    = pd.to_numeric(df["Yearly Change"].str.replace(",", ""), errors="coerce")
            df["Migrants (net)"]   = pd.to_numeric(df["Migrants (net)"].str.replace(",", ""), errors="coerce")
            df["Urban Pop %"]      = pd.to_numeric(df["Urban Pop %"].str.replace("%", ""), errors="coerce")
            df["Urban Population"] = pd.to_numeric(df["Urban Population"].str.replace(",", ""), errors="coerce")
            df["Country's Share of World Pop"] = pd.to_numeric(df["Country's Share of World Pop"].str.replace("%", ""), errors="coerce")
            df["World Population"] = pd.to_numeric(df["World Population"].str.replace(",", ""), errors="coerce")
        df_p["Country"] = "Palestine"
        df_i["Country"] = "Israel"
        return df_p, df_i

    df_p, df_i = load_population_data()

    # ------------------------------
    # 4.2.1.5 Population Growth Overview (1955 vs 2025)
    # ------------------------------
    # Calculate population growth from 1955 to 2025
    def calculate_growth(df, country_name):
        pop_1955 = df[df["Year"] == 1955]["Population"].iloc[0] if len(df[df["Year"] == 1955]) > 0 else None
        pop_2025 = df[df["Year"] == 2025]["Population"].iloc[0] if len(df[df["Year"] == 2025]) > 0 else None
        
        if pop_1955 and pop_2025:
            growth_percent = ((pop_2025 - pop_1955) / pop_1955) * 100
            return pop_1955, pop_2025, growth_percent
        return None, None, None

    # Get growth data
    pal_1955, pal_2025, pal_growth = calculate_growth(df_p, "Palestine")
    isr_1955, isr_2025, isr_growth = calculate_growth(df_i, "Israel")

    # Display overview
    st.markdown(
        """
        <style>
        .growth-overview {
            background: linear-gradient(135deg, rgba(43, 45, 66, 0.9), rgba(43, 45, 66, 0.7));
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0;
            border: 1px solid rgba(229, 192, 86, 0.3);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        .growth-number {
            font-size: 2.2rem;
            font-weight: bold;
            margin: 0.2rem 0;
        }
        .growth-subtitle {
            margin-bottom: 0.5rem;
            margin-top: 0;
        }
        .growth-description {
            font-size: 0.9rem;
            margin-top: 0.5rem;
            opacity: 0.9;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h3>Population Growth Overview (1955 - 2025)</h3>", unsafe_allow_html=True)
    
    overview_col1, overview_col2, overview_col3 = st.columns([1,1,1])
    
    with overview_col1:
        if pal_growth is not None and isr_growth is not None:
            total_growth = (pal_growth + isr_growth) / 2
            st.markdown(
                f"""
                <div class="growth-overview">
                    <h3 class="growth-subtitle" style="color:{COLOR_WHITE};">Average Growth</h3>
                    <div class="growth-number" style="color:{COLOR_ACCENT};">+{total_growth:.1f}%</div>
                    <p class="growth-description" style="color:{COLOR_WHITE};">
                        Combined regional population growth over 70 years
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with overview_col2:
        if pal_growth is not None:
            growth_arrow = "↗️" if pal_growth > 0 else "↘️"
            st.markdown(
                f"""
                <div class="growth-overview">
                    <h3 class="growth-subtitle" style="color:{COLOR_WHITE};">
                        <span style="color:{COLOR_ACCENT};">Palestinian</span> Growth
                    </h3>
                    <div class="growth-number" style="color:{COLOR_ACCENT};">
                        {growth_arrow} {pal_growth:+.1f}%
                    </div>
                    <p class="growth-description" style="color:{COLOR_WHITE};">
                        From {pal_1955:,.0f} to {pal_2025:,.0f} people
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with overview_col3:
        if isr_growth is not None:
            growth_arrow = "↗️" if isr_growth > 0 else "↘️"
            st.markdown(
                f"""
                <div class="growth-overview">
                    <h3 class="growth-subtitle" style="color:{COLOR_WHITE};">
                        <span style="color:{COLOR_ACCENT}">Israeli</span> Growth
                    </h3>
                    <div class="growth-number" style="color:{COLOR_ACCENT};">
                        {growth_arrow} {isr_growth:+.1f}%
                    </div>
                    <p class="growth-description" style="color:{COLOR_WHITE};">
                        From {isr_1955:,.0f} to {isr_2025:,.0f} people
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")

    # Combine both dataframes for trend chart
    population_combined = pd.concat([
        df_p[["Year", "Population", "Country"]],
        df_i[["Year", "Population", "Country"]]
    ], ignore_index=True)

    # ------------------------------
    # 4.2.2 Chart 1: Population Trend (Line Chart)
    # ------------------------------
    st.markdown("<h3>Yearly Overview</h3>", unsafe_allow_html=True)

    fig_trend = px.line(
        population_combined,
        x="Year",
        y="Population",
        color="Country",
        color_discrete_map={"Palestine": COLOR_ACCENT, "Israel": COLOR_PRIMARY},
        markers=True,
        labels={"Population": "Population", "Year": "Year"},
    )
    fig_trend.update_layout(
        plot_bgcolor="rgba(255,255,255,1)",
        paper_bgcolor="rgba(255,255,255,1)",
        font=dict(color="#000000"),
        legend=dict(
            title="", 
            font=dict(color="#000000"),
            bgcolor="rgba(255,255,255,1)"
        ),
        xaxis=dict(
            title=dict(text="Year", font=dict(size=14, color="#000000")),
            showgrid=True, 
            gridcolor="rgba(0,0,0,0.1)", 
            tickfont=dict(color="#000000")
        ),
        yaxis=dict(
            title=dict(text="Population", font=dict(size=14, color="#000000")),
            showgrid=True, 
            gridcolor="rgba(0,0,0,0.1)", 
            tickfont=dict(color="#000000")
        ),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # ------------------------------
    # 4.2.3 Chart 2: Yearly Growth Rate (Separate Line Charts)
    # ------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3>Growth Rate Palestine (%)</h3>", unsafe_allow_html=True)
        fig_grow_p = px.line(
            df_p,
            x="Year",
            y="Yearly % Change",
            markers=True,
            color_discrete_sequence=[COLOR_ACCENT],
            labels={"Yearly % Change": "Growth Rate (%)", "Year": "Year"},
        )
        fig_grow_p.update_layout(
            plot_bgcolor="rgba(255,255,255,1)",
            paper_bgcolor="rgba(255,255,255,1)",
            font=dict(color="#000000"),
            xaxis=dict(
                title=dict(text="Year", font=dict(size=14, color="#000000")),
                showgrid=True, 
                gridcolor="rgba(0,0,0,0.1)", 
                tickfont=dict(color="#000000")
            ),
            yaxis=dict(
                title=dict(text="Growth Rate (%)", font=dict(size=14, color="#000000")),
                showgrid=True, 
                gridcolor="rgba(0,0,0,0.1)", 
                tickfont=dict(color="#000000")
            ),
        )
        st.plotly_chart(fig_grow_p, use_container_width=True)

    with col2:
        st.markdown("<h3>Growth Rate Israel (%)</h3>", unsafe_allow_html=True)
        fig_grow_i = px.line(
            df_i,
            x="Year",
            y="Yearly % Change",
            markers=True,
            color_discrete_sequence=[COLOR_PRIMARY],
            labels={"Yearly % Change": "Growth Rate (%)", "Year": "Year"},
        )
        fig_grow_i.update_layout(
            plot_bgcolor="rgba(255,255,255,1)",
            paper_bgcolor="rgba(255,255,255,1)",
            font=dict(color="#000000"),
            xaxis=dict(
                title=dict(text="Year", font=dict(size=14, color="#000000")),
                showgrid=True, 
                gridcolor="rgba(0,0,0,0.1)", 
                tickfont=dict(color="#000000")
            ),
            yaxis=dict(
                title=dict(text="Growth Rate (%)", font=dict(size=14, color="#000000")),
                showgrid=True, 
                gridcolor="rgba(0,0,0,0.1)", 
                tickfont=dict(color="#000000")
            ),
        )
        st.plotly_chart(fig_grow_i, use_container_width=True)


# 4.3 "The Cost" Page
def show_cost():
    st.markdown("<h1>The <span class='highlight'>Cost</span></h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="div-box">
        <p>
        Behind every data point is a life lost. This section illustrates the human cost 
        of the Israel–Palestine conflict over the decades—civilian and military casualties 
        by year, for both sides and other affected countries. Peaks in the chart align 
        with key escalations and wars.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------
    # 4.3.1 Load death/casualties dataset
    # -----------------------------------
    url_body_complete = "https://drive.google.com/uc?id=1wwXqjPVl2Uv81Xs8XANO2AhViMnVPcbD"  # dataset with gender, date, age, citizenship
    url_body_simple   = "https://drive.google.com/uc?id=1rCjmp3-wjvqD7a0TmorOUDXv1cqnpczC"  # dataset without gender
    @st.cache_data(show_spinner=False)
    def load_death_data():
        df_full = pd.read_csv(url_body_complete, encoding="windows-1252")
        df_simple = pd.read_csv(url_body_simple)
        # Convert Date of Death to datetime
        df_full["Date of death"] = pd.to_datetime(df_full["Date of death"], errors="coerce")
        df_full = df_full.dropna(subset=["Date of death"])
        # Convert Age column to int
        df_full["Age"] = pd.to_numeric(df_full["Age"], errors="coerce").fillna(0).astype(int)
        return df_full, df_simple

    df_full, df_simple = load_death_data()

    # -----------------------------
    # 4.3.2 Death Overview (2000–2021)
    # -----------------------------
    df = df_full.copy()
    df["Year"] = df["Date of death"].dt.year
    df_filtered = df[df["Year"].between(2000, 2021)]

    death_counts = df_filtered["Citizenship"].value_counts()
    palestinian_deaths = int(death_counts.get("Palestinian", 0))
    israeli_deaths     = int(death_counts.get("Israeli", 0))
    total_deaths       = palestinian_deaths + israeli_deaths

    overview_col1, overview_col2, overview_col3 = st.columns([1,1,1])
    with overview_col1:
        st.markdown(f"<h2 style='color:{COLOR_WHITE};'>Over</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='font-size:2.5rem; color:{COLOR_ACCENT}; margin-top:-1rem;'>{total_deaths:,}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{COLOR_WHITE}; font-size:0.9rem;'>lives lost across all sides since 2000.</p>", unsafe_allow_html=True)
    with overview_col2:
        st.markdown(f"<h3 style='color:{COLOR_WHITE};'><span style='color:{COLOR_ACCENT};'>Palestinian</span> lives lost</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:{COLOR_ACCENT};'>{palestinian_deaths:,}</h2>", unsafe_allow_html=True)
    with overview_col3:
        st.markdown(f"<h3 style='color:{COLOR_WHITE};'><span style='color:{COLOR_ACCENT}'>Israeli</span> lives lost</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:{COLOR_ACCENT};'>{israeli_deaths:,}</h2>", unsafe_allow_html=True)

    st.markdown("---")

    # ---------------------------------------
    # 4.3.3 Line Chart Deaths per Year (2000–2021)
    # ---------------------------------------
    st.markdown("<h3>Deaths per Year (2000–2021)</h3>", unsafe_allow_html=True)
    death_counts_year = df_filtered.groupby(["Citizenship", "Year"]).size().reset_index(name="Deaths")

    death_israeli = death_counts_year[death_counts_year["Citizenship"] == "Israeli"]
    death_palest = death_counts_year[death_counts_year["Citizenship"] == "Palestinian"]

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=death_palest["Year"], 
        y=death_palest["Deaths"],
        mode="lines+markers",
        name="Palestinian",
        line=dict(color=COLOR_ACCENT, width=2.5),
        marker=dict(size=6)
    ))
    fig_line.add_trace(go.Scatter(
        x=death_israeli["Year"],
        y=death_israeli["Deaths"],
        mode="lines+markers",
        name="Israeli",
        line=dict(color=COLOR_PRIMARY, width=2.5),
        marker=dict(size=6)
    ))
    fig_line.update_layout(
        plot_bgcolor="rgba(255,255,255,1)",
        paper_bgcolor="rgba(255,255,255,1)",
        font=dict(color="#000000"),
        xaxis=dict(
            title=dict(text="Year", font=dict(size=14, color="#000000")),
            showgrid=True, 
            gridcolor="rgba(0,0,0,0.1)", 
            tickfont=dict(color="#000000")
        ),
        yaxis=dict(
            title=dict(text="Number of Deaths", font=dict(size=14, color="#000000")),
            showgrid=True, 
            gridcolor="rgba(0,0,0,0.1)", 
            tickfont=dict(color="#000000")
        ),
        legend=dict(title="", font=dict(color="#000000"), bgcolor="rgba(255,255,255,1)"),
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("***")

    # -----------------------------------------------------------
    # 4.3.4 Heatmap Deaths per Month × Year (Date 2000–2021)
    # -----------------------------------------------------------
    st.markdown("<h3>Monthly Cost (Heatmap per Month & Year)</h3>", unsafe_allow_html=True)

    # Create custom colormap for heatmap
    custom_cmap = LinearSegmentedColormap.from_list("custom", ['#FFFFFF', COLOR_ACCENT, COLOR_PRIMARY])

    # Pivot table for each group
    def prepare_heatmap(df_group, title_group):
        pivot = df_group.groupby([df_group["Date of death"].dt.month, df_group["Date of death"].dt.year]) \
                        .size().unstack(fill_value=0)
        # Change month number index to month names
        month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        pivot.index = [month_names[m-1] for m in pivot.index]
        return pivot

    israeli_df  = df_filtered[df_filtered["Citizenship"] == "Israeli"]
    palestine_df= df_filtered[df_filtered["Citizenship"] == "Palestinian"]

    heat_iso  = prepare_heatmap(israeli_df, "Israeli")
    heat_pale = prepare_heatmap(palestine_df, "Palestinian")

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown("<h4 style='color: " + COLOR_ACCENT + ";'>Israeli Deaths per Month & Year</h4>", unsafe_allow_html=True)
        fig_iso_heat = px.imshow(
            heat_iso,
            aspect="auto",
            color_continuous_scale=["#FFFFFF", COLOR_ACCENT, COLOR_PRIMARY],
            labels=dict(x="Year", y="Month", color="Number of Deaths"),
        )
        fig_iso_heat.update_layout(
            plot_bgcolor="rgba(255,255,255,1)",
            paper_bgcolor="rgba(255,255,255,1)",
            xaxis=dict(tickfont=dict(color="#000000")),
            yaxis=dict(tickfont=dict(color="#000000")),
            font=dict(color="#000000"),
            coloraxis_showscale=True,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_iso_heat, use_container_width=True)

    with col_h2:
        st.markdown("<h4 style='color: " + COLOR_ACCENT + ";'>Palestinian Deaths per Month & Year</h4>", unsafe_allow_html=True)
        fig_pale_heat = px.imshow(
            heat_pale,
            aspect="auto",
            color_continuous_scale=["#FFFFFF", COLOR_ACCENT, COLOR_PRIMARY],
            labels=dict(x="Year", y="Month", color="Number of Deaths"),
        )
        fig_pale_heat.update_layout(
            plot_bgcolor="rgba(255,255,255,1)",
            paper_bgcolor="rgba(255,255,255,1)",
            xaxis=dict(tickfont=dict(color="#000000")),
            yaxis=dict(tickfont=dict(color="#000000")),
            font=dict(color="#000000"),
            coloraxis_showscale=True,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_pale_heat, use_container_width=True)

    st.markdown("***")

    # ----------------------------------
    # 4.3.5 Pie Chart Deaths by Gender
    # ----------------------------------
    st.markdown("<h3>Deaths by Gender</h3>", unsafe_allow_html=True)

    # Only valid gender F/M
    df_gender = df_full[df_full["Gender"].isin(["F","M"])].copy()
    df_gender["Gender Label"] = df_gender["Gender"].map({"F":"Female","M":"Male"})

    iso_gender  = df_gender[df_gender["Citizenship"] == "Israeli"]["Gender Label"].value_counts()
    pale_gender = df_gender[df_gender["Citizenship"] == "Palestinian"]["Gender Label"].value_counts()

    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("<h4 style='color: " + COLOR_ACCENT + ";'>Israeli Deaths by Gender</h4>", unsafe_allow_html=True)
        fig_iso_gender = go.Figure(data=[go.Pie(
            labels=iso_gender.index,
            values=iso_gender.values,
            marker_colors=[COLOR_PRIMARY, COLOR_ACCENT],
            hole=0.4,
            textinfo="percent+label"
        )])
        fig_iso_gender.update_layout(
            plot_bgcolor="rgba(255,255,255,1)",
            paper_bgcolor="rgba(255,255,255,1)",
            font=dict(color="#000000"),
            legend=dict(font=dict(color="#000000")),
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=True
        )
        st.plotly_chart(fig_iso_gender, use_container_width=True)
    
    with col_g2:
        st.markdown("<h4 style='color: " + COLOR_ACCENT + ";'>Palestinian Deaths by Gender</h4>", unsafe_allow_html=True)
        fig_pale_gender = go.Figure(data=[go.Pie(
            labels=pale_gender.index,
            values=pale_gender.values,
            marker_colors=[COLOR_PRIMARY, COLOR_ACCENT],
            hole=0.4,
            textinfo="percent+label"
        )])
        fig_pale_gender.update_layout(
            plot_bgcolor="rgba(255,255,255,1)",
            paper_bgcolor="rgba(255,255,255,1)",
            font=dict(color="#000000"),
            legend=dict(font=dict(color="#000000")),
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=True
        )
        st.plotly_chart(fig_pale_gender, use_container_width=True)

    st.markdown("***")

    # -----------------------------------
    # 4.3.6 Bar Chart Deaths by Age Group
    # -----------------------------------
    st.markdown("<h3>Deaths by Age Group & Gender</h3>", unsafe_allow_html=True)

    # Prepare data: age-group + gender for each side
    valid_df = df_full[df_full["Gender"].isin(["F","M"]) & (df_full["Age"] > 0)].copy()
    age_bins = [0, 17, 30, 45, 60, 75, 120]
    age_labels = ["0-17","18-30","31-45","46-60","61-75","76+"]
    valid_df["Age Group"] = pd.cut(valid_df["Age"], bins=age_bins, labels=age_labels)
    valid_df["Gender Label"] = valid_df["Gender"].map({"F":"Female","M":"Male"})

    def plot_age_bar(df_group, title_group):
        grouped = df_group.groupby(["Age Group","Gender Label"]).size().unstack(fill_value=0)
        # Create new DataFrame for Plotly
        df_plot = grouped.reset_index().melt(id_vars="Age Group", value_vars=["Female","Male"], var_name="Gender", value_name="Count")
        fig = px.bar(
            df_plot,
            x="Age Group",
            y="Count",
            color="Gender",
            barmode="group",
            color_discrete_map={"Female": COLOR_ACCENT, "Male": COLOR_PRIMARY},
            labels={"Count":"Number of Deaths", "Age Group":"Age Group", "Gender":"Gender"}
        )
        fig.update_layout(
            plot_bgcolor="rgba(255,255,255,1)",
            paper_bgcolor="rgba(255,255,255,1)",
            font=dict(color="#000000"),
            xaxis=dict(
                title=dict(text="Age Group", font=dict(size=14, color="#000000")),
                tickfont=dict(color="#000000")
            ),
            yaxis=dict(
                title=dict(text="Number of Deaths", font=dict(size=14, color="#000000")),
                tickfont=dict(color="#000000")
            ),
            legend=dict(title="", font=dict(color="#000000")),
            margin=dict(t=40, b=20, l=20, r=20),
            showlegend=True
        )
        return fig

    iso_age  = valid_df[valid_df["Citizenship"] == "Israeli"]
    pale_age = valid_df[valid_df["Citizenship"] == "Palestinian"]

    fig_age_iso  = plot_age_bar(iso_age, "Israeli Deaths by Age Group & Gender")
    fig_age_pale = plot_age_bar(pale_age, "Palestinian Deaths by Age Group & Gender")

    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown("<h4 style='color: " + COLOR_ACCENT + ";'>Israeli Deaths by Age Group & Gender</h4>", unsafe_allow_html=True)
        st.plotly_chart(fig_age_iso, use_container_width=True)
    with col_a2:
        st.markdown("<h4 style='color: " + COLOR_ACCENT + ";'>Palestinian Deaths by Age Group & Gender</h4>", unsafe_allow_html=True)
        st.plotly_chart(fig_age_pale, use_container_width=True)


# 4.4 "Data Sources" Page
def show_data_sources():
    st.markdown("<h1>Data <span class='highlight'>Sources</span></h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="div-box">
        <p style="color: #FFFFFF; margin-bottom: 1.5rem;">
        This dashboard is built using various reliable data sources to provide accurate insights 
        into the Israel-Palestine conflict. Below are the primary datasets and sources used:
        </p>
        
        <div style="margin-bottom: 1rem;">
            <h4 style="color: #E5C056; margin-bottom: 0.5rem;">Primary Datasets</h4>
            <ul style="list-style-type: none; padding-left: 0; color: #FFFFFF;">
                <li style="margin-bottom: 0.8rem; padding-left: 1rem; border-left: 3px solid #E5C056;">
                    <strong>Israel vs Palestine Dataset</strong><br>
                    <span style="font-size: 0.9rem; opacity: 0.9;">Comprehensive conflict data including casualties and incidents</span><br>
                    <a href="https://www.kaggle.com/datasets/zsinghrahulk/israel-vs-palestine/code" 
                       target="_blank" style="color: #E5C056; text-decoration: none; font-size: 0.9rem;">
                       🔗 Kaggle Dataset
                    </a>
                </li>
                <li style="margin-bottom: 0.8rem; padding-left: 1rem; border-left: 3px solid #E5C056;">
                    <strong>Palestine Body Count (2000–2021)</strong><br>
                    <span style="font-size: 0.9rem; opacity: 0.9;">Detailed casualty data with demographics and dates</span><br>
                    <a href="https://www.kaggle.com/datasets/zusmani/palestine-body-count/data" 
                       target="_blank" style="color: #E5C056; text-decoration: none; font-size: 0.9rem;">
                       🔗 Kaggle Dataset
                    </a>
                </li>
            </ul>
        </div>
        
        <div style="margin-bottom: 1rem;">
            <h4 style="color: #E5C056; margin-bottom: 0.5rem;">Population Data</h4>
            <ul style="list-style-type: none; padding-left: 0; color: #FFFFFF;">
                <li style="margin-bottom: 0.8rem; padding-left: 1rem; border-left: 3px solid #E5C056;">
                    <strong>Israel Population Statistics</strong><br>
                    <span style="font-size: 0.9rem; opacity: 0.9;">Historical and current population data for Israel</span><br>
                    <a href="https://www.worldometers.info/world-population/israel-population/" 
                       target="_blank" style="color: #E5C056; text-decoration: none; font-size: 0.9rem;">
                       🔗 Worldometer
                    </a>
                </li>
                <li style="margin-bottom: 0.8rem; padding-left: 1rem; border-left: 3px solid #E5C056;">
                    <strong>Palestine Population Statistics</strong><br>
                    <span style="font-size: 0.9rem; opacity: 0.9;">Historical and current population data for Palestine</span><br>
                    <a href="https://www.worldometers.info/world-population/state-of-palestine-population/" 
                       target="_blank" style="color: #E5C056; text-decoration: none; font-size: 0.9rem;">
                       🔗 Worldometer
                    </a>
                </li>
            </ul>
        </div>
        
        <div style="margin-bottom: 1rem;">
            <h4 style="color: #E5C056; margin-bottom: 0.5rem;">Geographic Visualization</h4>
            <ul style="list-style-type: none; padding-left: 0; color: #FFFFFF;">
                <li style="margin-bottom: 0.8rem; padding-left: 1rem; border-left: 3px solid #E5C056;">
                    <strong>Shrinking Palestine Maps</strong><br>
                    <span style="font-size: 0.9rem; opacity: 0.9;">Historical border changes and territorial control visualization</span><br>
                    <a href="https://visualizingpalestine.org/visual/shrinking-palestine/" 
                       target="_blank" style="color: #E5C056; text-decoration: none; font-size: 0.9rem;">
                       🔗 Visualizing Palestine
                    </a>
                </li>
            </ul>
        </div>
        
        <div style="margin-top: 2rem; padding: 1rem; background-color: rgba(229, 192, 86, 0.1); border-radius: 8px; border-left: 4px solid #E5C056;">
            <p style="color: #FFFFFF; margin: 0; font-size: 0.9rem; opacity: 0.9;">
                <strong>Note:</strong> All data presented in this dashboard is sourced from publicly available datasets 
                and reputable organizations. The visualizations aim to present factual information objectively 
                to promote understanding of this complex situation.
            </p>
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------------
# 5. MAIN: Choose function to run based on menu
# ---------------------------------------------------------------
if menu == "Changing Borders":
    show_changing_borders()
elif menu == "The Population":
    show_population()
elif menu == "The Cost":
    show_cost()
elif menu == "Data Sources":
    show_data_sources()

# Add custom footer
st.markdown(
    """
    <div class="custom-footer">
        © 2025 Visdat Group 5's Dashboard. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
