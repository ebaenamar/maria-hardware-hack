# Flujo de Datos del Sistema

## Diagrama General del Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PICAR-X ROBOT                               │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   CÁMARA     │  │  MICRÓFONO   │  │ ULTRASONIDO  │            │
│  │   (Visión)   │  │   (Audio)    │  │  (Distancia) │            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
│         │                  │                  │                     │
│         └──────────────────┴──────────────────┘                     │
│                            │                                        │
│                            ▼                                        │
│                  ┌─────────────────┐                               │
│                  │  FEEDBACK LOOP  │                               │
│                  │   (10 Hz)       │                               │
│                  └────────┬────────┘                               │
│                           │                                         │
│         ┌─────────────────┼─────────────────┐                     │
│         │                 │                 │                      │
│         ▼                 ▼                 ▼                      │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐                 │
│  │  MOTORES │     │  SERVOS  │     │ SPEAKER  │                 │
│  │ (Ruedas) │     │ (Cámara) │     │  (TTS)   │                 │
│  └──────────┘     └──────────┘     └──────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
```

## Flujo Detallado del Feedback Loop

### 1. FASE DE PERCEPCIÓN

```
┌─────────────────────────────────────────────────────────────┐
│                    PERCEPCIÓN                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  VisionSensor.capture_frame()                              │
│  ├─ Captura frame de cámara (640x480)                     │
│  ├─ Procesa detecciones con vilib:                        │
│  │  ├─ Caras (Haar Cascade)                              │
│  │  ├─ Colores (HSV filtering)                           │
│  │  ├─ QR Codes (pyzbar)                                 │
│  │  ├─ Gestos (clasificador)                             │
│  │  └─ Señales de tráfico (clasificador)                 │
│  └─ Retorna: {                                            │
│       'timestamp': 1234567890.123,                        │
│       'faces': [{'x': 320, 'y': 240, 'w': 100, 'h': 120}],│
│       'colors': [{'x': 400, 'y': 300, 'color': 'red'}],  │
│       ...                                                  │
│     }                                                      │
│                                                             │
│  AudioSensor.get_last_transcription()                      │
│  ├─ Captura audio del micrófono (16kHz)                  │
│  ├─ Procesa con Vosk STT                                  │
│  └─ Retorna: "forward please" o None                      │
│                                                             │
│  RobotController.get_distance()                            │
│  ├─ Lee sensor ultrasónico                                │
│  └─ Retorna: 45.3 (cm)                                    │
│                                                             │
│  RobotController.get_state()                               │
│  └─ Retorna: {'speed': 30, 'state': 'forward'}           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
```

### 2. FASE DE CONSTRUCCIÓN DE CONTEXTO

```
┌─────────────────────────────────────────────────────────────┐
│              CONSTRUCCIÓN DE CONTEXTO                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ContextBuilder.build_context(                             │
│      vision_data,                                          │
│      audio_data,                                           │
│      robot_state,                                          │
│      distance                                              │
│  )                                                         │
│                                                             │
│  Procesa y normaliza datos:                                │
│  ├─ Convierte detecciones a booleanos                     │
│  ├─ Calcula métricas derivadas                            │
│  ├─ Determina tiempo de inactividad                       │
│  └─ Construye contexto unificado                          │
│                                                             │
│  Retorna contexto:                                         │
│  {                                                         │
│    'face_detected': True,                                 │
│    'color_detected': True,                                │
│    'color_size': 12000,                                   │
│    'voice_detected': True,                                │
│    'voice_text': "forward please",                        │
│    'obstacle_distance': 45.3,                             │
│    'has_obstacle': False,                                 │
│    'idle_time': 0.5,                                      │
│    'is_moving': True                                      │
│  }                                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
```

### 3. FASE DE DECISIÓN

#### Opción A: Motor de Reglas

```
┌─────────────────────────────────────────────────────────────┐
│                  MOTOR DE REGLAS                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RuleEngine.evaluate(context)                              │
│                                                             │
│  Para cada regla (ordenadas por prioridad):                │
│  ├─ Evaluar condiciones:                                   │
│  │  ├─ face_detected == True? ✓                          │
│  │  ├─ obstacle_distance > 20? ✓                         │
│  │  └─ Todas las condiciones cumplen? ✓                  │
│  │                                                         │
│  ├─ Si cumple, retornar acciones de esta regla:           │
│  │  └─ ['track_face', 'move_forward_slow']               │
│  │                                                         │
│  └─ Si no cumple, probar siguiente regla                  │
│                                                             │
│  Reglas evaluadas (ejemplo):                               │
│  1. avoid_obstacle (prioridad 1.0) ✗ No cumple           │
│  2. voice_command (prioridad 0.95) ✗ No cumple           │
│  3. follow_face (prioridad 0.9) ✓ CUMPLE                 │
│     └─ Retorna: ['track_face', 'move_forward_slow']      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Opción B: Motor LLM

```
┌─────────────────────────────────────────────────────────────┐
│                    MOTOR LLM                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LLMEngine.evaluate(context)                               │
│                                                             │
│  1. Construir prompt:                                      │
│     "ESTADO ACTUAL DEL ROBOT:                             │
│      - Cara detectada                                      │
│      - Color detectado (tamaño: 12000)                    │
│      - Comando de voz: 'forward please'                   │
│      - Distancia a obstáculo: 45.3cm                      │
│      - Robot en movimiento                                 │
│                                                             │
│      ¿Qué debe hacer el robot?"                           │
│                                                             │
│  2. Enviar a OpenAI GPT-4o-mini                           │
│     └─ Latencia: ~500-2000ms                              │
│                                                             │
│  3. Recibir respuesta JSON:                                │
│     {                                                      │
│       "actions": ["track_face", "move_forward"],          │
│       "reasoning": "Detected face and voice command...",  │
│       "priority": "high"                                   │
│     }                                                      │
│                                                             │
│  4. Parsear y retornar acciones:                          │
│     └─ ['track_face', 'move_forward']                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4. FASE DE ACCIÓN

```
┌─────────────────────────────────────────────────────────────┐
│                      ACCIÓN                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Para cada acción en ['track_face', 'move_forward_slow']:  │
│                                                             │
│  Acción 1: 'track_face'                                    │
│  ├─ Obtener centro de cara: (320, 240)                    │
│  ├─ Calcular error desde centro del frame:                │
│  │  ├─ error_x = 320 - 320 = 0                           │
│  │  └─ error_y = 240 - 240 = 0                           │
│  ├─ Ajustar servos de cámara:                             │
│  │  ├─ pan_adjustment = 0 * 0.3 * 0.1 = 0               │
│  │  └─ tilt_adjustment = 0 * 0.3 * 0.1 = 0              │
│  └─ RobotController.set_camera_pan(0)                     │
│     RobotController.set_camera_tilt(-10)                  │
│                                                             │
│  Acción 2: 'move_forward_slow'                            │
│  ├─ Velocidad = 15 (slow_speed)                           │
│  └─ RobotController.move_forward(speed=15)                │
│     └─ Envía señal PWM a motores                          │
│                                                             │
│  Resultado:                                                │
│  ├─ Cámara centrada en cara                               │
│  └─ Robot avanzando a velocidad lenta                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
```

### 5. FASE DE EVALUACIÓN

```
┌─────────────────────────────────────────────────────────────┐
│                    EVALUACIÓN                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RobotController.check_safety()                            │
│                                                             │
│  1. Verificar obstáculo de emergencia:                     │
│     ├─ Distancia actual: 45.3cm                           │
│     ├─ Umbral de emergencia: 10cm                         │
│     └─ 45.3 > 10? ✓ OK                                    │
│                                                             │
│  2. Verificar tiempo de movimiento continuo:               │
│     ├─ Tiempo transcurrido: 2.3s                          │
│     ├─ Tiempo máximo: 5.0s                                │
│     └─ 2.3 < 5.0? ✓ OK                                    │
│                                                             │
│  3. Actualizar métricas:                                   │
│     ├─ loop_count += 1                                     │
│     ├─ avg_loop_time = 0.098s                             │
│     └─ Registrar en logs                                   │
│                                                             │
│  Resultado: ✓ Seguro continuar                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
                            └──────┐
                                   │
                                   ▼
                    ┌──────────────────────┐
                    │  Esperar 0.002s      │
                    │  (mantener 10 Hz)    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  VOLVER A PERCEPCIÓN │
                    └──────────────────────┘
```

## Flujo de Datos por Componente

### VisionSensor → ContextBuilder

```
VisionSensor.capture_frame()
    │
    ├─ faces: [{'x': 320, 'y': 240, 'width': 100, 'height': 120}]
    ├─ colors: [{'x': 400, 'y': 300, 'width': 80, 'height': 90, 'color': 'red'}]
    ├─ qr_codes: []
    ├─ gestures: []
    └─ traffic_signs: []
    │
    ▼
ContextBuilder.build_context()
    │
    ├─ face_detected: True (len(faces) > 0)
    ├─ color_detected: True (len(colors) > 0)
    ├─ color_size: 7200 (80 * 90)
    └─ ...
```

### AudioSensor → ContextBuilder

```
AudioSensor.get_last_transcription()
    │
    └─ "forward please"
    │
    ▼
ContextBuilder.build_context()
    │
    ├─ voice_detected: True (len(text) > 0)
    └─ voice_text: "forward please"
```

### ContextBuilder → RuleEngine

```
Context:
{
    'face_detected': True,
    'color_detected': True,
    'color_size': 7200,
    'voice_detected': True,
    'voice_text': "forward please",
    'obstacle_distance': 45.3,
    'has_obstacle': False,
    'idle_time': 0.5,
    'is_moving': True
}
    │
    ▼
RuleEngine.evaluate(context)
    │
    └─ Evalúa reglas en orden de prioridad
    │
    ▼
Actions: ['track_face', 'move_forward_slow']
```

### RuleEngine → RobotController

```
Actions: ['track_face', 'move_forward_slow']
    │
    ├─ 'track_face'
    │  └─ RobotController.track_object(320, 240)
    │     ├─ set_camera_pan(0)
    │     └─ set_camera_tilt(-10)
    │
    └─ 'move_forward_slow'
       └─ RobotController.move_forward(speed=15)
          └─ Picarx.forward(15)
             └─ Motores PWM
```

## Timing del Loop

```
Ciclo completo @ 10 Hz (100ms):

0ms    ┌─ Percepción (30ms)
       │  ├─ Captura de visión: 20ms
       │  ├─ Lectura de audio: 5ms
       │  └─ Lectura de distancia: 5ms
       │
30ms   ├─ Construcción de contexto (5ms)
       │
35ms   ├─ Decisión (10ms con reglas, 500-2000ms con LLM)
       │  └─ Evaluación de reglas
       │
45ms   ├─ Acción (40ms)
       │  ├─ Ajuste de cámara: 20ms
       │  └─ Control de motores: 20ms
       │
85ms   ├─ Evaluación (10ms)
       │  └─ Verificaciones de seguridad
       │
95ms   ├─ Actualización de métricas (3ms)
       │
98ms   └─ Espera (2ms) para mantener 10 Hz
       
100ms  ┌─ Siguiente ciclo...
```

## Flujo de Comandos de Voz

```
Usuario dice: "forward"
    │
    ▼
Micrófono captura audio
    │
    ▼
AudioSensor procesa con Vosk
    │
    ├─ Transcripción: "forward"
    │
    ▼
ContextBuilder
    │
    ├─ voice_detected: True
    ├─ voice_text: "forward"
    │
    ▼
RuleEngine evalúa
    │
    ├─ Regla 'voice_command' cumple
    ├─ Acción: 'execute_command'
    │
    ▼
FeedbackLoop._execute_voice_command()
    │
    ├─ Parsea comando: "forward" → 'forward'
    ├─ Mapea a acción: lambda: robot.move_forward(duration=1.0)
    │
    ▼
RobotController.move_forward(duration=1.0)
    │
    └─ Robot avanza 1 segundo
```

## Flujo de Seguridad

```
Cada ciclo del loop:
    │
    ▼
RobotController.check_safety()
    │
    ├─ ¿Obstáculo < 10cm?
    │  ├─ SÍ → STOP inmediato ⚠️
    │  └─ NO → Continuar ✓
    │
    ├─ ¿Movimiento > 5s continuo?
    │  ├─ SÍ → STOP automático ⚠️
    │  └─ NO → Continuar ✓
    │
    └─ Retorna: True (seguro) o False (detener)
```

## Resumen de Latencias

| Componente | Latencia Típica |
|------------|----------------|
| Captura de visión | 20-30ms |
| Detección de objetos | 10-20ms |
| Reconocimiento de voz (Vosk) | 50-100ms |
| Motor de reglas | 1-5ms |
| Motor LLM (OpenAI) | 500-2000ms |
| Control de motores | 10-20ms |
| Control de servos | 20-30ms |
| **Ciclo completo (reglas)** | **~100ms (10 Hz)** |
| **Ciclo completo (LLM)** | **~600-2100ms (0.5-1.6 Hz)** |

---

Este flujo de datos muestra cómo la información viaja desde los sensores hasta las acciones del robot en un ciclo continuo de feedback.
