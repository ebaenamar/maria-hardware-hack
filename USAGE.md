# Guía de Uso - PiCar-X Feedback Loop

## Instalación Rápida

### En Raspberry Pi

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd picar-x-feedback-loop

# Ejecutar instalación automática
chmod +x install.sh
./install.sh

# Configurar API keys (opcional, solo para LLM)
cp config/secret.py.example config/secret.py
nano config/secret.py
```

## Calibración del Robot

Antes de usar el feedback loop, calibra el PiCar-X:

```bash
cd /tmp/picar-x/example
sudo python3 calibration.py
```

Sigue las instrucciones en pantalla para calibrar:
- Dirección (steering)
- Cámara (pan y tilt)

## Ejemplos de Uso

### 1. Modo Básico (Reglas)

El modo más simple, usa reglas predefinidas:

```bash
sudo python3 examples/basic_loop.py
```

**Comportamiento**:
- Sigue caras detectadas
- Se acerca a colores detectados
- Evita obstáculos
- Explora cuando no hay actividad

### 2. Modo Avanzado (LLM)

Usa inteligencia artificial para decisiones:

```bash
# Primero configurar API key
echo "OPENAI_API_KEY = 'sk-...'" > config/secret.py

# Ejecutar
sudo python3 examples/advanced_loop.py
```

**Ventajas**:
- Decisiones más inteligentes
- Adaptación contextual
- Razonamiento complejo

**Nota**: Requiere conexión a internet y API key de OpenAI.

### 3. Control por Voz

Controla el robot con comandos de voz:

```bash
sudo python3 examples/voice_control.py
```

**Comandos disponibles**:
- `"forward"` / `"adelante"` - Mover adelante
- `"backward"` / `"atrás"` - Mover atrás
- `"left"` / `"izquierda"` - Girar izquierda
- `"right"` / `"derecha"` - Girar derecha
- `"stop"` / `"para"` - Detener
- `"follow me"` / `"sígueme"` - Modo seguimiento
- `"explore"` / `"explora"` - Modo exploración
- `"take photo"` / `"toma foto"` - Capturar imagen
- `"status"` / `"estado"` - Reportar estado

### 4. Seguimiento de Objetos

Sigue caras o colores automáticamente:

```bash
sudo python3 examples/object_tracking.py
```

## Configuración Personalizada

### Cambiar Color a Seguir

Edita `config/settings.py`:

```python
VISION_CONFIG = {
    'default_color': 'blue',  # red, orange, yellow, green, blue, purple
    ...
}
```

### Ajustar Velocidad

```python
ROBOT_CONFIG = {
    'default_speed': 40,  # 0-100
    'slow_speed': 20,
    'fast_speed': 60,
    ...
}
```

### Cambiar Frecuencia del Loop

```python
LOOP_FREQUENCY = 10  # Hz (ciclos por segundo)
```

### Añadir Nueva Regla

```python
BEHAVIOR_RULES['mi_regla'] = {
    'enabled': True,
    'priority': 0.85,  # 0-1, mayor = más prioritaria
    'conditions': {
        'qr_detected': True,
        'obstacle_distance': ('>', 30),
    },
    'actions': ['stop', 'take_photo', 'speak:QR code detected'],
}
```

## Comandos de Voz Personalizados

Edita `config/settings.py`:

```python
VOICE_COMMANDS = {
    'mi_comando': ['palabra1', 'palabra2', 'frase completa'],
    ...
}
```

## Uso Programático

### Crear un Script Personalizado

```python
#!/usr/bin/env python3
from src.core.feedback_loop import FeedbackLoop, LoopMode

# Crear feedback loop
loop = FeedbackLoop(use_llm=False)

# Personalizar configuración
loop.vision.set_color_detection('red')
loop.robot.config['default_speed'] = 25

# Iniciar
loop.start(mode=LoopMode.AUTONOMOUS)
```

### Acceder a Componentes Individuales

```python
# Solo visión
from src.sensors.vision_sensor import VisionSensor

vision = VisionSensor()
vision.start()

while True:
    frame = vision.capture_frame()
    print(f"Caras detectadas: {len(frame['faces'])}")
    time.sleep(0.1)
```

```python
# Solo audio
from src.sensors.audio_sensor import AudioSensor

audio = AudioSensor()
audio.start()

text = audio.listen_once(timeout=5.0)
print(f"Escuché: {text}")
```

```python
# Solo robot
from src.actions.robot_controller import RobotController

robot = RobotController()
robot.initialize()

robot.move_forward(speed=30, duration=2.0)
robot.turn_left(duration=1.0)
robot.stop()
```

## Debugging

### Activar Logs Detallados

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Ver Estado en Tiempo Real

```python
# Durante el loop
metrics = loop.get_metrics()
print(f"Ciclos: {metrics['loop_count']}")
print(f"Tiempo promedio: {metrics['avg_loop_time']:.3f}s")
```

### Capturar Screenshots

```python
# Manual
vision.take_screenshot('mi_foto')
# → Guardado en ~/Pictures/feedback_loop/mi_foto.jpg

# Automático en cada ciclo
VISION_CONFIG['save_screenshots'] = True
```

## Solución de Problemas

### Error: "vilib no disponible"

```bash
# Reinstalar picar-x
cd /tmp/picar-x
sudo python3 setup.py install
```

### Error: "Modelo Vosk no encontrado"

```bash
# Descargar modelo
cd ~
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

### Audio no funciona

```bash
# Configurar I2S
cd /tmp/picar-x
sudo bash i2samp.sh
sudo reboot
```

### Robot no se mueve

1. Verificar calibración:
   ```bash
   cd /tmp/picar-x/example
   sudo python3 calibration.py
   ```

2. Verificar batería del PiCar-X

3. Verificar conexiones de hardware

### LLM muy lento

- Usar modelo más rápido: `gpt-3.5-turbo` en lugar de `gpt-4`
- Reducir frecuencia del loop: `LOOP_FREQUENCY = 5`
- Usar modo de reglas en lugar de LLM

## Mejores Prácticas

### Seguridad

1. **Siempre** tener espacio libre alrededor del robot
2. Verificar batería antes de iniciar
3. Mantener `emergency_stop_distance` en al menos 10cm
4. Supervisar el robot durante operación

### Rendimiento

1. Usar reglas para aplicaciones en tiempo real
2. Usar LLM solo cuando se necesite razonamiento complejo
3. Ajustar `LOOP_FREQUENCY` según necesidades
4. Deshabilitar detecciones no usadas

### Desarrollo

1. Probar en modo simulación primero (sin hardware)
2. Usar logs para debugging
3. Empezar con velocidades bajas
4. Calibrar antes de cada sesión

## Recursos Adicionales

- **Documentación PiCar-X**: https://docs.sunfounder.com/projects/picar-x-v20/
- **Robot HAT**: https://docs.sunfounder.com/projects/robot-hat-v4/
- **Vosk Models**: https://alphacephei.com/vosk/models
- **OpenAI API**: https://platform.openai.com/docs

## Soporte

Para problemas o preguntas:
1. Revisar logs: `~/picar-x-feedback.log`
2. Verificar configuración: `config/settings.py`
3. Consultar documentación: `ARCHITECTURE.md`
