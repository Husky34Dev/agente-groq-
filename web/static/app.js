document.addEventListener('DOMContentLoaded', () => {
    // --- Referencias a elementos del DOM ---
    const chatWindow = document.getElementById('chat-window');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const userRoleSelect = document.getElementById('user-role');
    const clearChatButton = document.getElementById('clear-chat');

    // --- Manejador del botón limpiar chat ---
    clearChatButton.addEventListener('click', () => {
        if (confirm('¿Estás seguro de que quieres limpiar todo el chat?')) {
            clearChat();
        }
    });

    // --- Manejador del envío del formulario ---
    messageForm.addEventListener('submit', event => {
        event.preventDefault();
        const messageText = messageInput.value.trim();
        if (messageText) {
            // Muestra el mensaje del usuario y limpia el input
            displayMessage(messageText, 'user');
            messageInput.value = '';
            
            // Muestra el indicador de "escribiendo..." y obtiene la respuesta del bot
            showBotTyping();
            getBotResponse(messageText);
        }
    });

    /**
     * Añade un mensaje a la ventana del chat.
     * @param {string | HTMLElement} content - El texto o elemento HTML del mensaje.
     * @param {'user' | 'bot'} sender - Quién envía el mensaje.
     */
    function displayMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        if (typeof content === 'string') {
            bubble.textContent = content;
        } else {
            bubble.appendChild(content);
        }

        messageDiv.appendChild(bubble);
        chatWindow.appendChild(messageDiv);
        scrollToBottom();
    }
    
    /**
     * Muestra el indicador de "escribiendo...".
     */
    function showBotTyping() {
        // Elimina cualquier indicador previo
        const existingTyping = document.getElementById('typing-indicator');
        if (existingTyping) existingTyping.remove();
        
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'message bot';
        typingDiv.innerHTML = `
            <div class="message-bubble typing-indicator">
                <span></span><span></span><span></span>
            </div>
        `;
        chatWindow.appendChild(typingDiv);
        scrollToBottom();
    }
    
    /**
     * Elimina el indicador de "escribiendo...".
     */
    function hideBotTyping() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    /**
     * Obtiene una respuesta del backend.
     * @param {string} userMessage - El mensaje del usuario.
     */
    async function getBotResponse(userMessage) {
        try {
            const selectedRole = userRoleSelect.value;
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    user_role: selectedRole
                })
            });

            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }

            const data = await response.json();
            hideBotTyping();
            handleResponse(data);

        } catch (error) {
            console.error('Error enviando mensaje:', error);
            hideBotTyping();
            displayMessage('❌ Error conectando con el servidor. Por favor, inténtalo de nuevo.', 'bot');
        }
    }

    /**
     * Maneja la respuesta del backend.
     * @param {object} data - Los datos de respuesta del servidor.
     */
    function handleResponse(data) {
        if (data.type === 'chat') {
            displayMessage(data.response || 'No se recibió respuesta', 'bot');
        } else if (data.type === 'tool_calls') {
            handleToolCallsResponse(data);
        } else if (data.type === 'error') {
            displayMessage(`❌ Error: ${data.error}`, 'bot');
        } else {
            displayMessage('🤔 Respuesta inesperada del servidor', 'bot');
        }
    }

    /**
     * Maneja respuestas de llamadas a herramientas.
     * @param {object} data - Los datos de tool_calls.
     */
    function handleToolCallsResponse(data) {
        if (data.results && data.results.length > 0) {
            data.results.forEach(result => {
                if (result.error) {
                    displayMessage(`❌ Error en ${result.tool}: ${result.error}`, 'bot');
                } else if (result.response) {
                    const formattedResponse = formatToolResponse(result);
                    const jsonCard = createResponseCard(formattedResponse);
                    displayMessage(jsonCard, 'bot');
                }
            });
        } else {
            displayMessage('✅ Operación completada', 'bot');
        }
    }

    /**
     * Formatea la respuesta de una herramienta.
     * @param {object} result - El resultado de la herramienta.
     * @returns {object} Los datos formateados.
     */
    function formatToolResponse(result) {
        const toolName = result.tool;
        const response = result.response;
        
        return {
            tool: toolName,
            data: response
        };
    }

    /**
     * Crea una tarjeta HTML para visualizar respuestas del backend.
     * @param {object} responseData - Los datos de respuesta formateados.
     * @returns {HTMLElement} El elemento de la tarjeta.
     */
    function createResponseCard(responseData) {
        const card = document.createElement('div');
        card.className = 'response-card';
        
        // Título de la herramienta
        const header = document.createElement('div');
        header.className = 'response-header';
        header.innerHTML = `<span class="tool-icon">🔧</span><strong>${responseData.tool}</strong>`;
        card.appendChild(header);
        
        // Contenido de los datos
        const content = document.createElement('div');
        content.className = 'response-content';
        content.appendChild(renderResponseData(responseData.data));
        card.appendChild(content);
        
        return card;
    }

    /**
     * Renderiza los datos de respuesta con formato especial para datos de abonado.
     * @param {object} data - Los datos a renderizar.
     * @returns {HTMLElement} El elemento renderizado.
     */
    function renderResponseData(data) {
        const container = document.createElement('div');
        
        // Casos especiales para datos de abonado
        if (data.nombre || data.dni || data.direccion) {
            return createSubscriberCard(data);
        }
        
        // Casos especiales para facturas
        if (data.facturas && Array.isArray(data.facturas)) {
            return createFacturasCard(data.facturas);
        }
        
        // Renderizado genérico
        return renderObject(data);
    }

    /**
     * Crea una tarjeta especial para datos de abonado.
     * @param {object} data - Los datos del abonado.
     * @returns {HTMLElement} La tarjeta del abonado.
     */
    function createSubscriberCard(data) {
        const card = document.createElement('div');
        card.className = 'subscriber-card';
        
        if (data.nombre) {
            const name = document.createElement('h3');
            name.className = 'subscriber-name';
            name.innerHTML = `👤 ${data.nombre}`;
            card.appendChild(name);
        }
        
        const fields = [
            { key: 'dni', label: 'DNI', icon: '🆔' },
            { key: 'direccion', label: 'Dirección', icon: '📍' },
            { key: 'correo', label: 'Email', icon: '📧' },
            { key: 'telefono', label: 'Teléfono', icon: '📞' },
            { key: 'poliza', label: 'Póliza', icon: '📋' }
        ];
        
        fields.forEach(field => {
            if (data[field.key]) {
                const fieldDiv = document.createElement('div');
                fieldDiv.className = 'subscriber-field';
                fieldDiv.innerHTML = `
                    <span class="field-icon">${field.icon}</span>
                    <span class="field-label">${field.label}:</span>
                    <span class="field-value">${data[field.key]}</span>
                `;
                card.appendChild(fieldDiv);
            }
        });
        
        return card;
    }

    /**
     * Crea una tarjeta especial para facturas.
     * @param {Array} facturas - Array de facturas.
     * @returns {HTMLElement} La tarjeta de facturas.
     */
    function createFacturasCard(facturas) {
        const card = document.createElement('div');
        card.className = 'facturas-card';
        
        const header = document.createElement('h3');
        header.innerHTML = `📄 Facturas (${facturas.length})`;
        card.appendChild(header);
        
        facturas.forEach(factura => {
            const facturaDiv = document.createElement('div');
            facturaDiv.className = 'factura-item';
            
            const estadoClass = factura.estado === 'Pagado' ? 'estado-pagado' : 'estado-pendiente';
            facturaDiv.innerHTML = `
                <div class="factura-fecha">${factura.fecha || 'Sin fecha'}</div>
                <div class="factura-estado ${estadoClass}">${factura.estado || 'Sin estado'}</div>
                <div class="factura-importe">€${factura.importe || '0'}</div>
            `;
            card.appendChild(facturaDiv);
        });
        
        return card;
    }

    function renderObject(obj) {
        const container = document.createElement('div');
        for (const key in obj) {
            if (Object.prototype.hasOwnProperty.call(obj, key)) {
                const entry = document.createElement('div');
                entry.className = 'json-entry';
                
                const keySpan = document.createElement('span');
                keySpan.className = 'json-key';
                keySpan.textContent = `${key}: `;
                entry.appendChild(keySpan);
                
                const value = obj[key];
                
                if (typeof value === 'object' && value !== null) {
                    const nestedContainer = document.createElement('div');
                    nestedContainer.className = 'json-nested-object';
                    nestedContainer.appendChild(Array.isArray(value) ? renderArray(value) : renderObject(value));
                    entry.appendChild(nestedContainer);
                } else {
                    const valueSpan = document.createElement('span');
                    valueSpan.className = 'json-value';
                    valueSpan.textContent = JSON.stringify(value);
                    entry.appendChild(valueSpan);
                }
                container.appendChild(entry);
            }
        }
        return container;
    }

    function renderArray(arr) {
        const list = document.createElement('div');
        arr.forEach((item, index) => {
            const itemEntry = document.createElement('div');
            itemEntry.className = 'json-entry';
            itemEntry.textContent = `[${index}]: `;
            
            const nestedContainer = document.createElement('div');
            nestedContainer.className = 'json-nested-object';
            
            if (typeof item === 'object' && item !== null) {
                nestedContainer.appendChild(renderObject(item));
            } else {
                nestedContainer.textContent = JSON.stringify(item);
            }
            itemEntry.appendChild(nestedContainer);
            list.appendChild(itemEntry);
        });
        return list;
    }

    /**
     * Desplaza la ventana del chat hasta el final.
     */
    function scrollToBottom() {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    /**
     * Limpia todo el contenido del chat.
     */
    function clearChat() {
        chatWindow.innerHTML = '';
        // Mostrar mensaje de confirmación
        setTimeout(() => {
            displayMessage('🧹 Chat limpiado correctamente', 'bot');
        }, 100);
    }

    // --- Event listeners adicionales ---
    userRoleSelect.addEventListener('change', () => {
        const selectedRole = userRoleSelect.value;
        const roleText = selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1);
        displayMessage(`🔄 Rol cambiado a: ${roleText}`, 'bot');
    });

    // Muestra un mensaje inicial del bot
    setTimeout(() => {
        const initialRole = userRoleSelect.value;
        const roleText = initialRole.charAt(0).toUpperCase() + initialRole.slice(1);
        displayMessage(`¡Bienvenido! Soy tu asistente especializado en gestión de abonados. Estás conectado como: ${roleText}. Puedes preguntarme sobre datos de abonados, facturas, incidencias o el clima.`, 'bot');
    }, 500);
});