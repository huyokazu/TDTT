import streamlit as st
import cv2
import mediapipe as mp
import urllib.request
import os
import av
from streamlit_webrtc import webrtc_streamer, RTCConfiguration

# 1. Cấu hình giao diện trang web
st.set_page_config(page_title="Nhận dạng Ngôn ngữ Ký hiệu", page_icon="🤟")
st.title("🤟 Web App: Nhận dạng Cử chỉ Ký hiệu")
st.write("Bật camera và thử đưa các ký hiệu: 👍, 👎, ✌️ (Victory), 🤟 (I Love You), ✊ (Nắm tay), 🖐️ (Mở tay).")

# 2. Tải và nạp mô hình AI (Sử dụng cache để không phải tải lại mỗi lần có frame mới)
@st.cache_resource
def load_model():
    # Lấy đường dẫn tuyệt đối của thư mục đang chứa file app.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'gesture_recognizer.task')
    
    if not os.path.exists(model_path):
        st.info("Đang tải mô hình AI từ Google lần đầu tiên. Vui lòng đợi khoảng vài giây...")
        url = 'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task'
        urllib.request.urlretrieve(url, model_path)
    
    options = mp.tasks.vision.GestureRecognizerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
        running_mode=mp.tasks.vision.RunningMode.IMAGE
    )
    return mp.tasks.vision.GestureRecognizer.create_from_options(options)

recognizer = load_model()

# 3. Hàm xử lý từng khung hình video từ webcam người dùng
def process_frame(frame: av.VideoFrame) -> av.VideoFrame:
    # Chuyển đổi khung hình video thành mảng hình ảnh OpenCV
    img = frame.to_ndarray(format="bgr24")
    img = cv2.flip(img, 1) # Lật ảnh như gương
    
    # Chuyển đổi sang định dạng MediaPipe
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
    
    # AI nhận dạng
    recognition_result = recognizer.recognize(mp_image)
    
    # Vẽ kết quả lên hình
    if recognition_result.gestures:
        for gesture in recognition_result.gestures:
            name = gesture[0].category_name
            score = gesture[0].score
            
            if score > 0.5:
                text = f"{name} ({score*100:.0f}%)"
                cv2.putText(img, text, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                
    # Trả lại khung hình đã vẽ chữ cho người dùng
    return av.VideoFrame.from_ndarray(img, format="bgr24")

# 4. Cấu hình máy chủ kết nối WebRTC (Vượt tường lửa mạng)
rtc_configuration = RTCConfiguration(
    {"iceServers": [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
        {"urls": ["stun:stun2.l.google.com:19302"]},
        {"urls": ["stun:stun3.l.google.com:19302"]},
        {"urls": ["stun:stun4.l.google.com:19302"]},
    ]}
)

# 5. Khởi chạy luồng camera trên web
webrtc_streamer(
    key="sign_language_camera",
    video_frame_callback=process_frame,
    rtc_configuration=rtc_configuration,
    media_stream_constraints={"video": True, "audio": False}
)
