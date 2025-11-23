# Ejemplos de Código - PiCar-X Feedback Loop

## Ejemplos Básicos

### 1. Captura Simple de Visión

```python
from src.sensors.vision_sensor import VisionSensor
import time

# Inicializar sensor
vision = VisionSensor()
vision.start()

# Capturar frames
for i in range(10):
    frame_data = vision.capture_frame()
    
    # Verificar detecciones
    if vision.has_detection('face'):
        print("¡Cara detectada!")
        center = vision.get_object_center('face')
        print(f"Posición: {center}")
    
    time.sleep(0.5)

vision.stop()
```

### 2. Reconocimiento de Voz Simple

```python
from src.sensors.audio_sensor import AudioSensor

# Inicializar sensor
audio = AudioSensor()
audio.start()

# Escuchar una vez
print("Di algo...")
text = audio.listen_once(timeout=5.0)

if text:
    print(f"Escuché: {text}")
else:
    print("No se detectó voz")

audio.stop()
```

### 3. Control Básico del Robot

```python
from src.actions.robot_controller import RobotController
import time

# Inicializar robot
robot = RobotController()
robot.initialize()

# Secuencia de movimientos
robot.move_forward(speed=30, duration=2.0)
time.sleep(0.5)

robot.turn_left(duration=1.0)
time.sleep(0.5)

robot.move_forward(speed=30, duration=2.0)
time.sleep(0.5)

robot.stop()
robot.cleanup()
```

## Ejemplos Intermedios

### 4. Seguimiento de Objeto con Cámara

```python
from src.sensors.vision_sensor import VisionSensor
from src.actions.robot_controller import RobotController
import time

# Inicializar
vision = VisionSensor()
robot = RobotController()
vision.start()
robot.initialize()

# Habilitar detección de color rojo
vision.set_color_detection('red')

# Loop de seguimiento
try:
    while True:
        # Capturar frame
        frame = vision.capture_frame()
        
        # Si hay color detectado
        if vision.has_detection('color'):
            # Obtener posición
            center = vision.get_object_center('color')
            
            if center:
                # Ajustar cámara para seguir
                robot.track_object(center[0], center[1])
                print(f"Siguiendo objeto en {center}")
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Deteniendo...")

finally:
    robot.stop()
    vision.stop()
    robot.cleanup()
```

### 5. Navegación con Evitar Obstáculos

```python
from src.actions.robot_controller import RobotController
import time

robot = RobotController()
robot.initialize()

try:
    while True:
        # Leer distancia
        distance = robot.get_distance()
        print(f"Distancia: {distance:.1f}cm")
        
        # Si hay obstáculo cercano
        if robot.has_obstacle(threshold=30):
            print("¡Obstáculo detectado!")
            robot.avoid_obstacle()
        else:
            # Avanzar normalmente
            robot.move_forward(speed=30)
        
        time.sleep(0.2)

except KeyboardInterrupt:
    print("Deteniendo...")

finally:
    robot.stop()
    robot.cleanup()
```

### 6. Sistema de Wake Word

```python
from src.sensors.audio_sensor import AudioSensor

audio = AudioSensor()
audio.start()

# Configurar wake words
audio.set_wake_words(['hey robot', 'hello picar'])

print("Esperando wake word...")
detected = audio.wait_for_wake_word(timeout=30)

if detected:
    print("¡Wake word detectada!")
    
    # Ahora escuchar comando
    print("Escuchando comando...")
    command = audio.listen_once(timeout=5.0)
    print(f"Comando: {command}")
else:
    print("Timeout - no se detectó wake word")

audio.stop()
```

## Ejemplos Avanzados

### 7. Feedback Loop Personalizado

```python
from src.sensors.vision_sensor import VisionSensor
from src.sensors.audio_sensor import AudioSensor
from src.actions.robot_controller import RobotController
from src.decision.rule_engine import RuleEngine, ContextBuilder
import time

# Inicializar componentes
vision = VisionSensor()
audio = AudioSensor()
robot = RobotController()
engine = RuleEngine()
context_builder = ContextBuilder()

vision.start()
audio.start()
robot.initialize()

# Añadir regla personalizada
engine.add_rule(
    name='celebrar_cara',
    priority=0.95,
    conditions={'face_detected': True},
    actions=['play_sound', 'speak:Hello human!']
)

try:
    while True:
        # 1. PERCEPCIÓN
        vision_data = vision.capture_frame()
        audio_data = audio.get_last_transcription()
        distance = robot.get_distance()
        robot_state = {'speed': robot.current_speed}
        
        # 2. CONTEXTO
        context = context_builder.build_context(
            vision_data, audio_data, robot_state, distance
        )
        
        # 3. DECISIÓN
        actions = engine.evaluate(context)
        
        # 4. ACCIÓN
        for action in actions:
            if action == 'play_sound':
                robot.play_sound('beep')
            elif action.startswith('speak:'):
                text = action.split(':', 1)[1]
                robot.speak(text)
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Deteniendo...")

finally:
    robot.stop()
    vision.stop()
    audio.stop()
    robot.cleanup()
```

### 8. Integración con LLM

```python
from src.sensors.vision_sensor import VisionSensor
from src.actions.robot_controller import RobotController
from src.decision.llm_engine import LLMEngine
from src.decision.rule_engine import ContextBuilder
import time

# Inicializar
vision = VisionSensor()
robot = RobotController()
llm = LLMEngine(provider='openai', model='gpt-4o-mini')
context_builder = ContextBuilder()

vision.start()
robot.initialize()

try:
    while True:
        # Capturar datos
        vision_data = vision.capture_frame()
        distance = robot.get_distance()
        robot_state = {'speed': robot.current_speed}
        
        # Construir contexto
        context = context_builder.build_context(
            vision_data, None, robot_state, distance
        )
        
        # Obtener decisión del LLM
        actions = llm.evaluate(context)
        
        # Ejecutar acciones
        for action in actions:
            if action == 'move_forward':
                robot.move_forward()
            elif action == 'stop':
                robot.stop()
            elif action == 'track_face':
                if vision.has_detection('face'):
                    center = vision.get_object_center('face')
                    robot.track_object(center[0], center[1])
        
        time.sleep(0.5)  # LLM es más lento

except KeyboardInterrupt:
    print("Deteniendo...")

finally:
    robot.stop()
    vision.stop()
    robot.cleanup()
```

### 9. Sistema Multi-Modal (Visión + Audio + Movimiento)

```python
from src.core.feedback_loop import FeedbackLoop, LoopMode
import time

# Crear loop
loop = FeedbackLoop(use_llm=False)

# Personalizar configuración
loop.vision.config['enable_face_detect'] = True
loop.vision.config['enable_color_detect'] = True
loop.vision.set_color_detection('blue')

# Habilitar control por voz
loop.enable_voice_control()

# Añadir regla personalizada
loop.decision_engine.add_rule(
    name='reaccionar_a_azul',
    priority=0.85,
    conditions={
        'color_detected': True,
        'color_size': ('>', 200),
    },
    actions=['stop', 'take_photo', 'speak:Blue object detected']
)

# Iniciar
try:
    loop.start(mode=LoopMode.AUTONOMOUS)
except KeyboardInterrupt:
    print("Deteniendo...")
finally:
    loop.stop()
```

### 10. Comportamiento Complejo: Patrullar y Reportar

```python
from src.core.feedback_loop import FeedbackLoop
from src.decision.rule_engine import ContextBuilder
import time

class PatrolBot:
    def __init__(self):
        self.loop = FeedbackLoop(use_llm=False)
        self.patrol_points = [
            ('forward', 3.0),
            ('turn_left', 1.0),
            ('forward', 3.0),
            ('turn_left', 1.0),
        ]
        self.current_point = 0
        self.last_report_time = time.time()
    
    def patrol(self):
        """Ejecuta patrón de patrullaje"""
        action, duration = self.patrol_points[self.current_point]
        
        if action == 'forward':
            self.loop.robot.move_forward(duration=duration)
        elif action == 'turn_left':
            self.loop.robot.turn_left(duration=duration)
        
        self.current_point = (self.current_point + 1) % len(self.patrol_points)
    
    def report_status(self):
        """Reporta estado periódicamente"""
        current_time = time.time()
        
        if current_time - self.last_report_time > 10:  # Cada 10 segundos
            # Capturar estado
            vision_summary = self.loop.vision.get_summary()
            distance = self.loop.robot.get_distance()
            
            # Reportar
            report = f"Status report. {vision_summary}. Distance: {distance:.1f} centimeters."
            print(report)
            self.loop.robot.speak(report)
            
            # Tomar foto si hay algo interesante
            if self.loop.vision.has_detection('any'):
                self.loop.vision.take_screenshot()
            
            self.last_report_time = current_time
    
    def run(self):
        """Ejecuta el bot"""
        if not self.loop.initialize():
            print("Error al inicializar")
            return
        
        try:
            while True:
                # Patrullar
                self.patrol()
                
                # Reportar
                self.report_status()
                
                # Verificar seguridad
                if self.loop.robot.has_obstacle(threshold=20):
                    self.loop.robot.avoid_obstacle()
                
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("Deteniendo patrulla...")
        
        finally:
            self.loop.stop()

# Ejecutar
bot = PatrolBot()
bot.run()
```

## Snippets Útiles

### Capturar Screenshot con Timestamp

```python
from datetime import datetime

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'capture_{timestamp}'
path = vision.take_screenshot(filename)
print(f"Guardado en: {path}")
```

### Verificar Estado del Sistema

```python
print("=== ESTADO DEL SISTEMA ===")
print(f"Visión: {vision.get_summary()}")
print(f"Audio: {audio.get_summary()}")
print(f"Robot: {robot.get_state_summary()}")
print(f"Distancia: {robot.get_distance():.1f}cm")
```

### Logging Personalizado

```python
import logging

# Configurar logger
logger = logging.getLogger('mi_app')
logger.setLevel(logging.DEBUG)

# Handler para archivo
fh = logging.FileHandler('mi_robot.log')
fh.setLevel(logging.DEBUG)

# Handler para consola
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Formato
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

# Usar
logger.info("Robot iniciado")
logger.debug("Frame capturado")
logger.warning("Obstáculo detectado")
logger.error("Error en sensor")
```

### Manejo de Errores Robusto

```python
import traceback

def safe_execute(func, *args, **kwargs):
    """Ejecuta función con manejo de errores"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error en {func.__name__}: {e}")
        logger.debug(traceback.format_exc())
        return None

# Usar
result = safe_execute(robot.move_forward, speed=30)
```

## Tips y Trucos

### Optimizar Rendimiento

```python
# Reducir resolución de cámara
VISION_CONFIG['resolution'] = (320, 240)

# Deshabilitar detecciones no usadas
vision.config['enable_gesture_detect'] = False
vision.config['enable_qr_detect'] = False

# Ajustar frecuencia del loop
LOOP_FREQUENCY = 5  # 5 Hz en lugar de 10 Hz
```

### Debug de Detecciones

```python
# Imprimir todas las detecciones
frame = vision.capture_frame()
print(f"Timestamp: {frame['timestamp']}")
print(f"Caras: {len(frame['faces'])}")
print(f"Colores: {len(frame['colors'])}")
print(f"QR: {len(frame['qr_codes'])}")

# Detalles de cada detección
for face in frame['faces']:
    print(f"  Cara en ({face['x']}, {face['y']}) - {face['width']}x{face['height']}")
```

### Calibración Fina de Cámara

```python
# Ajustar rango de movimiento
robot.config['camera_pan_range'] = (-60, 60)
robot.config['camera_tilt_range'] = (-20, 20)

# Ajustar suavizado de seguimiento
robot.config['track_smoothness'] = 0.5  # 0-1, mayor = más suave
```
