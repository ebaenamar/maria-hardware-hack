"""
Sistema de Feedback Loop principal para PiCar-X
Integra sensores, decisión y acciones en un ciclo continuo
"""

import time
import logging
import signal
import sys
from typing import Optional, Dict, List
from enum import Enum

from src.sensors.vision_sensor import VisionSensor
from src.sensors.audio_sensor import AudioSensor
from src.actions.robot_controller import RobotController
from src.decision.rule_engine import RuleEngine, ContextBuilder
from src.decision.llm_engine import LLMEngine
from config.settings import LOOP_FREQUENCY, DECISION_CONFIG, VOICE_COMMANDS


class LoopMode(Enum):
    """Modos de operación del feedback loop"""
    AUTONOMOUS = "autonomous"      # Modo autónomo con reglas
    VOICE_CONTROL = "voice_control"  # Control por voz
    TRACKING = "tracking"          # Seguimiento de objetos
    EXPLORATION = "exploration"    # Exploración libre


class FeedbackLoop:
    """
    Sistema principal de feedback loop que integra percepción, decisión y acción
    """
    
    def __init__(self, use_llm: bool = False):
        """
        Inicializa el feedback loop
        
        Args:
            use_llm: Si True, usa LLM para decisiones. Si False, usa reglas
        """
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Componentes del sistema
        self.vision = VisionSensor()
        self.audio = AudioSensor()
        self.robot = RobotController()
        
        # Motor de decisión
        self.use_llm = use_llm
        if use_llm:
            self.decision_engine = LLMEngine()
            self.logger.info("Usando motor LLM para decisiones")
        else:
            self.decision_engine = RuleEngine()
            self.logger.info("Usando motor de reglas para decisiones")
        
        self.context_builder = ContextBuilder()
        
        # Estado del loop
        self.is_running = False
        self.mode = LoopMode.AUTONOMOUS
        self.loop_frequency = LOOP_FREQUENCY
        self.loop_count = 0
        
        # Métricas
        self.last_loop_time = 0
        self.avg_loop_time = 0
        
        # Manejo de señales para shutdown limpio
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Maneja señales de sistema para shutdown limpio"""
        self.logger.info("Señal de interrupción recibida. Deteniendo...")
        self.stop()
        sys.exit(0)
    
    def initialize(self) -> bool:
        """
        Inicializa todos los componentes del sistema
        
        Returns:
            True si la inicialización fue exitosa
        """
        self.logger.info("Inicializando sistema de feedback loop...")
        
        # Inicializar robot
        if not self.robot.initialize():
            self.logger.error("Fallo al inicializar robot")
            return False
        
        # Inicializar visión
        if not self.vision.start():
            self.logger.error("Fallo al inicializar visión")
            return False
        
        # Inicializar audio (opcional)
        if not self.audio.start():
            self.logger.warning("Audio no disponible, continuando sin audio")
        
        self.logger.info("Sistema inicializado correctamente")
        return True
    
    def start(self, mode: LoopMode = LoopMode.AUTONOMOUS):
        """
        Inicia el feedback loop
        
        Args:
            mode: Modo de operación
        """
        if not self.initialize():
            self.logger.error("No se pudo inicializar el sistema")
            return
        
        self.is_running = True
        self.mode = mode
        self.loop_count = 0
        
        self.logger.info(f"Iniciando feedback loop en modo: {mode.value}")
        
        try:
            self._run_loop()
        except Exception as e:
            self.logger.error(f"Error en el loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Detiene el feedback loop y limpia recursos"""
        self.logger.info("Deteniendo feedback loop...")
        
        self.is_running = False
        
        # Detener componentes
        self.robot.cleanup()
        self.vision.stop()
        self.audio.stop()
        
        self.logger.info(f"Loop detenido. Total de ciclos: {self.loop_count}")
        self.logger.info(f"Tiempo promedio por ciclo: {self.avg_loop_time:.3f}s")
    
    def _run_loop(self):
        """Ejecuta el loop principal"""
        loop_period = 1.0 / self.loop_frequency
        
        while self.is_running:
            loop_start = time.time()
            
            try:
                # 1. PERCEPCIÓN: Capturar datos de sensores
                perception_data = self._perceive()
                
                # 2. DECISIÓN: Evaluar y decidir acciones
                actions = self._decide(perception_data)
                
                # 3. ACCIÓN: Ejecutar acciones
                self._act(actions, perception_data)
                
                # 4. EVALUACIÓN: Verificar seguridad y estado
                self._evaluate()
                
                # Actualizar métricas
                self.loop_count += 1
                loop_time = time.time() - loop_start
                self.avg_loop_time = (self.avg_loop_time * (self.loop_count - 1) + loop_time) / self.loop_count
                
                # Log periódico
                if self.loop_count % 50 == 0:
                    self.logger.info(f"Loop #{self.loop_count} - Tiempo: {loop_time:.3f}s")
                
                # Esperar para mantener frecuencia
                sleep_time = loop_period - loop_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    self.logger.warning(f"Loop tomó más tiempo que el período: {loop_time:.3f}s")
            
            except Exception as e:
                self.logger.error(f"Error en ciclo del loop: {e}", exc_info=True)
                time.sleep(0.5)  # Pausa de recuperación
    
    def _perceive(self) -> Dict:
        """
        Fase de percepción: captura datos de todos los sensores
        
        Returns:
            Diccionario con datos de percepción
        """
        perception = {
            'vision': {},
            'audio': None,
            'distance': 0,
            'robot_state': {},
        }
        
        # Capturar visión
        perception['vision'] = self.vision.capture_frame()
        
        # Capturar audio (si está en modo de escucha)
        if self.audio.is_listening:
            perception['audio'] = self.audio.get_last_transcription()
        
        # Leer distancia
        perception['distance'] = self.robot.get_distance()
        
        # Estado del robot
        perception['robot_state'] = {
            'speed': self.robot.current_speed,
            'state': self.robot.current_state.value,
        }
        
        return perception
    
    def _decide(self, perception: Dict) -> List[str]:
        """
        Fase de decisión: evalúa percepción y decide acciones
        
        Args:
            perception: Datos de percepción
        
        Returns:
            Lista de acciones a ejecutar
        """
        # Construir contexto
        context = self.context_builder.build_context(
            vision_data=perception['vision'],
            audio_data=perception['audio'],
            robot_state=perception['robot_state'],
            distance=perception['distance']
        )
        
        # Evaluar con motor de decisión
        actions = self.decision_engine.evaluate(context)
        
        return actions
    
    def _act(self, actions: List[str], perception: Dict):
        """
        Fase de acción: ejecuta las acciones decididas
        
        Args:
            actions: Lista de acciones a ejecutar
            perception: Datos de percepción (para acciones que los necesiten)
        """
        for action in actions:
            try:
                self._execute_action(action, perception)
            except Exception as e:
                self.logger.error(f"Error ejecutando acción '{action}': {e}")
    
    def _execute_action(self, action: str, perception: Dict):
        """
        Ejecuta una acción específica
        
        Args:
            action: Nombre de la acción
            perception: Datos de percepción
        """
        # Movimiento básico
        if action == 'stop':
            self.robot.stop()
        
        elif action == 'move_forward':
            self.robot.move_forward()
        
        elif action == 'move_forward_slow':
            self.robot.move_forward(speed=self.robot.config['slow_speed'])
        
        elif action == 'move_backward':
            self.robot.move_backward()
        
        elif action == 'turn_left':
            self.robot.turn_left()
        
        elif action == 'turn_right':
            self.robot.turn_right()
        
        elif action == 'turn_random':
            import random
            if random.random() > 0.5:
                self.robot.turn_left(duration=0.5)
            else:
                self.robot.turn_right(duration=0.5)
        
        # Seguimiento
        elif action == 'track_face':
            face_center = self.vision.get_object_center('face')
            if face_center:
                self.robot.track_object(face_center[0], face_center[1])
        
        elif action == 'track_color':
            color_center = self.vision.get_object_center('color')
            if color_center:
                self.robot.track_object(color_center[0], color_center[1])
        
        # Comportamientos complejos
        elif action == 'scan_environment':
            self.robot.scan_environment()
        
        elif action == 'avoid_obstacle':
            self.robot.avoid_obstacle()
        
        # Captura
        elif action == 'take_photo':
            self.vision.take_screenshot()
        
        # Audio
        elif action == 'play_sound':
            self.robot.play_sound('beep')
        
        elif action.startswith('speak:'):
            text = action.split(':', 1)[1]
            self.robot.speak(text)
        
        # Comandos de voz
        elif action == 'parse_command':
            self._parse_voice_command(perception.get('audio'))
        
        elif action == 'execute_command':
            self._execute_voice_command(perception.get('audio'))
        
        else:
            self.logger.warning(f"Acción desconocida: {action}")
    
    def _parse_voice_command(self, voice_text: Optional[str]) -> Optional[str]:
        """
        Parsea un comando de voz y retorna la acción correspondiente
        
        Args:
            voice_text: Texto del comando de voz
        
        Returns:
            Nombre de la acción o None
        """
        if not voice_text:
            return None
        
        voice_lower = voice_text.lower()
        
        # Buscar en comandos configurados
        for action, keywords in VOICE_COMMANDS.items():
            for keyword in keywords:
                if keyword in voice_lower:
                    return action
        
        return None
    
    def _execute_voice_command(self, voice_text: Optional[str]):
        """
        Ejecuta un comando de voz
        
        Args:
            voice_text: Texto del comando de voz
        """
        action = self._parse_voice_command(voice_text)
        
        if action:
            self.logger.info(f"Ejecutando comando de voz: {action}")
            
            # Mapear acción a método del robot
            action_map = {
                'forward': lambda: self.robot.move_forward(duration=1.0),
                'backward': lambda: self.robot.move_backward(duration=1.0),
                'left': lambda: (self.robot.turn_left(), self.robot.move_forward(duration=0.5)),
                'right': lambda: (self.robot.turn_right(), self.robot.move_forward(duration=0.5)),
                'stop': lambda: self.robot.stop(),
                'follow_me': lambda: self._set_mode(LoopMode.TRACKING),
                'explore': lambda: self._set_mode(LoopMode.EXPLORATION),
                'track_red': lambda: self.vision.set_color_detection('red'),
                'track_blue': lambda: self.vision.set_color_detection('blue'),
                'take_photo': lambda: self.vision.take_screenshot(),
                'status': lambda: self._report_status(),
            }
            
            if action in action_map:
                action_map[action]()
            else:
                self.logger.warning(f"Comando no implementado: {action}")
    
    def _set_mode(self, mode: LoopMode):
        """Cambia el modo de operación"""
        self.mode = mode
        self.logger.info(f"Modo cambiado a: {mode.value}")
        self.robot.play_sound('success')
    
    def _report_status(self):
        """Reporta el estado del sistema"""
        vision_summary = self.vision.get_summary()
        robot_summary = self.robot.get_state_summary()
        
        status = f"Modo {self.mode.value}. {vision_summary}. {robot_summary}"
        self.logger.info(f"Estado: {status}")
        self.robot.speak(status)
    
    def _evaluate(self):
        """
        Fase de evaluación: verifica seguridad y ajusta comportamiento
        """
        # Verificar seguridad
        if not self.robot.check_safety():
            self.logger.warning("Verificación de seguridad falló")
            return
        
        # Aquí se pueden agregar más evaluaciones y ajustes
    
    def enable_voice_control(self):
        """Habilita el control por voz"""
        self.audio.start_listening()
        self.logger.info("Control por voz habilitado")
    
    def disable_voice_control(self):
        """Deshabilita el control por voz"""
        self.audio.stop_listening()
        self.logger.info("Control por voz deshabilitado")
    
    def get_metrics(self) -> Dict:
        """
        Obtiene métricas del sistema
        
        Returns:
            Diccionario con métricas
        """
        return {
            'loop_count': self.loop_count,
            'avg_loop_time': self.avg_loop_time,
            'is_running': self.is_running,
            'mode': self.mode.value,
        }
