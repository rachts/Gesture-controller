# Gesture-Based Media Player Controller

Control your media playback using hand gestures captured via webcam. Works with Spotify, VLC, YouTube, and any media application that responds to system media keys.

## Features

- **Real-time hand tracking** using MediaPipe
- **Gesture recognition** for media control
- **Visual feedback** with HUD overlay
- **FPS monitoring** for performance tracking
- **Gesture cooldowns** to prevent repeated triggers
- **Smooth motion** using moving average filtering

## Supported Gestures

| Gesture | Action |
|---------|--------|
| Pinch (Thumb + Index) | Play / Pause |
| Swipe Right | Next Track |
| Swipe Left | Previous Track |
| Hand Move Up | Volume Up |
| Hand Move Down | Volume Down |
| Fist | Mute |
| Open Palm (5 fingers) | Resume / Unmute |

## Installation

1. **Create a virtual environment** (recommended):
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

2. **Install dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

## Usage

Run the main script:

\`\`\`bash
python main.py
\`\`\`

Press **Q** to quit the application.

## Project Structure

\`\`\`
gesture_media_player/
├── main.py                 # Main application entry point
├── hand_tracker.py         # MediaPipe hand tracking module
├── gesture_recognition.py  # Gesture detection logic
├── media_controls.py       # System media key controls
├── utils.py               # Utility functions and filters
├── requirements.txt       # Python dependencies
└── README.md             # This file
\`\`\`

## Requirements

- Python 3.10+
- Webcam
- Windows OS (for media key support)

## Configuration

You can adjust sensitivity in `main.py`:

\`\`\`python
self.gesture_recognizer = GestureRecognizer(
    swipe_threshold=80,      # Horizontal pixels for swipe
    pinch_threshold=40,      # Max pixels for pinch detection
    volume_threshold=30      # Vertical pixels for volume
)
\`\`\`

## Troubleshooting

**Webcam not detected:**
- Check if webcam is connected
- Close other applications using the camera
- Try changing `camera_id` in main.py

**Gestures not recognized:**
- Ensure good lighting
- Keep hand within frame
- Adjust threshold values
- Keep hand at arm's length from camera

**Media keys not working:**
- Some applications may not respond to media keys
- Try with Spotify or VLC
- Ensure the media application is focused

## License

MIT License - Feel free to use and modify!
