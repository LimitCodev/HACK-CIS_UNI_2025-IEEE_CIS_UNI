// Configuración de la API
const API_URL = 'http://localhost:3000/api'; // CAMBIAR POR TU BACKEND

// Obtener token de autenticación
function getAuthToken() {
    return localStorage.getItem('authToken');
}

// Función genérica para hacer peticiones autenticadas
async function fetchAPI(endpoint, options = {}) {
    const token = getAuthToken();
    
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${token}`,
            ...options.headers
        }
    };
    
    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        ...defaultOptions
    });
    
    return response;
}

// ========== APIs PARA PDF ==========

// Procesar PDF
async function processPDFAPI(file) {
    try {
        const formData = new FormData();
        formData.append('pdf', file);
        
        const response = await fetchAPI('/process/pdf', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Error al procesar PDF');
        }
        
        return await response.json();
        /* Respuesta esperada:
        {
            file_id: "pdf_12345",
            filename: "calculo.pdf",
            status: "processed",
            page_count: 45
        }
        */
    } catch (error) {
        console.error('Error en processPDFAPI:', error);
        throw error;
    }
}

// ========== APIs PARA VIDEO ==========

// Procesar Video de YouTube
async function processVideoAPI(videoUrl) {
    try {
        const response = await fetchAPI('/process/video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: videoUrl })
        });
        
        if (!response.ok) {
            throw new Error('Error al procesar video');
        }
        
        return await response.json();
        /* Respuesta esperada:
        {
            video_id: "video_12345",
            title: "Cálculo Diferencial",
            url: "https://youtube.com/...",
            duration: "15:30",
            status: "processed"
        }
        */
    } catch (error) {
        console.error('Error en processVideoAPI:', error);
        throw error;
    }
}

// ========== API DE CHAT ==========

// Enviar mensaje al chat
async function sendChatMessage(message, context, type) {
    try {
        const response = await fetchAPI('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                context_id: context.file_id || context.video_id,
                type: type, // 'pdf' o 'video'
                timestamp: new Date().toISOString()
            })
        });
        
        if (!response.ok) {
            throw new Error('Error al enviar mensaje');
        }
        
        return await response.json();
        /* Respuesta esperada:
        {
            reply: "Respuesta de la IA...",
            timestamp: "2024-11-05T10:30:00"
        }
        */
    } catch (error) {
        console.error('Error en sendChatMessage:', error);
        throw error;
    }
}

// ========== API DE QUIZ ==========

// Generar quiz basado en el contenido
async function generateQuizAPI(context, type) {
    try {
        const response = await fetchAPI('/quiz/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                context_id: context.file_id || context.video_id,
                type: type,
                num_questions: 5
            })
        });
        
        if (!response.ok) {
            throw new Error('Error al generar quiz');
        }
        
        return await response.json();
        /* Respuesta esperada:
        {
            questions: [
                {
                    question: "¿Qué es un límite?",
                    options: ["Opción A", "Opción B", "Opción C", "Opción D"],
                    correct: 2
                },
                ...
            ]
        }
        */
    } catch (error) {
        console.error('Error en generateQuizAPI:', error);
        throw error;
    }
}

// Guardar resultados del quiz
async function saveQuizResults(type, answers, correctCount) {
    try {
        const response = await fetchAPI('/quiz/results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: type,
                answers: answers,
                correct_count: correctCount,
                total_questions: answers.length,
                timestamp: new Date().toISOString()
            })
        });
        
        if (!response.ok) {
            throw new Error('Error al guardar resultados');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error en saveQuizResults:', error);
        throw error;
    }
}

// ========== API DE HISTORIAL ==========

// Obtener historial de consultas
async function getHistory() {
    try {
        const response = await fetchAPI('/history');
        
        if (!response.ok) {
            throw new Error('Error al obtener historial');
        }
        
        return await response.json();
        /* Respuesta esperada:
        {
            history: [
                {
                    id: "session_123",
                    title: "Cálculo.pdf",
                    type: "pdf",
                    date: "2024-11-05T10:00:00",
                    preview: "Chat sobre límites...",
                    message_count: 15
                },
                ...
            ]
        }
        */
    } catch (error) {
        console.error('Error en getHistory:', error);
        return { history: [] };
    }
}

// Cargar una sesión específica del historial
async function loadHistorySession(sessionId) {
    try {
        const response = await fetchAPI(`/history/${sessionId}`);
        
        if (!response.ok) {
            throw new Error('Error al cargar sesión');
        }
        
        return await response.json();
        /* Respuesta esperada:
        {
            session_id: "session_123",
            context: { ... },
            messages: [
                {
                    type: "user",
                    message: "¿Qué es un límite?",
                    timestamp: "..."
                },
                {
                    type: "ai",
                    message: "Un límite es...",
                    timestamp: "..."
                }
            ]
        }
        */
    } catch (error) {
        console.error('Error en loadHistorySession:', error);
        throw error;
    }
}

// ========== API DE USUARIO ==========

// Obtener datos del usuario actual
async function getCurrentUser() {
    try {
        const response = await fetchAPI('/user/me');
        
        if (!response.ok) {
            throw new Error('Error al obtener datos del usuario');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error en getCurrentUser:', error);
        throw error;
    }
}