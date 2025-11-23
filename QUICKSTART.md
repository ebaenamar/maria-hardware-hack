# 🚀 Quick Start Guide

## ⚡ Instalación en 5 Minutos

### Paso 1: Clonar el Repositorio
```bash
cd ~
git clone <url-del-repo> picar-x-feedback-loop
cd picar-x-feedback-loop
```

### Paso 2: Ejecutar Instalación Automática
```bash
chmod +x install.sh
./install.sh
```

Este script instalará:
- ✅ Dependencias del sistema
- ✅ robot-hat y picar-x
- ✅ Librerías Python
- ✅ Modelo Vosk para reconocimiento de voz
- ✅ Configuración de audio I2S

### Paso 3: Calibrar el Robot
```bash
cd /tmp/picar-x/example
sudo python3 calibration.py
```

### Paso 4: Ejecutar Primer Ejemplo
```bash
cd ~/picar-x-feedback-loop
sudo python3 examples/basic_loop.py
```

¡Listo! Tu robot ahora tiene un feedback loop funcionando.

---

## 🎯 Primeros Pasos

### Opción A: Demo Interactivo (Recomendado)
```bash
sudo python3 examples/demo.py
```

El demo te permite probar todos los modos:
1. Seguimiento de caras
2. Seguimiento de colores
3. Evitar obstáculos
4. Control por voz
5. Exploración autónoma
6. Decisiones con IA (LLM)

### Opción B: Ejemplos Individuales

**Modo Básico (Reglas)**
```bash
sudo python3 examples/basic_loop.py
```

**Control por Voz**
```bash
sudo python3 examples/voice_control.py
# Di: "forward", "stop", "take photo", etc.
```

**Seguimiento de Objetos**
```bash
sudo python3 examples/object_tracking.py
# Muestra tu cara o un objeto rojo
```

---

## 🔧 Configuración Rápida

### Cambiar Color a Seguir

Edita `config/settings.py`:
```python
VISION_CONFIG = {
    'default_color': 'blue',  # Cambiar a: red, orange, yellow, green, blue, purple
}
```

### Ajustar Velocidad

```python
ROBOT_CONFIG = {
    'default_speed': 25,  # Reducir para más control
}
```

### Habilitar LLM (Opcional)

1. Crear archivo de secrets:
```bash
cp config/secret.py.example config/secret.py
nano config/secret.py
```

2. Añadir tu API key:
```python
OPENAI_API_KEY = "sk-..."
```

3. Ejecutar ejemplo avanzado:
```bash
sudo python3 examples/advanced_loop.py
```

---

## 📱 Comandos de Voz

### Movimiento
- `"forward"` / `"adelante"` → Avanzar
- `"backward"` / `"atrás"` → Retroceder
- `"left"` / `"izquierda"` → Girar izquierda
- `"right"` / `"derecha"` → Girar derecha
- `"stop"` / `"para"` → Detener

### Modos
- `"follow me"` / `"sígueme"` → Modo seguimiento
- `"explore"` / `"explora"` → Modo exploración

### Otros
- `"take photo"` / `"toma foto"` → Capturar imagen
- `"status"` / `"estado"` → Reportar estado

---

## 🎮 Modos de Operación

### 1. AUTONOMOUS (Autónomo)
El robot sigue reglas predefinidas:
- Sigue caras detectadas
- Se acerca a colores
- Evita obstáculos
- Explora cuando no hay actividad

### 2. VOICE_CONTROL (Control por Voz)
El robot espera y ejecuta comandos de voz.

### 3. TRACKING (Seguimiento)
El robot se enfoca en seguir objetos (caras o colores).

### 4. EXPLORATION (Exploración)
El robot explora libremente evitando obstáculos.

---

## 🔍 Verificar que Todo Funciona

### Test de Visión
```bash
cd /tmp/picar-x/example
sudo python3 7.computer_vision.py
```
Abre en navegador: `http://<ip-del-robot>:9000/mjpg`

### Test de Audio
```bash
# Verificar micrófono
arecord -l

# Grabar y reproducir
arecord -d 3 test.wav
aplay test.wav
```

### Test de Movimiento
```bash
cd /tmp/picar-x/example
sudo python3 1.move.py
```

---

## 🐛 Solución Rápida de Problemas

### "vilib no disponible"
```bash
cd /tmp/picar-x
sudo python3 setup.py install
```

### "Modelo Vosk no encontrado"
```bash
cd ~
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

### Audio no funciona
```bash
cd /tmp/picar-x
sudo bash i2samp.sh
sudo reboot
```

### Robot no responde
1. Verificar batería
2. Verificar conexiones
3. Ejecutar calibración

---

## 📚 Próximos Pasos

### Aprender Más
- Lee `ARCHITECTURE.md` para entender el sistema
- Revisa `EXAMPLES.md` para código de ejemplo
- Consulta `USAGE.md` para uso avanzado

### Personalizar
1. Añade nuevas reglas en `config/settings.py`
2. Crea tus propios ejemplos en `examples/`
3. Modifica comportamientos en `src/`

### Experimentar
- Prueba diferentes colores de seguimiento
- Ajusta velocidades y umbrales
- Combina múltiples sensores
- Crea comportamientos complejos

---

## 💡 Tips Rápidos

### Mejor Rendimiento
```python
# En config/settings.py
LOOP_FREQUENCY = 5  # Reducir si es muy lento
```

### Más Seguridad
```python
ROBOT_CONFIG = {
    'emergency_stop_distance': 15,  # Aumentar distancia de seguridad
}
```

### Debug
```python
# En tu script
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Screenshots Automáticos
```python
VISION_CONFIG = {
    'save_screenshots': True,
}
```

---

## 🎓 Recursos

### Documentación
- [README.md](README.md) - Introducción
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura
- [USAGE.md](USAGE.md) - Guía de uso
- [EXAMPLES.md](EXAMPLES.md) - Ejemplos de código

### Enlaces Externos
- [PiCar-X Docs](https://docs.sunfounder.com/projects/picar-x-v20/)
- [Vosk Models](https://alphacephei.com/vosk/models)
- [OpenAI API](https://platform.openai.com/docs)

---

## ✅ Checklist de Inicio

- [ ] Instalación completada (`./install.sh`)
- [ ] Robot calibrado (`calibration.py`)
- [ ] Ejemplo básico funciona (`basic_loop.py`)
- [ ] Visión funciona (detecta caras/colores)
- [ ] Audio funciona (reconoce voz)
- [ ] Robot se mueve correctamente
- [ ] Screenshots se guardan en `~/Pictures/feedback_loop/`

---

## 🆘 Ayuda

Si tienes problemas:
1. Revisa los logs: `~/picar-x-feedback.log`
2. Verifica la configuración: `config/settings.py`
3. Consulta la documentación completa
4. Ejecuta tests individuales de cada componente

---

**¡Disfruta tu PiCar-X con feedback loop inteligente!** 🤖✨
