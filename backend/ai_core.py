import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma

load_dotenv()

# 1. Configuración de Modelos (Usando Gemini)
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
PERSIST_DIRECTORY = "./chroma_db"

# Inicializamos el vector store con persistencia
vector_store = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embeddings_model
)

def process_and_store_document(file_path: str, role_id: int):
    # 1. Cargar el documento PDF
    loader = PyPDFLoader(file_path)
    documentos = loader.load()
    
    # 2. Cortar el documento en pedacitos (AQUÍ NACE LA VARIABLE 'chunks')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documentos)
    
    # 3. Inyectar el nivel de seguridad a la metadata de cada chunk
    for chunk in chunks:
        chunk.metadata["role_id"] = role_id
        
    # 4. Guardar en la base de datos persistente ChromaDB
    vector_store.add_documents(chunks)
    
    return len(chunks)

def ask_assistant(question: str, user_role_id: int) -> str:
    """Busca la respuesta filtrando por el rol del usuario."""
    
    # FILTRO DE CIBERSEGURIDAD: Solo trae documentos si el required_role_id es menor o igual al del usuario
    def security_filter(doc):
        # Si el documento no tiene rol (por si acaso), asumimos seguridad máxima (999)
        doc_role = doc.metadata.get("role_id", 999)
        return doc_role <= user_role_id

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 5} # Trae los 5 fragmentos más relevantes
    )

    system_prompt = (
        "Eres un asistente técnico para Raptor Solutions. "
        "Utiliza ÚNICAMENTE los siguientes fragmentos de contexto recuperado para responder a la pregunta. "
        "Si no sabes la respuesta o no está en el contexto, di que no tienes acceso a esa información. "
        "No inventes respuestas.\n\n"
        "{context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    response = rag_chain.invoke({"input": question})
    respuesta_raw = response["answer"]
    documentos_usados = response.get("context", [])
    fuentes = set()
    
    if hasattr(respuesta_raw, "content"):
        answer = respuesta_raw.content
    else:
        answer = str(respuesta_raw)
    
    for doc in documentos_usados:
        # PyPDFLoader guarda la ruta del archivo en doc.metadata["source"]
        ruta_completa = doc.metadata.get("source", "Documento desconocido")
        nombre_archivo = os.path.basename(ruta_completa) # Extrae solo "manual.pdf"
        fuentes.add(nombre_archivo)
    
    if fuentes:
        # Usamos formato Markdown para que tu Frontend lo renderice bonito
        nombres_formateados = ", ".join(fuentes)
        answer += f"\n\n---\n**Fuentes consultadas:** *{nombres_formateados}*"

        
    return answer

def get_uploaded_documents():
    """Lee la metadata de ChromaDB y devuelve una lista de los nombres de archivos únicos."""
    # Accedemos a la colección nativa de ChromaDB
    collection = vector_store._collection
    results = collection.get(include=["metadatas"])
    
    fuentes = set()
    for meta in results.get("metadatas", []):
        if meta and "source" in meta:
            nombre_archivo = os.path.basename(meta["source"])
            fuentes.add(nombre_archivo)
            
    return list(fuentes)

def delete_document(filename: str):
    """Busca y elimina todos los vectores (chunks) que pertenezcan a un archivo específico."""
    collection = vector_store._collection
    results = collection.get(include=["metadatas"])
    
    ids_to_delete = []
    # Buscamos los IDs de los fragmentos que coincidan con el nombre del archivo
    for i, meta in enumerate(results.get("metadatas", [])):
        if meta and "source" in meta:
            if os.path.basename(meta["source"]) == filename:
                ids_to_delete.append(results["ids"][i])
                
    # Si encontramos fragmentos, los borramos
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
        
    return len(ids_to_delete)