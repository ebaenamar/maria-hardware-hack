#!/usr/bin/env python3
"""
Demo interactivo del sistema de feedback loop
Muestra todas las capacidades del sistema
"""

import sys
import os
import time

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.feedback_loop import FeedbackLoop, LoopMode
import logging


def print_banner():
    """Imprime el banner del demo"""
    print("\n" + "=" * 70)
    print(" " * 15 + "PiCar-X FEEDBACK LOOP DEMO")
    print("=" * 70)
    print()


def print_menu():
    """Imprime el menú de opciones"""
    print("\n" + "-" * 70)
    print("SELECCIONA UN MODO DE DEMOSTRACIÓN:")
    print("-" * 70)
    print("1. Seguimiento de Caras")
    print("   → El robot detecta y sigue caras automáticamente")
    print()
    print("2. Seguimiento de Color Rojo")
    print("   → El robot busca y se acerca a objetos rojos")
    print()
    print("3. Evitar Obstáculos")
    print("   → El robot navega evitando obstáculos")
    print()
    print("4. Control por Voz")
    print("   → Controla el robot con comandos de voz")
    print()
    print("5. Exploración Autónoma")
    print("   → El robot explora el entorno libremente")
    print()
    print("6. Demo con LLM (requiere API key)")
    print("   → Usa IA para tomar decisiones inteligentes")
    print()
    print("0. Salir")
    print("-" * 70)


def demo_face_tracking(loop):
    """Demo de seguimiento de caras"""
    print("\n" + "=" * 70)
    print("DEMO: SEGUIMIENTO DE CARAS")
    print("=" * 70)
    print()
    print("El robot:")
    print("  • Detectará caras en su campo de visión")
    print("  • Ajustará la cámara para mantener la cara centrada")
    print("  • Se moverá lentamente hacia la cara")
    print("  • Evitará obstáculos automáticamente")
    print()
    print("Colócate frente al robot y observa cómo te sigue")
    print()
    input("Presiona ENTER para iniciar (Ctrl+C para detener)...")
    
    # Configurar
    loop.vision.config['enable_face_detect'] = True
    loop.vision.config['enable_color_detect'] = False
    loop.decision_engine.enable_rule('follow_face', True)
    loop.decision_engine.enable_rule('approach_color', False)
    
    # Iniciar
    loop.start(mode=LoopMode.TRACKING)


def demo_color_tracking(loop):
    """Demo de seguimiento de color"""
    print("\n" + "=" * 70)
    print("DEMO: SEGUIMIENTO DE COLOR ROJO")
    print("=" * 70)
    print()
    print("El robot:")
    print("  • Detectará objetos de color rojo")
    print("  • Ajustará la cámara para seguir el objeto")
    print("  • Se acercará al objeto detectado")
    print("  • Se detendrá al llegar cerca")
    print()
    print("Muestra un objeto rojo al robot")
    print()
    input("Presiona ENTER para iniciar (Ctrl+C para detener)...")
    
    # Configurar
    loop.vision.set_color_detection('red')
    loop.vision.config['enable_face_detect'] = False
    loop.decision_engine.enable_rule('follow_face', False)
    loop.decision_engine.enable_rule('approach_color', True)
    
    # Iniciar
    loop.start(mode=LoopMode.TRACKING)


def demo_obstacle_avoidance(loop):
    """Demo de evitar obstáculos"""
    print("\n" + "=" * 70)
    print("DEMO: EVITAR OBSTÁCULOS")
    print("=" * 70)
    print()
    print("El robot:")
    print("  • Se moverá hacia adelante")
    print("  • Detectará obstáculos con el sensor ultrasónico")
    print("  • Se detendrá y girará al detectar un obstáculo")
    print("  • Continuará explorando")
    print()
    print("Coloca obstáculos en el camino del robot")
    print()
    input("Presiona ENTER para iniciar (Ctrl+C para detener)...")
    
    # Configurar
    loop.decision_engine.enable_rule('avoid_obstacle', True)
    loop.decision_engine.enable_rule('explore', True)
    
    # Iniciar
    loop.start(mode=LoopMode.EXPLORATION)


def demo_voice_control(loop):
    """Demo de control por voz"""
    print("\n" + "=" * 70)
    print("DEMO: CONTROL POR VOZ")
    print("=" * 70)
    print()
    print("Comandos disponibles:")
    print("  • 'forward' / 'adelante' - Mover adelante")
    print("  • 'backward' / 'atrás' - Mover atrás")
    print("  • 'left' / 'izquierda' - Girar izquierda")
    print("  • 'right' / 'derecha' - Girar derecha")
    print("  • 'stop' / 'para' - Detener")
    print("  • 'take photo' / 'toma foto' - Capturar imagen")
    print("  • 'status' / 'estado' - Reportar estado")
    print()
    input("Presiona ENTER para iniciar (Ctrl+C para detener)...")
    
    # Habilitar control por voz
    loop.enable_voice_control()
    
    # Iniciar
    loop.start(mode=LoopMode.VOICE_CONTROL)


def demo_exploration(loop):
    """Demo de exploración autónoma"""
    print("\n" + "=" * 70)
    print("DEMO: EXPLORACIÓN AUTÓNOMA")
    print("=" * 70)
    print()
    print("El robot:")
    print("  • Explorará el entorno libremente")
    print("  • Evitará obstáculos automáticamente")
    print("  • Escaneará el entorno periódicamente")
    print("  • Reaccionará a estímulos (caras, colores)")
    print()
    print("Deja que el robot explore libremente")
    print()
    input("Presiona ENTER para iniciar (Ctrl+C para detener)...")
    
    # Configurar
    loop.decision_engine.enable_rule('explore', True)
    loop.decision_engine.enable_rule('avoid_obstacle', True)
    
    # Iniciar
    loop.start(mode=LoopMode.EXPLORATION)


def demo_llm(loop):
    """Demo con LLM"""
    print("\n" + "=" * 70)
    print("DEMO: DECISIONES CON IA (LLM)")
    print("=" * 70)
    print()
    
    # Verificar API key
    try:
        from config.secret import OPENAI_API_KEY
        if not OPENAI_API_KEY:
            print("ERROR: OPENAI_API_KEY no configurada")
            print()
            print("Para usar este demo:")
            print("1. Crea el archivo config/secret.py")
            print("2. Añade: OPENAI_API_KEY = 'tu-api-key'")
            print()
            input("Presiona ENTER para volver al menú...")
            return
    except ImportError:
        print("ERROR: Archivo config/secret.py no encontrado")
        print()
        print("Para usar este demo:")
        print("1. Crea el archivo config/secret.py")
        print("2. Añade: OPENAI_API_KEY = 'tu-api-key'")
        print()
        input("Presiona ENTER para volver al menú...")
        return
    
    print("El robot usará GPT-4o-mini para:")
    print("  • Analizar el entorno en tiempo real")
    print("  • Tomar decisiones contextuales inteligentes")
    print("  • Explicar su razonamiento")
    print("  • Adaptar su comportamiento dinámicamente")
    print()
    print("NOTA: Requiere conexión a internet")
    print()
    input("Presiona ENTER para iniciar (Ctrl+C para detener)...")
    
    # Crear nuevo loop con LLM
    llm_loop = FeedbackLoop(use_llm=True)
    
    # Iniciar
    llm_loop.start(mode=LoopMode.AUTONOMOUS)


def main():
    """Función principal"""
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print_banner()
    
    print("Inicializando sistema...")
    
    # Crear feedback loop
    loop = FeedbackLoop(use_llm=False)
    
    while True:
        try:
            print_menu()
            choice = input("\nSelecciona una opción (0-6): ").strip()
            
            if choice == '0':
                print("\n¡Hasta luego!")
                break
            
            elif choice == '1':
                demo_face_tracking(loop)
            
            elif choice == '2':
                demo_color_tracking(loop)
            
            elif choice == '3':
                demo_obstacle_avoidance(loop)
            
            elif choice == '4':
                demo_voice_control(loop)
            
            elif choice == '5':
                demo_exploration(loop)
            
            elif choice == '6':
                demo_llm(loop)
            
            else:
                print("\nOpción inválida. Intenta de nuevo.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\nDemo interrumpido. Volviendo al menú...")
            loop.stop()
            time.sleep(1)
        
        except Exception as e:
            print(f"\nError: {e}")
            loop.stop()
            time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n¡Adiós!")
    except Exception as e:
        print(f"\nError fatal: {e}")
