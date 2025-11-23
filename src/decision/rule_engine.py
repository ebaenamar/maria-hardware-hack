"""
Motor de decisión basado en reglas para el feedback loop
Evalúa condiciones y determina acciones basándose en reglas predefinidas
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import operator

from config.settings import BEHAVIOR_RULES, DECISION_CONFIG


@dataclass
class Rule:
    """Representa una regla de comportamiento"""
    name: str
    enabled: bool
    priority: float
    conditions: Dict[str, Any]
    actions: List[str]


class RuleEngine:
    """
    Motor de reglas que evalúa condiciones y determina acciones
    """
    
    def __init__(self, rules: Optional[Dict] = None):
        """
        Inicializa el motor de reglas
        
        Args:
            rules: Diccionario de reglas (usa BEHAVIOR_RULES por defecto)
        """
        self.logger = logging.getLogger(__name__)
        self.rules = self._parse_rules(rules or BEHAVIOR_RULES)
        self.config = DECISION_CONFIG
        
        # Operadores de comparación
        self.operators = {
            '>': operator.gt,
            '<': operator.lt,
            '>=': operator.ge,
            '<=': operator.le,
            '==': operator.eq,
            '!=': operator.ne,
        }
    
    def _parse_rules(self, rules_dict: Dict) -> List[Rule]:
        """
        Parsea el diccionario de reglas a objetos Rule
        
        Args:
            rules_dict: Diccionario con definiciones de reglas
        
        Returns:
            Lista de objetos Rule
        """
        rules = []
        
        for name, rule_data in rules_dict.items():
            rule = Rule(
                name=name,
                enabled=rule_data.get('enabled', True),
                priority=rule_data.get('priority', 0.5),
                conditions=rule_data.get('conditions', {}),
                actions=rule_data.get('actions', [])
            )
            rules.append(rule)
        
        # Ordenar por prioridad (mayor primero)
        rules.sort(key=lambda r: r.priority, reverse=True)
        
        return rules
    
    def evaluate(self, context: Dict[str, Any]) -> List[str]:
        """
        Evalúa todas las reglas y retorna las acciones a ejecutar
        
        Args:
            context: Diccionario con el estado actual del sistema
                Ejemplo: {
                    'face_detected': True,
                    'color_detected': False,
                    'obstacle_distance': 15.5,
                    'voice_detected': False,
                    'idle_time': 3.2,
                }
        
        Returns:
            Lista de acciones a ejecutar (de la regla con mayor prioridad que se cumpla)
        """
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self._evaluate_conditions(rule.conditions, context):
                self.logger.info(f"Regla activada: {rule.name} (prioridad: {rule.priority})")
                return rule.actions
        
        # Si ninguna regla se cumple, retornar lista vacía
        return []
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evalúa si todas las condiciones de una regla se cumplen
        
        Args:
            conditions: Diccionario de condiciones de la regla
            context: Contexto actual del sistema
        
        Returns:
            True si todas las condiciones se cumplen
        """
        for key, condition_value in conditions.items():
            context_value = context.get(key)
            
            # Si la clave no está en el contexto, la condición no se cumple
            if context_value is None:
                return False
            
            # Evaluar condición
            if not self._evaluate_single_condition(condition_value, context_value):
                return False
        
        return True
    
    def _evaluate_single_condition(self, condition_value: Any, context_value: Any) -> bool:
        """
        Evalúa una condición individual
        
        Args:
            condition_value: Valor de la condición (puede ser valor directo o tupla con operador)
            context_value: Valor del contexto
        
        Returns:
            True si la condición se cumple
        """
        # Si es una tupla, es una comparación con operador
        if isinstance(condition_value, tuple) and len(condition_value) == 2:
            op_str, threshold = condition_value
            
            if op_str in self.operators:
                op_func = self.operators[op_str]
                return op_func(context_value, threshold)
            else:
                self.logger.warning(f"Operador desconocido: {op_str}")
                return False
        
        # Si no es tupla, es comparación directa
        return context_value == condition_value
    
    def add_rule(self, name: str, priority: float, conditions: Dict, actions: List[str]):
        """
        Añade una nueva regla dinámicamente
        
        Args:
            name: Nombre de la regla
            priority: Prioridad (0-1)
            conditions: Diccionario de condiciones
            actions: Lista de acciones
        """
        rule = Rule(
            name=name,
            enabled=True,
            priority=priority,
            conditions=conditions,
            actions=actions
        )
        
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        
        self.logger.info(f"Regla añadida: {name}")
    
    def remove_rule(self, name: str):
        """
        Elimina una regla
        
        Args:
            name: Nombre de la regla a eliminar
        """
        self.rules = [r for r in self.rules if r.name != name]
        self.logger.info(f"Regla eliminada: {name}")
    
    def enable_rule(self, name: str, enable: bool = True):
        """
        Habilita o deshabilita una regla
        
        Args:
            name: Nombre de la regla
            enable: True para habilitar, False para deshabilitar
        """
        for rule in self.rules:
            if rule.name == name:
                rule.enabled = enable
                self.logger.info(f"Regla {name} {'habilitada' if enable else 'deshabilitada'}")
                return
        
        self.logger.warning(f"Regla no encontrada: {name}")
    
    def get_active_rules(self) -> List[str]:
        """
        Obtiene la lista de reglas activas
        
        Returns:
            Lista de nombres de reglas habilitadas
        """
        return [r.name for r in self.rules if r.enabled]
    
    def explain_decision(self, context: Dict[str, Any]) -> str:
        """
        Explica qué regla se activaría con el contexto dado
        
        Args:
            context: Contexto del sistema
        
        Returns:
            Explicación textual de la decisión
        """
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self._evaluate_conditions(rule.conditions, context):
                conditions_str = ", ".join([f"{k}={v}" for k, v in rule.conditions.items()])
                actions_str = ", ".join(rule.actions)
                
                return (f"Regla '{rule.name}' (prioridad {rule.priority})\n"
                       f"Condiciones: {conditions_str}\n"
                       f"Acciones: {actions_str}")
        
        return "Ninguna regla se cumple con el contexto actual"


class ContextBuilder:
    """
    Constructor de contexto que convierte datos de sensores en un contexto evaluable
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.last_activity_time = None
    
    def build_context(
        self,
        vision_data: Dict,
        audio_data: Optional[str],
        robot_state: Dict,
        distance: float
    ) -> Dict[str, Any]:
        """
        Construye el contexto para el motor de reglas
        
        Args:
            vision_data: Datos del sensor de visión
            audio_data: Transcripción de audio (o None)
            robot_state: Estado del robot
            distance: Distancia del sensor ultrasónico
        
        Returns:
            Diccionario de contexto
        """
        import time
        
        context = {}
        
        # Visión
        context['face_detected'] = len(vision_data.get('faces', [])) > 0
        context['color_detected'] = len(vision_data.get('colors', [])) > 0
        context['qr_detected'] = len(vision_data.get('qr_codes', [])) > 0
        context['gesture_detected'] = len(vision_data.get('gestures', [])) > 0
        context['traffic_sign_detected'] = len(vision_data.get('traffic_signs', [])) > 0
        
        # Tamaño del objeto de color (si existe)
        if context['color_detected']:
            color_obj = vision_data['colors'][0]
            context['color_size'] = color_obj.get('width', 0) * color_obj.get('height', 0)
        else:
            context['color_size'] = 0
        
        # Audio
        context['voice_detected'] = audio_data is not None and len(audio_data) > 0
        context['voice_text'] = audio_data or ""
        
        # Distancia
        context['obstacle_distance'] = distance
        context['has_obstacle'] = 0 < distance < DECISION_CONFIG['obstacle_distance_threshold']
        
        # Tiempo de inactividad
        current_time = time.time()
        if context['face_detected'] or context['color_detected'] or context['voice_detected']:
            self.last_activity_time = current_time
        
        if self.last_activity_time:
            context['idle_time'] = current_time - self.last_activity_time
        else:
            context['idle_time'] = 0
        
        # Estado del robot
        context['is_moving'] = robot_state.get('speed', 0) > 0
        
        return context
