from contextlib import contextmanager
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).parent
DB = ROOT / "olist.duckdb"

BASE = "#2F6DB5"
BASE_TUA = "#1E4E86"
MUDA = "#A9C6E4"
MERAH = "#C0392B"
INK = "#2F3E4E"
MUTED = "#7A8A9A"
LINE = "#C9D6E2"

NAMA = "Prayuda Affan Handoyo"
NIM = "L02424008"

PLOT_CFG = {"displayModeBar": False, "responsive": True}

st.set_page_config(
    page_title="CRM Dashboard, Olist",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
:root {
  --ink: #2F3E4E; --muted: #7A8A9A; --line: #C9D6E2;
  --blue: #2F6DB5; --red: #C0392B;
}
.stApp { background: #EDF1F6; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppDeployButton"] { display: none; }
.block-container { padding: 0.7rem 1.4rem 2.5rem; max-width: 1420px; }

.st-key-sheet {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0.8rem 0.9rem 1rem;
}

.crm-topbar {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 1rem;
  background: #DCE6F0;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 0.5rem 0.85rem;
  margin-bottom: 0.55rem;
}
.crm-topbar .left { font-size: 0.67rem; color: #4A5A6A; line-height: 1.25; }
.crm-topbar .left b { display: block; font-size: 0.78rem; color: var(--ink); font-weight: 600; }
.crm-topbar .center { font-size: 1.02rem; font-weight: 700; color: var(--ink); }
.crm-topbar .right { text-align: right; font-size: 0.67rem; color: #4A5A6A; line-height: 1.25; }
.crm-topbar .right b { display: block; font-size: 0.78rem; color: var(--ink); font-weight: 600; }

.kpi-card {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 0.55rem 0.7rem;
  text-align: center;
  height: 100%;
}
.kpi-label { font-size: 0.74rem; color: var(--muted); margin-bottom: 0.12rem; }
.kpi-value { font-size: 1.4rem; font-weight: 600; color: var(--ink); line-height: 1.15; }
.kpi-value.red { color: var(--red); }
.kpi-sub { font-size: 0.76rem; color: #4A5A6A; margin-top: 0.18rem; min-height: 1.1em; line-height: 1.3; }

.card-title { font-size: 0.82rem; font-weight: 600; color: var(--ink); margin: 0 0 0.15rem; }
.card-sub { font-size: 0.78rem; color: #5A6B7B; margin: 0 0 0.2rem; }

div[data-testid="stVerticalBlockBorderWrapper"] {
  background: #FFFFFF !important;
  border: 1px solid var(--line) !important;
  border-radius: 6px !important;
  padding: 0.5rem 0.7rem 0.25rem !important;
}

.def-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; margin-top: 0.2rem; }
.def-table th { text-align: left; font-weight: 600; background: #F4F7FB;
  border-bottom: 1px solid var(--line); padding: 0.42rem 0.55rem; font-size: 0.72rem;
  text-transform: uppercase; letter-spacing: 0.03em; color: #4A5A6A; }
.def-table td { border-bottom: 1px solid #E3EAF3; padding: 0.45rem 0.55rem;
  vertical-align: top; color: #4A5A6A; line-height: 1.45; }
.def-table tr:last-child td { border-bottom: none; }
.def-table td.metric { color: #2F6DB5; font-weight: 600; white-space: nowrap; }
.def-table code { background: #F1F5FA; border: 1px solid #E1E9F2; border-radius: 4px;
  padding: 1px 6px; font-size: 0.74rem; color: #3A4C60; font-family: ui-monospace, monospace; }
.def-foot { font-size: 0.74rem; color: #6A7A8A; margin-top: 0.55rem; line-height: 1.6; }
.def-foot a { color: #2F6DB5; text-decoration: none; }
.def-foot a:hover { text-decoration: underline; }

div[data-testid="stPills"] button { font-size: 0.75rem; }
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stDataFrame"] { border: none; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(ttl=600, show_spinner=False)
def q(sql: str, params: tuple = ()) -> pd.DataFrame:
    con = duckdb.connect(str(DB), read_only=True)
    try:
        return con.execute(sql, list(params)).df()
    finally:
        con.close()


def jarak(px: int = 12) -> None:
    st.markdown(f"<div style='height:{px}px'></div>", unsafe_allow_html=True)


def angka(v: float) -> str:
    return f"{v:,.0f}".replace(",", ".")


def rp(v: float) -> str:
    return "R$ " + angka(v)


def rupiah_ringkas(v: float) -> str:
    if v >= 1_000_000:
        return f"R$ {v / 1_000_000:.2f}".replace(".", ",") + " jt"
    if v >= 1_000:
        return f"R$ {v / 1_000:.1f}".replace(".", ",") + " rb"
    return f"R$ {v:.0f}"


def skala_gmv(nilai_maks: float) -> tuple[float, str]:
    if nilai_maks >= 1_000_000:
        return 1_000_000, "juta R$"
    if nilai_maks >= 1_000:
        return 1_000, "ribu R$"
    return 1, "R$"


def label_gmv(v: float, skala: float) -> str:
    n = v / skala
    if skala == 1:
        return f"{n:.0f}"
    return f"{n:.1f}".replace(".", ",")


def topbar() -> None:
    st.markdown(
        f"""
        <div class="crm-topbar">
          <div class="left"><b>Olist Brazilian E-commerce</b>Periode Januari 2017 - Agustus 2018</div>
          <div class="center">CRM Dashboard</div>
          <div class="right"><b>{NAMA}</b>{NIM}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi(label: str, value: str, merah: bool = False, sub: str = "") -> None:
    kelas = "kpi-value red" if merah else "kpi-value"
    isi_sub = sub if sub else "&nbsp;"
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="{kelas}">{value}</div>'
        f'<div class="kpi-sub">{isi_sub}</div></div>',
        unsafe_allow_html=True,
    )


@contextmanager
def kartu(judul: str, sub: str = "", key: str | None = None):
    opsi = {"border": True}
    if key:
        opsi["key"] = key
    with st.container(**opsi):
        sub_html = f'<div class="card-sub">{sub}</div>' if sub else ""
        st.markdown(f'<div class="card-title">{judul}</div>{sub_html}', unsafe_allow_html=True)
        yield


def gaya(fig: go.Figure, tinggi: int = 300, legenda: bool = False) -> go.Figure:
    fig.update_layout(
        height=tinggi,
        margin=dict(l=6, r=14, t=10, b=6),
        font=dict(size=12, color="#3F4F5F", family="Source Sans Pro, sans-serif"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        separators=",.",
        autosize=True,
        showlegend=legenda,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.0, x=0, font=dict(size=12)
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#D5DFE9",
        tickcolor="#D5DFE9",
        tickfont=dict(size=12, color="#3F4F5F"),
        title_font=dict(size=12, color="#3F4F5F"),
        automargin=True,
    )
    fig.update_yaxes(
        gridcolor="#E2EAF3",
        zeroline=False,
        linecolor="#D5DFE9",
        tickfont=dict(size=12, color="#3F4F5F"),
        title_font=dict(size=12, color="#3F4F5F"),
        automargin=True,
    )
    return fig


def kondisi_state(kolom: str, pilihan: list[str]) -> tuple[str, list]:
    if not pilihan:
        return "", []
    tanda = ", ".join(["?"] * len(pilihan))
    return f" AND {kolom} IN ({tanda})", list(pilihan)


# ---------------------------------------------------------------- filter Ringkasan
def simpan_filter() -> None:
    st.session_state["simpan_state"] = st.session_state.get("f_state", [])
    st.session_state["simpan_kat"] = st.session_state.get("f_kat", [])
    st.session_state["simpan_tahun"] = st.session_state.get("f_tahun", "Semua")


def reset_filter() -> None:
    st.session_state["f_state"] = []
    st.session_state["f_kat"] = []
    st.session_state["f_tahun"] = "Semua"
    st.session_state["simpan_state"] = []
    st.session_state["simpan_kat"] = []
    st.session_state["simpan_tahun"] = "Semua"


def filter_bar() -> tuple[str, list]:
    if "f_state" not in st.session_state:
        st.session_state["f_state"] = st.session_state.get("simpan_state", [])
    if "f_kat" not in st.session_state:
        st.session_state["f_kat"] = st.session_state.get("simpan_kat", [])
    if "f_tahun" not in st.session_state:
        st.session_state["f_tahun"] = st.session_state.get("simpan_tahun", "Semua")

    semua_state = q("SELECT state FROM marts.agg_state ORDER BY state")["state"].tolist()
    semua_kat = q(
        "SELECT category, count(*) n FROM marts.fct_orders WHERE category IS NOT NULL "
        "GROUP BY 1 ORDER BY 2 DESC LIMIT 20"
    )["category"].tolist()

    k1, k2, k3, k4 = st.columns([1, 1.4, 0.8, 0.5])
    pilih_state = k1.multiselect(
        "State", semua_state, placeholder="Semua", key="f_state", on_change=simpan_filter
    )
    pilih_kat = k2.multiselect(
        "Kategori", semua_kat, placeholder="Semua", key="f_kat", on_change=simpan_filter
    )
    tahun = k3.selectbox(
        "Tahun", ["Semua", "2017", "2018"], key="f_tahun", on_change=simpan_filter
    )
    k4.markdown("<div style='height:1.55rem'></div>", unsafe_allow_html=True)
    k4.button("Reset", on_click=reset_filter, use_container_width=True)

    w = " WHERE 1 = 1"
    p: list = []
    if pilih_state:
        frag, add = kondisi_state("customer_state", pilih_state)
        w += frag
        p += add
    if pilih_kat:
        frag, add = kondisi_state("category", pilih_kat)
        w += frag
        p += add
    if tahun != "Semua":
        w += " AND year(order_date) = ?"
        p.append(int(tahun))
    return w, p


# ---------------------------------------------------------------- halaman 1
def page_overview(w: str, p: list) -> None:
    kpi_row = q(
        f"""
        SELECT
            count(*)                           AS orders,
            count(DISTINCT customer_unique_id) AS customers,
            sum(payment_total)                 AS gmv,
            avg(payment_total)                 AS aov,
            avg(review_score)                  AS rating
        FROM marts.fct_orders
        {w}
        """,
        tuple(p),
    ).iloc[0]

    rr = q(
        f"""
        WITH c AS (
            SELECT customer_unique_id, count(*) AS n
            FROM marts.fct_orders
            {w}
            GROUP BY 1
        )
        SELECT 100.0 * count(*) FILTER (WHERE n >= 2) / count(*) AS repeat_rate
        FROM c
        """,
        tuple(p),
    ).iloc[0, 0]

    if kpi_row.orders == 0:
        st.warning(
            "Tidak ada order untuk kombinasi filter ini. "
            "Longgarkan state, kategori, atau tahun."
        )
        st.stop()

    rating_teks = (
        f"{kpi_row.rating:.2f}".replace(".", ",") if pd.notna(kpi_row.rating) else "-"
    )

    kol = st.columns(6)
    with kol[0]:
        kpi("Total GMV", rupiah_ringkas(kpi_row.gmv))
    with kol[1]:
        kpi("Order", angka(kpi_row.orders))
    with kol[2]:
        kpi("AOV", rp(kpi_row.aov))
    with kol[3]:
        kpi("Pelanggan", angka(kpi_row.customers))
    with kol[4]:
        kpi("Repeat rate", f"{rr:.2f}%".replace(".", ","), merah=True)
    with kol[5]:
        kpi("Rating", rating_teks)

    jarak(18)

    bulanan = q(
        f"""
        SELECT order_month, sum(payment_total) AS gmv
        FROM marts.fct_orders
        {w}
        GROUP BY 1
        ORDER BY 1
        """,
        tuple(p),
    )
    bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    bulanan["label"] = bulanan["order_month"].apply(
        lambda d: f"{bulan[d.month - 1]} {str(d.year)[2:]}"
    )
    skala, satuan = skala_gmv(bulanan["gmv"].max())
    bulanan["nilai"] = bulanan["gmv"] / skala
    tick = ",.0f" if bulanan["nilai"].max() >= 10 else ",.1f"

    with kartu("Tren Penjualan", f"GMV per bulan, dalam {satuan}"):
        fig = go.Figure(
            go.Scatter(
                x=bulanan["label"],
                y=bulanan["nilai"],
                mode="lines+markers",
                line=dict(color=BASE, width=2.8),
                marker=dict(size=6, color=BASE),
                fill="tozeroy",
                fillcolor="rgba(47, 109, 181, 0.10)",
                hovertemplate=f"%{{x}}<br>%{{y:,.2f}} {satuan}<extra></extra>",
            )
        )
        fig.update_yaxes(title_text=satuan, tickformat=tick)
        st.plotly_chart(gaya(fig, 300), config=PLOT_CFG, use_container_width=True, key="trend")

    kiri, kanan = st.columns(2)

    with kiri:
        state = q(
            f"""
            SELECT customer_state AS state, sum(payment_total) AS gmv
            FROM marts.fct_orders
            {w}
            GROUP BY 1
            ORDER BY 2 DESC
            LIMIT 10
            """,
            tuple(p),
        )
        skala_s, satuan_s = skala_gmv(state["gmv"].max())
        state["nilai"] = state["gmv"] / skala_s
        state["label"] = state["gmv"].map(lambda v: label_gmv(v, skala_s))
        with kartu("Performa Daerah", "GMV per state, 10 teratas"):
            fig = px.bar(
                state.sort_values("nilai"),
                x="nilai",
                y="state",
                orientation="h",
                text="label",
                color_discrete_sequence=[BASE],
            )
            fig.update_traces(textposition="outside", cliponaxis=False, textfont_size=12)
            fig.update_xaxes(
                title_text=satuan_s,
                tickformat=",.0f" if state["nilai"].max() >= 10 else ",.2f",
                range=[0, state["nilai"].max() * 1.25],
            )
            fig.update_yaxes(showgrid=False, title_text="")
            st.plotly_chart(gaya(fig, 320), config=PLOT_CFG, use_container_width=True, key="state_gmv")

    with kanan:
        kat = q(
            f"""
            SELECT category, sum(payment_total) AS gmv
            FROM marts.fct_orders
            {w} AND category IS NOT NULL
            GROUP BY 1
            ORDER BY 2 DESC
            LIMIT 8
            """,
            tuple(p),
        )
        skala_k, satuan_k = skala_gmv(kat["gmv"].max())
        kat["nilai"] = kat["gmv"] / skala_k
        kat["label"] = kat["gmv"].map(lambda v: label_gmv(v, skala_k))
        with kartu("Performa Kategori", "GMV per kategori, 8 teratas"):
            fig = px.bar(
                kat.sort_values("nilai"),
                x="nilai",
                y="category",
                orientation="h",
                text="label",
                color_discrete_sequence=[BASE],
            )
            fig.update_traces(textposition="outside", cliponaxis=False, textfont_size=12)
            fig.update_xaxes(
                title_text=satuan_k,
                tickformat=",.0f" if kat["nilai"].max() >= 10 else ",.2f",
                range=[0, kat["nilai"].max() * 1.3],
            )
            fig.update_yaxes(showgrid=False, title_text="")
            st.plotly_chart(gaya(fig, 320), config=PLOT_CFG, use_container_width=True, key="kategori_gmv")


# ---------------------------------------------------------------- halaman 2
def page_customers() -> None:
    r = q(
        """
        SELECT
            count(*)                                      AS customers,
            quantile_cont(monetary, 0.5)                  AS median_belanja,
            count(*) FILTER (WHERE n_orders >= 2)         AS repeater,
            count(*) FILTER (WHERE n_orders >= 2
                               AND churn_reason = 'Pernah repeat, lalu berhenti') AS berhenti
        FROM marts.dim_customer
        """
    ).iloc[0]

    kol = st.columns(4)
    with kol[0]:
        kpi("Pelanggan", angka(r.customers))
    with kol[1]:
        kpi("Median belanja", rp(r.median_belanja))
    with kol[2]:
        kpi("Pernah repeat", angka(r.repeater))
    with kol[3]:
        kpi(
            "Repeat yang berhenti",
            angka(r.berhenti),
            merah=True,
            sub=f"{100 * r.berhenti / r.repeater:.1f}% dari repeater".replace(".", ","),
        )

    jarak(18)

    seg = q("SELECT * FROM marts.agg_segment ORDER BY gmv DESC")

    with kartu("Performa Segmen", "Porsi pelanggan dibanding porsi GMV per segmen"):
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=seg["segment"],
                x=seg["pct_gmv"],
                orientation="h",
                name="porsi GMV",
                marker_color=BASE,
                hovertemplate="%{y}<br>porsi GMV %{x:.1f}%<extra></extra>",
            )
        )
        fig.add_trace(
            go.Bar(
                y=seg["segment"],
                x=seg["pct_customers"],
                orientation="h",
                name="porsi pelanggan",
                marker_color=MUDA,
                hovertemplate="%{y}<br>porsi pelanggan %{x:.1f}%<extra></extra>",
            )
        )
        fig.update_layout(barmode="group")
        fig.update_xaxes(title_text="persen", ticksuffix="%")
        fig.update_yaxes(showgrid=False, title_text="")
        st.plotly_chart(gaya(fig, 340, legenda=True), config=PLOT_CFG, use_container_width=True, key="segmen")

    with st.container(border=True):
        st.markdown('<div class="card-title">Daftar Pelanggan</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Pelanggan terbaik", "Berisiko berhenti"])

        with tab1:
            urut = st.radio(
                "Urutkan",
                ["Skor RFM", "Nilai belanja", "Frekuensi order"],
                horizontal=True,
                label_visibility="collapsed",
                key="sort_pelanggan",
            )
            kolom = {
                "Skor RFM": "rfm_total",
                "Nilai belanja": "monetary",
                "Frekuensi order": "n_orders",
            }[urut]
            keterangan = {
                "Skor RFM": "Skor RFM menggabungkan recency, frekuensi, dan nilai belanja.",
                "Nilai belanja": "Diurutkan berdasarkan total belanja. Banyak di antaranya hanya sekali membeli.",
                "Frekuensi order": "Diurutkan berdasarkan jumlah order. Ini pelanggan yang benar-benar kembali.",
            }[urut]
            atas = q(
                f"""
                SELECT
                    customer_unique_id AS pelanggan,
                    state              AS state,
                    n_orders           AS order,
                    rfm_total          AS rfm,
                    round(monetary, 2) AS total_belanja,
                    recency_days       AS hari_sejak_order,
                    segment            AS segmen
                FROM marts.dim_customer
                ORDER BY {kolom} DESC, monetary DESC
                LIMIT 20
                """
            )
            st.dataframe(
                atas,
                width="stretch",
                hide_index=True,
                column_config={
                    "total_belanja": st.column_config.NumberColumn(
                        "total belanja", format="%.2f"
                    ),
                    "hari_sejak_order": st.column_config.NumberColumn("hari sejak order"),
                    "pelanggan": st.column_config.TextColumn("pelanggan", width="medium"),
                    "rfm": st.column_config.NumberColumn("RFM", format="%d"),
                },
            )
            st.caption(keterangan)
            st.download_button(
                "Unduh 20 teratas (CSV)",
                atas.to_csv(index=False).encode("utf-8"),
                file_name="pelanggan_terbaik.csv",
                mime="text/csv",
            )

        with tab2:
            alasan = q(
                "SELECT DISTINCT churn_reason FROM marts.dim_customer "
                "WHERE at_risk_flag = 1 ORDER BY 1"
            )["churn_reason"].tolist()
            f1, f2 = st.columns([1.4, 1])
            bawaan = [a for a in alasan if a == "Pernah repeat, lalu berhenti"] or alasan
            pilih = f1.multiselect("Alasan berhenti", alasan, default=bawaan, key="f_alasan")
            minimum = f2.slider("Minimal total belanja (R$)", 0, 5000, 500, 100)

            if pilih:
                tanda = ", ".join(["?"] * len(pilih))
                resiko = q(
                    f"""
                    SELECT
                        customer_unique_id AS pelanggan,
                        segment            AS segmen,
                        n_orders           AS order,
                        round(monetary, 2) AS total_belanja,
                        recency_days       AS hari_sejak_order,
                        churn_reason       AS alasan
                    FROM marts.dim_customer
                    WHERE at_risk_flag = 1
                      AND churn_reason IN ({tanda})
                      AND monetary >= ?
                    ORDER BY monetary DESC
                    """,
                    tuple(pilih) + (minimum,),
                )
                dasar = q(
                    f"""
                    SELECT count(*) AS n
                    FROM marts.dim_customer
                    WHERE at_risk_flag = 1 AND churn_reason IN ({tanda})
                    """,
                    tuple(pilih),
                ).iloc[0, 0]
                if minimum > 0:
                    st.caption(
                        f"{angka(len(resiko))} dari {angka(dasar)} pelanggan berisiko, "
                        f"karena minimum belanja R$ {angka(minimum)}."
                    )
                else:
                    st.caption(
                        f"{angka(len(resiko))} dari {angka(dasar)} pelanggan berisiko."
                    )
                st.dataframe(
                    resiko.head(300),
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "total_belanja": st.column_config.NumberColumn(
                            "total belanja", format="%.2f"
                        )
                    },
                )
                st.download_button(
                    "Unduh daftar (CSV)",
                    resiko.to_csv(index=False).encode("utf-8"),
                    file_name="pelanggan_berisiko.csv",
                    mime="text/csv",
                )




# ---------------------------------------------------------------- halaman 3
def page_strategy() -> None:
    loyal = q("SELECT * FROM marts.agg_loyalty ORDER BY urutan, repeat_rate_pct DESC")
    kirim = loyal[loyal.factor == "pengiriman pertama"].set_index("bucket")
    tepat = float(kirim.loc["tepat waktu", "repeat_rate_pct"])
    telat = float(kirim.loc["terlambat", "repeat_rate_pct"])

    kat = loyal[loyal.factor == "kategori pertama"].copy()
    kat = kat[kat["customers"] >= 300].sort_values("repeat_rate_pct", ascending=False).head(12)
    kat["label"] = kat["repeat_rate_pct"].map(lambda v: f"{v:.1f}%".replace(".", ","))

    with kartu(
        "Ranking Kategori",
        "Repeat rate berdasarkan kategori pembelian pertama, minimal 300 pelanggan",
    ):
        plot_kat = kat.sort_values("repeat_rate_pct")
        warna_bar = [
            BASE_TUA if b == kat["bucket"].iloc[0] else BASE for b in plot_kat["bucket"]
        ]
        fig = px.bar(
            plot_kat,
            x="repeat_rate_pct",
            y="bucket",
            orientation="h",
            text="label",
            hover_data={"customers": ":,.0f"},
        )
        fig.update_traces(
            marker_color=warna_bar,
            textposition="outside",
            cliponaxis=False,
            textfont_size=12,
        )
        fig.update_xaxes(
            title_text="repeat rate (%)", ticksuffix="%", range=[0, kat["repeat_rate_pct"].max() * 1.25]
        )
        fig.update_yaxes(showgrid=False, title_text="")
        st.plotly_chart(gaya(fig, 360), config=PLOT_CFG, use_container_width=True, key="ranking_kat")

    kiri, kanan = st.columns(2)

    with kiri:
        rating = loyal[loyal.factor == "rating pertama"].copy()
        urut = ["< 3.0", "3.0 - 4.0", "4.0 - 4.5", "4.5 - 5"]
        rating["bucket"] = pd.Categorical(rating["bucket"], urut, ordered=True)
        rating = rating.sort_values("bucket")
        rating["label"] = rating["repeat_rate_pct"].map(lambda v: f"{v:.1f}%".replace(".", ","))
        with kartu("Repeat rate berdasarkan rating pertama", "Rating pada pembelian pertama"):
            fig = px.bar(
                rating,
                x="bucket",
                y="repeat_rate_pct",
                text="label",
                color_discrete_sequence=[BASE],
            )
            fig.update_traces(textposition="outside", textfont_size=12)
            fig.update_xaxes(title_text="")
            fig.update_yaxes(
                title_text="repeat rate (%)",
                ticksuffix="%",
                range=[0, rating["repeat_rate_pct"].max() * 1.3],
            )
            st.plotly_chart(gaya(fig, 280), config=PLOT_CFG, use_container_width=True, key="rating")

    with kanan:
        kirim_df = kirim.reset_index()
        warna = [BASE if b == "tepat waktu" else MERAH for b in kirim_df["bucket"]]
        kirim_df["label"] = kirim_df["repeat_rate_pct"].map(
            lambda v: f"{v:.2f}%".replace(".", ",")
        )
        with kartu("Repeat rate berdasarkan ketepatan kirim", "Status kirim pada pembelian pertama"):
            fig = px.bar(
                kirim_df,
                x="bucket",
                y="repeat_rate_pct",
                text="label",
            )
            fig.update_traces(marker_color=warna, textposition="outside", textfont_size=12)
            fig.update_xaxes(title_text="")
            fig.update_yaxes(
                title_text="repeat rate (%)",
                ticksuffix="%",
                range=[0, kirim_df["repeat_rate_pct"].max() * 1.3],
            )
            st.plotly_chart(gaya(fig, 280), config=PLOT_CFG, use_container_width=True, key="kirim")
            selisih = f"{tepat - telat:.2f}".replace(".", ",")
            tepat_txt = f"{tepat:.2f}".replace(".", ",")
            telat_txt = f"{telat:.2f}".replace(".", ",")
            st.caption(
                f"Selisih {selisih} pp, dari {tepat_txt}% dan {telat_txt}%. "
                "Hanya pembelian pertama yang sudah tiba yang dihitung."
            )

    state = q("SELECT * FROM marts.agg_state")
    state["terlambat_pct"] = state["late_rate"] * 100
    state["warna"] = ["Darurat" if v > 15 else "Normal" for v in state["terlambat_pct"]]
    state["ukuran"] = state["customers"] ** 0.5
    with kartu(
        "Prioritas Wilayah",
        "Ukuran lingkaran menggambarkan jumlah pelanggan, state kecil diperbesar agar tetap terlihat. "
        "Garis putus-putus menandai batas 15%.",
    ):
        fig = px.scatter(
            state,
            x="terlambat_pct",
            y="gmv_per_customer",
            size="ukuran",
            color="warna",
            color_discrete_map={"Normal": BASE, "Darurat": MERAH},
            labels={"warna": ""},
            hover_name="state",
            hover_data={"customers": ":,.0f", "ukuran": False},
            size_max=38,
        )
        fig.update_layout(legend_title_text="")
        fig.update_xaxes(title_text="pengiriman terlambat (%)", ticksuffix="%")
        fig.update_yaxes(title_text="GMV per pelanggan (R$)", tickformat=",.0f")
        fig.add_vline(
            x=15,
            line_dash="dash",
            line_color=MERAH,
            line_width=1.5,
            annotation_text="batas 15%",
            annotation_position="top",
            annotation_font_size=11,
            annotation_font_color=MERAH,
        )
        st.plotly_chart(
            gaya(fig, 360, legenda=True),
            config=PLOT_CFG,
            use_container_width=True,
            key="wilayah",
        )
        st.caption(
            "Titik di kanan garis berwarna merah dan perlu perhatian. Wilayah kanan atas "
            "bernilai tinggi tetapi layanannya bermasalah."
        )

    seg_aksi = q("SELECT * FROM marts.agg_segment").set_index("segment")

    def baris(nama: str, tujuan: str, taktik: str, ukuran: str) -> dict:
        r = seg_aksi.loc[nama]
        return {
            "Segmen": nama,
            "Pelanggan": angka(r.customers),
            "Porsi GMV": f"{r.pct_gmv:.1f}".replace(".", ",") + "%",
            "Tujuan": tujuan,
            "Taktik": taktik,
            "Ukuran": ukuran,
        }

    aksi = pd.DataFrame(
        [
            baris(
                "Dormant High Value",
                "Reaktivasi dalam 90 hari",
                "Email personal, tawarkan kategori terakhir, tanpa diskon besar",
                "Pelanggan kembali",
            ),
            baris(
                "Dormant",
                "Aktivasi massal murah",
                "Satu kampanye email berbiaya rendah",
                "Biaya per order",
            ),
            baris(
                "New High Value",
                "Konversi order kedua",
                "Voucher order kedua, batas 30 hari",
                "Konversi order kedua",
            ),
            baris(
                "At Risk",
                "Menangkan kembali",
                "Win-back dengan kategori yang pernah dibeli",
                "Reaktivasi",
            ),
            baris(
                "Loyal",
                "Naikkan nilai",
                "Bundling kategori favorit",
                "AOV",
            ),
            baris(
                "Champions",
                "Pertahankan",
                "Akses awal produk baru, program referral",
                "Repeat rate",
            ),
        ]
    )

    with kartu("Rencana Aksi", "Taktik per segmen, diurutkan menurut porsi GMV"):
        st.dataframe(
            aksi,
            width="stretch",
            hide_index=True,
            column_config={
                "Segmen": st.column_config.TextColumn("Segmen", width="medium"),
                "Pelanggan": st.column_config.TextColumn("Pelanggan", width="small"),
                "Porsi GMV": st.column_config.TextColumn("Porsi GMV", width="small"),
                "Tujuan": st.column_config.TextColumn("Tujuan", width="medium"),
                "Taktik": st.column_config.TextColumn("Taktik", width="large"),
                "Ukuran": st.column_config.TextColumn("Ukuran", width="medium"),
            },
        )



with st.container(key="sheet"):
    topbar()
    halaman = st.pills(
        "Navigasi",
        ["Ringkasan", "Pelanggan", "Strategi"],
        default="Ringkasan",
        label_visibility="collapsed",
        key="nav",
    )

    if halaman == "Pelanggan":
        page_customers()
    elif halaman == "Strategi":
        page_strategy()
    else:
        w, p = filter_bar()
        page_overview(w, p)

    jarak(12)
    with st.expander("Definisi metrik dan sumber data"):
        st.markdown(
            """
            <table class="def-table">
              <thead>
                <tr><th>Metrik</th><th>Definisi</th><th>Rumus</th></tr>
              </thead>
              <tbody>
                <tr>
                  <td class="metric">GMV (Gross Merchandise Value)</td>
                  <td>Total pembayaran pada order yang tidak dibatalkan atau gagal.</td>
                  <td><code>sum(payment_total)</code></td>
                </tr>
                <tr>
                  <td class="metric">Repeat rate</td>
                  <td>Pelanggan dengan minimal dua order dibagi total pelanggan.</td>
                  <td><code>count(n &gt;= 2) / count(*)</code></td>
                </tr>
                <tr>
                  <td class="metric">RFM (Recency, Frequency, Monetary)</td>
                  <td>Recency berupa pita hari, frequency berupa jumlah order, monetary berupa quintile belanja.</td>
                  <td><code>ntile(5)</code></td>
                </tr>
                <tr>
                  <td class="metric">Berhenti</td>
                  <td>Tidak ada order lebih dari 90 hari, atau melewati dua kali jarak belanja biasanya.</td>
                  <td><code>greatest(2 x median gap, 90)</code></td>
                </tr>
                <tr>
                  <td class="metric">Segmen</td>
                  <td>Champions, Loyal, Need Attention, At Risk, New, dan Dormant, dibentuk dari frekuensi lalu recency.</td>
                  <td><code>n_orders x recency</code></td>
                </tr>
              </tbody>
            </table>
            <div class="def-foot">Sumber data,
            <a href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
               target="_blank" rel="noopener">Olist Brazilian E-commerce, Kaggle</a>.</div>
            """,
            unsafe_allow_html=True,
        )
