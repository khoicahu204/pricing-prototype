import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
import os

def image_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

def render_car_cards(df_filtered):
    st.markdown("### 🧾 Danh sách xe (cuộn ngang)")
    st.markdown(
        """
        <div style="display: flex; overflow-x: auto; padding: 1rem 0;">
        """,
        unsafe_allow_html=True
    )

    for _, row in df_filtered.iterrows():
        b64_img = image_to_base64(row['image_path'])
        st.markdown(
            f"""
            <div style="min-width: 320px; margin-right: 1rem; border: 1px solid #ccc; border-radius: 8px; padding: 10px;">
                <img src="data:image/jpeg;base64,{b64_img}" style="width:100%; object-fit: cover; border-radius: 6px;" />
                <p><strong>{row['brand']} {row['model']} {int(row['manufacture_date'])}</strong><br>
                💰 {int(row['price']):,} VND<br>
                🛞 {int(row['mileage_v2']):,} km</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

def render_price_chart(df_filtered):
    st.markdown("### 📊 Biểu đồ giá trung bình theo thời gian")

    df_plot = df_filtered.copy()
    df_plot['list_time'] = pd.to_datetime(df_plot['list_time'], unit='ms', errors='coerce')
    df_plot = df_plot.dropna(subset=['list_time'])

    if df_plot.empty:
        st.info("Không có dữ liệu đủ để vẽ biểu đồ.")
        return

    df_grouped = df_plot.groupby(df_plot['list_time'].dt.to_period('M'))['price'].mean().reset_index()
    df_grouped['list_time'] = df_grouped['list_time'].astype(str)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=df_grouped, x='list_time', y='price', marker='o', ax=ax)
    plt.xticks(rotation=45)
    plt.ylabel("Giá trung bình (VND)")
    plt.xlabel("Thời gian đăng bán")
    plt.grid(True)
    st.pyplot(fig)
