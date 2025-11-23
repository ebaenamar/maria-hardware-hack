#!/usr/bin/env python3
"""
Ejemplo de control por voz con feedback loop
El robot escucha comandos y responde en consecuencia
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.feedback_loop import FeedbackLoop, LoopMode
import logging


def main():
    """Función principal"""
    print("=" * 60)
    print("PiCar-X Feedback Loop - Control por Voz")
    print("=" * 60)
    print()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Crear feedback loop
    loop = FeedbackLoop(use_llm=False)
    
    print("Inicializando sistema...")
    print()
    
    print("COMANDOS DE VOZ DISPONIBLES:")
    print("-" * 60)
    print("Movimiento:")
    print("  - 'forward' / 'adelante': Mover hacia adelante")
    print("  - 'backward' / 'atrás': Mover hacia atrás")
    print("  - 'left' / 'izquierda': Girar a la izquierda")
    print("  - 'right' / 'derecha': Girar a la derecha")
    print("  - 'stop' / 'para': Detener")
    print()
    print("Modos:")
    print("  - 'follow me' / 'sígueme': Modo seguimiento")
    print("  - 'explore' / 'explora': Modo exploración")
    print("  - 'track red' / 'busca rojo': Seguir color rojo")
    print("  - 'track blue' / 'busca azul': Seguir color azul")
    print()
    print("Otros:")
    print("  - 'take photo' / 'toma foto': Capturar imagen")
    print("  - 'status' / 'estado': Reportar estado")
    print()
    print("Presiona Ctrl+C para detener")
    print("=" * 60)
    print()
    
    try:
        # Habilitar control por voz
        loop.enable_voice_control()
        
        # Iniciar en modo de control por voz
        loop.start(mode=LoopMode.VOICE_CONTROL)
    
    except KeyboardInterrupt:
        print("\n\nDeteniendo...")
    
    finally:
        # Mostrar métricas
        metrics = loop.get_metrics()
        print()
        print("=" * 60)
        print("MÉTRICAS DEL SISTEMA")
        print("=" * 60)
        print(f"Total de ciclos: {metrics['loop_count']}")
        print(f"Tiempo promedio por ciclo: {metrics['avg_loop_time']:.3f}s")
        print()


if __name__ == '__main__':
    main()
