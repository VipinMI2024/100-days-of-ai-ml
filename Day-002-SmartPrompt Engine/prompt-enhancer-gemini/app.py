"""
Main Streamlit application - Prompt Enhancer with Gemini AI.
Unique "Gemini-Style" Studio Layout.
"""
import streamlit as st
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
import json

load_dotenv()

# --- (Assuming utils.gemini_client and enhancer.prompt_enhancer are in place) ---
# Placeholder functions if files are missing, remove these if you have the real ones.
try:
    from utils.gemini_client import get_gemini_client
    from enhancer.prompt_enhancer import PromptEnhancer
except ImportError:
    st.error("Missing 'utils' or 'enhancer' modules. Using dummy functions.")
    # Dummy class for PromptEnhancer
    class PromptEnhancer:
        ENHANCEMENT_MODES = {"Standard": "", "Creative": "", "Technical": ""}
        def apply_heuristic_enhancement(self, prompt: str) -> str:
            return f"[HEURISTIC] {prompt} - improved."
    
    # Dummy class for Gemini Client
    class DummyGeminiClient:
        def enhance_prompt(self, prompt: str, **kwargs) -> str:
            return f"[GEMINI] {prompt} - enhanced with {kwargs.get('mode', 'default')} mode."
    
    def get_gemini_client():
        # Return None to test fallback, or DummyGeminiClient() to test success
        return DummyGeminiClient() 
# --- End of placeholder section ---


# Page config
st.set_page_config(page_title="Prompt Studio", layout="wide")

# --- Apply Custom CSS for Background and Styling ---
def apply_styles():
    st.markdown(
        """
    <style>
    /* Main app background */
    [data-testid="stAppViewContainer"] {
        background: conic-gradient(at bottom left, #0f172a, #334155);
        color: #FAFAFA; /* Light text for readability */
    }
    
    /* Make headers lighter */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF;
    }
    
    /* Style text input/output boxes */
    [data-testid="stTextArea"] > div > textarea,
    [data-testid="stTextArea"] > div > div[data-baseweb="textarea"] > textarea {
        background-color: #1e293b; /* Darker blue-gray background */
        color: #E2E8F0; /* Light gray text */
        border: 1px solid #334155;
        height: 500px; /* Force a tall text area */
    }
    
    /* Style output code block */
    [data-testid="stCodeBlock"] > pre {
        background-color: #0f172a; /* Even darker for output */
        border: 1px dashed #334155;
        min-height: 500px; /* Match the text area height */
    }
    
    /* Hide the default Streamlit header/footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Style for the 'command bar' at the bottom */
    [data-testid="stHorizontalBlock"] {
        border-top: 1px solid #334155;
        padding-top: 10px;
        background-color: #0f172a; /* Match background */
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

apply_styles()

# --- Session State Initialization ---
if "history" not in st.session_state:
    st.session_state.history = []
if "prompt" not in st.session_state:
    st.session_state.prompt = ""
if "enhanced_text" not in st.session_state:
    st.session_state.enhanced_text = ""
if "enhanced_length" not in st.session_state:
    st.session_state.enhanced_length = 0
if "gemini_client" not in st.session_state:
    st.session_state.gemini_client = get_gemini_client()
if "local_enhancer" not in st.session_state:
    st.session_state.local_enhancer = PromptEnhancer()
if "mode" not in st.session_state:
    st.session_state.mode = "Creative" # Default mode

# --- Backend Functions ---
def save_record(original: str, enhanced: str, mode: str, llm_used: bool, length: int):
    st.session_state.history.append(
        {"timestamp": datetime.utcnow().isoformat() + "Z", "original": original, "enhanced": enhanced, "mode": mode, "llm_used": llm_used, "length": length}
    )

def run_enhancement(prompt: str, mode: str, use_gemini: bool) -> str:
    # Hardcoded values for temperature and max_tokens
    temperature = 0.7
    max_tokens = 500000 

    if use_gemini and st.session_state.gemini_client:
        try:
            enhanced = st.session_state.gemini_client.enhance_prompt(
                prompt, 
                mode=mode, 
                temperature=temperature, 
                max_tokens=max_tokens
            )
            return enhanced
        except Exception as e:
            st.warning(f"Gemini failed, falling back to heuristic: {e}")

    # heuristic fallback
    return st.session_state.local_enhancer.apply_heuristic_enhancement(prompt)

def export_json(record: dict) -> str:
    return json.dumps(record, indent=2)

# --- Main Application ---
st.title("Prompt Studio")

# The main content area
col_in, col_out = st.columns(2)

with col_in:
    st.subheader("Original")
    # Use file_text as default if available, otherwise use last prompt
    prompt_input = st.text_area("Original", value=st.session_state.prompt, height=500, placeholder="Type or paste your prompt here...", label_visibility="collapsed")
    st.session_state.prompt = prompt_input # Save last input

with col_out:
    st.subheader("Enhanced")
    if st.session_state.enhanced_length > 0:
        st.caption(f"Length: {st.session_state.enhanced_length} characters")
    
    st.code(st.session_state.enhanced_text or "Your enhanced prompt will appear here.", language=None)


# --- The "Command Bar" at the bottom ---
st.divider()

col_controls, col_action, col_history = st.columns([1, 2, 1])

with col_controls:
    # Control Panel as a Popover Button
    with st.popover("Controls", use_container_width=True):
        st.header("Settings")
        st.session_state.mode = st.selectbox("Mode", list(st.session_state.local_enhancer.ENHANCEMENT_MODES.keys()), index=1)
        
        # File upload section - tucked away
        with st.expander("Upload a File"):
            uploaded_file = st.file_uploader("Upload", type=["txt"])
            if uploaded_file is not None:
                file_text = uploaded_file.read().decode("utf-8")
                st.session_state.prompt = file_text
                st.success("Text file loaded!")
                st.rerun() # Rerun to update the text area

with col_action:
    if st.button("Enhance", use_container_width=True, type="primary"):
        if not st.session_state.prompt.strip():
            st.error("Please enter a prompt")
        else:
            with st.spinner("Enhancing..."):
                enhanced_text = run_enhancement(st.session_state.prompt, st.session_state.mode, True)
                st.session_state.enhanced_text = enhanced_text # Save to session state
                st.session_state.enhanced_length = len(enhanced_text)
                save_record(st.session_state.prompt, enhanced_text, st.session_state.mode, llm_used=(st.session_state.gemini_client is not None), length=st.session_state.enhanced_length)
                st.rerun()

with col_history:
    # History as a Popover Button
    with st.popover("History", use_container_width=True):
        st.header("History")
        if st.session_state.history:
            if st.button("Clear History", use_container_width=True):
                st.session_state.history = []
                st.session_state.prompt = ""
                st.session_state.enhanced_text = ""
                st.session_state.enhanced_length = 0
                st.rerun()
            
            st.divider()
            
            for rec in reversed(st.session_state.history):
                expander_title = f"{rec['mode']} @ {rec['timestamp']} (Length: {rec['length']})"
                with st.expander(expander_title):
                    st.text_area("Original", value=rec['original'], disabled=True, height=100)
                    st.text_area("Enhanced", value=rec['enhanced'], disabled=True, height=100)
                    st.download_button(
                        "Download JSON", 
                        export_json(rec), 
                        file_name=f"enhancement_{rec['timestamp']}.json",
                        mime="application/json"
                    )
        else:
            st.caption("Enhancement history is empty.")