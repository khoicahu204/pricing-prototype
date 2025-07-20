
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Load dữ liệu
df = pd.read_csv("cleaned_data_f.csv")

st.title("🚗 Định giá sơ bộ xe đã qua sử dụng")
st.set_page_config(layout="wide")

def create_card(title, content, color="#f0f2f6"):
    st.markdown(f"""
    <div style='background-color: {color}; padding: 20px; border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 25px;'>
        <h4 style='color:#333;'>{title}</h4>
        <p style='color:#555; line-height: 1.5;'>{content}</p>
    </div>
    """, unsafe_allow_html=True)



# Điều hướng trang bằng session_state
if "page" not in st.session_state:
    st.session_state.page = "form"
if "step" not in st.session_state:
    st.session_state.step = "price"

def train_model_for_vehicle(df, brand, model):
    df_filtered = df[
        (df["brand"].str.lower() == brand.lower()) &
        (df["model"].str.strip().str.lower() == model.lower())
    ].dropna(subset=["manufacture_date", "mileage_v2", "price"])

    if len(df_filtered) < 20:
        return None, None, None

    X = df_filtered[["manufacture_date", "mileage_v2"]]
    y = df_filtered["price"]

    # Thay LinearRegression bằng RandomForestRegressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    y_pred = model.predict(X)
    mae = mean_absolute_error(y, y_pred)

    return model, mae, df_filtered

# ===== TRANG FORM =====
if st.session_state.page == "form":
    st.subheader("📝 Nhập thông tin xe")

    selected_brand = st.selectbox("Hãng xe", sorted(df["brand"].dropna().unique()))
    filtered_models = df[df["brand"] == selected_brand]["model"].dropna().unique()
    selected_model = st.selectbox("Dòng xe", sorted(filtered_models))
    filtered_years = df[
        (df["brand"] == selected_brand) & (df["model"] == selected_model)
    ]["manufacture_date"].dropna().unique()
    selected_year = st.selectbox("Đời xe", sorted(filtered_years, reverse=True))
    input_mileage = st.number_input("Số km đã đi", min_value=0, step=1000)

    if st.button("📊 Định giá sơ bộ"):
        st.session_state.selected_brand = selected_brand
        st.session_state.selected_model = selected_model
        st.session_state.selected_year = selected_year
        st.session_state.input_mileage = input_mileage
        st.session_state.page = "result"
        st.session_state.step = "price"
        st.rerun()

# ===== TRANG KẾT QUẢ =====
elif st.session_state.page == "result":
    selected_brand = st.session_state.selected_brand
    selected_model = st.session_state.selected_model
    selected_year = st.session_state.selected_year
    input_mileage = st.session_state.input_mileage

    if st.button("🔙 Quay lại form"):
        st.session_state.page = "form"
        st.rerun()

    model, mae, df_filtered = train_model_for_vehicle(df, selected_brand, selected_model)

    if model:
        input_df = pd.DataFrame([{
            "manufacture_date": selected_year,
            "mileage_v2": input_mileage
        }])
        predicted_price = model.predict(input_df)[0]
        lower = predicted_price - mae
        upper = predicted_price + mae

        col_left, col_right = st.columns([1, 2])

        with col_left:
            


            st.subheader("💰 Giá đề xuất")
            st.success(f"✅ {lower:,.0f} – {upper:,.0f} VND")

            if st.session_state.step == "price":
                st.markdown("### 🤔 Giá này có phù hợp với mong muốn của bạn không?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💬 Tôi muốn nhập giá mong muốn"):
                        st.session_state.step = "offer"
                        st.rerun()
                with col2:
                    if st.button("🤝 Kết nối ngay với người mua"):
                        st.session_state.step = "contact"
                        st.rerun()

            elif st.session_state.step == "offer":
                your_price = st.number_input("💡 Giá mong muốn của bạn (VND)", min_value=0, step=1000000)
                if st.button("🚀 Gửi và kết nối với người mua"):
                    st.session_state.offer_price = your_price
                    st.session_state.step = "contact"
                    st.rerun()

            elif st.session_state.step == "contact":
                st.markdown("### 📇 Nhập thông tin liên hệ để chúng tôi hỗ trợ kết nối")
                name = st.text_input("👤 Họ tên")
                phone = st.text_input("📱 Số điện thoại")
                note = st.text_area("📝 Ghi chú thêm (tuỳ chọn)")
                if st.button("✅ Gửi thông tin"):
                    st.session_state.page = "thankyou"
                    st.rerun()
            

        with col_right:
            

            st.subheader("🚘 Các xe tương tự đã đăng bán")
            similar_cars = df[
                (df["brand"].str.lower() == selected_brand.lower()) &
                (df["model"].str.strip().str.lower() == selected_model.lower()) &
                (df["manufacture_date"] == selected_year)
            ].copy()
            similar_cars["list_time"] = pd.to_datetime(similar_cars["list_time"], errors="coerce")
            similar_cars = similar_cars.sort_values(by="list_time", ascending=False).head(6)

            cols = st.columns(3)
            for i, (_, row) in enumerate(similar_cars.iterrows()):
                with cols[i % 3]:
                    try:
                        image = Image.open(row['image_path']).resize((300, 200))
                        st.image(image, use_container_width=True)
                    except:
                        st.image("default.jpg", use_container_width=True)

                    st.markdown(f"**{row['brand']} {row['model']} {int(row['manufacture_date'])}**")
                    st.markdown("📍 TP.HCM")
                    st.markdown(f"🔧 {int(row['mileage_v2']):,} km")
                    st.markdown(f"💰 {int(row['price']):,} VND")
                    
            st.subheader("📈 Biểu đồ giá xe tương tự theo thời gian")
            df_filtered["list_time"] = pd.to_datetime(df_filtered["list_time"], errors="coerce")
            df_filtered["date_only"] = df_filtered["list_time"].dt.date

            st.markdown("### 🎯 Chọn khoảng số km đã đi để phân tích")
            option = st.radio(
                "Khoảng số km",
                (
                    f"Gần với bạn: ±10,000 km",
                    "Dưới 10,000 km",
                    "Dưới 20,000 km",
                    "Dưới 50,000 km",
                    "Dưới 70,000 km"
                ),
                horizontal=True
            )

            if option.startswith("Gần với"):
                lower_km = max(0, input_mileage - 10000)
                upper_km = input_mileage + 10000
            else:
                upper_km = int(option.split(" ")[1].replace(",", "").replace("km", ""))
                lower_km = 0

            df_chart = df_filtered[
                (df_filtered["mileage_v2"] >= lower_km) &
                (df_filtered["mileage_v2"] <= upper_km)
            ]
            df_grouped = df_chart.groupby("date_only")["price"].mean().reset_index()

            plt.figure(figsize=(10, 4))
            sns.lineplot(data=df_grouped, x="date_only", y="price", marker="o")
            plt.xticks(rotation=45)
            plt.ylabel("Giá trung bình (VND)")
            plt.xlabel("Ngày đăng")
            plt.title(f"Giá xe {selected_brand} {selected_model} {selected_year} theo thời gian")
            plt.grid(True)
            st.pyplot(plt.gcf())

    else:
        st.warning("⚠️ Không đủ dữ liệu để định giá dòng xe này.")

# ===== TRANG CẢM ƠN =====
elif st.session_state.page == "thankyou":
    st.balloons()
    st.success("🎉 Cảm ơn bạn! Chúng tôi sẽ cố gắng kết nối bạn với người mua sớm nhất.")
    st.info("📞 Chúng tôi sẽ liên hệ bạn qua số **0968639504** hoặc thông tin bạn đã cung cấp.")
    if st.button("🔁 Làm định giá khác"):
        st.session_state.page = "form"
        st.rerun()
