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
# 1. KONFIGURASI HALAMAN & BACKGROUND
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Lines Drawn, Lives Lost",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Fungsi untuk meng‐embed background image (bg.png) via base64
def set_background(png_path: str):
    """
    Memuat gambar dari assets/bg.png dan meng‐embed ke CSS background full‐screen.
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
# 2. CUSTOM FONTS & WARNA GLOBAL
# ---------------------------------------------------------------------------

FONT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');

/* Terapan untuk seluruh aplikasi */
body, * {
    font-family: 'Poppins', sans-serif !important;
    color: #FFFFFF;
}

/* Judul utama & sub‐judul menggunakan Bernard MT Condensed */
h1 {
    font-family: 'Bernard MT Condensed', serif !important;
    color: #E5C056;
    margin-bottom: 0.25rem;
}
h2 {
    font-family: 'Bernard MT Condensed', serif !important;
    color: #E5C056;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}

/* Untuk subtitle/h3 kita pakai Poppins Bold */
h3 {
    font-family: 'Poppins', sans-serif !important;
    color: #E5C056;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

/* Warna box, card, dll */
.div-box {
    background-color: rgba(43, 45, 66, 0.8);
    padding: 1rem;
    border-radius: 8px;
}

/* Hide default Streamlit menu & footer jika di‐inginkan */
# MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(FONT_CSS, unsafe_allow_html=True)

# Global color palette
COLOR_PRIMARY = "#2B2D42"   # navy gelap
COLOR_ACCENT  = "#E5C056"   # kuning keemasan
COLOR_WHITE   = "#FFFFFF"

# ---------------------------------------------------------------------------
# 3. NAVIGASI HORIZONTAL (menu top bar)
# ---------------------------------------------------------------------------
menu = st.radio(
    "", 
    ("Changing Borders", "The Population", "The Cost", "Data Sources"),
    horizontal=True,
    index=0,
    label_visibility="collapsed"
)

# ---------------------------------------------------------------
# 4. FUNGSIONALITAS MENGISI SETIAP HALAMAN (PAGE) BERDASARKAN MENU
# ---------------------------------------------------------------

# 4.1 Halaman "Changing Borders" (todo: sementara placeholder)
def show_changing_borders():
    st.markdown("<h1>Changing Borders</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="div-box">
        <p>
        This interactive map will trace shifting borders between Israel and Palestine over time, 
        visualizing territorial changes from 1947 to present. 
        Each year reflects major geopolitical events that reshaped land and lives.
        </p>
        <p style="font-size:0.9rem; color:#FFFFFF;">
        *Klik tombol di bawah nanti untuk memilih tahun dan melihat peta interaktif.*
        </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # Placeholder untuk dropdown tahun & peta
    tahun = st.slider("Pilih Tahun:", 1947, 2021, 1967, step=1)
    st.info(f"🗺️ [Placeholder] Peta untuk tahun {tahun} akan di‐render di sini.")
    st.write("Map + grafik interaktif di bagian ini menyusul (geojson + folium/plotly).")


# 4.2 Halaman "The Population"
def show_population():
    st.markdown("<h1>The Population</h1>", unsafe_allow_html=True)
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
    # 4.2.1 Load dataset Populasi
    # ------------------------------
    url_palestine = "https://drive.google.com/uc?id=1Kr3mWDhTErT9OlibX_aBaHVtNvRTlZhx"
    url_israel    = "https://drive.google.com/uc?id=1pfdUGsK4uKs-c7KUQ_zsnKVOkWadu0cw"

    @st.cache_data(show_spinner=False)
    def load_population_data():
        df_p = pd.read_csv(url_palestine)
        df_i = pd.read_csv(url_israel)
        # Bersihkan kolom string (hilangkan ',' dan '%')
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

    # Gabungkan kedua df untuk chart trend
    population_combined = pd.concat([
        df_p[["Year", "Population", "Country"]],
        df_i[["Year", "Population", "Country"]]
    ], ignore_index=True)

    # ------------------------------
    # 4.2.2 Chart 1: Population Trend (Line Chart)
    # ------------------------------
    st.markdown("<h3>Overview Per Tahun</h3>", unsafe_allow_html=True)

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
        plot_bgcolor="rgba(0,0,0,0)",    # transparan
        paper_bgcolor="rgba(0,0,0,0)",   # transparan
        font=dict(color=COLOR_WHITE),
        legend=dict(
            title="", 
            font=dict(color=COLOR_WHITE),
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color=COLOR_WHITE)),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color=COLOR_WHITE)),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # ------------------------------
    # 4.2.3 Chart 2: Yearly Growth Rate (Line Chart terpisah)
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
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLOR_WHITE),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color=COLOR_WHITE)),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color=COLOR_WHITE)),
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
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLOR_WHITE),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color=COLOR_WHITE)),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color=COLOR_WHITE)),
        )
        st.plotly_chart(fig_grow_i, use_container_width=True)


# 4.3 Halaman "The Cost"
def show_cost():
    st.markdown("<h1>The Cost</h1>", unsafe_allow_html=True)
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
    # 4.3.1 Load dataset death/casualties
    # -----------------------------------
    url_body_complete = "https://drive.google.com/uc?id=1wwXqjPVl2Uv81Xs8XANO2AhViMnVPcbD"  # dataset with gender, date, age, citizenship
    url_body_simple   = "https://drive.google.com/uc?id=1rCjmp3-wjvqD7a0TmorOUDXv1cqnpczC"  # dataset tanpa gender
    @st.cache_data(show_spinner=False)
    def load_death_data():
        df_full = pd.read_csv(url_body_complete, encoding="windows-1252")
        df_simple = pd.read_csv(url_body_simple)
        # Convert Date of Death ke datetime
        df_full["Date of death"] = pd.to_datetime(df_full["Date of death"], errors="coerce")
        df_full = df_full.dropna(subset=["Date of death"])
        # Kolom Age di‐convert int
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
        st.markdown(f"<h1 style='font-size:2.5rem; color:{COLOR_ACCENT};'>{total_deaths:,}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{COLOR_WHITE}; font-size:0.9rem;'>lives lost across all sides since 1948.</p>", unsafe_allow_html=True)
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
    st.markdown("<h3>Death per Year (2000–2021)</h3>", unsafe_allow_html=True)
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
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLOR_WHITE),
        xaxis=dict(title="Year", showgrid=True, gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color=COLOR_WHITE)),
        yaxis=dict(title="Number of Deaths", showgrid=True, gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color=COLOR_WHITE)),
        legend=dict(title="", font=dict(color=COLOR_WHITE), bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("***")

    # -----------------------------------------------------------
    # 4.3.4 Heatmap Death per Bulan × Tahun (Tanggal 2000–2021)
    # -----------------------------------------------------------
    st.markdown("<h3>Monthly Cost (Heatmap per Bulan×Tahun)</h3>", unsafe_allow_html=True)

    # Buat custom colormap untuk heatmap
    custom_cmap = LinearSegmentedColormap.from_list("custom", ['#FFFFFF', COLOR_ACCENT, COLOR_PRIMARY])

    # Pivot table untuk masing-masing group
    def prepare_heatmap(df_group, title_group):
        pivot = df_group.groupby([df_group["Date of death"].dt.month, df_group["Date of death"].dt.year]) \
                        .size().unstack(fill_value=0)
        # Ubah index angka bulan jadi nama bulan
        month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        pivot.index = [month_names[m-1] for m in pivot.index]
        return pivot

    israeli_df  = df_filtered[df_filtered["Citizenship"] == "Israeli"]
    palestine_df= df_filtered[df_filtered["Citizenship"] == "Palestinian"]

    heat_iso  = prepare_heatmap(israeli_df, "Israeli")
    heat_pale = prepare_heatmap(palestine_df, "Palestinian")

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown("<h4 style='color: " + COLOR_ACCENT + ";'>Israeli Deaths per Month×Year</h4>", unsafe_allow_html=True)
        fig_iso_heat = px.imshow(
            heat_iso,
            aspect="auto",
            color_continuous_scale=["#FFFFFF", COLOR_ACCENT, COLOR_PRIMARY],
            labels=dict(x="Year", y="Month", color="Number of Deaths"),
        )
        fig_iso_heat.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color=COLOR_WHITE)),
            yaxis=dict(tickfont=dict(color=COLOR_WHITE)),
            font=dict(color=COLOR_WHITE),
            coloraxis_showscale=True,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_iso_heat, use_container_width=True)

    with col_h2:
        st.markdown("<h4 style='color: " + COLOR_ACCENT + ";'>Palestinian Deaths per Month×Year</h4>", unsafe_allow_html=True)
        fig_pale_heat = px.imshow(
            heat_pale,
            aspect="auto",
            color_continuous_scale=["#FFFFFF", COLOR_ACCENT, COLOR_PRIMARY],
            labels=dict(x="Year", y="Month", color="Number of Deaths"),
        )
        fig_pale_heat.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color=COLOR_WHITE)),
            yaxis=dict(tickfont=dict(color=COLOR_WHITE)),
            font=dict(color=COLOR_WHITE),
            coloraxis_showscale=True,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_pale_heat, use_container_width=True)

    st.markdown("***")

    # ----------------------------------
    # 4.3.5 Pie Chart Death by Gender
    # ----------------------------------
    st.markdown("<h3>Deaths by Gender</h3>", unsafe_allow_html=True)

    # Hanya valid gender F/M
    df_gender = df_full[df_full["Gender"].isin(["F","M"])].copy()
    df_gender["Gender Label"] = df_gender["Gender"].map({"F":"Female","M":"Male"})

    iso_gender  = df_gender[df_gender["Citizenship"] == "Israeli"]["Gender Label"].value_counts()
    pale_gender = df_gender[df_gender["Citizenship"] == "Palestinian"]["Gender Label"].value_counts()

    fig_gender = make_subplots(rows=1, cols=2,
                               specs=[[{"type":"domain"}, {"type":"domain"}]],
                               subplot_titles=("Israeli Deaths by Gender", "Palestinian Deaths by Gender"))
    fig_gender.add_trace(go.Pie(
        labels=iso_gender.index,
        values=iso_gender.values,
        name="Israeli",
        marker_colors=[COLOR_PRIMARY, COLOR_ACCENT],
        hole=0.4
    ), row=1, col=1)
    fig_gender.add_trace(go.Pie(
        labels=pale_gender.index,
        values=pale_gender.values,
        name="Palestinian",
        marker_colors=[COLOR_PRIMARY, COLOR_ACCENT],
        hole=0.4
    ), row=1, col=2)

    fig_gender.update_traces(textinfo="percent+label")
    fig_gender.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLOR_WHITE),
        legend=dict(font=dict(color=COLOR_WHITE)),
        margin=dict(t=50, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_gender, use_container_width=True)

    st.markdown("***")

    # -----------------------------------
    # 4.3.6 Bar Chart Death by Age Group
    # -----------------------------------
    st.markdown("<h3>Deaths by Age Group & Gender</h3>", unsafe_allow_html=True)

    # Siapkan data: age‐group + gender untuk masing‐masing side
    valid_df = df_full[df_full["Gender"].isin(["F","M"]) & (df_full["Age"] > 0)].copy()
    age_bins = [0, 17, 30, 45, 60, 75, 120]
    age_labels = ["0-17","18-30","31-45","46-60","61-75","76+"]
    valid_df["Age Group"] = pd.cut(valid_df["Age"], bins=age_bins, labels=age_labels)
    valid_df["Gender Label"] = valid_df["Gender"].map({"F":"Female","M":"Male"})

    def plot_age_bar(df_group, title_group):
        grouped = df_group.groupby(["Age Group","Gender Label"]).size().unstack(fill_value=0)
        # Buat DataFrame baru untuk Plotly
        df_plot = grouped.reset_index().melt(id_vars="Age Group", value_vars=["Female","Male"], var_name="Gender", value_name="Count")
        fig = px.bar(
            df_plot,
            x="Age Group",
            y="Count",
            color="Gender",
            barmode="group",
            color_discrete_map={"Female": COLOR_ACCENT, "Male": COLOR_PRIMARY},
            labels={"Count":"Number of Deaths", "Age Group":"Age Group", "Gender":"Gender"},
            title=title_group
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLOR_WHITE),
            xaxis=dict(tickfont=dict(color=COLOR_WHITE)),
            yaxis=dict(tickfont=dict(color=COLOR_WHITE)),
            legend=dict(title="", font=dict(color=COLOR_WHITE)),
            margin=dict(t=40, b=20, l=20, r=20)
        )
        return fig

    iso_age  = valid_df[valid_df["Citizenship"] == "Israeli"]
    pale_age = valid_df[valid_df["Citizenship"] == "Palestinian"]

    fig_age_iso  = plot_age_bar(iso_age, "Israeli Deaths by Age Group & Gender")
    fig_age_pale = plot_age_bar(pale_age, "Palestinian Deaths by Age Group & Gender")

    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.plotly_chart(fig_age_iso, use_container_width=True)
    with col_a2:
        st.plotly_chart(fig_age_pale, use_container_width=True)


# 4.4 Halaman "Data Sources"
def show_data_sources():
    st.markdown("<h1>Data Sources</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="div-box">
        <ul style="list-style-type: disc; padding-left: 1.5rem; color: #FFFFFF;">
          <li>Israel vs Palestine Dataset on Kaggle</li>
          <li>Palestine Body Count 2000–2021 Dataset on Kaggle</li>
          <li>Israel Population on Worldometer</li>
          <li>Palestine Population on Worldometer</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------------
# 5. MAIN: Pilih fungsi yang akan dijalankan berdasarkan menu
# ---------------------------------------------------------------
if menu == "Changing Borders":
    show_changing_borders()
elif menu == "The Population":
    show_population()
elif menu == "The Cost":
    show_cost()
elif menu == "Data Sources":
    show_data_sources()
