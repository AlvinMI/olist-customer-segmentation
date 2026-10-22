import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title = "Olist_Dashboard", layout = "wide")
st.title("Olist Customer Segmentation Dashboard")
st.write("Dashboard Analisis Segmentasi Pelanggan Menggunakan Model Machine Learning RFM K-Means.")
df_rfm = pd.read_csv("dataset/olist_rfm_segmented.csv")
st.sidebar.header("Filter Data")
segment_choice = st.sidebar.multiselect(
    "Pilih Segmen Customer : ",
    options = df_rfm ["customer_segment"].unique(),
    default = df_rfm ["customer_segment"].unique()
)

df_filtered = df_rfm[df_rfm["customer_segment"].isin(segment_choice)]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Customer Filtered", f"{len(df_filtered):,} customer")

with col2:
    st.metric("Rata-rata Belanja (Monetary)", f"R$ {df_filtered['monetary'].mean():.2f}")

with col3:
    st.metric("Rata-rata Recency", f"{df_filtered['recency'].mean():.1f} hari")
    
st.subheader("📊 Distribusi Segmen Pelanggan")
fig, ax = plt.subplots(figsize=(8, 4))
sns.countplot (data=df_filtered, x = "customer_segment", palette = "viridis", ax=ax)
plt.title("Jumlah Customer Per Segmen")
plt.xlabel("Segmen")
plt.ylabel("Jumlah")

st.pyplot(fig)
st.subheader("📄 Detail Data Pelanggan")
st.dataframe(df_filtered.head(10))