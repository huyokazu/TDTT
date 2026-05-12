import streamlit as st
import cv2
import mediapipe as mp
import urllib.request
import os
import av
from streamlit_webrtc import webrtc_streamer, RTCConfiguration

# 1. Cấu hình giao diện web
st.set_page_config(page_title="Nhận dạng Ngôn ngữ Ký hiệu", page_icon="🤟")
st.title("🤟 Nhận dạng Cử chỉ Ký hiệu")
st.write("Bật camera, giơ tay lên và kết quả sẽ hiển thị ngay trên video!")
st.write("Các ký hiệu hỗ trợ: 👍 (Like), 👎 (Dislike), ✌️ (Victory), 🤟 (I Love You), ✊ (Nắm tay), 🖐️ (Mở tay).")

# 2. Tải mô hình AI
@st.cache_resource
def load_model():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'gesture_recognizer.task')
    
    if not os.path.exists(model_path):
        url = 'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task'
        urllib.request.urlretrieve(url, model_path)
    
    options = mp.tasks.vision.GestureRecognizerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
        running_mode=mp.tasks.vision.RunningMode.IMAGE
    )
    return mp.tasks.vision.GestureRecognizer.create_from_options(options)

recognizer = load_model()

# 3. Hàm xử lý: Nhận dạng và IN CHỮ LÊN MÀN HÌNH
def process_frame(frame: av.VideoFrame) -> av.VideoFrame:
    # Chuyển frame thành ảnh
    img = frame.to_ndarray(format="bgr24")
    img = cv2.flip(img, 1) # Lật ảnh như soi gương
    
    # AI xử lý
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
    recognition_result = recognizer.recognize(mp_image)
    
    # NẾU PHÁT HIỆN CỬ CHỈ -> VẼ CHỮ LÊN MÀN HÌNH
    if recognition_result.gestures:
        for gesture in recognition_result.gestures:
            name = gesture[0].category_name
            score = gesture[0].score
            
            # Chỉ hiện chữ nếu AI chắc chắn > 50%
            if score > 0.5:
                text = f"{name} ({score*100:.0f}%)"
                # Lệnh vẽ chữ: Màu xanh lá cây (0, 255, 0), font to (chỉ số 2), nét đậm (chỉ số 4)
                cv2.putText(img, text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4, cv2.LINE_AA)
                
    # Trả lại khung hình đã có chữ lên web
    return av.VideoFrame.from_ndarray(img, format="bgr24")

# 4. Vượt tường lửa mạng để Camera không bị xoay vòng
rtc_configuration = RTCConfiguration(
    {"iceServers": [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
        {"urls": ["stun:stun2.l.google.com:19302"]},
        {"urls": ["stun:stun3.l.google.com:19302"]},
        {"urls": ["stun:stun4.l.google.com:19302"]},
    ]}
)

# 5. Khởi động luồng Camera
webrtc_streamer(
    key="sign_language",
    video_frame_callback=process_frame,
    rtc_configuration=rtc_configuration,
    media_stream_constraints={"video": True, "audio": False}
)
