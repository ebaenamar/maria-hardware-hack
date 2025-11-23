#!/usr/bin/env python3
"""
Ejemplo básico de feedback loop sin LLM
Usa el motor de reglas para tomar decisiones
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
    print("PiCar-X Feedback Loop - Ejemplo Básico")
    print("Motor de decisión: Reglas")
    print("=" * 60)
    print()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Crear feedback loop (sin LLM)
    loop = FeedbackLoop(use_llm=False)
    
    print("Inicializando sistema...")
    print()
    
    try:
        # Iniciar en modo autónomo
        print("Iniciando feedback loop en modo AUTÓNOMO")
        print("El robot seguirá las reglas predefinidas:")
        print("  - Seguir caras detectadas")
        print("  - Acercarse a colores detectados")
        print("  - Evitar obstáculos")
        print("  - Explorar cuando no hay actividad")
        print()
        print("Presiona Ctrl+C para detener")
        print("-" * 60)
        print()
        
        loop.start(mode=LoopMode.AUTONOMOUS)
    
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
        print(f"Modo final: {metrics['mode']}")
        print()


if __name__ == '__main__':
    main()
