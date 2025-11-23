"""
Configuración del sistema de feedback loop para PiCar-X
"""

# ============================================================================
# CONFIGURACIÓN DEL FEEDBACK LOOP
# ============================================================================

# Frecuencia del loop (Hz)
LOOP_FREQUENCY = 1  # 1 ciclo por segundo (reducido para evitar sobrecarga de cámara)

# Timeout para operaciones (segundos)
SENSOR_TIMEOUT = 1.0
ACTION_TIMEOUT = 2.0

# ============================================================================
# CONFIGURACIÓN DE VISIÓN
# ============================================================================

VISION_CONFIG = {
    # Resolución de la cámara
    'resolution': (640, 480),
    
    # Flip de la cámara
    'vflip': False,
    'hflip': False,
    
    # Habilitar detección
    'enable_face_detect': False,  # Deshabilitado para reducir carga de CPU
    'enable_color_detect': False,  # Deshabilitado temporalmente para debug
    'enable_qr_detect': False,
    'enable_gesture_detect': False,
    'enable_traffic_sign_detect': False,
    
    # Colores a detectar (red, orange, yellow, green, blue, purple)
    'default_color': 'red',
    
    # Umbrales de detección
    'min_object_size': 50,  # píxeles
    'confidence_threshold': 0.5,
    
    # Guardar screenshots
    'save_screenshots': True,
    'screenshot_dir': '/home/pi/Pictures/feedback_loop/',
}

# ============================================================================
# CONFIGURACIÓN DE AUDIO
# ============================================================================

AUDIO_CONFIG = {
    # Configuración de captura
    'sample_rate': 16000,
    'channels': 1,
    'chunk_size': 4000,
    
    # Vosk STT
    'vosk_model_path': '/home/pi/vosk-model-small-en-us-0.15',
    'language': 'en-us',  # en-us, cn, es, etc.
    
    # Detección de voz
    'silence_threshold': 500,  # Umbral de silencio
    'silence_duration': 1.5,   # Segundos de silencio para terminar
    
    # Wake word
    'enable_wake_word': True,
    'wake_words': ['hey robot', 'hey buddy'],
}

# ============================================================================
# CONFIGURACIÓN DEL MOTOR DE DECISIÓN
# ============================================================================

DECISION_CONFIG = {
    # Tipo de motor: 'rule_based' o 'llm'
    'engine_type': 'rule_based',
    
    # Configuración LLM (si engine_type == 'llm')
    'llm_provider': 'openai',  # openai, anthropic
    'llm_model': 'gpt-4o-mini',
    'llm_temperature': 0.7,
    'llm_max_tokens': 500,
    
    # Prioridades de decisión
    'priority_weights': {
        'obstacle_avoidance': 1.0,
        'object_tracking': 0.8,
        'voice_command': 0.9,
        'exploration': 0.3,
    },
    
    # Umbrales
    'obstacle_distance_threshold': 20,  # cm
    'object_tracking_distance': 50,     # cm
}

# ============================================================================
# CONFIGURACIÓN DE ACCIONES DEL ROBOT
# ============================================================================

ROBOT_CONFIG = {
    # Velocidades
    'default_speed': 30,      # 0-100
    'slow_speed': 15,
    'fast_speed': 50,
    
    # Ángulos de dirección
    'steering_center': 0,
    'steering_left': -30,
    'steering_right': 30,
    
    # Ángulos de cámara
    'camera_pan_center': 0,
    'camera_pan_range': (-90, 90),
    'camera_tilt_center': -10,
    'camera_tilt_range': (-30, 30),
    
    # Comportamientos
    'scan_interval': 2.0,      # segundos entre escaneos
    'track_smoothness': 0.3,   # factor de suavizado (0-1)
    
    # Seguridad
    'emergency_stop_distance': 10,  # cm
    'max_continuous_movement': 5.0,  # segundos
}

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'log_to_file': True,
    'log_file': '/home/pi/picar-x-feedback.log',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}

# ============================================================================
# REGLAS DE COMPORTAMIENTO
# ============================================================================

BEHAVIOR_RULES = {
    # Regla: Si detecta cara, seguirla
    'follow_face': {
        'enabled': True,
        'priority': 0.9,
        'conditions': {
            'face_detected': True,
        },
        'actions': ['track_face', 'move_forward_slow'],
    },
    
    # Regla: Si detecta color objetivo, acercarse
    'approach_color': {
        'enabled': True,
        'priority': 0.8,
        'conditions': {
            'color_detected': True,
            'color_size': ('>', 100),
        },
        'actions': ['track_color', 'move_forward'],
    },
    
    # Regla: Si hay obstáculo cercano, evitarlo
    'avoid_obstacle': {
        'enabled': True,
        'priority': 1.0,
        'conditions': {
            'obstacle_distance': ('<', 20),
        },
        'actions': ['stop', 'turn_random', 'move_forward'],
    },
    
    # Regla: Si escucha comando de voz, ejecutarlo
    'voice_command': {
        'enabled': True,
        'priority': 0.95,
        'conditions': {
            'voice_detected': True,
        },
        'actions': ['parse_command', 'execute_command'],
    },
    
    # Regla: Si no hay nada interesante, explorar
    'explore': {
        'enabled': True,
        'priority': 0.3,
        'conditions': {
            'idle_time': ('>', 5.0),
        },
        'actions': ['scan_environment', 'move_forward', 'turn_random'],
    },
}

# ============================================================================
# COMANDOS DE VOZ
# ============================================================================

VOICE_COMMANDS = {
    # Movimiento
    'forward': ['forward', 'go forward', 'move forward', 'adelante'],
    'backward': ['backward', 'go back', 'move back', 'atrás'],
    'left': ['left', 'turn left', 'go left', 'izquierda'],
    'right': ['right', 'turn right', 'go right', 'derecha'],
    'stop': ['stop', 'halt', 'freeze', 'para', 'detente'],
    
    # Modos
    'follow_me': ['follow me', 'follow', 'sígueme'],
    'explore': ['explore', 'look around', 'explora'],
    'track_red': ['track red', 'find red', 'busca rojo'],
    'track_blue': ['track blue', 'find blue', 'busca azul'],
    
    # Cámara
    'look_up': ['look up', 'mira arriba'],
    'look_down': ['look down', 'mira abajo'],
    'look_left': ['look left', 'mira izquierda'],
    'look_right': ['look right', 'mira derecha'],
    
    # Sistema
    'take_photo': ['take photo', 'take picture', 'toma foto'],
    'status': ['status', 'report', 'estado'],
}
