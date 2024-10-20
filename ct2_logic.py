import pyaudio
import wave
import os
import tempfile
import threading
from faster_whisper import WhisperModel
import yaml
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QClipboard

class VoiceRecorder:
    def __init__(self, window, format=pyaudio.paInt16, channels=1, rate=44100, chunk=1024):
        self.format, self.channels, self.rate, self.chunk = format, channels, rate, chunk
        self.window = window
        self.is_recording, self.frames = False, []
        self.load_settings()

    def load_settings(self):
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
                if "device_type" not in config:
                    config["device_type"] = "cuda"
                if "model_name" not in config:
                    config["model_name"] = "large-v3"
                if "quantization_type" not in config:
                    config["quantization_type"] = "int8-float16"

                self.update_model(config["model_name"], config["quantization_type"], config["device_type"])
        except FileNotFoundError:
            self.update_model("base.en", "int8", "cpu")

    def save_settings(self, model_name, quantization_type, device_type):
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            config = {}

        config["model_name"] = model_name
        config["quantization_type"] = quantization_type
        config["device_type"] = device_type

        with open("config.yaml", "w") as f:
            yaml.safe_dump(config, f)

    def update_model(self, model_name, quantization_type, device_type):
        if model_name == "large-v3":
            model_str = "Systran/faster-whisper-large-v3"
            self.model = WhisperModel(model_str, device=device_type, compute_type=quantization_type, cpu_threads=26)
        else:
            model_str = f"ctranslate2-4you/whisper-{model_name}-ct2-{quantization_type}" 
            self.model = WhisperModel(model_str, device=device_type, compute_type=quantization_type, cpu_threads=26)
        self.window.update_status(f"Model updated to {model_name} with {quantization_type} quantization on {device_type} device")
        self.save_settings(model_name, quantization_type, device_type)
    
    def transcribe_audio(self, audio_file):
        segments, _ = self.model.transcribe(audio_file)
        transcription = "\n".join([segment.text for segment in segments])
        return transcription

    def translate_audio(self, audio_file):
        segments, _ = self.model.transcribe(audio_file, task="translate", language="en")
        translation = "\n".join([segment.text for segment in segments])
        return translation

    def record_audio(self):
        self.window.update_status("Recording...")
        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
            [self.frames.append(stream.read(self.chunk)) for _ in iter(lambda: self.is_recording, False)]
            stream.stop_stream()
            stream.close()
        finally:
            p.terminate()


    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            threading.Thread(target=self.record_audio).start()