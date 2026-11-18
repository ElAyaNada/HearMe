# SignSpeak

SignSpeak is a real-time sign-language letter recognition demo built with
Streamlit, OpenCV, MediaPipe Hands, and a trained Random Forest model. The
dashboard shows the camera stream with hand landmarks, a bounding box, and the
predicted letter overlaid on the frame.

## Features

- In-browser webcam preview with start and stop controls
- Hand landmark tracking and sign prediction
- Adds a predicted letter after the sign remains steady for one second
- Recognized-text controls to clear, delete the last character, or add a space
- Camera, hand-detection, and current-letter status
- Recognized text retained in Streamlit session state

## Requirements

- Python 3.10–3.12
- A webcam
- The trained model at `assets/model.p`
- Webcam permission in the browser

Install the pinned and compatible dependencies from the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The requirements pin MediaPipe to 0.10.21 for its `solutions` API, NumPy below
2 for compatibility with the model and MediaPipe, and PyArrow below 21 for
Streamlit custom-component support.

## Run

From the project directory, with the virtual environment activated:

```powershell
python -m streamlit run app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`) and
allow webcam access. Use **Start** and **Stop** in the camera panel to control
the camera. Hold a sign steady for about one second to add its letter. Use the
text controls to edit the recognized output.

Browser camera access generally requires `localhost` or HTTPS. For a remote
deployment, configure HTTPS and the WebRTC network settings appropriate for
that environment.

## Project structure

```text
SignLanguageRecognition/
├── app.py
├── requirements.txt
└── assets/
    └── model.p
```

## Troubleshooting

- **MediaPipe `solutions` error:** Confirm the app is using this project's
  virtual environment and reinstall its dependencies:

  ```powershell
  python -m pip install -r requirements.txt
  ```

- **Webcam does not start:** Allow camera access in the browser, check that
  another application is not using the camera, and use `localhost` or HTTPS.
- **Wrong Python environment:** Run Streamlit through the active environment
  with `python -m streamlit run app.py`.
