"""
Feedback loop system configuration for PiCar-X
"""

# ============================================================================
# FEEDBACK LOOP CONFIGURATION
# ============================================================================

# Loop frequency (Hz)
LOOP_FREQUENCY = 1  # 1 cycle per second (reduced to avoid camera overload)

# Timeout for operations (seconds)
SENSOR_TIMEOUT = 1.0
ACTION_TIMEOUT = 2.0

# ============================================================================
# VISION CONFIGURATION
# ============================================================================

VISION_CONFIG = {
    # Camera resolution
    'resolution': (640, 480),
    
    # Camera flip
    'vflip': False,
    'hflip': False,
    
    # Enable detection
    'enable_face_detect': False,  # Disabled to reduce CPU load
    'enable_color_detect': False,  # Temporarily disabled for debugging
    'enable_qr_detect': False,
    'enable_gesture_detect': False,
    'enable_traffic_sign_detect': False,
    
    # Colors to detect (red, orange, yellow, green, blue, purple)
    'default_color': 'red',
    
    # Detection thresholds
    'min_object_size': 50,  # pixels
    'confidence_threshold': 0.5,
    
    # Save screenshots
    'save_screenshots': True,
    'screenshot_dir': '/home/pi/Pictures/feedback_loop/',
}

# ============================================================================
# AUDIO CONFIGURATION
# ============================================================================

AUDIO_CONFIG = {
    # Capture configuration
    'sample_rate': 16000,
    'channels': 1,
    'chunk_size': 4000,
    
    # Vosk STT
    'vosk_model_path': '/home/pi/vosk-model-small-en-us-0.15',
    'language': 'en-us',  # en-us, cn, es, etc.
    
    # Voice detection
    'silence_threshold': 500,  # Silence threshold
    'silence_duration': 1.5,   # Seconds of silence to finish
    
    # Wake word
    'enable_wake_word': True,
    'wake_words': ['hey robot', 'hey buddy'],
}

# ============================================================================
# DECISION ENGINE CONFIGURATION
# ============================================================================

DECISION_CONFIG = {
    # Engine type: 'rule_based' or 'llm'
    'engine_type': 'rule_based',
    
    # LLM configuration (if engine_type == 'llm')
    'llm_provider': 'openai',  # openai, anthropic
    'llm_model': 'gpt-4o-mini',
    'llm_temperature': 0.7,
    'llm_max_tokens': 500,
    
    # Decision priorities
    'priority_weights': {
        'obstacle_avoidance': 1.0,
        'object_tracking': 0.8,
        'voice_command': 0.9,
        'exploration': 0.3,
    },
    
    # Thresholds
    'obstacle_distance_threshold': 20,  # cm
    'object_tracking_distance': 50,     # cm
}

# ============================================================================
# ROBOT ACTIONS CONFIGURATION
# ============================================================================

ROBOT_CONFIG = {
    # Speeds
    'default_speed': 30,      # 0-100
    'slow_speed': 15,
    'fast_speed': 50,
    
    # Steering angles
    'steering_center': 0,
    'steering_left': -30,
    'steering_right': 30,
    
    # Camera angles
    'camera_pan_center': 0,
    'camera_pan_range': (-90, 90),
    'camera_tilt_center': -10,
    'camera_tilt_range': (-30, 30),
    
    # Behaviors
    'scan_interval': 2.0,      # seconds between scans
    'track_smoothness': 0.3,   # smoothing factor (0-1)
    
    # Safety
    'emergency_stop_distance': 10,  # cm
    'max_continuous_movement': 5.0,  # seconds
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'log_to_file': True,
    'log_file': '/home/pi/picar-x-feedback.log',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}

# ============================================================================
# BEHAVIOR RULES
# ============================================================================

BEHAVIOR_RULES = {
    # Rule: If face detected, follow it
    'follow_face': {
        'enabled': True,
        'priority': 0.9,
        'conditions': {
            'face_detected': True,
        },
        'actions': ['track_face', 'move_forward_slow'],
    },
    
    # Rule: If target color detected, approach it
    'approach_color': {
        'enabled': True,
        'priority': 0.8,
        'conditions': {
            'color_detected': True,
            'color_size': ('>', 100),
        },
        'actions': ['track_color', 'move_forward'],
    },
    
    # Rule: If obstacle nearby, avoid it
    'avoid_obstacle': {
        'enabled': True,
        'priority': 1.0,
        'conditions': {
            'obstacle_distance': ('<', 20),
        },
        'actions': ['stop', 'turn_random', 'move_forward'],
    },
    
    # Rule: If voice command heard, execute it
    'voice_command': {
        'enabled': True,
        'priority': 0.95,
        'conditions': {
            'voice_detected': True,
        },
        'actions': ['parse_command', 'execute_command'],
    },
    
    # Rule: If nothing interesting, explore
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
# VOICE COMMANDS
# ============================================================================

VOICE_COMMANDS = {
    # Movement
    'forward': ['forward', 'go forward', 'move forward'],
    'backward': ['backward', 'go back', 'move back'],
    'left': ['left', 'turn left', 'go left'],
    'right': ['right', 'turn right', 'go right'],
    'stop': ['stop', 'halt', 'freeze'],
    
    # Modes
    'follow_me': ['follow me', 'follow'],
    'explore': ['explore', 'look around'],
    'track_red': ['track red', 'find red'],
    'track_blue': ['track blue', 'find blue'],
    
    # Camera
    'look_up': ['look up'],
    'look_down': ['look down'],
    'look_left': ['look left'],
    'look_right': ['look right'],
    
    # System
    'take_photo': ['take photo', 'take picture'],
    'status': ['status', 'report'],
}
