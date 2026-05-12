import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH AI ---
genai.configure(api_key="AIzaSyC5qGYjTI_SldZ_r2eIAqtZYn-wYaA1oEw")
model = genai.GenerativeModel('models/gemini-3.1-flash-lite')

# --- GIAO DIỆN ---
st.set_page_config(page_title="Trợ lý Dinh dưỡng AI", layout="wide")

st.title("🥗 Trợ lý Dinh dưỡng & Sức khỏe AI")
st.markdown("---")

# --- PHẦN 1: NHẬP THÔNG TIN (SIDEBAR) ---
with st.sidebar:
    st.header("Thông tin cá nhân")
    weight = st.number_input("Cân nặng (kg)", min_value=30.0, max_value=200.0, value=60.0)
    height = st.number_input("Chiều cao (cm)", min_value=100.0, max_value=250.0, value=165.0)
    age = st.number_input("Tuổi", min_value=1, max_value=100, value=25)
    gender = st.selectbox("Giới tính", ["Nam", "Nữ"])
    activity = st.selectbox("Mức độ vận động", [
        "Ít vận động (Văn phòng)",
        "Vận động nhẹ (1-3 buổi/tuần)",
        "Vận động vừa (3-5 buổi/tuần)",
        "Vận động nặng (6-7 buổi/tuần)"
    ])
    goal = st.selectbox("Mục tiêu", ["Giảm cân", "Giữ cân", "Tăng cơ"])

# --- PHẦN 2: TÍNH TOÁN CHỈ SỐ ---
# Công thức BMI
bmi = weight / ((height/100) ** 2)

# Tính BMR sơ bộ (Công thức Mifflin-St Jeor)
if gender == "Nam":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

# Quy đổi mức độ vận động sang TDEE
activity_multipliers = {
    "Ít vận động (Văn phòng)": 1.2,
    "Vận động nhẹ (1-3 buổi/tuần)": 1.375,
    "Vận động vừa (3-5 buổi/tuần)": 1.55,
    "Vận động nặng (6-7 buổi/tuần)": 1.725
}
tdee = bmr * activity_multipliers[activity]

# --- HIỂN THỊ KẾT QUẢ ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Chỉ số BMI", f"{bmi:.1f}")
with col2:
    st.metric("Lượng Calo cần thiết (TDEE)", f"{int(tdee)} kcal")
with col3:
    status = "Bình thường" if 18.5 <= bmi <= 24.9 else "Cần chú ý"
    st.metric("Tình trạng", status)

# --- PHẦN 3: TƯ VẤN THỰC ĐƠN BẰNG AI ---
st.markdown("---")
st.subheader("🤖 AI Gợi ý thực đơn trong ngày")

if st.button("Tạo thực đơn cá nhân hóa"):
    prompt = f"""
    Tôi là {gender}, {age} tuổi, nặng {weight}kg, cao {height}cm. 
    Mức độ vận động: {activity}. Mục tiêu của tôi là {goal}.
    Chỉ số TDEE của tôi là {int(tdee)} kcal.
    Hãy gợi ý cho tôi thực đơn 3 bữa (Sáng, Trưa, Tối) sao cho lành mạnh, 
    phù hợp với người Việt Nam và đạt mục tiêu {goal}.
    Hãy trình bày dưới dạng danh sách gạch đầu dòng rõ ràng.
    """
    
    with st.spinner("AI đang lên thực đơn cho bạn..."):
        response = model.generate_content(prompt)
        st.write(response.text)

st.info("Lưu ý: Các chỉ số và thực đơn mang tính chất tham khảo. Hãy tham vấn bác sĩ trước khi thay đổi chế độ ăn nghiêm ngặt.")
