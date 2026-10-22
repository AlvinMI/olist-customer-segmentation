# 📊 Olist E-Commerce Customer Segmentation & Analytics Dashboard

An end-to-end Data Science & Analytics project built on the **Olist E-Commerce Public Dataset** (100k+ Brazilian transactions). This project implements Data Wrangling, Exploratory Data Analysis (EDA), **RFM Feature Engineering**, and Unsupervised Machine Learning (**K-Means Clustering with Elbow Method Evaluation**) to segment customers and serve interactive business insights via a **Streamlit Dashboard**.

---

## 📌 Business Problem & Objectives
E-commerce marketing teams often struggle to personalize promotions due to raw, unsegmented customer data. Sending mass promotions leads to high ad spend and low conversion rates.

**Key Objectives:**
1. Clean and aggregate transactional history at the unique `customer_id` level.
2. Extract behavioral metrics using the **RFM Model**:
   - **Recency ($R$):** Days since last purchase (relative to snapshot date).
   - **Frequency ($F$):** Total order count per customer.
   - **Monetary ($M$):** Total monetary value spent.
3. Apply **StandardScaler** and **K-Means Clustering** evaluated with the **Elbow Method** ($K=3$).
4. Deploy an interactive **Streamlit Dashboard** for real-time CRM filtering and KPI tracking.

---

## 🏗️ Project Architecture & Pipeline

```text
[Raw Datasets (Orders & Items)]
              │
              ▼
    [Data Cleansing & Merging] ──► Handle NULLs (order_approved_at) & Datetime Parsing
              │
              ▼
   [RFM Feature Engineering]   ──► Extract Recency, Frequency, Monetary
              │
              ▼
   [Scaling & K-Means Model]   ──► StandardScaler + Elbow Method (Optimal K=3)
              │
              ▼
  [Olist Segmented CSV Export] ──► dataset/olist_rfm_segmented.csv
              │
              ▼
  [Streamlit Web Application]  ──► KPI Cards, Multi-select Filters & Seaborn Bar Charts