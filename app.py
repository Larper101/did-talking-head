import os
import time
import base64
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env / .env.local if present
load_dotenv(".env.local")
load_dotenv(".env")

# ─── Page Configuration ───
st.set_page_config(
    page_title="D-ID Studio — AI Talking Head Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS Styling ───
st.markdown("""
<style>
    /* Dark Theme Custom Styling */
    .stApp {
        background-color: #0b0f1a;
        color: #f1f5f9;
    }
    
    /* Header Container */
    .main-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 28px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .main-header h1 {
        background: linear-gradient(135deg, #818cf8, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin: 0 0 6px 0;
        font-size: 2.2rem;
    }

    .main-header p {
        color: #94a3b8;
        font-size: 1rem;
        margin: 0;
    }

    /* Warning Banner */
    .warning-banner {
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #fbbf24;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.85rem;
        margin-top: 6px;
        margin-bottom: 16px;
    }

    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .status-done {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    /* Card styling */
    div[data-testid="stForm"], div[data-testid="stVerticalBlock"] > div.element-container {
        border-radius: 12px;
    }

    /* Primary Button */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Constants & Voice Options ───
VOICE_OPTIONS = {
    "en-US-JennyNeural": "Jenny (Female) — en-US-JennyNeural",
    "en-US-GuyNeural": "Guy (Male) — en-US-GuyNeural",
    "en-US-AriaNeural": "Aria (Female) — en-US-AriaNeural",
    "en-US-DavisNeural": "Davis (Male) — en-US-DavisNeural",
}

DEFAULT_AVATAR_URL = "https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg"
D_ID_API_URL = "https://api.d-id.com/talks"
MAX_TEXT_LENGTH = 1000

# ─── Initialize Session State ───
if "history" not in st.session_state:
    st.session_state.history = []

if "generated_video_url" not in st.session_state:
    st.session_state.generated_video_url = None

# ─── API Helper Functions ───
def get_api_key():
    """Retrieve API key from Streamlit secrets, environment, or user input."""
    # Check Streamlit secrets first
    if "D_ID_API_KEY" in st.secrets:
        return st.secrets["D_ID_API_KEY"]
    
    # Check environment variables
    env_key = os.getenv("D_ID_API_KEY")
    if env_key:
        return env_key
    
    # Check session state override
    if "user_api_key" in st.session_state and st.session_state.user_api_key:
        return st.session_state.user_api_key
        
    return None

def get_auth_header(api_key: str) -> dict:
    """Construct Basic Auth header for D-ID API."""
    encoded_key = base64.b64encode(api_key.strip().encode("utf-8")).decode("utf-8")
    return {
        "Authorization": f"Basic {encoded_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def create_talk(api_key: str, text: str, source_url: str, voice_id: str):
    """Call D-ID POST /talks endpoint."""
    headers = get_auth_header(api_key)
    payload = {
        "script": {
            "type": "text",
            "input": text.strip(),
            "provider": {
                "type": "microsoft",
                "voice_id": voice_id
            }
        },
        "source_url": source_url.strip()
    }
    
    response = requests.post(D_ID_API_URL, json=payload, headers=headers, timeout=30)
    return response

def get_talk_status(api_key: str, talk_id: str):
    """Call D-ID GET /talks/{id} endpoint."""
    headers = get_auth_header(api_key)
    response = requests.get(f"{D_ID_API_URL}/{talk_id}", headers=headers, timeout=30)
    return response

# ─── Sidebar ───
with st.sidebar:
    st.image("https://studio.d-id.com/favicon.ico", width=36)
    st.title("D-ID Configuration")
    
    api_key = get_api_key()
    
    if api_key:
        st.success("✓ D-ID API Key Loaded", icon="🔑")
        with st.expander("Change API Key"):
            new_key = st.text_input("D-ID API Key", value=api_key, type="password", key="key_input_override")
            if new_key and new_key != api_key:
                st.session_state.user_api_key = new_key
                st.rerun()
    else:
        st.warning("⚠ D-ID API Key not found in environment or secrets.")
        user_key = st.text_input("Enter D-ID API Key:", type="password", help="Found at https://studio.d-id.com → Settings → API Keys")
        if user_key:
            st.session_state.user_api_key = user_key
            st.rerun()

    st.markdown("---")
    st.markdown("### ℹ About D-ID Studio")
    st.markdown("""
    Generates realistic AI talking-head videos from text using **D-ID's Talks API** with **Microsoft Azure** neural voices.
    
    - **Host on Streamlit Cloud**: Set `D_ID_API_KEY` in Streamlit App Secrets.
    - **Run Locally**: Add `D_ID_API_KEY` to `.env.local` or `.env`.
    """)
    st.markdown("---")
    st.caption("Powered by D-ID API & Streamlit")

# ─── Header ───
st.markdown("""
<div class="main-header">
    <h1>🎬 D-ID Studio AI Talking Head Generator</h1>
    <p>Transform plain text into dynamic talking-head AI videos in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ─── Main Content Layout (Split Screen) ───
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("⚙ Configuration")
    
    # Avatar Image URL Input
    avatar_url = st.text_input(
        "Avatar Image URL (source_url):",
        value=DEFAULT_AVATAR_URL,
        help="Provide a direct link to a front-facing face photo."
    )
    st.markdown("""
    <div class="warning-banner">
        ⚠ <strong>This MUST be a publicly accessible image URL</strong> (e.g. ends in .jpg or .png)
    </div>
    """, unsafe_allow_html=True)
    
    # Avatar Preview
    if avatar_url:
        with st.expander("👁 Preview Avatar Image", expanded=True):
            try:
                st.image(avatar_url, caption="Avatar Preview", width=180)
            except Exception:
                st.caption("Unable to load preview image.")

    # Script Input
    script_text = st.text_area(
        "Script Text:",
        value="Hello! Welcome to D-ID Studio. I am an AI talking head avatar powered by D-ID.",
        height=140,
        max_chars=MAX_TEXT_LENGTH,
        help="Type what you want the talking head to say (max 1000 chars)."
    )
    
    char_count = len(script_text)
    st.caption(f"Character count: {char_count} / {MAX_TEXT_LENGTH}")

    # Voice Selection
    selected_voice_key = st.selectbox(
        "Voice Selection (Microsoft Azure Neural Voices):",
        options=list(VOICE_OPTIONS.keys()),
        format_func=lambda k: VOICE_OPTIONS[k]
    )

    # Generate Button
    generate_clicked = st.button("▶ Generate Video", use_container_width=True)

# ─── Video Generation Logic & Output Column ───
with col_output:
    st.subheader("📺 Video Output")
    
    if generate_clicked:
        current_key = get_api_key()
        
        if not current_key:
            st.error("🔑 API Key Missing! Please enter your D-ID API key in the sidebar.")
        elif not script_text.strip():
            st.warning("Please enter a script text.")
        elif not avatar_url.strip():
            st.warning("Please enter an avatar image URL.")
        else:
            with st.spinner("Initiating video generation with D-ID API..."):
                res = create_talk(current_key, script_text, avatar_url, selected_voice_key)
                
                if res.status_code == 201:
                    data = res.json()
                    talk_id = data.get("id")
                    st.success(f"Request accepted! Talk ID: `{talk_id}`")
                    
                    # Progress & Polling
                    progress_text = "Generating video... This usually takes 10-30 seconds."
                    progress_bar = st.progress(0, text=progress_text)
                    
                    attempts = 0
                    max_attempts = 60 # 3s * 60 = 3 mins
                    done = False
                    
                    while attempts < max_attempts and not done:
                        attempts += 1
                        time.sleep(3)
                        
                        # Update progress bar
                        percent = min(int((attempts / 10) * 100), 95)
                        progress_bar.progress(percent, text=f"Generating video... ({attempts * 3}s elapsed)")
                        
                        poll_res = get_talk_status(current_key, talk_id)
                        
                        if poll_res.status_code == 200:
                            poll_data = poll_res.json()
                            status = poll_data.get("status")
                            
                            if status == "done":
                                done = True
                                progress_bar.progress(100, text="Generation complete!")
                                result_url = poll_data.get("result_url")
                                st.session_state.generated_video_url = result_url
                                
                                # Add to history
                                history_item = {
                                    "id": talk_id,
                                    "text": script_text[:80] + ("..." if len(script_text) > 80 else ""),
                                    "avatar": avatar_url,
                                    "voice": VOICE_OPTIONS.get(selected_voice_key, selected_voice_key),
                                    "result_url": result_url,
                                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                                }
                                st.session_state.history.insert(0, history_item)
                                st.toast("Video generated successfully!", icon="✅")
                                
                            elif status in ["error", "rejected"]:
                                done = True
                                progress_bar.empty()
                                error_info = poll_data.get("error", {})
                                st.error(f"❌ Video generation failed ({status}): {error_info.get('description', 'Unknown error')}")
                        else:
                            done = True
                            progress_bar.empty()
                            st.error(f"Error checking talk status ({poll_res.status_code}): {poll_res.text}")
                    
                    if not done:
                        progress_bar.empty()
                        st.error("⏰ Generation timed out. Please check back later.")
                        
                elif res.status_code == 401:
                    st.error("🔑 Authentication failed (401). Invalid D-ID API Key. Please check your API key.")
                elif res.status_code == 402:
                    st.error("💳 Out of credits (402). Your D-ID account has insufficient credits.")
                elif res.status_code == 400:
                    err_json = res.json() if res.headers.get("content-type") == "application/json" else {}
                    st.error(f"❌ Bad Request (400): {err_json.get('description', res.text)}")
                else:
                    st.error(f"❌ D-ID API Error ({res.status_code}): {res.text}")

    # Display Video Player if available
    if st.session_state.generated_video_url:
        st.video(st.session_state.generated_video_url)
        
        # Download button
        try:
            video_bytes = requests.get(st.session_state.generated_video_url, timeout=30).content
            st.download_button(
                label="⬇ Download Video (MP4)",
                data=video_bytes,
                file_name="did_talking_head.mp4",
                mime="video/mp4",
                use_container_width=True
            )
        except Exception:
            st.markdown(f"[⬇ Open Direct Video Link]({st.session_state.generated_video_url})")
    else:
        if not generate_clicked:
            st.info("👋 Enter your script on the left and click **Generate Video** to create your AI talking-head video.")

# ─── History Section ───
if st.session_state.history:
    st.markdown("---")
    st.subheader("📜 Generation History")
    
    col_h_header, col_h_clear = st.columns([4, 1])
    with col_h_clear:
        if st.button("🗑 Clear History"):
            st.session_state.history = []
            st.session_state.generated_video_url = None
            st.rerun()

    for idx, item in enumerate(st.session_state.history):
        with st.expander(f"🎬 {item['text']} ({item['timestamp']})", expanded=(idx == 0)):
            h_col1, h_col2 = st.columns([1, 2])
            with h_col1:
                try:
                    st.image(item['avatar'], caption="Avatar", width=120)
                except Exception:
                    pass
                st.caption(f"**Voice:** {item['voice']}")
            with h_col2:
                st.video(item['result_url'])
                st.markdown(f"[⬇ Download MP4]({item['result_url']})")
