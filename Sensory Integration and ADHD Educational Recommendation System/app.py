import streamlit as st
from recommendations_engine import EducationalRecommender
import plotly.graph_objects as go
import pandas as pd

# Inicializar el motor de recomendaciones
recommender = EducationalRecommender()

def create_radar_chart(scores):
    """Crear gráfico de radar con los resultados de las evaluaciones."""
    categories = list(scores.keys())
    values = list(scores.values())
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Evaluación'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False
    )
    return fig

def display_recommendations(analysis):
    """Mostrar análisis y recomendaciones personalizadas."""
    st.subheader("📊 Análisis de Resultados")
    
    # Gráfico de radar
    st.plotly_chart(create_radar_chart(analysis['scores']))
    
    # Fortalezas y áreas de mejora
    col1, col2 = st.columns(2)
    with col1:
        st.write("💪 **Fortalezas:**")
        for strength in analysis['strengths']:
            st.write(f"- {strength.title()}")
    
    with col2:
        st.write("🎯 **Áreas de mejora:**")
        for concern in analysis['primary_concerns']:
            st.write(f"- {concern.title()}")
    
    # Recomendaciones
    st.subheader("🎯 Recomendaciones Personalizadas")
    tabs = st.tabs(["Integración Sensorial", "Mindfulness", "Estrategias TDAH", "Generales"])
    
    with tabs[0]:
        st.write("### 🌟 Integración Sensorial")
        for rec in analysis['recommendations']['sensory']:
            st.write(f"- {rec}")
    
    with tabs[1]:
        st.write("### 🧘‍♂️ Mindfulness")
        for rec in analysis['recommendations']['mindfulness']:
            st.write(f"- {rec}")
    
    with tabs[2]:
        st.write("### 📝 Estrategias TDAH")
        for rec in analysis['recommendations']['adhd']:
            st.write(f"- {rec}")
    
    with tabs[3]:
        st.write("### 📌 Recomendaciones Generales")
        for rec in analysis['recommendations']['general']:
            st.write(f"- {rec}")

def main():
    st.title("Recomendaciones Educativas Personalizadas")
    st.write("Proporciona los datos para obtener un análisis detallado y recomendaciones personalizadas.")
    
    # Formulario para entrada de datos
    with st.form(key="evaluation_form"):
        st.subheader("📋 Datos de Evaluación")
        
        form_data = {}
        categories = recommender.categories
        for category, fields in categories.items():
            st.write(f"### {category.title()}")
            for field in fields:
                form_data[field] = st.slider(
                    f"{field.title()}",
                    min_value=0, max_value=10, value=5
                )
        
        submit_button = st.form_submit_button(label="Generar Recomendaciones")
    
    if submit_button:
        analysis = recommender.get_personalized_recommendations(form_data)
        display_recommendations(analysis)

if __name__ == "__main__":
    main()
