# document_upload.py
import streamlit as st
from knowledge_extractor import DocumentProcessor
import os
import tempfile

def render_document_upload():
    st.header("📚 Gestión de Base de Conocimiento")
    
    # Inicializar procesador de documentos
    doc_processor = DocumentProcessor()
    
    # Sección de carga de documentos
    st.subheader("Cargar Nuevos Documentos")
    uploaded_files = st.file_uploader(
        "Selecciona documentos para procesar (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write("### Documentos Cargados:")
        
        for uploaded_file in uploaded_files:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                # Procesar documento
                with st.spinner(f'Procesando {uploaded_file.name}...'):
                    file_type = uploaded_file.name.split('.')[-1]
                    extracted_knowledge = doc_processor.process_document(tmp_path, file_type)
                
                # Mostrar resultados del procesamiento
                with st.expander(f"📄 {uploaded_file.name}"):
                    # Mostrar patrones encontrados
                    if extracted_knowledge['patterns']:
                        st.write("**Patrones Identificados:**")
                        for pattern in extracted_knowledge['patterns'][:5]:
                            st.write(f"- {pattern}")
                    
                    # Mostrar intervenciones
                    if extracted_knowledge['interventions']:
                        st.write("**Intervenciones Extraídas:**")
                        for intervention in extracted_knowledge['interventions'][:5]:
                            st.write(f"- {intervention}")
                    
                    # Mostrar recomendaciones
                    if extracted_knowledge['recommendations']:
                        st.write("**Recomendaciones:**")
                        for rec in extracted_knowledge['recommendations'][:5]:
                            st.write(f"- {rec}")
                
                st.success(f"✅ {uploaded_file.name} procesado exitosamente")
            
            except Exception as e:
                st.error(f"❌ Error procesando {uploaded_file.name}: {str(e)}")
            
            finally:
                # Limpiar archivo temporal
                os.unlink(tmp_path)
    
    # Mostrar estadísticas de la base de conocimiento
    st.subheader("📊 Estadísticas de la Base de Conocimiento")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Patrones", len(doc_processor.knowledge_base['patterns']))
    with col2:
        st.metric("Intervenciones", len(doc_processor.knowledge_base['interventions']))
    with col3:
        st.metric("Recomendaciones", len(doc_processor.knowledge_base['recommendations']))
    with col4:
        total_items = sum(len(items) for items in doc_processor.knowledge_base.values())
        st.metric("Total Items", total_items)

if __name__ == "__main__":
    render_document_upload()