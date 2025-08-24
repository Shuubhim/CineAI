import os
import json
from typing import List, Dict, Optional, Tuple, Union, Any
from openai import OpenAI
import streamlit as st
import requests
import whisper


def transcribe_audio_with_whisper(audio_path: str, model_name: str = "base") -> Optional[List[Dict[str, Union[str, float]]]]:
    """Transcribes audio using the locally installed Whisper model.
    
    This function loads the specified Whisper model and transcribes the provided audio file
    with word-level timestamps. It handles the transcription process and returns
    a structured list of words with their timing information.
    
    Args:
        audio_path: Path to the audio file to be transcribed.
        model_name: Name of the Whisper model to use ('base', 'small', 'medium').
            Defaults to 'base'.
        
    Returns:
        A list of dictionaries containing word information with keys:
        - 'text': The transcribed word
        - 'start': Start time of the word in seconds
        - 'end': End time of the word in seconds
        Returns None if transcription fails.
        
    Raises:
        Exception: If there's an error during model loading or transcription.
    """
    try:
        st.info(f"Loading local Whisper model ({model_name})... (This might take a moment on first run)")
        model = whisper.load_model(model_name)
        st.info("Model loaded. Starting transcription...")
        result = model.transcribe(audio_path, word_timestamps=True)
        
        words_with_timestamps = []
        for segment in result["segments"]:
            for word_info in segment["words"]:
                words_with_timestamps.append({
                    "text": word_info["word"],
                    "start": word_info["start"],
                    "end": word_info["end"]
                })
        return words_with_timestamps
    except Exception as e:
        st.error(f"An error occurred during local transcription: {e}")
        st.info("Please ensure you have installed PyTorch and ffmpeg correctly.")
        return None


def parse_structured_script(text: str) -> List[Dict[str, Union[str, int]]]:
    """Parses a structured script for dialogue, b-roll, and overlay cues.
    
    This function parses a text script that contains structured sections marked
    with keywords like 'dialogue:', 'b-roll:', and 'overlay:'. It extracts the
    content and links b-roll and overlay cues to their corresponding dialogue
    sections by index.
    
    Args:
        text: The raw script text containing structured sections.
        
    Returns:
        A list of dictionaries representing script cues, each containing:
        - 'type': The cue type ('dialogue', 'b-roll', or 'overlay')
        - 'content': The actual content of the cue
        - 'dialogue_index': Index linking b-roll/overlay to dialogue (0-based)
        
    Example:
        Input text:
        "dialogue: Hello world
         b-roll: [showing computer screen]
         dialogue: How are you?"
        
        Returns:
        [
            {'type': 'dialogue', 'content': 'Hello world', 'dialogue_index': 0},
            {'type': 'b-roll', 'content': '[showing computer screen]', 'dialogue_index': 0},
            {'type': 'dialogue', 'content': 'How are you?', 'dialogue_index': 1}
        ]
    """
    script_cues = []
    lines = text.split('\n')
    dialogue_indices = [i for i, line in enumerate(lines) if line.strip().lower() == 'dialogue:']
    dialogue_count = 0
    for i, line in enumerate(lines):
        clean_line = line.strip().lower()
        if clean_line in ['dialogue:', 'b-roll:', 'overlay:']:
            cue_type = clean_line.replace(':', '')
            if i + 1 < len(lines):
                content = lines[i+1].strip()
                if content:
                    cue_data = {'type': cue_type, 'content': content}
                    if cue_type == 'dialogue':
                        cue_data['dialogue_index'] = dialogue_count
                        dialogue_count += 1
                    else:
                        last_dialogue_index = -1
                        for idx_dialogue_line in dialogue_indices:
                            if idx_dialogue_line < i:
                                last_dialogue_index = dialogue_indices.index(idx_dialogue_line)
                        cue_data['dialogue_index'] = last_dialogue_index
                    script_cues.append(cue_data)
    return script_cues


@st.cache_data
def get_ai_cut_list(perfect_script_sentences: List[str], 
                    messy_transcript_words: List[Dict[str, Union[str, float]]]) -> Optional[str]:
    """Uses AI to find 'good takes' by comparing a perfect script to a messy transcript.
    
    This function sends the perfect script sentences and messy transcript words to an
    AI service to identify the best segments (good takes) from the transcript that
    match the perfect script. The AI returns JSON-formatted cut points with timing
    information.
    
    Args:
        perfect_script_sentences: List of sentences from the perfect script.
        messy_transcript_words: List of dictionaries containing transcribed words
            with timestamps (from transcribe_audio_with_whisper).
            
    Returns:
        A JSON string containing the AI-generated cut list with format:
        [
            {"start": float, "end": float, "text": str},
            ...
        ]
        Returns None if the AI call fails.
        
    Note:
        This function uses OpenRouter API with GPT-OSS-20B model for processing.
        Requires OPENROUTER_API_KEY to be set in Streamlit secrets.
    """
    system_prompt = """
    You are an expert AI video editor. Your task is to find the start and end times of "good takes" from a messy, timestamped transcript by matching it against a perfect script.
    Your goal is to return a valid JSON list of objects. Each object must represent a sentence from the perfect script and contain three keys:
    1. "start": The start time of the first word in the matching segment.
    2. "end": The end time of the last word in the matching segment.
    3. "text": The sentence from the perfect script.
    Example of required output:
    [
      {"start": 45.2, "end": 51.7, "text": "Today we will review the new camera."},
      {"start": 92.5, "end": 98.1, "text": "It has amazing features."}
    ]
    RULES:
    - Match each sentence from the perfect script to a segment in the messy transcript.
    - ENSURE the output is ONLY the raw JSON list. DO NOT write any explanation or conversational text. The response MUST begin with a [ character.
    """
    user_prompt = f"PERFECT SCRIPT: {json.dumps(perfect_script_sentences)}\n\nMESSY TIMESTAMPED TRANSCRIPT: {json.dumps(messy_transcript_words)}"
    try:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"])
        completion = client.chat.completions.create(
          model="openai/gpt-oss-20b:free",
          messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
          ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling AI Alignment API: {e}")
        return None


def create_text_clip(text: str, 
                    duration: float, 
                    video_size: Tuple[int, int], 
                    font_size_ratio: int, 
                    position: Union[str, Tuple[str, str]]) -> Any:
    """Creates a MoviePy TextClip with specified styling and positioning.
    
    This function creates a text overlay clip that can be composited onto video.
    The text is styled with white color, black stroke, and Arial font. The font
    size is calculated based on the video width and the provided ratio.
    
    Args:
        text: The text content to display.
        duration: Duration of the text clip in seconds.
        video_size: Tuple of (width, height) of the video.
        font_size_ratio: Divisor for calculating font size (video_width / ratio).
        position: Position of the text on screen. Can be a string ('center', 'top', etc.)
            or a tuple of strings for x,y positioning ('center', 'bottom').
            
    Returns:
        A MoviePy TextClip object configured with the specified parameters.
        
    Note:
        This function requires ImageMagick to be installed on the system for
        text rendering capabilities.
    """
    from moviepy.editor import TextClip
    video_width, _ = video_size
    font_size = int(video_width / font_size_ratio)
    return TextClip(
        text, fontsize=font_size, color='white', font='Arial',
        stroke_color='black', stroke_width=2, method='caption',
        size=(video_width*0.8, None)
    ).set_pos(position).set_duration(duration)


def assemble_video(cut_list: List[Dict[str, Union[float, str]]], 
                  original_video_path: str, 
                  script_cues: List[Dict[str, Union[str, int]]], 
                  b_roll_files: Dict[str, str], 
                  b_roll_keyword_map: Dict[str, List[str]], 
                  logo_file: Optional[str], 
                  add_subtitles: bool, 
                  add_b_roll: bool, 
                  add_logo: bool, 
                  add_overlays: bool) -> Optional[str]:
    """Assembles the final video from a cut list and adds all requested features.
    
    This function takes the AI-generated cut list and assembles a final video by:
    1. Extracting the specified segments from the original video
    2. Optionally replacing segments with B-roll footage based on keyword matching
    3. Adding subtitles, overlays, and logo as requested
    4. Concatenating all segments into a final video file
    
    Args:
        cut_list: List of dictionaries containing cut information with keys:
            'start', 'end', 'text' (from AI analysis).
        original_video_path: Path to the original video file.
        script_cues: List of script cues from parse_structured_script().
        b_roll_files: Dictionary mapping B-roll filenames to their file paths.
        b_roll_keyword_map: Dictionary mapping B-roll filenames to lists of keywords.
        logo_file: Optional path to the logo image file.
        add_subtitles: Whether to add subtitle overlays to the video.
        add_b_roll: Whether to replace segments with B-roll footage.
        add_logo: Whether to add a logo overlay to the final video.
        add_overlays: Whether to add script overlay text.
        
    Returns:
        Path to the output video file ("CineAI_Final_Output.mp4") if successful,
        None if assembly fails or no valid clips are found.
        
    Note:
        The output video is encoded using H.264 codec with AAC audio, using 8 threads
        for processing. The logo is positioned in the top-right corner and scaled
        to 1/12th of the video height.
    """
    from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip
    
    main_clip = VideoFileClip(original_video_path)
    overlay_map = {cue['dialogue_index']: cue['content'] for cue in script_cues if cue['type'] == 'overlay'}
    
    final_clips = []
    for i, cut in enumerate(cut_list):
        try:
            start_time, end_time, dialogue_text = cut['start'], cut['end'], cut['text']
            if end_time > start_time:
                clip_duration = end_time - start_time
                current_clip = main_clip.subclip(start_time, end_time)
                
                if add_b_roll and b_roll_keyword_map:
                    matched_b_roll_path = None
                    for filename, keywords in b_roll_keyword_map.items():
                        for keyword in keywords:
                            if keyword and keyword in dialogue_text.lower():
                                matched_b_roll_path = b_roll_files.get(filename)
                                break
                        if matched_b_roll_path: break
                    if matched_b_roll_path:
                        try:
                            b_roll_clip = VideoFileClip(matched_b_roll_path).set_duration(clip_duration)
                            b_roll_clip = b_roll_clip.resize(height=main_clip.h).set_audio(current_clip.audio)
                            current_clip = b_roll_clip
                        except Exception as b_roll_error:
                            print(f"⚠️ Warning: Failed to process B-roll clip '{matched_b_roll_path}': {b_roll_error}")
                            # Continue with original clip if B-roll fails
                
                layers = [current_clip]
                if add_subtitles:
                    try:
                        layers.append(create_text_clip(dialogue_text, clip_duration, main_clip.size, 40, ('center', 'bottom')))
                    except Exception as subtitle_error:
                        print(f"⚠️ Warning: Failed to create subtitle for clip {i}: {subtitle_error}")
                if add_overlays and i in overlay_map:
                    try:
                        layers.append(create_text_clip(overlay_map[i], clip_duration, main_clip.size, 25, 'center'))
                    except Exception as overlay_error:
                        print(f"⚠️ Warning: Failed to create overlay for clip {i}: {overlay_error}")
                
                try:
                    final_clips.append(CompositeVideoClip(layers))
                except Exception as composite_error:
                    print(f"⚠️ Warning: Failed to composite clip {i}: {composite_error}")
                    # Try to add just the base clip without overlays
                    try:
                        final_clips.append(current_clip)
                    except Exception as fallback_error:
                        print(f"⚠️ Warning: Failed to add clip {i} even without overlays: {fallback_error}")
                        
        except Exception as clip_error:
            print(f"⚠️ Warning: Failed to process clip {i} (start: {cut.get('start', 'unknown')}, end: {cut.get('end', 'unknown')}): {clip_error}")
            continue

    if not final_clips: 
        main_clip.close()
        print("⚠️ Warning: No valid clips were processed. Cannot create final video.")
        return None
    
    try:
        final_video = concatenate_videoclips(final_clips)
    except Exception as concat_error:
        print(f"⚠️ Warning: Failed to concatenate video clips: {concat_error}")
        main_clip.close()
        return None

    if add_logo and logo_file:
        try:
            logo = (ImageClip(logo_file).set_duration(final_video.duration)
                    .resize(height=int(main_clip.h / 12)).set_pos(('right', 'top')))
            final_video = CompositeVideoClip([final_video, logo])
        except Exception as logo_error:
            print(f"⚠️ Warning: Failed to add logo to video: {logo_error}")
            # Continue without logo if it fails
        
    output_path = "CineAI_Final_Output.mp4"
    try:
        final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', threads=8)
        main_clip.close()
        return output_path
    except Exception as write_error:
        print(f"⚠️ Warning: Failed to write final video file: {write_error}")
        main_clip.close()
        return None