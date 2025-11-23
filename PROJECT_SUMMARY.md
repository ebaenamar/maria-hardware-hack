# Resumen del Proyecto: PiCar-X Feedback Loop

## 📋 Descripción

Sistema completo de **feedback loop** para el robot PiCar-X que integra:
- **Visión** (screenshots, detección de objetos, caras, colores)
- **Audio** (reconocimiento de voz con Vosk STT)
- **Toma de decisiones** (motor de reglas o LLM)
- **Acciones del robot** (movimiento, cámara, sensores)

## 🎯 Características Principales

### Percepción Multi-Sensorial
- ✅ Captura de imágenes en tiempo real
- ✅ Detección de caras, colores, QR codes, gestos, señales
- ✅ Reconocimiento de voz con Vosk
- ✅ Sensor ultrasónico para distancia
- ✅ Screenshots automáticos

### Motores de Decisión
- ✅ **Motor de Reglas**: Rápido, predecible, sin latencia
- ✅ **Motor LLM**: Inteligente, adaptativo, con razonamiento
- ✅ Sistema de prioridades configurable
- ✅ Reglas personalizables

### Control del Robot
- ✅ Movimiento (adelante, atrás, giros)
- ✅ Control de cámara (pan/tilt)
- ✅ Seguimiento suave de objetos
- ✅ Evitar obstáculos automático
- ✅ Text-to-Speech (TTS)
- ✅ Verificaciones de seguridad

### Modos de Operación
- ✅ Autónomo (sigue reglas)
- ✅ Control por voz
- ✅ Seguimiento de objetos
- ✅ Exploración libre

## 📁 Estructura del Proyecto

```
picar-x-feedback-loop/
├── README.md                    # Documentación principal
├── ARCHITECTURE.md              # Arquitectura detallada
├── USAGE.md                     # Guía de uso
├── PROJECT_SUMMARY.md           # Este archivo
├── requirements.txt             # Dependencias Python
├── install.sh                   # Script de instalación
├── .gitignore
│
├── config/
│   ├── settings.py              # Configuración central
│   └── secret.py.example        # Ejemplo de API keys
│
├── src/
│   ├── sensors/
│   │   ├── vision_sensor.py     # Captura y análisis de visión
│   │   └── audio_sensor.py      # Captura y análisis de audio
│   │
│   ├── decision/
│   │   ├── rule_engine.py       # Motor de reglas
│   │   └── llm_engine.py        # Motor con LLM
│   │
│   ├── actions/
│   │   └── robot_controller.py  # Control del robot
│   │
│   └── core/
│       └── feedback_loop.py     # Loop principal
│
└── examples/
    ├── basic_loop.py            # Ejemplo básico con reglas
    ├── advanced_loop.py         # Ejemplo con LLM
    ├── voice_control.py         # Control por voz
    ├── object_tracking.py       # Seguimiento de objetos
    └── demo.py                  # Demo interactivo
```

## 🔄 Ciclo de Feedback Loop

```
┌─────────────────────────────────────────────────────────┐
│                    FEEDBACK LOOP                        │
│                                                         │
│  1. PERCEPCIÓN                                         │
│     ├─ Capturar frame de cámara                       │
│     ├─ Detectar objetos (caras, colores, etc.)       │
│     ├─ Escuchar audio (si está habilitado)           │
│     └─ Leer sensor ultrasónico                        │
│                                                         │
│  2. CONSTRUCCIÓN DE CONTEXTO                          │
│     └─ Convertir datos de sensores en contexto       │
│                                                         │
│  3. DECISIÓN                                           │
│     ├─ Evaluar reglas (o consultar LLM)              │
│     └─ Determinar acciones a ejecutar                 │
│                                                         │
│  4. ACCIÓN                                             │
│     ├─ Ejecutar movimientos                           │
│     ├─ Ajustar cámara                                 │
│     └─ Reproducir sonidos/hablar                      │
│                                                         │
│  5. EVALUACIÓN                                         │
│     ├─ Verificar seguridad                            │
│     └─ Ajustar comportamiento                         │
│                                                         │
│  └─────────────────┐                                   │
│                    ↓                                    │
│              (repetir a 10 Hz)                         │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Inicio Rápido

### Instalación

```bash
# En Raspberry Pi con PiCar-X
git clone <url-del-repo>
cd picar-x-feedback-loop
chmod +x install.sh
./install.sh
```

### Uso Básico

```bash
# Ejemplo con reglas (sin LLM)
sudo python3 examples/basic_loop.py

# Control por voz
sudo python3 examples/voice_control.py

# Demo interactivo
sudo python3 examples/demo.py
```

### Uso Avanzado (con LLM)

```bash
# Configurar API key
cp config/secret.py.example config/secret.py
nano config/secret.py  # Añadir OPENAI_API_KEY

# Ejecutar con LLM
sudo python3 examples/advanced_loop.py
```

## 🎮 Ejemplos de Comportamiento

### 1. Seguimiento de Cara
```
Robot detecta cara → Ajusta cámara → Se mueve hacia la cara → Evita obstáculos
```

### 2. Seguimiento de Color
```
Robot detecta color rojo → Centra objeto → Se acerca → Se detiene cerca
```

### 3. Evitar Obstáculos
```
Robot avanza → Detecta obstáculo → Se detiene → Retrocede → Gira → Continúa
```

### 4. Control por Voz
```
Usuario: "forward" → Robot avanza 1 segundo → Se detiene
Usuario: "follow me" → Robot entra en modo seguimiento
```

### 5. Exploración Autónoma
```
Robot explora → Escanea entorno → Evita obstáculos → Reacciona a estímulos
```

## 🔧 Configuración Clave

### Frecuencia del Loop
```python
LOOP_FREQUENCY = 10  # Hz (10 ciclos por segundo)
```

### Velocidades
```python
ROBOT_CONFIG = {
    'default_speed': 30,  # 0-100
    'slow_speed': 15,
    'fast_speed': 50,
}
```

### Reglas de Comportamiento
```python
BEHAVIOR_RULES = {
    'follow_face': {
        'priority': 0.9,
        'conditions': {'face_detected': True},
        'actions': ['track_face', 'move_forward_slow'],
    },
    # ... más reglas
}
```

### Comandos de Voz
```python
VOICE_COMMANDS = {
    'forward': ['forward', 'go forward', 'adelante'],
    'stop': ['stop', 'halt', 'para'],
    # ... más comandos
}
```

## 📊 Métricas y Rendimiento

### Rendimiento Típico
- **Frecuencia**: 10 Hz (100ms por ciclo)
- **Latencia de visión**: ~30ms
- **Latencia de audio**: ~100ms (Vosk)
- **Latencia de LLM**: ~500-2000ms (depende del modelo)

### Optimizaciones
- Motor de reglas: Sin latencia de red
- Procesamiento asíncrono de audio
- Caché de detecciones
- Throttling de llamadas a LLM

## 🛡️ Seguridad

### Verificaciones Automáticas
- ✅ Distancia de emergencia (10cm)
- ✅ Tiempo máximo de movimiento continuo (5s)
- ✅ Verificación en cada ciclo del loop
- ✅ Prioridad máxima para evitar obstáculos

### Configuración de Seguridad
```python
ROBOT_CONFIG = {
    'emergency_stop_distance': 10,  # cm
    'max_continuous_movement': 5.0,  # segundos
}
```

## 🧪 Testing

### Modo Simulación
```python
# Para desarrollo sin hardware
PICARX_AVAILABLE = False
```

### Logs de Debug
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Documentación

- **README.md**: Introducción y características
- **ARCHITECTURE.md**: Arquitectura detallada del sistema
- **USAGE.md**: Guía completa de uso
- **PROJECT_SUMMARY.md**: Este resumen

## 🔮 Extensiones Futuras

### Posibles Mejoras
- [ ] Integración con más LLMs (Claude, Llama, etc.)
- [ ] Mapeo y navegación SLAM
- [ ] Reconocimiento de objetos con YOLO
- [ ] Control remoto vía web interface
- [ ] Grabación y replay de comportamientos
- [ ] Aprendizaje por refuerzo
- [ ] Multi-robot coordination

### Personalización
- Añadir nuevos sensores (IMU, GPS, etc.)
- Crear nuevas reglas de comportamiento
- Integrar con servicios externos (APIs, bases de datos)
- Desarrollar comportamientos complejos

## 📝 Notas Técnicas

### Dependencias Principales
- **robot-hat**: Librería de hardware del PiCar-X
- **picar-x**: API del robot
- **vilib**: Librería de visión
- **vosk**: Speech-to-Text
- **openai**: API de OpenAI (opcional)
- **opencv-python**: Procesamiento de imágenes
- **pyaudio**: Captura de audio

### Requisitos del Sistema
- Raspberry Pi 4 (recomendado)
- PiCar-X completo con cámara
- Micrófono USB o I2S
- Conexión a internet (para LLM)

## 🎓 Conceptos Implementados

### Robótica
- Feedback loop
- Sensor fusion
- Reactive behavior
- Deliberative planning

### IA/ML
- Computer vision
- Speech recognition
- Natural language processing
- Rule-based systems
- LLM integration

### Software
- Modular architecture
- Event-driven programming
- Asynchronous processing
- Configuration management

## 📄 Licencia

GNU General Public License v2.0

## 👥 Contribuciones

Este proyecto está diseñado para ser extensible y educativo. Siéntete libre de:
- Añadir nuevas funcionalidades
- Mejorar algoritmos existentes
- Crear nuevos ejemplos
- Reportar bugs
- Sugerir mejoras

---

**Desarrollado para PiCar-X v2.0**

*Sistema de feedback loop completo con visión, audio y toma de decisiones inteligente*
