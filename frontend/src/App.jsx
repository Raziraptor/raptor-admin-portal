import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, UploadCloud, Lock, User, Bot, FileText, Trash2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const API_URL = 'http://127.0.0.1:8000';

function App() {
  // Estados de la aplicación
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const [file, setFile] = useState(null);
  const [roleId, setRoleId] = useState(1);
  const [uploadMsg, setUploadMsg] = useState('');
  const [documents, setDocuments] = useState([]);

  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

const scrollToBottom = () => {
  chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
};

useEffect(() => {
  scrollToBottom();
}, [chatHistory]);

  // 1. Iniciar Sesión
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const res = await axios.post(`${API_URL}/token`, formData);
      setToken(res.data.access_token);
    } catch (error) {
      alert("Error de credenciales. ¿Ya creaste tu usuario en Swagger?");
    }
  };

  // 2. Subir Documento
  const handleUpload = async () => {
    if (!file) return alert("Selecciona un PDF primero");
    setUploadMsg("Subiendo y vectorizando...");
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('required_role_id', roleId);

    try {
      const res = await axios.post(`${API_URL}/documents/upload`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUploadMsg(`¡Éxito! ${res.data.message}`);
      fetchDocuments();
      setFile(null);
      setTimeout(() => setUploadMsg(''), 5000);
    } catch (error) {
      setUploadMsg("Error al subir el documento.");
    }
  };

  // Cargar lista de documentos
  const fetchDocuments = async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${API_URL}/documents`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDocuments(res.data.documents);
    } catch (error) {
      console.error("Error cargando documentos", error);
    }
  };

  // Cargar documentos al iniciar sesión
  useEffect(() => {
    fetchDocuments();
  }, [token]);

  // Borrar Documento
  const handleDeleteDoc = async (filename) => {
    if (!window.confirm(`¿Estás seguro de borrar ${filename}? La IA lo olvidará por completo.`)) return;
    
    try {
      await axios.delete(`${API_URL}/documents/${filename}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchDocuments(); // Recargamos la lista después de borrar
    } catch (error) {
      alert("Error al borrar el documento.");
    }
  };

  // 3. Preguntar a la IA
  const handleAskQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const newChat = [...chatHistory, { type: 'user', text: question }];
    setChatHistory(newChat);
    setQuestion('');
    setLoading(true); // <-- Iniciamos la animación

    try {
      const res = await axios.post(`${API_URL}/chat`, 
        { question: newChat[newChat.length - 1].text },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // 1. Apagamos la animación antes de renderizar
      setLoading(false); 

      // 2. ¡Imprimimos en consola para ver cómo se llama la variable real!
      console.log("Respuesta del backend:", res.data);

      // 3. CAMBIO CLAVE: Intenta buscar 'respuesta' si 'answer' no existe
      // También asegúrate de que venga como string.
      const botResponse = res.data.respuesta || res.data.answer || JSON.stringify(res.data);
      
      setChatHistory([...newChat, { type: 'bot', text: botResponse }]);

    } catch (error) {
      setLoading(false);
      setChatHistory([...newChat, { type: 'bot', text: "Error de conexión con la IA." }]);
    }
  };

  // PANTALLA DE LOGIN
  if (!token) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl shadow-2xl w-full max-w-md">
          <div className="flex flex-col items-center mb-8">
            <div className="bg-cyan-500/10 p-3 rounded-full mb-4">
              <Lock className="w-8 h-8 text-cyan-400" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-wider">RAPTOR ADMIN</h1>
            <p className="text-slate-400 text-sm mt-2">Acceso a Infraestructura RAG</p>
          </div>
          
          <form onSubmit={handleLogin} className="space-y-4">
            <input 
              type="text" placeholder="Usuario" 
              className="w-full bg-slate-950 border border-slate-800 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
              onChange={(e) => setUsername(e.target.value)} 
            />
            <input 
              type="password" placeholder="Contraseña" 
              className="w-full bg-slate-950 border border-slate-800 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
              onChange={(e) => setPassword(e.target.value)} 
            />
            <button type="submit" className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3 rounded-lg transition-colors shadow-[0_0_15px_rgba(8,145,178,0.4)]">
              INICIAR SESIÓN
            </button>
          </form>
        </div>
      </div>
    );
  }

  // PANTALLA PRINCIPAL (DASHBOARD)
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans flex flex-col md:flex-row">
      
      {/* PANEL IZQUIERDO: Ingesta de Datos */}
      <div className="w-full md:w-80 border-r border-slate-800 bg-slate-900 p-6 flex flex-col">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <FileText className="text-cyan-400" /> Base de Conocimiento
        </h2>
        
        <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 mb-6">
          <label className="block text-sm font-medium text-slate-400 mb-2">Subir Manual (PDF)</label>
          <input 
            type="file" accept=".pdf"
            className="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-cyan-900/30 file:text-cyan-400 hover:file:bg-cyan-900/50 mb-4 cursor-pointer"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <div className="flex gap-2 mb-4">
            <span className="text-sm self-center text-slate-400">Nivel de Seguridad:</span>
            <input 
              type="number" min="1" max="5" value={roleId}
              className="bg-slate-900 border border-slate-700 text-white w-16 px-2 py-1 rounded text-center focus:outline-none focus:border-cyan-500"
              onChange={(e) => setRoleId(e.target.value)}
            />
          </div>
          <button 
            onClick={handleUpload}
            className="w-full bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white py-2 rounded-md flex items-center justify-center gap-2 transition-colors"
          >
            <UploadCloud size={18} /> Procesar PDF
          </button>
          {uploadMsg && <p className="text-xs text-emerald-400 mt-3 text-center">{uploadMsg}</p>}
        </div>
        <div className="mt-6 flex-1">
            <h3 className="text-sm font-semibold text-slate-400 mb-3 uppercase tracking-wider">Manuales Activos</h3>
            {documents.length === 0 ? (
              <p className="text-xs text-slate-600 italic">No hay documentos en la base de datos.</p>
            ) : (
              <ul className="space-y-2">
                {documents.map((doc, index) => (
                  <li key={index} className="flex items-center justify-between bg-slate-950 p-3 rounded border border-slate-800 group">
                    <span className="text-sm text-slate-300 truncate pr-2" title={doc}>
                      {doc}
                    </span>
                    <button 
                      onClick={() => handleDeleteDoc(doc)}
                      className="text-slate-600 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                      title="Borrar documento"
                    >
                      <Trash2 size={16} />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          
          <div className="mt-6 pt-6 border-t border-slate-800 text-xs text-slate-500 text-center">
            Sistemas Integrados • Raptor Solutions
          </div>
        </div>

      {/* ÁREA PRINCIPAL: Chat RAG */}
      <div className="flex-1 flex flex-col h-screen">
        <div className="p-6 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md">
          <h2 className="text-lg font-semibold text-white">Terminal de Inteligencia Artificial</h2>
          <p className="text-sm text-slate-400">Conectado a Gemini 2.5 Flash</p>
        </div>

        {/* Historial de Chat */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-950">
          {chatHistory.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <Bot size={48} className="mb-4 opacity-50" />
              <p>Sube un manual a la izquierda y comienza a preguntar.</p>
            </div>
          ) : (
            chatHistory.map((msg, i) => (
              <div key={i} className={`flex gap-4 ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.type === 'bot' && <div className="w-8 h-8 rounded bg-cyan-900/50 flex items-center justify-center border border-cyan-800 shrink-0"><Bot size={18} className="text-cyan-400"/></div>}
                
                <div className={`max-w-[75%] p-4 rounded-lg leading-relaxed ${
                  msg.type === 'user' 
                    ? 'bg-cyan-600 text-white rounded-tr-none shadow-md' 
                    : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none shadow-sm'
                }`}>
                  <div className={`max-w-[75%] p-4 rounded-lg leading-relaxed ${
                    msg.type === 'user' 
                      ? 'bg-cyan-600 text-white rounded-tr-none shadow-md' 
                      : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none shadow-sm'
                  }`}>
                    {msg.type === 'bot' ? (
                      <div className="prose prose-invert max-w-none prose-sm">
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      </div>
                    ) : (
                      msg.text
                    )}
                    <div ref={chatEndRef} /> {/* Este es el punto de anclaje */}
                  </div>
                </div>

                {msg.type === 'user' && <div className="w-8 h-8 rounded bg-slate-800 flex items-center justify-center shrink-0"><User size={18} className="text-slate-400"/></div>}
              </div>
            ))
          )}
          {loading && (
            <div className="flex gap-4">
               <div className="w-8 h-8 rounded bg-cyan-900/50 flex items-center justify-center border border-cyan-800"><Bot size={18} className="text-cyan-400"/></div>
               <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg rounded-tl-none text-slate-400 animate-pulse">
                 Analizando vectores...
               </div>
            </div>
          )}
        </div>

        {/* Barra de Input */}
        <div className="p-4 bg-slate-900 border-t border-slate-800">
          <form onSubmit={handleAskQuestion} className="max-w-4xl mx-auto relative flex items-center">
            <input 
              type="text" 
              placeholder="Escribe tu consulta técnica aquí..." 
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-white rounded-xl pl-4 pr-12 py-4 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 shadow-inner"
              disabled={loading}
            />
            <button 
              type="submit" 
              disabled={loading}
              className="absolute right-2 p-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>

    </div>
  );
}

export default App;