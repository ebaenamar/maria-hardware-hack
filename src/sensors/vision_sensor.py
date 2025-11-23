"""
Módulo de captura y análisis de visión para PiCar-X
Utiliza la librería vilib para acceder a la cámara y detectar objetos
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple, List
import numpy as np

try:
    from vilib import Vilib
    VILIB_AVAILABLE = True
except ImportError:
    VILIB_AVAILABLE = False
    logging.warning("vilib no disponible. Ejecutar en Raspberry Pi con PiCar-X")

from config.settings import VISION_CONFIG


class VisionSensor:
    """
    Sensor de visión que captura imágenes y detecta objetos, colores, caras, etc.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el sensor de visión
        
        Args:
            config: Configuración personalizada (usa VISION_CONFIG por defecto)
        """
        self.config = config or VISION_CONFIG
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.last_frame_data = {}
        
        # Crear directorio para screenshots
        if self.config.get('save_screenshots'):
            os.makedirs(self.config['screenshot_dir'], exist_ok=True)
    
    def start(self) -> bool:
        """
        Inicia la cámara y los sistemas de detección
        
        Returns:
            True si se inició correctamente
        """
        if not VILIB_AVAILABLE:
            self.logger.error("vilib no disponible")
            return False
        
        try:
            # Iniciar cámara
            Vilib.camera_start(
                vflip=self.config['vflip'],
                hflip=self.config['hflip']
            )
            
            # Iniciar display (web y local si está disponible)
            Vilib.display(local=False, web=True)
            
            # Esperar a que la cámara se estabilice
            time.sleep(2)
            self.logger.info("Cámara inicializada, esperando estabilización...")
            
            # Habilitar detecciones según configuración
            if self.config['enable_face_detect']:
                Vilib.face_detect_switch(True)
                self.logger.info("Detección de caras habilitada")
            
            if self.config['enable_color_detect']:
                Vilib.color_detect(self.config['default_color'])
                self.logger.info(f"Detección de color habilitada: {self.config['default_color']}")
            
            if self.config['enable_qr_detect']:
                Vilib.qrcode_detect_switch(True)
                self.logger.info("Detección de QR habilitada")
            
            if self.config['enable_gesture_detect']:
                Vilib.gesture_detect_switch(True)
                self.logger.info("Detección de gestos habilitada")
            
            if self.config['enable_traffic_sign_detect']:
                Vilib.traffic_sign_detect_switch(True)
                self.logger.info("Detección de señales de tráfico habilitada")
            
            self.is_running = True
            self.logger.info("Sensor de visión iniciado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al iniciar sensor de visión: {e}")
            return False
    
    def stop(self):
        """Detiene la cámara y los sistemas de detección"""
        if VILIB_AVAILABLE and self.is_running:
            try:
                Vilib.camera_close()
                self.is_running = False
                self.logger.info("Sensor de visión detenido")
            except Exception as e:
                self.logger.error(f"Error al detener sensor de visión: {e}")
    
    def capture_frame(self) -> Dict:
        """
        Captura un frame actual con toda la información de detección
        
        Returns:
            Diccionario con información del frame:
            {
                'timestamp': float,
                'faces': List[Dict],
                'colors': List[Dict],
                'qr_codes': List[Dict],
                'gestures': List[Dict],
                'traffic_signs': List[Dict],
            }
        """
        if not self.is_running:
            return {}
        
        frame_data = {
            'timestamp': time.time(),
            'faces': [],
            'colors': [],
            'qr_codes': [],
            'gestures': [],
            'traffic_signs': [],
        }
        
        try:
            # Obtener datos de detección de Vilib
            detect_params = Vilib.detect_obj_parameter
            
            # Procesar detección de caras
            if self.config['enable_face_detect']:
                face_count = detect_params.get('human_n', 0)
                if face_count > 0:
                    face_data = {
                        'x': detect_params.get('human_x', 0),
                        'y': detect_params.get('human_y', 0),
                        'width': detect_params.get('human_w', 0),
                        'height': detect_params.get('human_h', 0),
                        'count': face_count,
                    }
                    frame_data['faces'].append(face_data)
            
            # Procesar detección de colores
            if self.config['enable_color_detect']:
                color_count = detect_params.get('color_n', 0)
                if color_count > 0:
                    color_data = {
                        'x': detect_params.get('color_x', 0),
                        'y': detect_params.get('color_y', 0),
                        'width': detect_params.get('color_w', 0),
                        'height': detect_params.get('color_h', 0),
                        'count': color_count,
                        'color': self.config['default_color'],
                    }
                    frame_data['colors'].append(color_data)
            
            # Procesar detección de QR
            if self.config['enable_qr_detect']:
                qr_data = detect_params.get('qr_data', 'None')
                if qr_data != 'None':
                    qr_info = {
                        'data': qr_data,
                        'x': detect_params.get('qr_x', 0),
                        'y': detect_params.get('qr_y', 0),
                        'width': detect_params.get('qr_w', 0),
                        'height': detect_params.get('qr_h', 0),
                    }
                    frame_data['qr_codes'].append(qr_info)
            
            # Procesar detección de gestos
            if self.config['enable_gesture_detect']:
                gesture_type = detect_params.get('gesture_t', None)
                if gesture_type:
                    gesture_data = {
                        'type': gesture_type,
                        'x': detect_params.get('gesture_x', 0),
                        'y': detect_params.get('gesture_y', 0),
                        'width': detect_params.get('gesture_w', 0),
                        'height': detect_params.get('gesture_h', 0),
                    }
                    frame_data['gestures'].append(gesture_data)
            
            # Procesar detección de señales de tráfico
            if self.config['enable_traffic_sign_detect']:
                sign_type = detect_params.get('traffic_sign_t', None)
                if sign_type:
                    sign_data = {
                        'type': sign_type,
                        'x': detect_params.get('traffic_sign_x', 0),
                        'y': detect_params.get('traffic_sign_y', 0),
                        'width': detect_params.get('traffic_sign_w', 0),
                        'height': detect_params.get('traffic_sign_h', 0),
                    }
                    frame_data['traffic_signs'].append(sign_data)
            
            self.last_frame_data = frame_data
            
        except Exception as e:
            self.logger.error(f"Error al capturar frame: {e}")
        
        return frame_data
    
    def take_screenshot(self, name: Optional[str] = None) -> Optional[str]:
        """
        Toma una captura de pantalla y la guarda
        
        Args:
            name: Nombre del archivo (sin extensión). Si es None, usa timestamp
        
        Returns:
            Ruta completa del archivo guardado, o None si falló
        """
        if not self.is_running or not VILIB_AVAILABLE:
            return None
        
        try:
            if name is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name = f'screenshot_{timestamp}'
            
            path = self.config['screenshot_dir']
            Vilib.take_photo(name, path)
            
            full_path = os.path.join(path, f'{name}.jpg')
            self.logger.info(f"Screenshot guardado: {full_path}")
            return full_path
            
        except Exception as e:
            self.logger.error(f"Error al tomar screenshot: {e}")
            return None
    
    def set_color_detection(self, color: str):
        """
        Cambia el color a detectar
        
        Args:
            color: Color a detectar (red, orange, yellow, green, blue, purple, close)
        """
        if not self.is_running:
            return
        
        try:
            if color == 'close':
                Vilib.color_detect_switch(False)
                self.config['enable_color_detect'] = False
            else:
                Vilib.color_detect(color)
                self.config['default_color'] = color
                self.config['enable_color_detect'] = True
            
            self.logger.info(f"Color de detección cambiado a: {color}")
            
        except Exception as e:
            self.logger.error(f"Error al cambiar color de detección: {e}")
    
    def get_object_center(self, obj_type: str = 'face') -> Optional[Tuple[int, int]]:
        """
        Obtiene las coordenadas del centro del objeto detectado
        
        Args:
            obj_type: Tipo de objeto (face, color, qr, gesture, traffic_sign)
        
        Returns:
            Tupla (x, y) con las coordenadas, o None si no hay objeto
        """
        if not self.last_frame_data:
            return None
        
        obj_map = {
            'face': 'faces',
            'color': 'colors',
            'qr': 'qr_codes',
            'gesture': 'gestures',
            'traffic_sign': 'traffic_signs',
        }
        
        obj_list = self.last_frame_data.get(obj_map.get(obj_type, 'faces'), [])
        
        if obj_list:
            obj = obj_list[0]  # Tomar el primero
            return (obj['x'], obj['y'])
        
        return None
    
    def has_detection(self, obj_type: str = 'any') -> bool:
        """
        Verifica si hay alguna detección
        
        Args:
            obj_type: Tipo de objeto (any, face, color, qr, gesture, traffic_sign)
        
        Returns:
            True si hay detección del tipo especificado
        """
        if not self.last_frame_data:
            return False
        
        if obj_type == 'any':
            return any([
                len(self.last_frame_data.get('faces', [])) > 0,
                len(self.last_frame_data.get('colors', [])) > 0,
                len(self.last_frame_data.get('qr_codes', [])) > 0,
                len(self.last_frame_data.get('gestures', [])) > 0,
                len(self.last_frame_data.get('traffic_signs', [])) > 0,
            ])
        
        obj_map = {
            'face': 'faces',
            'color': 'colors',
            'qr': 'qr_codes',
            'gesture': 'gestures',
            'traffic_sign': 'traffic_signs',
        }
        
        obj_list = self.last_frame_data.get(obj_map.get(obj_type, 'faces'), [])
        return len(obj_list) > 0
    
    def get_summary(self) -> str:
        """
        Obtiene un resumen textual de lo que ve la cámara
        
        Returns:
            String con resumen de detecciones
        """
        if not self.last_frame_data:
            return "No hay datos de visión disponibles"
        
        summary_parts = []
        
        faces = self.last_frame_data.get('faces', [])
        if faces:
            summary_parts.append(f"{len(faces)} cara(s) detectada(s)")
        
        colors = self.last_frame_data.get('colors', [])
        if colors:
            color_name = colors[0].get('color', 'unknown')
            summary_parts.append(f"Color {color_name} detectado")
        
        qr_codes = self.last_frame_data.get('qr_codes', [])
        if qr_codes:
            summary_parts.append(f"Código QR: {qr_codes[0].get('data', 'unknown')}")
        
        gestures = self.last_frame_data.get('gestures', [])
        if gestures:
            gesture_type = gestures[0].get('type', 'unknown')
            summary_parts.append(f"Gesto: {gesture_type}")
        
        signs = self.last_frame_data.get('traffic_signs', [])
        if signs:
            sign_type = signs[0].get('type', 'unknown')
            summary_parts.append(f"Señal: {sign_type}")
        
        if not summary_parts:
            return "No se detectaron objetos"
        
        return ", ".join(summary_parts)
