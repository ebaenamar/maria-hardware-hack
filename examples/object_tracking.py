#!/usr/bin/env python3
"""
Ejemplo de seguimiento de objetos con feedback loop
El robot detecta y sigue objetos (caras, colores) automáticamente
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
    print("PiCar-X Feedback Loop - Seguimiento de Objetos")
    print("=" * 60)
    print()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Crear feedback loop
    loop = FeedbackLoop(use_llm=False)
    
    print("Configurando modo de seguimiento...")
    print()
    
    # Configurar para seguir caras
    print("MODO: Seguimiento de Caras")
    print("-" * 60)
    print("El robot:")
    print("  1. Detectará caras en su campo de visión")
    print("  2. Ajustará la cámara para mantener la cara centrada")
    print("  3. Se moverá hacia adelante lentamente")
    print("  4. Evitará obstáculos automáticamente")
    print()
    print("Para cambiar a seguimiento de color:")
    print("  - Modifica VISION_CONFIG['default_color'] en config/settings.py")
    print("  - Opciones: red, orange, yellow, green, blue, purple")
    print()
    print("Presiona Ctrl+C para detener")
    print("=" * 60)
    print()
    
    try:
        # Habilitar detección de caras
        loop.vision.config['enable_face_detect'] = True
        loop.vision.config['enable_color_detect'] = False
        
        # Habilitar regla de seguimiento
        loop.decision_engine.enable_rule('follow_face', True)
        loop.decision_engine.enable_rule('approach_color', False)
        
        # Iniciar en modo tracking
        loop.start(mode=LoopMode.TRACKING)
    
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
