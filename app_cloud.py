# import streamlit as st
# from streamlit_webrtc import webrtc_streamer, WebRtcMode
# import av
# import numpy as np
# import tempfile
# import speech_recognition as sr

# from backend.rag import answer_query_with_cache
# from backend.digital_twin import PatientDigitalTwin

# st.set_page_config(page_title="AI Medical Chatbot", page_icon="🧠", layout="wide")
# st.title("🧠 AI Medical Chatbot (Cloud Version — Voice + RAG + Digital Twin)")

# # Session State
# if "twin" not in st.session_state:
#     st.session_state.twin = PatientDigitalTwin()
# if "history" not in st.session_state:
#     st.session_state.history = []
# if "audio_frames" not in st.session_state:
#     st.session_state.audio_frames = []


# # DIGITAL TWIN
# st.sidebar.header("🩺 Digital Twin — Patient Vitals")
# vitals = st.session_state.twin.get_vitals()
# for key, value in vitals.items():
#     st.sidebar.metric(key.replace("_", " ").title(), value)

# if st.sidebar.button("🔄 Refresh Vitals"):
#     st.session_state.twin.update_vitals()
#     st.rerun()


# # -------------------------- AUDIO RECEIVER --------------------------
# class AudioReceiver:
#     def __init__(self):
#         self.frames = []

#     def recv(self, frame):
#         audio = frame.to_ndarray()
#         self.frames.append(audio)
#         return frame


# # -------------------------- WEBRTC MICROPHONE --------------------------
# st.subheader("🎤 Speak your question (Browser Microphone)")

# ctx = webrtc_streamer(
#     key="speech",
#     mode=WebRtcMode.RECVONLY,
#     audio_receiver_size=1024,
#     media_stream_constraints={"audio": True, "video": False},
# )

# user_query = st.text_input("💬 Or type your medical question:")

# if ctx.audio_receiver:
#     if st.button("Convert Speech to Text"):
#         audio_frames = ctx.audio_receiver.get_frames(timeout=1)

#         if audio_frames:
#             audio_data = np.concatenate([f.to_ndarray() for f in audio_frames], axis=0)
#             audio_bytes = audio_data.astype(np.int16).tobytes()

#             with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
#                 audio_path = tmp.name
#                 with open(audio_path, "wb") as f:
#                     f.write(audio_bytes)

#             # Speech recognition
#             recognizer = sr.Recognizer()
#             with sr.AudioFile(audio_path) as source:
#                 audio_obj = recognizer.record(source)

#             try:
#                 spoken_text = recognizer.recognize_google(audio_obj)
#                 st.success(f"🗣 You said: {spoken_text}")
#                 user_query = spoken_text
#             except Exception as e:
#                 st.error(f"Speech Recognition Error: {e}")


# # -------------------------- RAG PIPELINE --------------------------
# vitals_short = (
#     f"HR={vitals['heart_rate']}, Temp={vitals['temperature']}F, "
#     f"BP={vitals['blood_pressure']}, RR={vitals['respiration_rate']}, "
#     f"SpO2={vitals['oxygen_saturation']}"
# )

# response = None

# if st.button("Ask"):
#     if user_query.strip():
#         with st.spinner("🤖 Generating medical response..."):
#             response = answer_query_with_cache(
#                 query=user_query,
#                 k=3,
#                 ttl_seconds=3600,
#                 include_vitals=vitals_short,
#             )

#         st.session_state.history.append(("You", user_query))
#         st.session_state.history.append(("Bot", response["answer"]))
#     else:
#         st.warning("Please speak or type your question.")


# # -------------------------- HISTORY --------------------------
# st.write("## 💬 Chat History")

# for role, msg in reversed(st.session_state.history):
#     st.markdown(f"**{role}:** {msg}")

# if response:
#     st.write("### 📚 Sources Used:")
#     for src in response["sources"]:
#         st.markdown(f"- {src['source']}")
###########################################################################################
#######################################################################################################################

import os
from dotenv import load_dotenv
load_dotenv()


import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import numpy as np
import tempfile
import speech_recognition as sr

from backend.rag import answer_query_with_cache
from backend.digital_twin import PatientDigitalTwin
import patches.fix_numpy2


# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(page_title="AI Medical Chatbot", page_icon="🧠", layout="wide")
st.title("🧠 AI Medical Chatbot (Cloud Version — Voice + RAG + Digital Twin)")


# ==========================================================
# SESSION STATE
# ==========================================================
if "twin" not in st.session_state:
    st.session_state.twin = PatientDigitalTwin()

if "history" not in st.session_state:
    st.session_state.history = []

if "audio_frames" not in st.session_state:
    st.session_state.audio_frames = None


# ==========================================================
# DIGITAL TWIN SIDEBAR
# ==========================================================
st.sidebar.header("🩺 Digital Twin — Patient Vitals")
vitals = st.session_state.twin.get_vitals()

st.sidebar.metric("Heart Rate", vitals["heart_rate"])
st.sidebar.metric("Temperature (°F)", vitals["temperature"])
st.sidebar.metric("Blood Pressure", vitals["blood_pressure"])
st.sidebar.metric("Respiration Rate", vitals["respiration_rate"])
st.sidebar.metric("Oxygen Saturation (%)", vitals["oxygen_saturation"])

if st.sidebar.button("🔄 Refresh Vitals"):
    st.session_state.twin.update_vitals()
    st.rerun()


# ==========================================================
# AUDIO RECEIVER CLASS (WebRTC)
# ==========================================================
class AudioProcessor:
    def __init__(self):
        self.frames = []

    def recv(self, frame):
        audio = frame.to_ndarray()
        self.frames.append(audio)
        return frame


# ==========================================================
# VOICE INPUT (WebRTC Microphone)
# ==========================================================
st.subheader("🎤 Speak your medical question (Streamlit Cloud Microphone)")

ctx = webrtc_streamer(
    key="speech",
    mode=WebRtcMode.RECVONLY,
    audio_receiver_size=1024,
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
)


# STORAGE FOR USER QUERY
user_query = st.text_input("💬 Or type your medical question:")


# ==========================================================
# CONVERT AUDIO → TEXT
# ==========================================================
if ctx.audio_receiver:
    if st.button("🎙 Convert Speech to Text"):
        frames = ctx.audio_receiver.get_frames(timeout=1)

        if frames:
            # Convert frames to wave-like raw bytes
            audio_data = np.concatenate([f.to_ndarray() for f in frames], axis=0)
            audio_bytes = audio_data.astype(np.int16).tobytes()

            # Save temporary WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                wav_path = tmp.name
                with open(wav_path, "wb") as f:
                    f.write(audio_bytes)

            # Speech-to-Text
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_obj = recognizer.record(source)

            try:
                spoken_text = recognizer.recognize_google(audio_obj)
                st.success(f"🗣 You said: {spoken_text}")
                user_query = spoken_text
            except Exception as e:
                st.error(f"Speech recognition failed: {e}")
        else:
            st.warning("⚠ No audio received. Try again.")


# ==========================================================
# RAG PIPELINE
# ==========================================================
response = None

vitals_short = (
    f"HR={vitals['heart_rate']}, Temp={vitals['temperature']}F, "
    f"BP={vitals['blood_pressure']}, RR={vitals['respiration_rate']}, "
    f"SpO2={vitals['oxygen_saturation']}"
)

if st.button("🤖 Ask AI"):
    if user_query.strip():
        with st.spinner("Generating medical response..."):
            response = answer_query_with_cache(
                query=user_query,
                k=3,
                ttl_seconds=3600,
                include_vitals=vitals_short,
            )

        st.session_state.history.append(("You", user_query))
        st.session_state.history.append(("Bot", response["answer"]))
    else:
        st.warning("Please type or speak a question.")


# ==========================================================
# DISPLAY CHAT HISTORY
# ==========================================================
st.write("## 💬 Chat History")

for role, msg in reversed(st.session_state.history):
    st.markdown(f"**{role}:** {msg}")

if response:
    st.write("### 📚 Sources Used:")
    for src in response["sources"]:
        st.markdown(f"- {src['source']}")
