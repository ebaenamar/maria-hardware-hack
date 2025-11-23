# Arquitectura del Sistema de Feedback Loop

## Visión General

El sistema implementa un **feedback loop clásico** para robótica:

```
┌─────────────┐
│  PERCEPCIÓN │ ← Sensores (Visión, Audio, Ultrasonido)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  DECISIÓN   │ ← Motor de Reglas o LLM
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   ACCIÓN    │ ← Control del Robot
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ EVALUACIÓN  │ ← Verificación de Seguridad
└──────┬──────┘
       │
       └──────→ (volver a PERCEPCIÓN)
```

## Componentes Principales

### 1. Sensores (`src/sensors/`)

#### VisionSensor (`vision_sensor.py`)
- **Propósito**: Captura y análisis de imágenes
- **Tecnología**: Librería `vilib` del PiCar-X
- **Capacidades**:
  - Detección de caras
  - Detección de colores (6 colores)
  - Detección de códigos QR
  - Detección de gestos (piedra, papel, tijera)
  - Detección de señales de tráfico
  - Captura de screenshots

**Flujo de datos**:
```python
vision.capture_frame() → {
    'faces': [{'x', 'y', 'width', 'height'}],
    'colors': [{'x', 'y', 'width', 'height', 'color'}],
    'qr_codes': [{'data', 'x', 'y'}],
    ...
}
```

#### AudioSensor (`audio_sensor.py`)
- **Propósito**: Captura y reconocimiento de voz
- **Tecnología**: Vosk STT (Speech-to-Text)
- **Capacidades**:
  - Reconocimiento de voz en tiempo real
  - Detección de wake words
  - Transcripción continua
  - Soporte multiidioma

**Flujo de datos**:
```python
audio.listen_once() → "texto transcrito"
```

### 2. Motor de Decisión (`src/decision/`)

#### RuleEngine (`rule_engine.py`)
- **Propósito**: Toma de decisiones basada en reglas
- **Método**: Sistema de reglas con prioridades
- **Ventajas**:
  - Rápido (sin latencia de red)
  - Predecible
  - Fácil de debuggear
  - No requiere API keys

**Ejemplo de regla**:
```python
{
    'follow_face': {
        'priority': 0.9,
        'conditions': {
            'face_detected': True,
        },
        'actions': ['track_face', 'move_forward_slow'],
    }
}
```

**Evaluación**:
1. Construir contexto desde sensores
2. Evaluar condiciones de cada regla
3. Retornar acciones de la regla con mayor prioridad que se cumpla

#### LLMEngine (`llm_engine.py`)
- **Propósito**: Toma de decisiones con IA
- **Método**: Modelo de lenguaje (GPT-4, Claude)
- **Ventajas**:
  - Decisiones más inteligentes
  - Adaptación contextual
  - Razonamiento complejo
  - Lenguaje natural

**Flujo**:
1. Construir prompt con estado del sistema
2. Enviar a LLM
3. Recibir respuesta JSON con acciones y razonamiento
4. Parsear y ejecutar

### 3. Control del Robot (`src/actions/`)

#### RobotController (`robot_controller.py`)
- **Propósito**: Interfaz con el hardware del PiCar-X
- **Tecnología**: Librería `picarx`
- **Capacidades**:
  - **Movimiento**: adelante, atrás, girar
  - **Dirección**: control de servo de dirección
  - **Cámara**: pan/tilt con 2 servos
  - **Sensores**: ultrasonido para distancia
  - **Audio**: TTS (text-to-speech) y sonidos

**API Principal**:
```python
robot.move_forward(speed=30)
robot.turn_left(angle=-30)
robot.set_camera_pan(angle=45)
robot.track_object(x, y)  # Seguimiento suave
robot.get_distance()  # Ultrasonido
robot.speak("Hello")  # TTS
```

### 4. Feedback Loop (`src/core/`)

#### FeedbackLoop (`feedback_loop.py`)
- **Propósito**: Orquestador principal del sistema
- **Ciclo**:

```python
while running:
    # 1. PERCEPCIÓN
    vision_data = vision.capture_frame()
    audio_data = audio.get_transcription()
    distance = robot.get_distance()
    
    # 2. DECISIÓN
    context = build_context(vision_data, audio_data, distance)
    actions = decision_engine.evaluate(context)
    
    # 3. ACCIÓN
    for action in actions:
        execute_action(action)
    
    # 4. EVALUACIÓN
    check_safety()
    
    # Mantener frecuencia (10 Hz por defecto)
    sleep(0.1)
```

## Flujo de Datos Completo

### Ejemplo: Seguimiento de Cara

1. **PERCEPCIÓN**
   ```
   VisionSensor detecta cara en (x=320, y=240)
   RobotController lee distancia = 50cm
   ```

2. **CONSTRUCCIÓN DE CONTEXTO**
   ```python
   context = {
       'face_detected': True,
       'obstacle_distance': 50,
       'is_moving': False,
   }
   ```

3. **DECISIÓN (RuleEngine)**
   ```
   Regla 'follow_face' se cumple (prioridad 0.9)
   → Acciones: ['track_face', 'move_forward_slow']
   ```

4. **ACCIÓN**
   ```python
   # track_face
   robot.track_object(320, 240)  # Ajusta cámara
   
   # move_forward_slow
   robot.move_forward(speed=15)
   ```

5. **EVALUACIÓN**
   ```python
   robot.check_safety()  # Verifica obstáculos
   ```

6. **SIGUIENTE CICLO**
   ```
   Cara ahora en (x=310, y=235)
   → Ajustar cámara ligeramente
   → Continuar movimiento
   ```

## Configuración

### settings.py
Archivo central de configuración con:
- Frecuencia del loop
- Configuración de sensores
- Reglas de comportamiento
- Comandos de voz
- Parámetros del robot

### Personalización

**Cambiar color a seguir**:
```python
VISION_CONFIG['default_color'] = 'blue'
```

**Añadir nueva regla**:
```python
BEHAVIOR_RULES['mi_regla'] = {
    'enabled': True,
    'priority': 0.85,
    'conditions': {'qr_detected': True},
    'actions': ['stop', 'take_photo', 'speak:QR detected'],
}
```

**Ajustar velocidad**:
```python
ROBOT_CONFIG['default_speed'] = 40  # 0-100
```

## Modos de Operación

### AUTONOMOUS
- Sigue reglas automáticamente
- Reacciona a estímulos del entorno
- Explora cuando no hay actividad

### VOICE_CONTROL
- Espera comandos de voz
- Ejecuta acciones según comandos
- Mantiene feedback loop activo

### TRACKING
- Enfocado en seguir objetos
- Prioriza reglas de seguimiento
- Mantiene objeto centrado

### EXPLORATION
- Movimiento libre
- Escaneo del entorno
- Evita obstáculos

## Extensibilidad

### Añadir Nuevo Sensor
```python
class MySensor:
    def start(self): ...
    def capture_data(self): ...
    def stop(self): ...

# En FeedbackLoop
self.my_sensor = MySensor()
```

### Añadir Nueva Acción
```python
# En RobotController
def my_action(self):
    # Implementación
    pass

# En FeedbackLoop._execute_action
elif action == 'my_action':
    self.robot.my_action()
```

### Usar Otro LLM
```python
# En LLMEngine
def _call_my_llm(self, prompt):
    # Implementación
    pass
```

## Consideraciones de Rendimiento

### Frecuencia del Loop
- **10 Hz** (recomendado): Balance entre reactividad y carga
- **5 Hz**: Más tiempo para LLM
- **20 Hz**: Máxima reactividad (solo con reglas)

### Optimizaciones
1. **Caché de detecciones**: Evitar reprocesar frames idénticos
2. **Throttling de LLM**: No llamar en cada ciclo
3. **Procesamiento asíncrono**: Sensores en threads separados
4. **Downsampling**: Reducir resolución de imagen

## Seguridad

### Verificaciones Automáticas
- Distancia de emergencia (10cm)
- Tiempo máximo de movimiento continuo (5s)
- Verificación en cada ciclo

### Prioridades
1. **Seguridad** (prioridad 1.0)
2. **Comandos de voz** (0.95)
3. **Seguimiento** (0.8-0.9)
4. **Exploración** (0.3)

## Testing

### Simulación
Para desarrollo sin hardware:
```python
PICARX_AVAILABLE = False  # Modo simulación
```

### Unit Tests
```bash
pytest tests/
```

### Logs
```python
LOGGING_CONFIG['level'] = 'DEBUG'
```
