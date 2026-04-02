# Codex AI Screen Tutor

An AI-powered screen tutoring assistant that analyzes your screen using Google Gemini and provides instant, contextual help via a floating overlay window.

## Features

- **Hotkey Capture**: Press `Ctrl+Shift+S` anywhere to capture your screen
- **AI Analysis**: Sends the screenshot to Google Gemini 2.0 Flash (vision model) with a specialized tutor system prompt
- **Overlay Display**: Shows the AI response in a semi-transparent, always-on-top window
- **Follow-up Chat**: Type follow-up questions while the screenshot stays in context
- **System Prompt**: Uses `SCREEN_TUTOR_SYSTEM_PROMPT.md` to configure the AI tutor's behavior

## Project Structure

```
FirstEverProject/
├── main.py                        # Core application loop & hotkey listener
├── ui.py                          # Tkinter overlay window
├── screen_capture.py              # Screenshot logic (pyautogui)
├── api_client.py                  # Gemini API calls, loads system prompt
├── SCREEN_TUTOR_SYSTEM_PROMPT.md  # AI tutor system prompt
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
└── README.md                      # This file
```

## Setup

### 1. Prerequisites

- Python 3.9 or higher
- A Google Gemini API key ([get one here](https://aistudio.google.com/app/apikey))

### 2. Clone the Repository

```bash
git clone https://github.com/BearCat-Stack/FirstEverProject.git
cd FirstEverProject
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

On Linux, you may also need to install tkinter and screenshot dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk python3-pil scrot

# Fedora
sudo dnf install python3-tkinter
```

### 4. Configure API Key

Copy the example environment file and add your Gemini API key:

```bash
cp .env.example .env
```

Edit `.env` and replace `your_gemini_api_key_here` with your actual API key:

```
GEMINI_API_KEY=AIza...your_key_here
```

### 5. Run the App

```bash
python main.py
```

The application will start and register the global hotkey. A small overlay window will appear.

## Usage

1. **Capture & Analyze**: Press `Ctrl+Shift+S` at any time to take a screenshot. The AI tutor will analyze what's on your screen and display its response in the overlay.

2. **Follow-up Questions**: While the overlay is visible, type a follow-up question in the chat input box and press `Enter` or click `Send`. The AI remembers the context of the current screenshot.

3. **New Capture**: Press `Ctrl+Shift+S` again to take a new screenshot and start a fresh analysis session.

4. **Close/Hide**: Click the X button on the overlay to hide it. Press `Ctrl+Shift+S` again to bring it back with a new screenshot.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Screenshots | `pyautogui` |
| AI API | `google-generativeai` (Gemini 2.0 Flash) |
| UI Overlay | `tkinter` |
| Environment Vars | `python-dotenv` |
| Hotkeys | `keyboard` |

## Configuration

### System Prompt

The AI tutor's behavior is defined in `SCREEN_TUTOR_SYSTEM_PROMPT.md`. You can customize this file to change how the AI responds, its areas of expertise, tone, and response format.

### Overlay Appearance

You can customize the overlay window's appearance by editing the color constants at the top of `ui.py`:

```python
BG_COLOR = "#1e1e2e"      # Background (dark)
ACCENT_COLOR = "#89b4fa"  # Accent (blue)
WINDOW_ALPHA = 0.92       # Transparency (0.0-1.0)
```

## Troubleshooting

**`GEMINI_API_KEY not set` error**: Make sure you've created a `.env` file (not just `.env.example`) and added your API key.

**Hotkey not working on Linux**: The `keyboard` library requires root privileges on Linux. Run with `sudo python main.py` or configure your system to allow user-level keyboard hooks.

**`python3-tk` not found**: Install tkinter for your OS (see Setup step 3 above).

**Screenshot is black or empty**: On some systems, pyautogui may need additional permissions. On macOS, grant Screen Recording permission in System Preferences.

## License

MIT License - see LICENSE file for details.
