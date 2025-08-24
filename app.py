import streamlit as st
import os
import tempfile
import json
from moviepy.editor import VideoFileClip
from utils import (
    parse_structured_script, 
    transcribe_audio_with_whisper,
    get_ai_cut_list,
    assemble_video
)

st.set_page_config(page_title="CineAI - Pro Editor", page_icon="🎬", layout="wide")
st.title("🎬 CineAI – Transcription-Based Editor")

# Initialize session state variables
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'cut_list' not in st.session_state:
    st.session_state.cut_list = None
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'proxy_path' not in st.session_state: # NEW: To store the proxy video path
    st.session_state.proxy_path = None
if 'script_cues' not in st.session_state:
    st.session_state.script_cues = None
if 'b_roll_keyword_map' not in st.session_state:
    st.session_state.b_roll_keyword_map = {}

with st.sidebar:
    st.header("Instructions")
    st.write("1. Upload assets.")
    st.write("2. Configure features & map B-Roll.")
    st.write("3. App will transcribe and align.")
    st.write("4. Click Assemble to render.")
    st.divider()
    st.header("⚙️ Features")
    add_subtitles = st.checkbox("Add Subtitles", value=True)
    add_overlays = st.checkbox("Add Script Overlays", value=True)
    add_b_roll = st.checkbox("Add B-Roll", value=True)
    add_logo = st.checkbox("Add Logo", value=False)
    st.divider()
    st.header("🎤 Whisper Model")
    whisper_model = st.selectbox(
        "Select Whisper Model Size",
        options=['base', 'small', 'medium'],
        index=1,  # Default to 'small' for a good balance
        help="Larger models are more accurate but slower and use more memory."
    )

st.subheader("1. Upload Assets")
col1, col2 = st.columns(2)
with col1:
    uploaded_video = st.file_uploader("Raw Video (with mistakes)", type=['mp4', 'mov'])
    uploaded_script = st.file_uploader("Perfect Script File", type=['txt'])
with col2:
    uploaded_logo = st.file_uploader("Logo Image", type=['png'])
    uploaded_b_roll_files = st.file_uploader("B-Roll Clips", type=['mp4', 'mov'], accept_multiple_files=True)

if uploaded_b_roll_files:
    st.subheader("2. Map B-Roll Keywords")
    for uploaded_file in uploaded_b_roll_files:
        keywords = st.text_input(f"Keywords for `{uploaded_file.name}`", key=uploaded_file.name)
        if keywords:
            st.session_state.b_roll_keyword_map[uploaded_file.name] = [k.strip().lower() for k in keywords.split(',')]

# --- Main Processing Logic ---
if uploaded_video and uploaded_script and not st.session_state.processing_complete:
    st.divider()
    st.subheader("3. AI Processing")

    # Input validation for script file
    script_text = uploaded_script.read().decode("utf-8")
    if not script_text.strip():
        st.warning("⚠️ The uploaded script file is empty. Please upload a valid script file.")
        st.stop()
    
    # Parse script and validate dialogue lines
    st.session_state.script_cues = parse_structured_script(script_text)
    perfect_sentences = [cue['content'] for cue in st.session_state.script_cues if cue['type'] == 'dialogue']
    
    if not perfect_sentences:
        st.warning("⚠️ No dialogue lines found in the script. Please ensure your script contains 'dialogue:' sections.")
        st.stop()
    
    st.success(f"✅ Perfect script parsed! Found {len(perfect_sentences)} dialogue lines.")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
        tfile.write(uploaded_video.read())
        st.session_state.video_path = tfile.name

    # --- PROXY FILE GENERATION FOR PERFORMANCE ---
    with st.spinner("Creating a low-resolution proxy for faster analysis..."):
        try:
            clip = VideoFileClip(st.session_state.video_path)
            # Create a proxy with a width of 480 pixels for faster processing
            proxy = clip.resize(width=480)
            proxy_path = "temp_proxy_video.mp4"
            proxy.write_videofile(proxy_path, codec="libx264", audio_codec="aac", logger=None)
            st.session_state.proxy_path = proxy_path
            clip.close()
            proxy.close()
            st.success("✅ Proxy file created for faster processing.")
        except Exception as e:
            st.error(f"Failed to create proxy file: {e}")
            st.stop()

    with st.spinner(f"Extracting audio and transcribing with '{whisper_model}' model (this can take time)..."):
        # Use the proxy file for faster audio extraction and transcription
        video_clip = VideoFileClip(st.session_state.proxy_path)
        audio_path = "temp_audio.mp3"
        video_clip.audio.write_audiofile(audio_path, logger=None)
        transcription_words = transcribe_audio_with_whisper(audio_path, whisper_model)
        video_clip.close()
        os.remove(audio_path)
    
    if not transcription_words:
        st.error("Audio transcription failed. Cannot proceed.")
        st.stop()
    st.success("✅ Audio transcription complete!")

    with st.spinner("AI is analyzing the transcript to find the 'good takes'..."):
        ai_response = get_ai_cut_list(perfect_sentences, transcription_words)
        if ai_response:
            try:
                start_index = ai_response.find('[')
                end_index = ai_response.rfind(']')
                json_string = ai_response[start_index : end_index + 1]
                st.session_state.cut_list = json.loads(json_string)
                st.session_state.processing_complete = True
                st.rerun()
            except Exception as e:
                st.error(f"Could not parse AI cut list. Error: {e}")
                st.write("AI Response:", ai_response)
        else:
            st.error("AI alignment failed. Cannot proceed.")

# --- Display Results and Assemble Button ---
if st.session_state.processing_complete:
    st.subheader("3. AI Processing Results")
    st.success("✅ AI alignment of good takes complete!")
    st.json(st.session_state.cut_list)
        
    st.divider()
    st.subheader("4. Final Video Assembly")
    if st.button("🎬 Assemble Final Video from Good Takes"):
        b_roll_temp_paths, logo_path = {}, None
        for f in uploaded_b_roll_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1]) as tfile:
                tfile.write(f.read())
                b_roll_temp_paths[f.name] = tfile.name
        if uploaded_logo:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tfile:
                tfile.write(uploaded_logo.read())
                logo_path = tfile.name
        
        with st.spinner("Rendering final video from ORIGINAL high-quality source... This can take several minutes."):
            output_video_path = assemble_video(
                st.session_state.cut_list, st.session_state.video_path, st.session_state.script_cues, 
                b_roll_temp_paths, st.session_state.b_roll_keyword_map,
                logo_path, add_subtitles, add_b_roll, add_logo, add_overlays
            )
            if output_video_path:
                st.success("🎉 Video assembly complete!")
                st.video(output_video_path)
                # Clean up ALL temporary files
                os.remove(st.session_state.video_path)
                os.remove(st.session_state.proxy_path) # Clean up proxy file
                for p in b_roll_temp_paths.values(): os.remove(p)
                if logo_path: os.remove(logo_path)
                
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.button("Start New Project")
            else: st.error("Failed to assemble the video.")