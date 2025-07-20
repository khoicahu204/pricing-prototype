import pandas as pd
import streamlit as st
from PIL import Image
import os

# ======================
# 🔧 TÙY CHỈNH CSS GIAO DIỆN
# ======================
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100% !important;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ======================
# 📦 LOAD DATA
# ======================
df = pd.read_csv("cleaned_data_sorted.csv")

# Gán đường dẫn ảnh
df['image_path'] = df['record_id'].apply(lambda x: f"images/{int(x)}.jpg")
df['image_path'] = df['image_path'].apply(lambda path: path if os.path.exists(path) else "images/default.jpg")

# ======================
# 🔍 SIDEBAR - BỘ LỌC
# ======================
st.sidebar.title("🔍 Bộ lọc")
selected_brand = st.sidebar.selectbox("📌 Hãng xe", sorted(df['brand'].dropna().unique()))

models = sorted(df[df['brand'] == selected_brand]['model'].dropna().unique())
selected_model = st.sidebar.selectbox("🚗 Dòng xe", models)

years = sorted(df[df['model'] == selected_model]['manufacture_date'].dropna().unique())
years.insert(0, "Tất cả")
selected_year = st.sidebar.selectbox("📅 Năm sản xuất", years)

min_price = 50_000_000  # Giả sử giá trị tối thiểu là 50 triệu
max_price = 2_000_000_000  # Giả sử giá trị tối đa là 5 tỷ


selected_price_range = st.sidebar.slider(
    "💰 Khoảng giá (VND)", 
    min_value=min_price, 
    max_value=max_price,
    value=(min_price, max_price),
    step=10_000_000,
    
)




# ======================
# 🔎 LỌC DỮ LIỆU
# ======================
df_filtered = df[
    (df['brand'] == selected_brand) &
    (df['model'] == selected_model) &
    
    (df['price'] >= selected_price_range[0]) &
    (df['price'] <= selected_price_range[1])

].sort_values(by='list_time', ascending=True).tail(15).iloc[::-1]

if selected_year != "Tất cả":
    df_filtered = df_filtered[df_filtered['manufacture_date'] == selected_year]

# ======================
# 🚗 HIỂN THỊ KẾT QUẢ DẠNG CARD
# ======================
st.markdown("## 🚗 Xe đã chọn")

cols = st.columns(3)

for i, (_, row) in enumerate(df_filtered.iterrows()):
    with cols[i % 3]:
        # Ảnh resize cố định
        image = Image.open(row['image_path']).resize((300, 200))
        st.image(image, use_container_width=True)

        # Thông tin
        st.markdown(f"**{row['brand']} {row['model']} {int(row['manufacture_date'])}**", unsafe_allow_html=True)
        st.markdown(f"📍 TP.HCM")  # có thể thay bằng `row['location']` nếu có
        st.markdown(f"🔧 {int(row['mileage_v2']):,} km")
        st.markdown(f"💰 **{int(row['price']):,} VND**", unsafe_allow_html=True)
