# knowledge_extractor.py
import PyPDF2
import docx
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import re

class DocumentProcessor:
    def __init__(self):
        # Inicializar NLTK y spaCy
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        self.nlp = spacy.load('es_core_news_md')
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('spanish'))
        
        # Categorías y términos clave para clasificación
        self.categories = {
            'sensory_integration': [
                'sensorial', 'vestibular', 'propioceptivo', 'táctil',
                'auditivo', 'visual', 'integración', 'procesamiento'
            ],
            'mindfulness': [
                'atención plena', 'meditación', 'respiración',
                'conciencia', 'presente', 'calma', 'autoregulación'
            ],
            'adhd': [
                'atención', 'hiperactividad', 'impulsividad',
                'concentración', 'organización', 'planificación'
            ]
        }
        
        # Base de conocimiento extraído
        self.knowledge_base = {
            'interventions': [],
            'recommendations': [],
            'research_evidence': [],
            'patterns': []
        }

    def read_pdf(self, file_path: str) -> str:
        """Lee y extrae texto de archivos PDF."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def read_docx(self, file_path: str) -> str:
        """Lee y extrae texto de archivos Word."""
        doc = docx.Document(file_path)
        return " ".join([paragraph.text for paragraph in doc.paragraphs])

    def read_txt(self, file_path: str) -> str:
        """Lee archivos de texto plano."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def preprocess_text(self, text: str) -> str:
        """Preprocesa el texto para análisis."""
        # Convertir a minúsculas y eliminar caracteres especiales
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        
        # Tokenización y lematización
        words = word_tokenize(text)
        words = [self.lemmatizer.lemmatize(word) for word in words 
                if word not in self.stop_words]
        
        return ' '.join(words)

    def extract_patterns(self, text: str) -> list:
        """Extrae patrones de comportamiento y síntomas."""
        doc = self.nlp(text)
        patterns = []
        
        # Buscar patrones usando spaCy
        for sent in doc.sents:
            # Identificar oraciones que describen patrones
            if any(word in sent.text.lower() for word in 
                  ['presenta', 'muestra', 'exhibe', 'manifiesta']):
                patterns.append(sent.text.strip())
        
        return patterns

    def extract_interventions(self, text: str) -> list:
        """Extrae intervenciones y tratamientos mencionados."""
        doc = self.nlp(text)
        interventions = []
        
        # Buscar intervenciones usando spaCy
        for sent in doc.sents:
            # Identificar oraciones que describen intervenciones
            if any(word in sent.text.lower() for word in 
                  ['intervención', 'tratamiento', 'terapia', 'estrategia']):
                interventions.append(sent.text.strip())
        
        return interventions

    def extract_recommendations(self, text: str) -> list:
        """Extrae recomendaciones específicas."""
        doc = self.nlp(text)
        recommendations = []
        
        # Buscar recomendaciones usando spaCy
        for sent in doc.sents:
            # Identificar oraciones que contienen recomendaciones
            if any(word in sent.text.lower() for word in 
                  ['recomienda', 'sugiere', 'aconseja', 'debe']):
                recommendations.append(sent.text.strip())
        
        return recommendations

    def categorize_content(self, text: str) -> dict:
        """Categoriza el contenido según las áreas definidas."""
        categorized_content = {}
        
        for category, keywords in self.categories.items():
            category_content = []
            for sentence in sent_tokenize(text):
                if any(keyword in sentence.lower() for keyword in keywords):
                    category_content.append(sentence)
            categorized_content[category] = category_content
        
        return categorized_content

    def process_document(self, file_path: str, file_type: str) -> dict:
        """Procesa el documento y extrae conocimiento estructurado."""
        # Leer documento según tipo
        if file_type == 'pdf':
            text = self.read_pdf(file_path)
        elif file_type == 'docx':
            text = self.read_docx(file_path)
        elif file_type == 'txt':
            text = self.read_txt(file_path)
        else:
            raise ValueError("Tipo de archivo no soportado")

        # Preprocesar texto
        processed_text = self.preprocess_text(text)

        # Extraer conocimiento
        extracted_knowledge = {
            'patterns': self.extract_patterns(text),
            'interventions': self.extract_interventions(text),
            'recommendations': self.extract_recommendations(text),
            'categorized_content': self.categorize_content(text)
        }

        # Actualizar base de conocimiento
        self.update_knowledge_base(extracted_knowledge)

        return extracted_knowledge

    def update_knowledge_base(self, new_knowledge: dict):
        """Actualiza la base de conocimiento con nueva información."""
        for key in self.knowledge_base.keys():
            if key in new_knowledge:
                self.knowledge_base[key].extend(new_knowledge[key])
        
        # Eliminar duplicados
        for key in self.knowledge_base.keys():
            self.knowledge_base[key] = list(set(self.knowledge_base[key]))

    def get_relevant_recommendations(self, query: str, top_n: int = 5) -> list:
        """Obtiene recomendaciones relevantes basadas en una consulta."""
        # Vectorizar la consulta y las recomendaciones
        vectorizer = TfidfVectorizer()
        recommendations = self.knowledge_base['recommendations']
        
        if not recommendations:
            return []
            
        tfidf_matrix = vectorizer.fit_transform([query] + recommendations)
        
        # Calcular similitud
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        # Obtener las recomendaciones más relevantes
        top_indices = similarities[0].argsort()[-top_n:][::-1]
        
        return [recommendations[i] for i in top_indices]