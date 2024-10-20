from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QHBoxLayout, QGroupBox, QTextEdit
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeySequence, QShortcut
from ct2_logic import VoiceRecorder
import yaml
import pyaudio
import wave
import os
import tempfile
from faster_whisper import WhisperModel

class MyWindow(QWidget):
    def __init__(self, cuda_available=False):
        super().__init__()

        layout = QVBoxLayout(self)

        # テキストウィンドウ1 (Transcription)
        self.text_edit1 = QTextEdit(self)
        layout.addWidget(self.text_edit1)

        # テキストウィンドウ2 (Translation)
        self.text_edit2 = QTextEdit(self)
        layout.addWidget(self.text_edit2)

        self.status_label = QLabel('', self)
        layout.addWidget(self.status_label)

        self.recorder = VoiceRecorder(self)

        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
                model = config.get("model_name", "base.en")
                quantization = config.get("quantization_type", "int8")
                device = config.get("device_type", "auto")
                self.supported_quantizations = config.get("supported_quantizations", {"cpu": [], "cuda": []})
        except FileNotFoundError:
            model, quantization, device = "base.en", "int8", "cpu"
            self.supported_quantizations = {"cpu": [], "cuda": []}

        self.recorder.update_model(model, quantization, device)

        for text, callback in [("Record", self.recorder.start_recording),
                            ("Stop and Copy Transcription to Clipboard", self.save_and_transcribe),
                            ("Stop and Copy Translation to Clipboard", self.save_and_translate)]:

            button = QPushButton(text, self)
            button.clicked.connect(callback)
            layout.addWidget(button)
            

        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()

        h_layout = QHBoxLayout()

        model_label = QLabel('Model')
        h_layout.addWidget(model_label)
        self.model_dropdown = QComboBox(self)
        self.model_dropdown.addItems(["tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "medium.en", "large-v2", "large-v3"])
        h_layout.addWidget(self.model_dropdown)
        self.model_dropdown.setCurrentText(model)

        quantization_label = QLabel('Quantization')
        h_layout.addWidget(quantization_label)
        self.quantization_dropdown = QComboBox(self)
        h_layout.addWidget(self.quantization_dropdown)

        device_label = QLabel('Device')
        h_layout.addWidget(device_label)
        self.device_dropdown = QComboBox(self)

        if cuda_available:
            self.device_dropdown.addItems(["cpu", "cuda"])
        else:
            self.device_dropdown.addItems(["cpu"])

        h_layout.addWidget(self.device_dropdown)
        self.device_dropdown.setCurrentText(device)

        settings_layout.addLayout(h_layout)

        update_model_btn = QPushButton("Update Settings", self)
        update_model_btn.clicked.connect(self.update_model)
        settings_layout.addWidget(update_model_btn)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        self.setFixedSize(425, 400)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.device_dropdown.currentTextChanged.connect(self.update_quantization_options)
        self.update_quantization_options(quantization)
        self.hotkey = QKeySequence(Qt.Key_F9)  # 録音のホットキーを設定 (この例ではF9キー)
        self.hotkey_shortcut = QShortcut(self.hotkey, self)
        self.hotkey_shortcut.activated.connect(self.on_hotkey_activated)

    def on_key_press(self, key):
        if key == self.hotkey:
            if not self.recorder.is_recording:
                self.recorder.start_recording()
            else:
                self.recorder.save_audio()

    def update_quantization_options(self, current_quantization):
        self.quantization_dropdown.clear()
        options = self.supported_quantizations.get(self.device_dropdown.currentText(), [])
        self.quantization_dropdown.addItems(options)
        if current_quantization in options:
            self.quantization_dropdown.setCurrentText(current_quantization)
        else:
            self.quantization_dropdown.setCurrentText("")

    def update_model(self):
        self.recorder.update_model(self.model_dropdown.currentText(), self.quantization_dropdown.currentText(), self.device_dropdown.currentText())

    def update_status(self, text):
        self.status_label.setText(text)

    def closeEvent(self, event):
        self.keyboard_listener.stop()
        super().closeEvent(event)
        
    def on_hotkey_activated(self):
        if not self.recorder.is_recording:
            self.recorder.start_recording()
        else:
            self.recorder.save_audio()

    def save_and_transcribe(self):
        self.recorder.is_recording = False
        temp_filename = tempfile.mktemp(suffix=".wav")
        with wave.open(temp_filename, "wb") as wf:
            wf.setnchannels(self.recorder.channels)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.recorder.format))
            wf.setframerate(self.recorder.rate)
            wf.writeframes(b"".join(self.recorder.frames))

        transcription = self.recorder.transcribe_audio(temp_filename)
        translation = self.recorder.translate_audio(temp_filename)

        self.text_edit1.setPlainText(transcription)
        self.text_edit2.setPlainText(translation)

        clipboard = QApplication.clipboard()
        clipboard.setText(transcription)

        os.remove(temp_filename)
        self.recorder.frames.clear()
        self.update_status("Audio saved, transcribed and translated")

    def save_and_translate(self):
        self.recorder.is_recording = False
        temp_filename = tempfile.mktemp(suffix=".wav")
        with wave.open(temp_filename, "wb") as wf:
            wf.setnchannels(self.recorder.channels)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.recorder.format))
            wf.setframerate(self.recorder.rate)
            wf.writeframes(b"".join(self.recorder.frames))

        transcription = self.recorder.transcribe_audio(temp_filename)
        translation = self.recorder.translate_audio(temp_filename)

        self.text_edit1.setPlainText(transcription)
        self.text_edit2.setPlainText(translation)

        clipboard = QApplication.clipboard()
        clipboard.setText(translation)

        os.remove(temp_filename)
        self.recorder.frames.clear()
        self.update_status("Audio saved and translated to Japanese")