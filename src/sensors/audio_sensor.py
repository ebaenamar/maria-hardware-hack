"""
Módulo de captura y análisis de audio para PiCar-X
Utiliza Vosk para reconocimiento de voz
"""

import os
import json
import logging
import queue
import threading
from typing import Optional, Dict, List, Callable
import time

try:
    import pyaudio
    import vosk
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logging.warning("pyaudio o vosk no disponibles")

from config.settings import AUDIO_CONFIG


class AudioSensor:
    """
    Sensor de audio que captura y reconoce voz usando Vosk STT
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el sensor de audio
        
        Args:
            config: Configuración personalizada (usa AUDIO_CONFIG por defecto)
        """
        self.config = config or AUDIO_CONFIG
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.is_listening = False
        
        # Audio stream
        self.audio = None
        self.stream = None
        self.model = None
        self.recognizer = None
        
        # Threading
        self.audio_queue = queue.Queue()
        self.listen_thread = None
        
        # Callbacks
        self.on_speech_callback: Optional[Callable] = None
        self.on_wake_word_callback: Optional[Callable] = None
        
        # Estado
        self.last_transcription = ""
        self.wake_word_detected = False
    
    def start(self) -> bool:
        """
        Inicia el sistema de audio y carga el modelo Vosk
        
        Returns:
            True si se inició correctamente
        """
        if not AUDIO_AVAILABLE:
            self.logger.error("pyaudio o vosk no disponibles")
            return False
        
        try:
            # Verificar que existe el modelo
            model_path = self.config['vosk_model_path']
            if not os.path.exists(model_path):
                self.logger.error(f"Modelo Vosk no encontrado en: {model_path}")
                self.logger.info("Descarga modelos desde: https://alphacephei.com/vosk/models")
                return False
            
            # Cargar modelo Vosk
            self.logger.info(f"Cargando modelo Vosk desde: {model_path}")
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(
                self.model,
                self.config['sample_rate']
            )
            
            # Inicializar PyAudio
            self.audio = pyaudio.PyAudio()
            
            # Abrir stream de audio
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.config['channels'],
                rate=self.config['sample_rate'],
                input=True,
                frames_per_buffer=self.config['chunk_size'],
                stream_callback=self._audio_callback
            )
            
            self.is_running = True
            self.logger.info("Sensor de audio iniciado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al iniciar sensor de audio: {e}")
            return False
    
    def stop(self):
        """Detiene el sistema de audio"""
        self.is_running = False
        self.is_listening = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        self.logger.info("Sensor de audio detenido")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback para el stream de audio"""
        if self.is_listening:
            self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
    
    def start_listening(self, callback: Optional[Callable] = None):
        """
        Comienza a escuchar y transcribir audio
        
        Args:
            callback: Función a llamar cuando se detecte voz (recibe texto)
        """
        if not self.is_running:
            self.logger.warning("Sensor de audio no está iniciado")
            return
        
        self.is_listening = True
        self.on_speech_callback = callback
        
        # Iniciar thread de procesamiento
        if self.listen_thread is None or not self.listen_thread.is_alive():
            self.listen_thread = threading.Thread(target=self._process_audio)
            self.listen_thread.daemon = True
            self.listen_thread.start()
        
        self.logger.info("Escuchando audio...")
    
    def stop_listening(self):
        """Detiene la escucha de audio"""
        self.is_listening = False
        self.logger.info("Escucha de audio detenida")
    
    def _process_audio(self):
        """Procesa el audio del queue y realiza reconocimiento"""
        silence_start = None
        
        while self.is_running:
            if not self.is_listening:
                time.sleep(0.1)
                continue
            
            try:
                # Obtener audio del queue
                data = self.audio_queue.get(timeout=0.5)
                
                # Procesar con Vosk
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').strip()
                    
                    if text:
                        self.last_transcription = text
                        self.logger.info(f"Transcripción: {text}")
                        
                        # Verificar wake word
                        if self.config['enable_wake_word']:
                            if self._check_wake_word(text):
                                self.wake_word_detected = True
                                if self.on_wake_word_callback:
                                    self.on_wake_word_callback(text)
                        
                        # Llamar callback
                        if self.on_speech_callback:
                            self.on_speech_callback(text)
                        
                        silence_start = None
                    else:
                        # Detectar silencio
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > self.config['silence_duration']:
                            # Silencio prolongado
                            silence_start = None
                
                else:
                    # Resultado parcial
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    if partial_text:
                        self.logger.debug(f"Parcial: {partial_text}")
            
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error procesando audio: {e}")
    
    def _check_wake_word(self, text: str) -> bool:
        """
        Verifica si el texto contiene una wake word
        
        Args:
            text: Texto transcrito
        
        Returns:
            True si se detectó wake word
        """
        text_lower = text.lower()
        wake_words = self.config.get('wake_words', [])
        
        for wake_word in wake_words:
            if wake_word.lower() in text_lower:
                self.logger.info(f"Wake word detectada: {wake_word}")
                return True
        
        return False
    
    def listen_once(self, timeout: float = 5.0) -> Optional[str]:
        """
        Escucha una vez y retorna la transcripción
        
        Args:
            timeout: Tiempo máximo de espera en segundos
        
        Returns:
            Texto transcrito o None si timeout
        """
        if not self.is_running:
            return None
        
        self.last_transcription = ""
        result_received = threading.Event()
        
        def callback(text):
            self.last_transcription = text
            result_received.set()
        
        self.start_listening(callback)
        
        # Esperar resultado o timeout
        result_received.wait(timeout)
        
        self.stop_listening()
        
        return self.last_transcription if self.last_transcription else None
    
    def wait_for_wake_word(self, timeout: Optional[float] = None) -> bool:
        """
        Espera hasta detectar una wake word
        
        Args:
            timeout: Tiempo máximo de espera (None = infinito)
        
        Returns:
            True si se detectó wake word, False si timeout
        """
        if not self.is_running:
            return False
        
        self.wake_word_detected = False
        wake_word_event = threading.Event()
        
        def callback(text):
            if self._check_wake_word(text):
                wake_word_event.set()
        
        self.on_wake_word_callback = callback
        self.start_listening()
        
        # Esperar wake word o timeout
        detected = wake_word_event.wait(timeout)
        
        self.stop_listening()
        self.on_wake_word_callback = None
        
        return detected
    
    def get_last_transcription(self) -> str:
        """
        Obtiene la última transcripción
        
        Returns:
            Texto de la última transcripción
        """
        return self.last_transcription
    
    def set_wake_words(self, wake_words: List[str]):
        """
        Configura las wake words
        
        Args:
            wake_words: Lista de wake words
        """
        self.config['wake_words'] = wake_words
        self.logger.info(f"Wake words configuradas: {wake_words}")
    
    def enable_wake_word(self, enable: bool = True):
        """
        Habilita o deshabilita la detección de wake word
        
        Args:
            enable: True para habilitar, False para deshabilitar
        """
        self.config['enable_wake_word'] = enable
        self.logger.info(f"Wake word {'habilitada' if enable else 'deshabilitada'}")
    
    def get_summary(self) -> str:
        """
        Obtiene un resumen del estado del audio
        
        Returns:
            String con resumen
        """
        if not self.is_running:
            return "Sensor de audio no iniciado"
        
        status = "Escuchando" if self.is_listening else "En espera"
        last = f"Última transcripción: '{self.last_transcription}'" if self.last_transcription else "Sin transcripciones"
        
        return f"{status}. {last}"
