# PiCar-X Feedback Loop System

Sistema avanzado de feedback loop para PiCar-X que integra visión, audio y toma de decisiones basada en IA.

## 🚀 Inicio Rápido

```bash
# Instalación automática
./install.sh

# Ejecutar demo interactivo
sudo python3 examples/demo.py
```

📖 **[Ver Guía de Inicio Rápido](QUICKSTART.md)**

## ✨ Características

- **Captura de Visión**: Screenshots en tiempo real de la cámara con detección de objetos, colores, caras y señales
- **Captura de Audio**: Reconocimiento de voz con Vosk STT y wake words
- **Motor de Decisión**: Sistema basado en reglas y opcionalmente LLM para tomar decisiones
- **Sistema de Acciones**: Control completo del robot (movimiento, cámara, sonidos)
- **Feedback Loop**: Ciclo continuo de percepción → decisión → acción → evaluación
- **4 Modos de Operación**: Autónomo, Control por Voz, Seguimiento, Exploración

## Arquitectura

```
picar-x-feedback-loop/
├── src/
│   ├── sensors/
│   │   ├── vision_sensor.py      # Captura y análisis de visión
│   │   └── audio_sensor.py       # Captura y análisis de audio
│   ├── decision/
│   │   ├── rule_engine.py        # Motor de reglas
│   │   └── llm_engine.py         # Motor con LLM (opcional)
│   ├── actions/
│   │   └── robot_controller.py   # Control del robot
│   └── core/
│       └── feedback_loop.py      # Loop principal
├── config/
│   └── settings.py               # Configuración
├── examples/
│   ├── basic_loop.py             # Ejemplo básico
│   └── advanced_loop.py          # Ejemplo avanzado con LLM
└── requirements.txt
```

## Instalación

### Prerrequisitos en Raspberry Pi

```bash
# Instalar dependencias del PiCar-X
git clone -b v2.0 https://github.com/sunfounder/robot-hat.git
cd robot-hat
sudo python3 setup.py install

git clone -b v2.0 https://github.com/sunfounder/picar-x.git
cd picar-x
sudo python3 setup.py install

# Instalar módulos adicionales
sudo apt-get install portaudio19-dev python3-pyaudio
pip3 install -r requirements.txt
```

### Instalar este proyecto

```bash
git clone <este-repo>
cd picar-x-feedback-loop
pip3 install -r requirements.txt
```

## Uso

### Ejemplo Básico (sin LLM)

```bash
sudo python3 examples/basic_loop.py
```

### Ejemplo Avanzado (con LLM)

```bash
# Configurar API key en config/secret.py
echo "OPENAI_API_KEY = 'tu-api-key'" > config/secret.py

sudo python3 examples/advanced_loop.py
```

## Configuración

Edita `config/settings.py` para personalizar:

- Frecuencia del feedback loop
- Umbrales de detección
- Comportamientos del robot
- Configuración de sensores

## Ejemplos de Uso

### Seguimiento de Objetos con Feedback

El robot detecta un objeto rojo, lo sigue, y ajusta su comportamiento basándose en la distancia.

### Navegación Autónoma

El robot navega evitando obstáculos, usando visión y ultrasonido en un feedback loop continuo.

### Interacción por Voz

El robot escucha comandos, los procesa, ejecuta acciones y reporta el resultado.

## 📚 Documentación Completa

- **[QUICKSTART.md](QUICKSTART.md)** - Guía de inicio en 5 minutos
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitectura detallada del sistema
- **[DATAFLOW.md](DATAFLOW.md)** - Flujo de datos y diagramas
- **[USAGE.md](USAGE.md)** - Guía completa de uso y configuración
- **[EXAMPLES.md](EXAMPLES.md)** - 10+ ejemplos de código
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Resumen ejecutivo

## 🎮 Ejemplos Disponibles

| Ejemplo | Descripción | Comando |
|---------|-------------|---------|
| **Demo Interactivo** | Menú con todos los modos | `sudo python3 examples/demo.py` |
| **Modo Básico** | Feedback loop con reglas | `sudo python3 examples/basic_loop.py` |
| **Modo Avanzado** | Feedback loop con LLM | `sudo python3 examples/advanced_loop.py` |
| **Control por Voz** | Comandos de voz | `sudo python3 examples/voice_control.py` |
| **Seguimiento** | Seguir objetos | `sudo python3 examples/object_tracking.py` |

## 🔧 Configuración Rápida

### Cambiar Color a Seguir
```python
# En config/settings.py
VISION_CONFIG['default_color'] = 'blue'  # red, orange, yellow, green, blue, purple
```

### Ajustar Velocidad
```python
ROBOT_CONFIG['default_speed'] = 25  # 0-100
```

### Habilitar LLM
```bash
cp config/secret.py.example config/secret.py
# Editar y añadir: OPENAI_API_KEY = 'sk-...'
```

## 🎯 Casos de Uso

1. **Seguimiento de Caras** - El robot detecta y sigue personas automáticamente
2. **Seguimiento de Colores** - Se acerca a objetos de color específico
3. **Evitar Obstáculos** - Navegación autónoma segura
4. **Control por Voz** - Comandos en inglés y español
5. **Exploración Autónoma** - Explora el entorno libremente
6. **Decisiones con IA** - Usa LLM para razonamiento complejo

## 🛡️ Seguridad

- ✅ Distancia de emergencia: 10cm (detención automática)
- ✅ Tiempo máximo de movimiento continuo: 5s
- ✅ Verificación en cada ciclo del loop
- ✅ Prioridad máxima para evitar obstáculos

## 🤝 Contribuciones

Este proyecto está diseñado para ser extensible y educativo. Siéntete libre de:
- Añadir nuevas funcionalidades
- Mejorar algoritmos existentes
- Crear nuevos ejemplos
- Reportar bugs y sugerir mejoras

## 📄 Licencia

GNU General Public License v2.0

---

**Desarrollado para PiCar-X v2.0** | Sistema completo de feedback loop con visión, audio y toma de decisiones inteligente
