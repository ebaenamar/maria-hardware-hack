#!/usr/bin/env python3
"""
Ejemplo avanzado de feedback loop con LLM
Usa un modelo de lenguaje para tomar decisiones inteligentes
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
    print("PiCar-X Feedback Loop - Ejemplo Avanzado")
    print("Motor de decisión: LLM (GPT-4o-mini)")
    print("=" * 60)
    print()
    
    # Verificar configuración
    try:
        from config.secret import OPENAI_API_KEY
        if not OPENAI_API_KEY:
            print("ERROR: OPENAI_API_KEY no configurada")
            print("Crea el archivo config/secret.py con:")
            print("  OPENAI_API_KEY = 'tu-api-key'")
            return
    except ImportError:
        print("ERROR: Archivo config/secret.py no encontrado")
        print("Crea el archivo config/secret.py con:")
        print("  OPENAI_API_KEY = 'tu-api-key'")
        print("  ANTHROPIC_API_KEY = 'tu-api-key'  # Opcional")
        return
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Crear feedback loop con LLM
    loop = FeedbackLoop(use_llm=True)
    
    print("Inicializando sistema...")
    print()
    
    try:
        # Iniciar en modo autónomo
        print("Iniciando feedback loop con LLM")
        print("El robot usará inteligencia artificial para:")
        print("  - Analizar el entorno en tiempo real")
        print("  - Tomar decisiones contextuales")
        print("  - Adaptar su comportamiento dinámicamente")
        print("  - Priorizar seguridad y eficiencia")
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
        print("NOTA: El uso de LLM puede aumentar el tiempo por ciclo")
        print("      debido a las llamadas a la API")
        print()


if __name__ == '__main__':
    main()
