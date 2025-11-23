"""
Motor de decisión basado en LLM para el feedback loop
Utiliza un modelo de lenguaje para tomar decisiones más inteligentes
"""

import logging
import json
from typing import Dict, List, Any, Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from config.settings import DECISION_CONFIG

# Intentar cargar API keys
try:
    from config.secret import OPENAI_API_KEY, ANTHROPIC_API_KEY
except ImportError:
    OPENAI_API_KEY = None
    ANTHROPIC_API_KEY = None


class LLMEngine:
    """
    Motor de decisión basado en LLM que usa modelos de lenguaje para decidir acciones
    """
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa el motor LLM
        
        Args:
            provider: Proveedor de LLM ('openai' o 'anthropic')
            model: Modelo específico a usar
        """
        self.logger = logging.getLogger(__name__)
        self.provider = provider or DECISION_CONFIG.get('llm_provider', 'openai')
        self.model = model or DECISION_CONFIG.get('llm_model', 'gpt-4o-mini')
        self.temperature = DECISION_CONFIG.get('llm_temperature', 0.7)
        self.max_tokens = DECISION_CONFIG.get('llm_max_tokens', 500)
        
        self.client = None
        self._initialize_client()
        
        # Sistema de prompts
        self.system_prompt = self._build_system_prompt()
    
    def _initialize_client(self):
        """Inicializa el cliente del LLM"""
        if self.provider == 'openai':
            if not OPENAI_AVAILABLE:
                self.logger.error("openai no está instalado")
                return
            
            if not OPENAI_API_KEY:
                self.logger.error("OPENAI_API_KEY no configurada en config/secret.py")
                return
            
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            self.logger.info(f"Cliente OpenAI inicializado con modelo {self.model}")
        
        elif self.provider == 'anthropic':
            if not ANTHROPIC_AVAILABLE:
                self.logger.error("anthropic no está instalado")
                return
            
            if not ANTHROPIC_API_KEY:
                self.logger.error("ANTHROPIC_API_KEY no configurada en config/secret.py")
                return
            
            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            self.logger.info(f"Cliente Anthropic inicializado con modelo {self.model}")
        
        else:
            self.logger.error(f"Proveedor desconocido: {self.provider}")
    
    def _build_system_prompt(self) -> str:
        """
        Construye el prompt del sistema para el LLM
        
        Returns:
            String con el prompt del sistema
        """
        return """Eres el cerebro de un robot PiCar-X. Tu trabajo es analizar la información de los sensores y decidir qué acciones debe tomar el robot.

ACCIONES DISPONIBLES:
- stop: Detener el robot
- move_forward: Mover hacia adelante
- move_forward_slow: Mover adelante lentamente
- move_backward: Mover hacia atrás
- turn_left: Girar a la izquierda
- turn_right: Girar a la derecha
- track_face: Seguir una cara detectada
- track_color: Seguir un color detectado
- scan_environment: Escanear el entorno
- avoid_obstacle: Evitar obstáculo
- take_photo: Tomar una foto
- speak: Hablar (requiere texto)
- play_sound: Reproducir sonido

REGLAS DE SEGURIDAD:
1. Si hay un obstáculo a menos de 20cm, SIEMPRE evitar o detenerse
2. No mover hacia adelante si hay obstáculo cercano
3. Priorizar la seguridad sobre cualquier otra acción

COMPORTAMIENTO:
- Sé reactivo a los estímulos del entorno
- Si detectas una cara, intenta seguirla
- Si detectas un color objetivo, acércate
- Si escuchas un comando de voz, ejecútalo
- Si no hay nada interesante, explora

Responde SOLO con un objeto JSON con este formato:
{
    "actions": ["accion1", "accion2"],
    "reasoning": "explicación breve de por qué tomaste esta decisión",
    "priority": "high/medium/low"
}"""
    
    def evaluate(self, context: Dict[str, Any]) -> List[str]:
        """
        Evalúa el contexto usando el LLM y retorna acciones
        
        Args:
            context: Diccionario con el estado actual del sistema
        
        Returns:
            Lista de acciones a ejecutar
        """
        if not self.client:
            self.logger.error("Cliente LLM no inicializado")
            return []
        
        try:
            # Construir prompt con el contexto
            user_prompt = self._build_user_prompt(context)
            
            # Llamar al LLM
            if self.provider == 'openai':
                response = self._call_openai(user_prompt)
            elif self.provider == 'anthropic':
                response = self._call_anthropic(user_prompt)
            else:
                return []
            
            # Parsear respuesta
            actions = self._parse_response(response)
            
            return actions
        
        except Exception as e:
            self.logger.error(f"Error al evaluar con LLM: {e}")
            return []
    
    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        """
        Construye el prompt del usuario con el contexto
        
        Args:
            context: Contexto del sistema
        
        Returns:
            String con el prompt
        """
        prompt_parts = ["ESTADO ACTUAL DEL ROBOT:\n"]
        
        # Visión
        if context.get('face_detected'):
            prompt_parts.append("- Cara detectada")
        if context.get('color_detected'):
            prompt_parts.append(f"- Color detectado (tamaño: {context.get('color_size', 0)})")
        if context.get('qr_detected'):
            prompt_parts.append("- Código QR detectado")
        if context.get('gesture_detected'):
            prompt_parts.append("- Gesto detectado")
        if context.get('traffic_sign_detected'):
            prompt_parts.append("- Señal de tráfico detectada")
        
        # Audio
        if context.get('voice_detected'):
            voice_text = context.get('voice_text', '')
            prompt_parts.append(f"- Comando de voz: '{voice_text}'")
        
        # Distancia
        distance = context.get('obstacle_distance', 0)
        if distance > 0:
            prompt_parts.append(f"- Distancia a obstáculo: {distance:.1f}cm")
            if context.get('has_obstacle'):
                prompt_parts.append("  ⚠️ OBSTÁCULO CERCANO")
        
        # Estado
        if context.get('is_moving'):
            prompt_parts.append("- Robot en movimiento")
        else:
            prompt_parts.append("- Robot detenido")
        
        idle_time = context.get('idle_time', 0)
        if idle_time > 5:
            prompt_parts.append(f"- Sin actividad por {idle_time:.1f}s")
        
        prompt_parts.append("\n¿Qué debe hacer el robot?")
        
        return "\n".join(prompt_parts)
    
    def _call_openai(self, user_prompt: str) -> str:
        """
        Llama a la API de OpenAI
        
        Args:
            user_prompt: Prompt del usuario
        
        Returns:
            Respuesta del modelo
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"}
        )
        
        return response.choices[0].message.content
    
    def _call_anthropic(self, user_prompt: str) -> str:
        """
        Llama a la API de Anthropic
        
        Args:
            user_prompt: Prompt del usuario
        
        Returns:
            Respuesta del modelo
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return message.content[0].text
    
    def _parse_response(self, response: str) -> List[str]:
        """
        Parsea la respuesta JSON del LLM
        
        Args:
            response: Respuesta del LLM
        
        Returns:
            Lista de acciones
        """
        try:
            data = json.loads(response)
            actions = data.get('actions', [])
            reasoning = data.get('reasoning', '')
            priority = data.get('priority', 'medium')
            
            self.logger.info(f"LLM Decision - Priority: {priority}")
            self.logger.info(f"Reasoning: {reasoning}")
            self.logger.info(f"Actions: {actions}")
            
            return actions
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Error al parsear respuesta JSON: {e}")
            self.logger.debug(f"Respuesta: {response}")
            return []
    
    def explain_decision(self, context: Dict[str, Any]) -> str:
        """
        Obtiene una explicación detallada de la decisión
        
        Args:
            context: Contexto del sistema
        
        Returns:
            Explicación textual
        """
        if not self.client:
            return "Cliente LLM no disponible"
        
        try:
            user_prompt = self._build_user_prompt(context)
            
            if self.provider == 'openai':
                response = self._call_openai(user_prompt)
            elif self.provider == 'anthropic':
                response = self._call_anthropic(user_prompt)
            else:
                return "Proveedor no soportado"
            
            data = json.loads(response)
            reasoning = data.get('reasoning', 'Sin explicación')
            actions = data.get('actions', [])
            
            return f"Acciones: {', '.join(actions)}\nRazonamiento: {reasoning}"
        
        except Exception as e:
            self.logger.error(f"Error al obtener explicación: {e}")
            return f"Error: {str(e)}"
