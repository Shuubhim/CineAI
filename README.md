# 🎬 CineAI - Transcription-Based Video Editor

CineAI is an intelligent video editing application that uses AI-powered transcription and alignment to automatically create polished videos from raw footage. By comparing a perfect script against a messy transcript, CineAI identifies the best takes and assembles them into a professional final video with automatic subtitles, overlays, and B-roll integration.

## ✨ Features

- **🎤 Local Audio Transcription**: Uses OpenAI Whisper models (base/small/medium) for accurate speech-to-text conversion with word-level timestamps
- **🤖 AI-Powered Alignment**: Intelligent matching of perfect script sentences to messy transcript segments to find the best takes
- **📝 Automatic Subtitles**: Generates and overlays subtitles on the final video
- **🎬 B-Roll Integration**: Automatically inserts B-roll footage based on keyword matching with dialogue
- **📋 Script Overlays**: Adds text overlays from structured script cues
- **🏷️ Logo Branding**: Optional logo overlay in the top-right corner
- **⚡ Multiple Whisper Models**: Choose between base (fastest), small (balanced), or medium (most accurate) models
- **🛡️ Robust Error Handling**: Graceful degradation when individual components fail
- **🎨 Professional Output**: H.264 video with AAC audio, optimized for quality and compatibility

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/cineai.git
   cd cineai
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🔧 Required Setup

### FFmpeg Installation

CineAI requires FFmpeg for video processing. Install it based on your operating system:

**Windows:**
- Download from [FFmpeg official website](https://ffmpeg.org/download.html)
- Add FFmpeg to your system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### ImageMagick Installation

ImageMagick is required for text overlay rendering:

**Windows:**
- Download from [ImageMagick official website](https://imagemagick.org/script/download.php#windows)
- Ensure "Install legacy utilities" is checked during installation

**macOS:**
```bash
brew install imagemagick
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install imagemagick
```

## ⚙️ Configuration

### API Key Setup

1. **Get an OpenRouter API Key**:
   - Visit [OpenRouter](https://openrouter.ai/)
   - Create an account and generate an API key

2. **Create Streamlit secrets file**:
   ```bash
   mkdir .streamlit
   ```

3. **Create `.streamlit/secrets.toml`**:
   ```toml
   OPENROUTER_API_KEY = "your_openrouter_api_key_here"
   ```

   **⚠️ Important**: Never commit this file to version control. It's already included in `.gitignore`.

## 🎯 Usage

1. **Launch the application**:
   ```bash
   streamlit run app.py
   ```

2. **Upload your assets**:
   - **Raw Video**: Upload your video with mistakes/retakes
   - **Perfect Script**: Upload a text file with structured dialogue
   - **B-Roll Clips** (optional): Upload additional footage
   - **Logo** (optional): Upload a PNG logo image

3. **Configure settings** in the sidebar:
   - Choose Whisper model size
   - Enable/disable features (subtitles, overlays, B-roll, logo)
   - Map B-roll keywords

4. **Process and assemble**:
   - The app will transcribe your video
   - AI will align the script with the transcript
   - Click "Assemble Final Video" to generate the output

## 📋 Script Format

Your script file should follow this structured format:

```
dialogue: Hello, welcome to our tutorial.
b-roll: [showing computer screen]
overlay: Tutorial Introduction

dialogue: Today we'll learn about video editing.
b-roll: [showing editing software]
overlay: Main Topic
```

- **`dialogue:`** - The perfect script text to match against
- **`b-roll:`** - Description of B-roll footage (for keyword matching)
- **`overlay:`** - Text to display as overlay on the video

## 🏗️ Project Structure

```
cineai/
├── app.py              # Main Streamlit application
├── utils.py            # Core processing functions
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
├── README.md          # This file
└── assets/            # Font files and other assets
```

## 🔍 Technical Details

- **Transcription**: OpenAI Whisper with word-level timestamps
- **AI Alignment**: OpenRouter API with GPT-OSS-20B model
- **Video Processing**: MoviePy with H.264/AAC encoding
- **Text Rendering**: ImageMagick integration
- **Web Interface**: Streamlit

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

**Transcription fails:**
- Ensure FFmpeg is installed and in your PATH
- Check that PyTorch is properly installed
- Verify audio file format is supported

**Text overlays not rendering:**
- Ensure ImageMagick is installed
- Check that legacy utilities are enabled (Windows)

**AI alignment fails:**
- Verify your OpenRouter API key is correct
- Check internet connection
- Ensure script format is correct

**Video assembly fails:**
- Check available disk space
- Ensure video files are not corrupted
- Verify all dependencies are installed

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section above
2. Search existing issues in the repository
3. Create a new issue with detailed information about your problem

---

**Made with ❤️ for content creators who want to focus on creativity, not editing.**
