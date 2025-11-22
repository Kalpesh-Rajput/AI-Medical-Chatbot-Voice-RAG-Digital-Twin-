import streamlit as st
import pyaudio
import wave
import speech_recognition as sr
import tempfile

from backend.rag import answer_query_with_cache
from backend.digital_twin import PatientDigitalTwin


# ---------------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------------
st.set_page_config(page_title="AI Medical Chatbot", page_icon="🧠", layout="wide")
st.title("🧠 AI Medical Chatbot (Voice + RAG + Digital Twin)")


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "twin" not in st.session_state:
    st.session_state.twin = PatientDigitalTwin()

if "history" not in st.session_state:
    st.session_state.history = []

if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False


# ---------------------------------------------------------
# SIDEBAR — DIGITAL TWIN
# ---------------------------------------------------------
st.sidebar.header("🩺 Digital Twin - Patient Vitals")

vitals = st.session_state.twin.get_vitals()

st.sidebar.metric("Heart Rate (bpm)", vitals["heart_rate"])
st.sidebar.metric("Temperature (°F)", vitals["temperature"])
st.sidebar.metric("Blood Pressure", vitals["blood_pressure"])
st.sidebar.metric("Respiration Rate", vitals["respiration_rate"])
st.sidebar.metric("Oxygen Saturation (%)", vitals["oxygen_saturation"])

if st.sidebar.button("🔄 Refresh Vitals"):
    st.session_state.twin.update_vitals()
    st.rerun()


# -------------------------------------------------------
# VOICE RECORDING FUNCTION (Works on Windows/Mac/Linux)
# ---------------------------------------------------------
def record_audio(duration=5, filename="voice.wav"):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    p = pyaudio.PyAudio()

    st.info("🎙 Recording... Speak now!")
    stream = p.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    for _ in range(int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()
    st.success("Recording complete!")

    wf = wave.open(filename, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    return filename


# ---------------------------------------------------------
# MAIN INPUT — TEXT + VOICE
# ---------------------------------------------------------
st.subheader("💬 Ask a medical question")

user_query = st.text_input("Type your question:", key="text_input_query")

# VOICE INPUT
st.write("🎤 **Or speak your question (5 seconds)**")

if st.button("Record Voice"):
    st.session_state.voice_mode = True
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio_file = record_audio(duration=5, filename=tmp.name)

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)
            st.success(f"🗣 You said: {text}")
            user_query = text
        except:
            st.warning("Could not understand the voice.")


# ---------------------------------------------------------
# RAG PIPELINE
# ---------------------------------------------------------
vitals_short = (
    f"HR={vitals['heart_rate']}, Temp={vitals['temperature']}F, "
    f"BP={vitals['blood_pressure']}, RR={vitals['respiration_rate']}, "
    f"SpO2={vitals['oxygen_saturation']}"
)

if st.button("Ask"):
    if user_query.strip():
        with st.spinner("🔍 Retrieving medical context and generating answer..."):
            response = answer_query_with_cache(
                query=user_query,
                k=3,
                ttl_seconds=3600,
                include_vitals=vitals_short,
            )

        # Store history (append at end)
        st.session_state.history.append(("You", user_query))
        st.session_state.history.append(("Bot", response["answer"]))

    else:
        st.warning("Please type or speak a question.")


# ---------------------------------------------------------
# DISPLAY CHAT HISTORY — NEWEST FIRST
# ---------------------------------------------------------
if st.session_state.history:
    st.write("## 💬 Conversation History")

    for role, msg in reversed(st.session_state.history):
        if role == "You":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 Bot:** {msg}")

    # Show sources only for last response
    if st.session_state.history[-1][0] == "Bot":
        last_sources = response["sources"]
        st.markdown("### 📚 Sources:")
        for src in last_sources:
            url = src.get("source", "")
            if url:
                st.markdown(f"- [{url}]({url})")
            else:
                st.markdown(f"- {src}")

    if response.get("cached"):
        st.success("⚡ Cached Answer")
    else:
        st.info("✨ Fresh Answer")


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.write("---")
st.markdown("⚠️ **Disclaimer:** This tool is not a medical diagnosis system. Always consult a doctor.")

