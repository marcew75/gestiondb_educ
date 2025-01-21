# recommendations_engine.py
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, List, Tuple
import pandas as pd
from sklearn.neighbors import NearestNeighbors

class EducationalRecommender:
    def __init__(self):
        # Categorías principales de evaluación
        self.categories = {
            'academic': ['matematicas', 'lectura', 'escritura', 'ciencias'],
            'cognitive': ['memoria', 'atencion', 'razonamiento', 'velocidad'],
            'social': ['equipo', 'comunicacion', 'empatia', 'autorregulacion'],
            'study_habits': ['organizacion', 'planificacion', 'constancia', 'metodologia']
        }
        
        # Base de conocimiento de recomendaciones
        self.knowledge_base = {
            'sensory_integration': {
                'attention_low': [
                    "Implementar actividades vestibulares como columpios y balanceo",
                    "Usar cojines de textura durante las sesiones de estudio",
                    "Incorporar pelotas terapéuticas para el trabajo en escritorio",
                    "Establecer rutinas de movimiento entre actividades"
                ],
                'attention_medium': [
                    "Alternar actividades sedentarias con movimiento moderado",
                    "Usar herramientas de escritura con diferentes texturas",
                    "Implementar descansos activos programados"
                ],
                'attention_high': [
                    "Mantener un ambiente de trabajo organizado",
                    "Usar recordatorios visuales para las transiciones",
                    "Implementar técnicas de autorregulación"
                ]
            },
            'mindfulness': {
                'anxiety_high': [
                    "Practicar respiración consciente durante 5 minutos",
                    "Realizar ejercicios de atención plena con objetos",
                    "Implementar pausas de conciencia corporal"
                ],
                'focus_low': [
                    "Ejercicios de observación mindful",
                    "Práctica de la uva pasa",
                    "Caminata consciente entre actividades"
                ]
            },
            'adhd_strategies': {
                'organization_low': [
                    "Implementar sistema de códigos de colores",
                    "Usar temporizadores visuales",
                    "Crear listas de verificación diarias"
                ],
                'attention_low': [
                    "Dividir tareas en pasos más pequeños",
                    "Usar recordatorios visuales",
                    "Implementar sistema de recompensas inmediatas"
                ]
            }
        }
        
        self.scaler = MinMaxScaler()
        
    def _calculate_category_scores(self, data: Dict) -> Dict[str, float]:
        """Calcula puntuaciones promedio por categoría."""
        scores = {}
        for category, fields in self.categories.items():
            category_values = [data[field] for field in fields if field in data]
            scores[category] = np.mean(category_values) if category_values else 0
        return scores
    
    def _identify_areas_of_concern(self, scores: Dict[str, float]) -> List[Tuple[str, str]]:
        """Identifica áreas que necesitan atención basadas en puntuaciones."""
        concerns = []
        for category, score in scores.items():
            if score < 4:
                concerns.append((category, 'low'))
            elif score < 7:
                concerns.append((category, 'medium'))
            else:
                concerns.append((category, 'high'))
        return concerns
    
    def _get_recommendations(self, concerns: List[Tuple[str, str]]) -> Dict[str, List[str]]:
        """Genera recomendaciones basadas en áreas de preocupación."""
        recommendations = {
            'sensory': [],
            'mindfulness': [],
            'adhd': [],
            'general': []
        }
        
        for category, level in concerns:
            # Recomendaciones de integración sensorial
            if category in ['cognitive', 'attention']:
                key = f'attention_{level}'
                if key in self.knowledge_base['sensory_integration']:
                    recommendations['sensory'].extend(
                        self.knowledge_base['sensory_integration'][key]
                    )
            
            # Recomendaciones de mindfulness
            if category in ['cognitive', 'social']:
                if 'anxiety_high' in self.knowledge_base['mindfulness']:
                    recommendations['mindfulness'].extend(
                        self.knowledge_base['mindfulness']['anxiety_high']
                    )
            
            # Recomendaciones TDAH
            if level == 'low':
                key = f'{category}_low'
                if key in self.knowledge_base['adhd_strategies']:
                    recommendations['adhd'].extend(
                        self.knowledge_base['adhd_strategies'][key]
                    )
        
        return recommendations
    
    def get_personalized_recommendations(self, data: Dict) -> Dict:
        """Procesa los datos y genera recomendaciones personalizadas."""
        # Calcular puntuaciones por categoría
        category_scores = self._calculate_category_scores(data)
        
        # Identificar áreas de preocupación
        concerns = self._identify_areas_of_concern(category_scores)
        
        # Generar recomendaciones
        recommendations = self._get_recommendations(concerns)
        
        # Agregar métricas y análisis
        analysis = {
            'scores': category_scores,
            'primary_concerns': [c[0] for c in concerns if c[1] == 'low'],
            'strengths': [c[0] for c in concerns if c[1] == 'high'],
            'recommendations': recommendations
        }
        
        return analysis

    def update_knowledge_base(self, new_recommendations: Dict):
        """Actualiza la base de conocimiento con nuevas recomendaciones."""
        for category, strategies in new_recommendations.items():
            if category in self.knowledge_base:
                self.knowledge_base[category].update(strategies)
            else:
                self.knowledge_base[category] = strategies