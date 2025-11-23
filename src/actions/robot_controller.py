"""
Módulo de control del robot PiCar-X
Maneja movimiento, dirección, cámara y sensores
"""

import time
import logging
import random
from typing import Optional, Dict, Tuple
from enum import Enum

try:
    from picarx import Picarx
    from robot_hat import Music, TTS
    PICARX_AVAILABLE = True
except ImportError:
    PICARX_AVAILABLE = False
    logging.warning("picarx no disponible. Ejecutar en Raspberry Pi con PiCar-X")

from config.settings import ROBOT_CONFIG


class MovementState(Enum):
    """Estados de movimiento del robot"""
    STOPPED = "stopped"
    FORWARD = "forward"
    BACKWARD = "backward"
    TURNING_LEFT = "turning_left"
    TURNING_RIGHT = "turning_right"


class RobotController:
    """
    Controlador del robot PiCar-X que maneja todas las acciones físicas
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el controlador del robot
        
        Args:
            config: Configuración personalizada (usa ROBOT_CONFIG por defecto)
        """
        self.config = config or ROBOT_CONFIG
        self.logger = logging.getLogger(__name__)
        
        # Estado del robot
        self.px = None
        self.music = None
        self.tts = None
        self.is_initialized = False
        
        # Estado de movimiento
        self.current_state = MovementState.STOPPED
        self.current_speed = 0
        self.current_steering = 0
        
        # Estado de cámara
        self.camera_pan = self.config['camera_pan_center']
        self.camera_tilt = self.config['camera_tilt_center']
        
        # Ultrasonido
        self.last_distance = 0
        
        # Tiempo de última acción
        self.last_action_time = time.time()
        self.movement_start_time = None
    
    def initialize(self) -> bool:
        """
        Inicializa el hardware del robot
        
        Returns:
            True si se inicializó correctamente
        """
        if not PICARX_AVAILABLE:
            self.logger.error("picarx no disponible")
            return False
        
        try:
            # Inicializar PiCar-X
            self.px = Picarx()
            
            # Inicializar música y TTS (opcional)
            try:
                self.music = Music()
                self.logger.info("Música inicializada")
            except Exception as e:
                self.logger.warning(f"No se pudo inicializar música: {e}")
                self.music = None
            
            try:
                self.tts = TTS()
                self.logger.info("TTS inicializado")
            except Exception as e:
                self.logger.warning(f"No se pudo inicializar TTS (pico2wave no instalado): {e}")
                self.tts = None
            
            # Configurar posición inicial
            self.stop()
            self.center_camera()
            
            self.is_initialized = True
            self.logger.info("Robot inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al inicializar robot: {e}")
            return False
    
    def cleanup(self):
        """Limpia y detiene el robot"""
        if self.is_initialized:
            self.stop()
            self.logger.info("Robot detenido y limpiado")
    
    # ========================================================================
    # MOVIMIENTO
    # ========================================================================
    
    def move_forward(self, speed: Optional[int] = None, duration: Optional[float] = None):
        """
        Mueve el robot hacia adelante
        
        Args:
            speed: Velocidad (0-100). Si es None, usa default_speed
            duration: Duración en segundos. Si es None, movimiento continuo
        """
        if not self.is_initialized:
            return
        
        speed = speed or self.config['default_speed']
        
        try:
            self.px.forward(speed)
            self.current_state = MovementState.FORWARD
            self.current_speed = speed
            self.movement_start_time = time.time()
            
            self.logger.debug(f"Moviendo adelante a velocidad {speed}")
            
            if duration:
                time.sleep(duration)
                self.stop()
        
        except Exception as e:
            self.logger.error(f"Error al mover adelante: {e}")
    
    def move_backward(self, speed: Optional[int] = None, duration: Optional[float] = None):
        """
        Mueve el robot hacia atrás
        
        Args:
            speed: Velocidad (0-100). Si es None, usa default_speed
            duration: Duración en segundos. Si es None, movimiento continuo
        """
        if not self.is_initialized:
            return
        
        speed = speed or self.config['default_speed']
        
        try:
            self.px.backward(speed)
            self.current_state = MovementState.BACKWARD
            self.current_speed = speed
            self.movement_start_time = time.time()
            
            self.logger.debug(f"Moviendo atrás a velocidad {speed}")
            
            if duration:
                time.sleep(duration)
                self.stop()
        
        except Exception as e:
            self.logger.error(f"Error al mover atrás: {e}")
    
    def turn_left(self, angle: Optional[int] = None, duration: Optional[float] = None):
        """
        Gira a la izquierda
        
        Args:
            angle: Ángulo de dirección. Si es None, usa steering_left
            duration: Duración en segundos. Si es None, giro continuo
        """
        if not self.is_initialized:
            return
        
        angle = angle or self.config['steering_left']
        
        try:
            self.px.set_dir_servo_angle(angle)
            self.current_steering = angle
            self.current_state = MovementState.TURNING_LEFT
            
            self.logger.debug(f"Girando izquierda {angle}°")
            
            if duration:
                time.sleep(duration)
                self.center_steering()
        
        except Exception as e:
            self.logger.error(f"Error al girar izquierda: {e}")
    
    def turn_right(self, angle: Optional[int] = None, duration: Optional[float] = None):
        """
        Gira a la derecha
        
        Args:
            angle: Ángulo de dirección. Si es None, usa steering_right
            duration: Duración en segundos. Si es None, giro continuo
        """
        if not self.is_initialized:
            return
        
        angle = angle or self.config['steering_right']
        
        try:
            self.px.set_dir_servo_angle(angle)
            self.current_steering = angle
            self.current_state = MovementState.TURNING_RIGHT
            
            self.logger.debug(f"Girando derecha {angle}°")
            
            if duration:
                time.sleep(duration)
                self.center_steering()
        
        except Exception as e:
            self.logger.error(f"Error al girar derecha: {e}")
    
    def stop(self):
        """Detiene el robot"""
        if not self.is_initialized:
            return
        
        try:
            self.px.stop()
            self.current_state = MovementState.STOPPED
            self.current_speed = 0
            self.movement_start_time = None
            
            self.logger.debug("Robot detenido")
        
        except Exception as e:
            self.logger.error(f"Error al detener robot: {e}")
    
    def center_steering(self):
        """Centra la dirección"""
        if not self.is_initialized:
            return
        
        try:
            self.px.set_dir_servo_angle(self.config['steering_center'])
            self.current_steering = self.config['steering_center']
        
        except Exception as e:
            self.logger.error(f"Error al centrar dirección: {e}")
    
    # ========================================================================
    # CÁMARA
    # ========================================================================
    
    def set_camera_pan(self, angle: int):
        """
        Ajusta el pan (horizontal) de la cámara
        
        Args:
            angle: Ángulo (-90 a 90)
        """
        if not self.is_initialized:
            return
        
        # Limitar ángulo
        min_pan, max_pan = self.config['camera_pan_range']
        angle = max(min_pan, min(max_pan, angle))
        
        try:
            self.px.set_cam_pan_angle(angle)
            self.camera_pan = angle
            self.logger.debug(f"Cámara pan: {angle}°")
        
        except Exception as e:
            self.logger.error(f"Error al ajustar pan de cámara: {e}")
    
    def set_camera_tilt(self, angle: int):
        """
        Ajusta el tilt (vertical) de la cámara
        
        Args:
            angle: Ángulo (-30 a 30)
        """
        if not self.is_initialized:
            return
        
        # Limitar ángulo
        min_tilt, max_tilt = self.config['camera_tilt_range']
        angle = max(min_tilt, min(max_tilt, angle))
        
        try:
            self.px.set_cam_tilt_angle(angle)
            self.camera_tilt = angle
            self.logger.debug(f"Cámara tilt: {angle}°")
        
        except Exception as e:
            self.logger.error(f"Error al ajustar tilt de cámara: {e}")
    
    def center_camera(self):
        """Centra la cámara"""
        self.set_camera_pan(self.config['camera_pan_center'])
        self.set_camera_tilt(self.config['camera_tilt_center'])
    
    def track_object(self, x: int, y: int, frame_width: int = 640, frame_height: int = 480):
        """
        Ajusta la cámara para seguir un objeto
        
        Args:
            x: Coordenada x del objeto
            y: Coordenada y del objeto
            frame_width: Ancho del frame
            frame_height: Alto del frame
        """
        if not self.is_initialized:
            return
        
        # Calcular error desde el centro
        center_x = frame_width / 2
        center_y = frame_height / 2
        
        error_x = x - center_x
        error_y = y - center_y
        
        # Aplicar suavizado
        smoothness = self.config['track_smoothness']
        
        # Ajustar pan
        pan_adjustment = int(error_x * smoothness * 0.1)
        new_pan = self.camera_pan + pan_adjustment
        self.set_camera_pan(new_pan)
        
        # Ajustar tilt
        tilt_adjustment = int(error_y * smoothness * 0.1)
        new_tilt = self.camera_tilt - tilt_adjustment  # Invertido
        self.set_camera_tilt(new_tilt)
    
    # ========================================================================
    # SENSORES
    # ========================================================================
    
    def get_distance(self) -> float:
        """
        Obtiene la distancia del sensor ultrasónico
        
        Returns:
            Distancia en cm
        """
        if not self.is_initialized:
            return 0.0
        
        try:
            distance = self.px.ultrasonic.read()
            self.last_distance = distance
            return distance
        
        except Exception as e:
            self.logger.error(f"Error al leer distancia: {e}")
            return 0.0
    
    def has_obstacle(self, threshold: Optional[float] = None) -> bool:
        """
        Verifica si hay un obstáculo cercano
        
        Args:
            threshold: Distancia umbral en cm. Si es None, usa obstacle_distance_threshold
        
        Returns:
            True si hay obstáculo
        """
        threshold = threshold or self.config.get('obstacle_distance_threshold', 20)
        distance = self.get_distance()
        return 0 < distance < threshold
    
    # ========================================================================
    # AUDIO
    # ========================================================================
    
    def play_sound(self, sound_name: str):
        """
        Reproduce un sonido
        
        Args:
            sound_name: Nombre del sonido (beep, alert, etc.)
        """
        if not self.is_initialized or not self.music:
            return
        
        try:
            # Mapeo de sonidos comunes
            sound_map = {
                'beep': [60, 0.1],
                'alert': [80, 0.2],
                'success': [72, 0.15],
                'error': [48, 0.3],
            }
            
            if sound_name in sound_map:
                note, duration = sound_map[sound_name]
                self.music.sound_play(note, duration)
            
            self.logger.debug(f"Reproduciendo sonido: {sound_name}")
        
        except Exception as e:
            self.logger.error(f"Error al reproducir sonido: {e}")
    
    def speak(self, text: str):
        """
        Hace que el robot hable usando TTS
        
        Args:
            text: Texto a pronunciar
        """
        if not self.is_initialized or not self.tts:
            return
        
        try:
            self.tts.say(text)
            self.logger.info(f"Hablando: {text}")
        
        except Exception as e:
            self.logger.error(f"Error al hablar: {e}")
    
    # ========================================================================
    # COMPORTAMIENTOS COMPLEJOS
    # ========================================================================
    
    def scan_environment(self):
        """Escanea el entorno girando la cámara"""
        if not self.is_initialized:
            return
        
        self.logger.info("Escaneando entorno...")
        
        # Girar cámara de izquierda a derecha
        for angle in range(-60, 61, 20):
            self.set_camera_pan(angle)
            time.sleep(0.3)
        
        # Volver al centro
        self.center_camera()
    
    def avoid_obstacle(self):
        """Comportamiento de evitar obstáculo"""
        if not self.is_initialized:
            return
        
        self.logger.info("Evitando obstáculo...")
        
        # Detenerse
        self.stop()
        time.sleep(0.2)
        
        # Retroceder un poco
        self.move_backward(duration=0.5)
        time.sleep(0.2)
        
        # Girar en dirección aleatoria
        if random.random() > 0.5:
            self.turn_left()
            self.move_forward(duration=0.8)
        else:
            self.turn_right()
            self.move_forward(duration=0.8)
        
        # Centrar dirección
        self.center_steering()
    
    def get_state_summary(self) -> str:
        """
        Obtiene un resumen del estado del robot
        
        Returns:
            String con resumen
        """
        if not self.is_initialized:
            return "Robot no inicializado"
        
        state_str = self.current_state.value
        speed_str = f"Velocidad: {self.current_speed}"
        distance_str = f"Distancia: {self.last_distance:.1f}cm"
        camera_str = f"Cámara: pan={self.camera_pan}° tilt={self.camera_tilt}°"
        
        return f"{state_str}, {speed_str}, {distance_str}, {camera_str}"
    
    def check_safety(self) -> bool:
        """
        Verifica condiciones de seguridad
        
        Returns:
            True si es seguro continuar
        """
        # Verificar obstáculo de emergencia
        if self.has_obstacle(self.config['emergency_stop_distance']):
            self.logger.warning("¡Obstáculo de emergencia detectado!")
            self.stop()
            return False
        
        # Verificar tiempo de movimiento continuo
        if self.movement_start_time:
            elapsed = time.time() - self.movement_start_time
            if elapsed > self.config['max_continuous_movement']:
                self.logger.warning("Tiempo máximo de movimiento alcanzado")
                self.stop()
                return False
        
        return True
