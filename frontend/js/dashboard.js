// Variables globales
let selectedFile = null;
let currentPdfContext = null;
let currentVideoContext = null;
let currentQuizData = { pdf: null, video: null };
let pdfZoom = 1.0;
let currentPage = 1;
let totalPages = 1;

// MODO DESARROLLO: Cambiar a false cuando tengas backend
const DEV_MODE = true;

// Verificar autenticación al cargar la página
window.addEventListener('DOMContentLoaded', () => {
    if (!DEV_MODE) {
        checkAuthDashboard();
    } else {
        // Modo desarrollo: simular usuario
        document.getElementById('userName').textContent = 'Usuario Demo';
    }
    loadHistory();
    setupFileUpload();

    // Listeners para los botones "Subir Otro"
    document.getElementById('newPdfBtn').addEventListener('click', resetPDFUpload);
    document.getElementById('newVideoBtn').addEventListener('click', resetVideoUpload);

    const hash = window.location.hash;
    
    let buttonToClick = null;
    
    if (hash === '#pdf') {
        // Asumo que tu botón de tab tiene: onclick="switchTab('pdf')"
        buttonToClick = document.querySelector('.tab[onclick="switchTab(\'pdf\')"]');
    } else if (hash === '#video') {
        // Asumo que tu botón de tab tiene: onclick="switchTab('video')"
        buttonToClick = document.querySelector('.tab[onclick="switchTab(\'video\')"]');
    }
    
    if (buttonToClick) {
        buttonToClick.click(); // Esto dispara tu función switchTab()
    }
});

// Verificar si el usuario está autenticado
function checkAuthDashboard() {
    const token = localStorage.getItem('authToken');
    const userName = localStorage.getItem('userName');
    
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    document.getElementById('userName').textContent = userName || 'Usuario';
}

// Cerrar sesión
function logout() {
    if (DEV_MODE) {
        alert('Modo desarrollo: logout desactivado');
        return;
    }
    localStorage.removeItem('authToken');
    localStorage.removeItem('userName');
    localStorage.removeItem('userId');
    window.location.href = 'login.html';
}

// Cambiar entre tabs
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tabName + 'Tab').classList.add('active');
}

// ========== UPLOAD PDF ==========

function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type === 'application/pdf') {
            handleFileSelect(files[0]);
        } else {
            alert('Por favor sube un archivo PDF válido');
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

function handleFileSelect(file) {
    selectedFile = file;
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.innerHTML = `
        <div class="upload-icon">✅</div>
        <h3>${file.name}</h3>
        <p>Listo para procesar</p>
    `;
    document.getElementById('processPdfBtn').disabled = false;
}

// Procesar PDF
async function processPDF() {
    if (!selectedFile) {
        alert('Por favor selecciona un archivo PDF');
        return;
    }
    
    const loading = document.getElementById('pdfLoading');
    const btn = document.getElementById('processPdfBtn');
    
    document.getElementById('pdfUploadSection').style.display = 'none';
    loading.classList.add('show');
    btn.disabled = true;
    document.getElementById('pdfViewerPanel').style.display = 'none';
    
    try {
        if (DEV_MODE) {
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            currentPdfContext = { 
                file_id: 'pdf_' + Date.now(),
                filename: selectedFile.name,
                size: selectedFile.size
            };
            document.getElementById('pdfFileNameViewer').textContent = selectedFile.name;
            
            const fileURL = URL.createObjectURL(selectedFile);
            document.getElementById('pdfFrame').src = fileURL;
            
            const chatMessages = document.getElementById('pdfChatMessages');
            chatMessages.innerHTML = `
                <div class="ai-message">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <p>¡Hola! He procesado tu PDF "${selectedFile.name}". Puedes hacerme cualquier pregunta.</p>
                    </div>
                </div>
            `;
            
            loading.classList.remove('show');
            document.getElementById('pdfViewerPanel').style.display = 'flex';
            
        } else {
            // Lógica del Backend
            const data = await processPDFAPI(selectedFile);
            currentPdfContext = data;
            document.getElementById('pdfFileNameViewer').textContent = data.filename;

            const fileURL = URL.createObjectURL(selectedFile);
            document.getElementById('pdfFrame').src = fileURL;
            
            loading.classList.remove('show');
            document.getElementById('pdfViewerPanel').style.display = 'flex';
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al procesar el PDF. Intenta de nuevo.');
        loading.classList.remove('show');
        document.getElementById('pdfUploadSection').style.display = 'flex';
        btn.disabled = false;
    }
}

// ========== VIDEO DE YOUTUBE ==========
async function processVideo() {
    const videoUrl = document.getElementById('videoUrl').value.trim();
    
    // 1. Usar la nueva función para convertir el link
    const embedUrl = getYouTubeEmbedUrl(videoUrl);

    if (!embedUrl) {
        alert('Por favor ingresa una URL válida de YouTube (ej: .../watch?v=... o youtu.be/...)');
        return;
    }
    
    const loading = document.getElementById('videoLoading');
    document.getElementById('videoUploadSection').style.display = 'none';
    loading.classList.add('show');
    document.getElementById('videoViewerPanel').style.display = 'none';

    try {
        if (DEV_MODE) {
            await new Promise(resolve => setTimeout(resolve, 2000)); // Simular carga
            
            currentVideoContext = { 
                video_id: 'video_' + Date.now(),
                url: videoUrl,
                title: 'Video de YouTube'
            };
            document.getElementById('videoTitleViewer').textContent = 'Video de YouTube';

            // 2. Poner el link convertido en el iframe
            document.getElementById('videoFrame').src = embedUrl;
            
            const chatMessages = document.getElementById('videoChatMessages');
            chatMessages.innerHTML = `
                <div class="ai-message">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <p>¡Hola! He analizado el video de YouTube. Pregúntame lo que necesites.</p>
                    </div>
                </div>
            `;
            
            loading.classList.remove('show');
            document.getElementById('videoViewerPanel').style.display = 'flex';
            
        } else {
            // Lógica del Backend (no cambia)
            const data = await processVideoAPI(videoUrl);
            currentVideoContext = data;
            document.getElementById('videoTitleViewer').textContent = data.title;

            // 2. Poner el link convertido en el iframe
            document.getElementById('videoFrame').src = embedUrl;

            loading.classList.remove('show');
            document.getElementById('videoViewerPanel').style.display = 'flex';
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al procesar el video. Verifica la URL e intenta de nuevo.');
        loading.classList.remove('show');
        document.getElementById('videoUploadSection').style.display = 'flex';
    }
}

function getYouTubeEmbedUrl(url) {
    let videoId = '';
    try {
        const urlObj = new URL(url);
        if (urlObj.hostname === 'youtu.be') {
            // Link corto: https://youtu.be/VIDEO_ID
            videoId = urlObj.pathname.substring(1);
        } else if (urlObj.hostname === 'www.youtube.com' || urlObj.hostname === 'youtube.com') {
            // Link normal: https://www.youtube.com/watch?v=VIDEO_ID
            videoId = urlObj.searchParams.get('v');
        }
        
        if (videoId) {
            return `https://www.youtube.com/embed/${videoId}`;
        } else {
            return null;
        }
    } catch (error) {
        console.error("Error al parsear URL de YouTube:", error);
        return null;
    }
}


// ========== SISTEMA DE CHAT ==========

function handleEnter(event, type) {
    if (event.key === 'Enter') {
        sendMessage(type);
    }
}

async function sendMessage(type) {
    const inputId = type === 'pdf' ? 'pdfChatInput' : 'videoChatInput';
    const messagesId = type === 'pdf' ? 'pdfChatMessages' : 'videoChatMessages';
    const context = type === 'pdf' ? currentPdfContext : currentVideoContext;
    
    const input = document.getElementById(inputId);
    const message = input.value.trim();
    
    if (!message) return; // 1. Si no hay mensaje, no hacer nada
    
    // 2. Agregar mensaje del usuario a la UI
    addMessage(messagesId, message, 'user');
    input.value = '';
    
    // 3. Mostrar indicador de "Escribiendo..."
    const typingId = addTypingIndicator(messagesId);
    
    try {
        // 4. PRIMERO revisar si estamos en DEV_MODE
        if (DEV_MODE) {
            // Si SÍ, solo simular la respuesta que quieres probar
            await new Promise(resolve => setTimeout(resolve, 1500));
            const aiResponse = generateMockAIResponse(message);
            removeTypingIndicator(messagesId, typingId);
            addMessage(messagesId, aiResponse, 'ai');
        } else {
            // Si NO (estamos en producción), AHORA SÍ revisamos el contexto
            if (!context) {
                removeTypingIndicator(messagesId, typingId);
                addMessage(messagesId, 'Por favor, carga un documento antes de preguntar.', 'ai');
                return; 
            }
            
            // Contexto existe Y estamos en producción: llamar al backend real
            const response = await sendChatMessage(message, context, type);
            removeTypingIndicator(messagesId, typingId);
            addMessage(messagesId, response.reply, 'ai');
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator(messagesId, typingId);
        addMessage(messagesId, 'Lo siento, ocurrió un error. Por favor intenta de nuevo.', 'ai');
    }
}

function addMessage(containerId, message, type) {
    const container = document.getElementById(containerId);
    const messageDiv = document.createElement('div');
    messageDiv.className = type === 'user' ? 'user-message' : 'ai-message';
    
    const avatar = type === 'user' ? '👤' : '🤖';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <p>${escapeHtml(message)}</p>
        </div>
    `;
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function addTypingIndicator(containerId) {
    const container = document.getElementById(containerId);
    const typingDiv = document.createElement('div');
    const typingId = 'typing_' + Date.now();
    typingDiv.id = typingId;
    typingDiv.className = 'ai-message';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <p>Escribiendo...</p>
        </div>
    `;
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
    return typingId;
}

function removeTypingIndicator(containerId, typingId) {
    const typingDiv = document.getElementById(typingId);
    if (typingDiv) {
        typingDiv.remove();
    }
}

function generateMockAIResponse(question) {
    const responses = [
        `Excelente pregunta. Basándome en el material, ${question.toLowerCase().includes('qué') ? 'te puedo explicar que' : 'la respuesta es'}:\n\n${getMockExplanation()}`,
        `Según el contenido del documento, ${getMockExplanation()}`,
        `Déjame ayudarte con eso. ${getMockExplanation()}\n\n¿Tienes alguna otra duda sobre este tema?`,
        `Buena pregunta. En el material se menciona que ${getMockExplanation()}`,
        `Te lo explico de forma sencilla: ${getMockExplanation()}\n\n¿Quieres que profundice en algún aspecto específico?`
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
}

function getMockExplanation() {
    const explanations = [
        'Este concepto se refiere a los fundamentos básicos que debes entender primero. Es importante porque forma la base para temas más avanzados.',
        'El método consiste en seguir una serie de pasos sistemáticos. Primero se identifica el problema, luego se analiza y finalmente se aplica la solución.',
        'La teoría explica que existe una relación directa entre las variables. Cuando una aumenta, la otra también cambia proporcionalmente.',
        'Este principio se aplica en múltiples contextos. Por ejemplo, en la práctica diaria se puede observar cuando trabajamos con casos reales.',
        'La definición formal establece que es un proceso mediante el cual se logra un objetivo específico siguiendo ciertas reglas establecidas.'
    ];
    
    return explanations[Math.floor(Math.random() * explanations.length)];
}

function clearChat(type) {
    const confirmDialogId = type === 'pdf' ? 'pdfClearConfirm' : 'videoClearConfirm';
    document.getElementById(confirmDialogId).style.display = 'flex';
}

function cancelClearChat(type) {
    const confirmDialogId = type === 'pdf' ? 'pdfClearConfirm' : 'videoClearConfirm';
    document.getElementById(confirmDialogId).style.display = 'none';
}

// Realiza la limpieza del chat y oculta el diálogo
function confirmClearChat(type) {
    const messagesId = type === 'pdf' ? 'pdfChatMessages' : 'videoChatMessages';
    const container = document.getElementById(messagesId);
    let fileName = "el documento"; // Mensaje por defecto

    const context = type === 'pdf' ? currentPdfContext : currentVideoContext;
    
    if(context) {
        fileName = type === 'pdf' 
            ? `"${document.getElementById('pdfFileNameViewer').textContent}"`
            : `"${document.getElementById('videoTitleViewer').textContent}"`;
    }

    // 1. Limpiar el contenido del chat
    container.innerHTML = `
        <div class="ai-message">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <p>Chat limpiado. ${context ? 'Puedes seguir preguntando sobre ' + fileName : 'Sube un documento para comenzar.'}</p>
            </div>
        </div>
    `;

    // 2. Ocultar el diálogo de confirmación
    cancelClearChat(type); // Re-usamos la función de cancelar para ocultarlo
}

// ===== INICIO DE NUEVA FUNCIÓN =====
// Oculta el modal de alerta del quiz
function closeQuizAlert(type) {
    const alertId = type === 'pdf' ? 'pdfQuizAlert' : 'videoQuizAlert';
    document.getElementById(alertId).style.display = 'none';
}
// ===== FIN DE NUEVA FUNCIÓN =====


function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}


// ========== SISTEMA DE QUIZ ==========
function toggleQuiz(type) {
    const quizSection = document.getElementById(type + 'QuizSection');
    const isVisible = quizSection.style.display === 'block';
    
    if (isVisible) {
        quizSection.style.display = 'none';
    } else {
        generateQuiz(type);
    }
}

function closeQuiz(type) {
    const quizSection = document.getElementById(type + 'QuizSection');
    quizSection.style.display = 'none';
}

async function generateQuiz(type) {
    const context = type === 'pdf' ? currentPdfContext : currentVideoContext;
    
    // ===== INICIO DE CAMBIO =====
    if (!context) {
        // Reemplazar el alert nativo
        // alert('Por favor carga primero un ' + (type === 'pdf' ? 'PDF' : 'video') + ' para generar un quiz.');
        
        const alertId = type === 'pdf' ? 'pdfQuizAlert' : 'videoQuizAlert';
        const textId = type === 'pdf' ? 'pdfQuizAlertText' : 'videoQuizAlertText';
        const message = 'Por favor carga primero un ' + (type === 'pdf' ? 'PDF' : 'video') + ' para generar un quiz.';
        
        document.getElementById(textId).textContent = message;
        document.getElementById(alertId).style.display = 'flex';
        
        return;
    }
    // ===== FIN DE CAMBIO =====
    
    const quizSection = document.getElementById(type + 'QuizSection');
    
    // Crear estructura del quiz si no existe
    if (!quizSection.innerHTML.trim()) {
        quizSection.innerHTML = `
            <div class="quiz-header">
                <h3>📝 Quiz Generado</h3>
                <button class="close-quiz-btn" onclick="closeQuiz('${type}')">✕</button>
            </div>
            <div id="${type}QuizLoading" class="loading">
                <div class="spinner"></div>
                <p>Generando preguntas...</p>
            </div>
            <div id="${type}QuizContent" class="quiz-content" style="display: none;">
                <div id="${type}QuizQuestions"></div>
                <button class="action-btn" onclick="submitQuiz('${type}')">Enviar Respuestas</button>
            </div>
        `;
    }
    
    const loading = document.getElementById(type + 'QuizLoading');
    const content = document.getElementById(type + 'QuizContent');
    
    quizSection.style.display = 'block';
    loading.classList.add('show');
    content.style.display = 'none';
    
    try {
        if (DEV_MODE) {
            // Generar quiz simulado
            await new Promise(resolve => setTimeout(resolve, 2000));
            const mockQuestions = generateMockQuiz();
            currentQuizData[type] = mockQuestions;
            renderQuiz(type, mockQuestions);
            content.style.display = 'block';
        } else {
            // Llamar al backend real
            const data = await generateQuizAPI(context, type);
            currentQuizData[type] = data.questions;
            renderQuiz(type, data.questions);
            content.style.display = 'block';
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al generar el quiz. Intenta de nuevo.');
        quizSection.style.display = 'none';
    } finally {
        loading.classList.remove('show');
    }
}

function generateMockQuiz() {
    return [
        {
            question: "¿Cuál es el concepto principal explicado en el material?",
            options: [
                "Conceptos fundamentales y su aplicación práctica",
                "Teoría avanzada sin aplicaciones",
                "Métodos históricos obsoletos",
                "Definiciones básicas sin contexto"
            ],
            correct: 0
        },
        {
            question: "¿Qué método se recomienda para resolver problemas del tema?",
            options: [
                "Memorización sin comprensión",
                "Análisis sistemático y aplicación práctica",
                "Ensayo y error aleatorio",
                "Consultar solo las conclusiones"
            ],
            correct: 1
        },
        {
            question: "¿Cuál es la aplicación más importante del contenido estudiado?",
            options: [
                "No tiene aplicaciones prácticas",
                "Solo para exámenes teóricos",
                "Resolución de problemas reales en el campo",
                "Únicamente para investigación académica"
            ],
            correct: 2
        },
        {
            question: "¿Qué aspecto es fundamental para entender completamente el tema?",
            options: [
                "Memorizar todas las fórmulas",
                "Comprender los conceptos base y su relación",
                "Leer solo los resúmenes",
                "Enfocarse en casos particulares únicamente"
            ],
            correct: 1
        },
        {
            question: "¿Cómo se relaciona este tema con otros conceptos del curso?",
            options: [
                "Es completamente independiente",
                "Forma parte de una secuencia lógica de aprendizaje",
                "No tiene relación con otros temas",
                "Solo se usa al final del curso"
            ],
            correct: 1
        }
    ];
}

function renderQuiz(type, questions) {
    const container = document.getElementById(type + 'QuizQuestions');
    container.innerHTML = '';
    
    questions.forEach((q, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'quiz-question';
        questionDiv.innerHTML = `
            <h4>${index + 1}. ${q.question}</h4>
            <div class="quiz-options">
                ${q.options.map((opt, i) => `
                    <div class="quiz-option" data-question="${index}" data-option="${i}" onclick="selectOption('${type}', ${index}, ${i}, this)">
                        ${opt}
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(questionDiv);
    });
}

function selectOption(type, questionIndex, optionIndex, element) {
    const siblings = element.parentElement.querySelectorAll('.quiz-option');
    siblings.forEach(s => s.classList.remove('selected'));
    element.classList.add('selected');
}

function submitQuiz(type) {
    const questions = document.querySelectorAll(`#${type}QuizQuestions .quiz-question`);
    const selectedAnswers = [];
    
    questions.forEach((q, index) => {
        const selected = q.querySelector('.quiz-option.selected');
        if (selected) {
            selectedAnswers.push({
                question: index,
                answer: parseInt(selected.dataset.option)
            });
        }
    });
    
    if (selectedAnswers.length < questions.length) {
        alert('Por favor responde todas las preguntas');
        return;
    }
    
    // Calcular resultados
    let correctCount = 0;
    selectedAnswers.forEach((ans, idx) => {
        if (currentQuizData[type][idx].correct === ans.answer) {
            correctCount++;
        }
    });
    
    const percentage = ((correctCount / questions.length) * 100).toFixed(0);
    const message = `¡Quiz completado!\n\nRespuestas correctas: ${correctCount}/${questions.length}\nPorcentaje: ${percentage}%\n\n${getQuizFeedback(percentage)}`;
    
    alert(message);
    
    if (!DEV_MODE) {
        // Guardar resultados en backend
        saveQuizResults(type, selectedAnswers, correctCount);
    }
}

function getQuizFeedback(percentage) {
    if (percentage >= 90) return '¡Excelente! Dominas muy bien el tema.';
    if (percentage >= 70) return '¡Muy bien! Tienes una buena comprensión.';
    if (percentage >= 50) return 'Bien, pero te recomiendo revisar algunos conceptos.';
    return 'Te sugerimos repasar el material nuevamente.';
}

// ========== HISTORIAL ==========
async function loadHistory() {
    try {
        if (DEV_MODE) {
            const mockHistory = [
                {
                    title: "Cálculo Diferencial - Capítulo 3.pdf",
                    type: "pdf",
                    date: new Date().toISOString(),
                    preview: "Chat sobre límites y continuidad"
                },
                {
                    title: "Video: Ecuaciones Diferenciales",
                    type: "video",
                    date: new Date(Date.now() - 86400000).toISOString(),
                    preview: "Consultas sobre métodos de resolución"
                },
                {
                    title: "Física II - Ondas.pdf",
                    type: "pdf",
                    date: new Date(Date.now() - 172800000).toISOString(),
                    preview: "Preguntas sobre propagación de ondas"
                }
            ];
            renderHistory(mockHistory);
        } else {
            const data = await getHistory();
            if (data.history && data.history.length > 0) {
                renderHistory(data.history);
            }
        }
    } catch (error) {
        console.error('Error cargando historial:', error);
    }
}

function renderHistory(history) {
    const grid = document.getElementById('historyGrid');
    
    if (history.length === 0) {
        grid.innerHTML = '<p style="color: #666;">Aún no tienes consultas guardadas</p>';
        return;
    }
    
    grid.innerHTML = history.map(item => `
        <div class="history-card" onclick="loadHistoryItem('${item.id || ''}')">
            <h4>${item.title}</h4>
            <div class="date">${formatDate(item.date)}</div>
            <div class="preview">${item.preview}</div>
        </div>
    `).join('');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-PE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function loadHistoryItem(itemId) {
    if (DEV_MODE) {
        alert('En modo desarrollo. Esta funcionalidad cargará la sesión guardada cuando conectes el backend.');
    } else {
        // Cargar sesión desde backend
        console.log('Cargando item:', itemId);
    }
}


// ========== NUEVAS FUNCIONES DE RESET ==========

// Resetea la vista de PDF
function resetPDFUpload() {
    // Mostrar sección de subida
    document.getElementById('pdfUploadSection').style.display = 'flex';
    // Ocultar el visor
    document.getElementById('pdfViewerPanel').style.display = 'none';
    
    // Resetear el área de subida
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.innerHTML = `
        <div class="upload-icon">📄</div>
        <h3>Arrastra tu PDF aquí</h3>
        <p>o haz click para seleccionar un archivo</p>
    `;
    document.getElementById('processPdfBtn').disabled = true;
    document.getElementById('fileInput').value = null;
    
    // Limpiar el iframe
    document.getElementById('pdfFrame').src = 'about:blank';
    
    selectedFile = null;
    currentPdfContext = null;
    
    // Resetear mensaje inicial del chat
    const chatMessages = document.getElementById('pdfChatMessages');
    chatMessages.innerHTML = `
        <div class="ai-message">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <p>¡Hola! Sube un PDF y te ayudaré a resolver tus dudas sobre el contenido.</p>
            </div>
        </div>
    `;
}

// Resetea la vista de Video
function resetVideoUpload() {
    document.getElementById('videoUploadSection').style.display = 'flex';
    document.getElementById('videoViewerPanel').style.display = 'none';
    
    document.getElementById('videoUrl').value = '';
    currentVideoContext = null;

    // 3. Limpiar el src del iframe
    document.getElementById('videoFrame').src = 'about:blank';
    
    const chatMessages = document.getElementById('videoChatMessages');
    chatMessages.innerHTML = `
        <div class="ai-message">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <p>¡Hola! Ingresa un video de YouTube y te ayudaré a entender el contenido.</p>
            </div>
        </div>
    `;
}