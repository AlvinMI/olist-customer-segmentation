import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- CONFIG ----------
st.set_page_config(page_title="Olist Customer Segmentation", page_icon="🛍️", layout="wide")

COLORS = {
    "Champion / VIP": "#F4B400",
    "Active New Buyers": "#1E88E5",
    "At Risk / Hibernating": "#E53935",
}
ACTIONS = {
    "Champion / VIP": "Beri program loyalty & akses eksklusif; jaga retensi, jangan over-diskon.",
    "Active New Buyers": "Dorong repeat order: voucher pembelian kedua, rekomendasi produk, email onboarding.",
    "At Risk / Hibernating": "Kampanye win-back: diskon reaktivasi, reminder personal, survei alasan berhenti.",
}

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem;}
    div[data-testid="stMetric"] {
        background: rgba(128,128,128,0.08);
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 12px; padding: 14px 18px;
    }
    .hero {
        background: linear-gradient(120deg, #1E88E5 0%, #7E57C2 100%);
        padding: 22px 28px; border-radius: 14px; color: white; margin-bottom: 18px;
    }
    .hero h1 {margin: 0; font-size: 1.8rem; color: white;}
    .hero p {margin: 4px 0 0; opacity: .9;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- DATA ----------
@st.cache_data
def load_data():
    df = pd.read_csv("dataset/olist_rfm_segmented.csv")
    if "order_purchase_timestamp" in df.columns:
        df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df


df = load_data()

# ---------- SIDEBAR ----------
st.sidebar.title("🎛️ Filter Data")
segments = sorted(df["customer_segment"].unique())
segment_choice = st.sidebar.multiselect("Segmen Customer", segments, default=segments)

rec_min, rec_max = int(df["recency"].min()), int(df["recency"].max())
rec_range = st.sidebar.slider("Recency (hari)", rec_min, rec_max, (rec_min, rec_max))

mon_cap = float(df["monetary"].quantile(0.99))
mon_range = st.sidebar.slider(
    "Monetary (R$)", 0.0, round(mon_cap, 0), (0.0, round(mon_cap, 0)),
    help="Dibatasi sampai persentil 99 supaya outlier tidak merusak slider.",
)
st.sidebar.caption("Monetary di atas batas slider otomatis ikut terfilter.")

df_f = df[
    df["customer_segment"].isin(segment_choice)
    & df["recency"].between(*rec_range)
    & df["monetary"].between(*mon_range)
]

# ---------- HEADER ----------
st.markdown(
    """
    <div class="hero">
        <h1>🛍️ Olist Customer Segmentation Dashboard</h1>
        <p>Segmentasi pelanggan e-commerce dengan RFM + K-Means Clustering</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if df_f.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Longgarkan filter di sidebar.")
    st.stop()

# ---------- KPI ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 Total Customer", f"{len(df_f):,}", f"{len(df_f) / len(df):.0%} dari total")
c2.metric("💰 Total Revenue", f"R$ {df_f['monetary'].sum():,.0f}")
c3.metric("🛒 Rata-rata Monetary", f"R$ {df_f['monetary'].mean():,.2f}")
c4.metric("⏱️ Rata-rata Recency", f"{df_f['recency'].mean():.0f} hari")

st.write("")

# ---------- TABS ----------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔬 Analisis RFM", "🎯 Profil & Strategi", "📄 Data"])

with tab1:
    seg_count = df_f["customer_segment"].value_counts().reset_index()
    seg_count.columns = ["customer_segment", "jumlah"]
    seg_rev = df_f.groupby("customer_segment", as_index=False)["monetary"].sum()

    a, b = st.columns(2)
    with a:
        fig = px.pie(
            seg_count, names="customer_segment", values="jumlah", hole=0.55,
            color="customer_segment", color_discrete_map=COLORS,
            title="Proporsi Customer per Segmen",
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")
    with b:
        fig = px.bar(
            seg_rev, x="customer_segment", y="monetary", text_auto=".3s",
            color="customer_segment", color_discrete_map=COLORS,
            title="Kontribusi Revenue per Segmen (R$)",
            labels={"customer_segment": "Segmen", "monetary": "Revenue"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    if "order_purchase_timestamp" in df_f.columns:
        trend = (
            df_f.set_index("order_purchase_timestamp")
            .groupby("customer_segment")
            .resample("MS")
            .size()
            .reset_index(name="jumlah")
        )
        fig = px.area(
            trend, x="order_purchase_timestamp", y="jumlah", color="customer_segment",
            color_discrete_map=COLORS, title="Tren Pembelian Terakhir Customer per Bulan",
            labels={"order_purchase_timestamp": "Bulan", "jumlah": "Jumlah Customer"},
        )
        st.plotly_chart(fig, width="stretch")

with tab2:
    sample = df_f.sample(min(len(df_f), 5000), random_state=42)
    st.caption(f"Scatter plot memakai sampel {len(sample):,} customer supaya tetap ringan.")
    a, b = st.columns(2)
    with a:
        fig = px.scatter(
            sample, x="recency", y="monetary", color="customer_segment",
            color_discrete_map=COLORS, opacity=0.6, log_y=True,
            title="Recency vs Monetary (skala log)",
            hover_data=["frequency"],
        )
        st.plotly_chart(fig, width="stretch")
    with b:
        metric = st.selectbox("Distribusi metrik", ["recency", "monetary", "frequency"])
        fig = px.box(
            df_f, x="customer_segment", y=metric, color="customer_segment",
            color_discrete_map=COLORS, log_y=(metric == "monetary"),
            title=f"Distribusi {metric.title()} per Segmen",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    fig = px.scatter_3d(
        sample, x="recency", y="frequency", z="monetary", color="customer_segment",
        color_discrete_map=COLORS, opacity=0.6, title="Visualisasi 3D Cluster RFM",
    )
    fig.update_layout(height=560)
    st.plotly_chart(fig, width="stretch")

with tab3:
    profile = (
        df_f.groupby("customer_segment")
        .agg(
            customer=("customer_id", "count"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            total_revenue=("monetary", "sum"),
        )
        .round(2)
        .reset_index()
    )
    st.dataframe(
        profile.rename(columns={
            "customer_segment": "Segmen", "customer": "Jumlah Customer",
            "avg_recency": "Avg Recency (hari)", "avg_frequency": "Avg Frequency",
            "avg_monetary": "Avg Monetary (R$)", "total_revenue": "Total Revenue (R$)",
        }),
        width="stretch", hide_index=True,
    )

    st.subheader("💡 Rekomendasi Strategi Marketing")
    cols = st.columns(len(profile))
    for col, seg in zip(cols, profile["customer_segment"]):
        with col:
            with st.container(border=True):
                st.markdown(f"**{seg}**")
                st.write(ACTIONS.get(seg, "-"))

with tab4:
    q = st.text_input("🔍 Cari customer_id")
    show = df_f[df_f["customer_id"].str.contains(q, case=False, na=False)] if q else df_f
    st.caption(f"{len(show):,} baris")
    st.dataframe(show, width="stretch", hide_index=True, height=420)
    st.download_button(
        "⬇️ Download data terfilter (CSV)",
        show.to_csv(index=False).encode("utf-8"),
        "olist_rfm_filtered.csv", "text/csv",
    )

st.caption("Dibuat oleh Alvin Mahesa Irawadi • Dataset: Olist E-Commerce • Stack: Pandas, Scikit-Learn, Plotly, Streamlit")