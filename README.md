# 🎬 CineAI – Transcription-Based Video Editor

CineAI is an intelligent video editing application that uses AI-powered transcription and script alignment to automatically create professional videos from raw footage. By comparing a perfect script to a messy transcript, CineAI identifies the best takes and assembles them into a polished final video.

## ✨ Features

- **AI-Powered Transcription**: Uses OpenAI Whisper for accurate speech-to-text conversion
- **Smart Script Alignment**: Automatically matches perfect script lines to the best takes in raw footage
- **Proxy Workflow**: Creates low-resolution proxies for faster processing while maintaining original quality
- **B-Roll Integration**: Automatically inserts relevant B-roll footage based on keyword matching
- **Professional Overlays**: Adds subtitles, script overlays, and logo branding
- **Multiple Whisper Models**: Choose from base, small, or medium models for speed vs. accuracy trade-offs
- **Robust Error Handling**: Continues processing even if individual clips fail
- **Cloud-Ready**: CPU-compatible dependencies for easy deployment

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd project
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 🔧 Required Setup

### FFmpeg Installation

CineAI requires FFmpeg for video processing. Install it based on your operating system:

**Windows**:
1. Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your system PATH

**macOS**:
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install ffmpeg
```

### ImageMagick Installation

ImageMagick is required for text overlays and logo rendering:

**Windows**:
1. Download from [https://imagemagick.org/script/download.php](https://imagemagick.org/script/download.php)
2. Install and ensure "Add to system PATH" is checked

**macOS**:
```bash
brew install imagemagick
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install imagemagick
```

## ⚙️ Configuration

### API Key Setup

1. **Get an OpenRouter API Key**:
   - Visit [https://openrouter.ai/](https://openrouter.ai/)
   - Create an account and generate an API key

2. **Create Streamlit secrets file**:
   ```bash
   mkdir .streamlit
   ```

3. **Create `.streamlit/secrets.toml`**:
   ```toml
   OPENROUTER_API_KEY = "your-api-key-here"
   ```

## 📖 Usage

### 1. Prepare Your Assets

- **Raw Video**: Upload your unedited video file (MP4, MOV)
- **Perfect Script**: Create a text file with structured dialogue sections:
  ```
  dialogue: Hello, welcome to our tutorial.
  b-roll: [showing computer screen]
  dialogue: Today we'll learn about video editing.
  overlay: [Key Point: Video Editing Basics]
  ```
- **B-Roll Clips** (optional): Upload additional video clips
- **Logo** (optional): Upload a PNG logo for branding

### 2. Configure Settings

In the sidebar, you can:
- **Select Whisper Model**: Choose between 'base', 'small', or 'medium'
- **Enable Features**: Toggle subtitles, overlays, B-roll, and logo
- **Map B-Roll Keywords**: Associate B-roll clips with specific keywords

### 3. Process and Assemble

1. Upload your assets
2. The app will create a proxy file for faster processing
3. AI will transcribe the audio and align it with your script
4. Review the AI-generated cut list
5. Click "Assemble Final Video" to render the final high-quality output

### 4. Workflow Details

- **Proxy Generation**: Creates a 480px wide proxy for faster analysis
- **Transcription**: Uses the selected Whisper model for speech recognition
- **AI Alignment**: Matches perfect script lines to the best takes
- **Final Assembly**: Uses original high-quality video with proxy-generated timestamps
- **Cleanup**: Automatically removes temporary files after processing

## 🔍 Troubleshooting

### Common Issues

**"FFmpeg not found" Error**:
- Ensure FFmpeg is installed and added to your system PATH
- Restart your terminal/IDE after installation

**"ImageMagick not found" Error**:
- Install ImageMagick and ensure it's in your system PATH
- On Windows, check that the installation added it to PATH

**"OpenAI API Error"**:
- Verify your OpenRouter API key is correct in `.streamlit/secrets.toml`
- Check your API key balance on OpenRouter

**"No dialogue lines found" Warning**:
- Ensure your script file contains sections marked with `dialogue:`
- Check that the script file is not empty

**"Failed to create proxy file" Error**:
- Verify your video file is not corrupted
- Ensure sufficient disk space for temporary files

**"B-Roll processing failed" Warning**:
- Check that B-roll video files are not corrupted
- Verify file formats are supported (MP4, MOV)

### Performance Tips

- Use the 'base' Whisper model for faster processing
- Keep video files under 1GB for optimal performance
- Ensure adequate RAM (8GB+ recommended)
- Use SSD storage for faster file operations

### Memory Management

- The app automatically cleans up temporary files
- Large videos may require more memory during processing
- Consider processing videos in smaller segments if memory is limited

## 🛠️ Technical Details

- **Framework**: Streamlit for web interface
- **AI Models**: OpenAI Whisper for transcription, GPT-OSS-20B for alignment
- **Video Processing**: MoviePy with FFmpeg backend
- **Text Rendering**: ImageMagick for overlays and subtitles
- **Deployment**: CPU-compatible PyTorch versions for cloud deployment

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For support and questions, please open an issue on the project repository.
