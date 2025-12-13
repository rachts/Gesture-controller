# Gesture Media Controller

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
</p>

Control your media playback using hand gestures captured via webcam. Works with Spotify, VLC, YouTube, and any media application that responds to system media keys.

**Developed by Rachit**

---

## Features

- Real-time hand tracking using Google MediaPipe
- Intuitive gesture recognition for media control
- Visual feedback with heads-up display overlay
- FPS monitoring for performance tracking
- Gesture cooldowns to prevent accidental repeated triggers
- Smooth motion detection using moving average filtering

## Demo

| Gesture | Action |
|---------|--------|
| Pinch (Thumb + Index) | Play / Pause |
| Swipe Right | Next Track |
| Swipe Left | Previous Track |
| 3 Fingers (Thumb+Index+Middle) + Move Up | Volume Up |
| 3 Fingers (Thumb+Index+Middle) + Move Down | Volume Down |
| Fist | Mute |
| Open Palm (5 fingers) | Unmute |

## Requirements

- Python 3.10 or higher
- Webcam
- Windows / macOS / Linux

## Installation

1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/rachit/gesture-media-controller.git
   cd gesture-media-controller
   \`\`\`

2. Create a virtual environment (recommended):
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

3. Install dependencies:
   \`\`\`bash
   pip install -r scripts/gesture_media_player/requirements.txt
   \`\`\`

## Usage

Run the application:

\`\`\`bash
cd scripts/gesture_media_player
python main.py
\`\`\`

Press **Q** to quit the application.

## Project Structure

\`\`\`
gesture-media-controller/
├── scripts/
│   └── gesture_media_player/
│       ├── main.py                 # Main application entry point
│       ├── hand_tracker.py         # MediaPipe hand tracking module
│       ├── gesture_recognition.py  # Gesture detection logic
│       ├── media_controls.py       # System media key controls
│       ├── utils.py                # Utility functions and filters
│       └── requirements.txt        # Python dependencies
└── README.md                       # This file
\`\`\`

## Configuration

Adjust gesture sensitivity by modifying the parameters in `main.py`:

\`\`\`python
self.gesture_recognizer = GestureRecognizer(
    swipe_threshold=80,         # Horizontal pixels for swipe detection
    pinch_threshold=40,         # Maximum pixels between fingers for pinch
    volume_y_threshold=0.03     # Normalized Y movement threshold for volume
)
\`\`\`

## Troubleshooting

### Webcam not detected
- Ensure your webcam is properly connected
- Close other applications that might be using the camera
- Try changing `camera_id` parameter in `main.py` (0, 1, 2, etc.)

### Gestures not recognized
- Ensure adequate lighting in your environment
- Keep your hand fully within the camera frame
- Position your hand at arm's length from the camera
- Try adjusting the threshold values in configuration

### Media keys not working
- Some applications may not respond to system media keys
- Test with Spotify, VLC, or Windows Media Player
- Ensure the media application window is active

## Dependencies

- opencv-python - Computer vision and image processing
- mediapipe - Hand landmark detection
- pyautogui - System keyboard simulation
- numpy - Numerical computations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Google MediaPipe](https://mediapipe.dev/) for the hand tracking solution
- [OpenCV](https://opencv.org/) for computer vision capabilities
- [PyAutoGUI](https://pyautogui.readthedocs.io/) for keyboard automation

---

<p align="center">
  Made with care by <strong>Rachit</strong>
</p>
