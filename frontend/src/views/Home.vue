<template>
    <div class="container">
        <!-- App Header -->
        <header class="app-header">
            <h1 class="heading">Hola Jaume</h1>
            <h2 class="sub-heading">En que puedo ayudarte?</h2>
        </header>

        <!-- Suggestions List -->
        <ul class="suggestions">
            <li class="suggestions-item">
                <p class="text">Prepara un informe sobre los gastos anuales de 2025</p>
                <span class="material-symbols-outlined">
                    draw
                </span>
            </li>
            <li class="suggestions-item">
                <p class="text">Cuántos gastos tenemos y en que departamentos están?</p>
                <span class="material-symbols-outlined">
                    lightbulb
                </span>
            </li>
            <li class="suggestions-item">
                <p class="text">Proporciona una lista de todos los trabajadores de la empresa</p>
                <span class="material-symbols-outlined">
                    explore
                </span>
            </li>
            <li class="suggestions-item">
                <p class="text">Diseña un plan de marketing para el próximo año</p>
                <span class="material-symbols-outlined">
                    code_blocks
                </span>
            </li>
        </ul>

        <!-- Chats Container -->
        <div class="chats-container"></div>

        <!-- Prompt Container -->
        <div class="prompt-container">
            <div class="prompt-wrapper">
                <form action="#" class="prompt-form">
                    <input type="text" placeholder="Pregúntame algo..." class="prompt-input" required />
                    <div class="prompt-actions">
                        <!-- Model Toggle Button -->
                        <button type="button" id="model-toggle-btn" class="model-toggle-btn"
                            title="Cambiar entre ChatGPT y Modelo Local">
                            <span class="material-symbols-outlined">computer</span>
                        </button>

                        <button type="button" id="stop-response-btn"
                            class="material-symbols-outlined">stop_circle</button>
                        <button id="send-prompt-btn" class="material-symbols-outlined">arrow_upward</button>
                    </div>
                </form>

                <button id="theme-toggle-btn" class="material-symbols-outlined">light_mode</button>
                <button id="delete-chats-btn" class="material-symbols-outlined">delete</button>
            </div>

            <p class="disclaimer-text">Atom can makes mistakes. Please use it responsibly.</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue"

let container = null
let chatsContainer = null
let promptForm = null
let promptInput = null
let themeToggle = null
let modelToggleBtn = null

let typingInterval, controller
const chatHistory = []
const userData = { message: "" }
const isUsingChatGPT = ref(false)

// Function to create chat message elements
const createMsgElement = (content, ...classes) => {
    const div = document.createElement("div")
    div.classList.add("message", ...classes)
    div.innerHTML = content
    return div
}

// Scroll to bottom of chats
const scrollToBottom = () => container.scrollTo({ top: container.scrollHeight, behavior: "smooth" })

// Typing effect
const typingEffect = (text, textElement, botMsgDiv) => {
    textElement.textContent = ""
    const words = text.split(" ")
    let wordIndex = 0

    typingInterval = setInterval(() => {
        if (wordIndex < words.length) {
            textElement.textContent += (wordIndex === 0 ? "" : " ") + words[wordIndex++]
            scrollToBottom()
        } else {
            clearInterval(typingInterval)
            botMsgDiv.classList.remove("loading")
            document.body.classList.remove("bot-responding")
        }
    }, 40)
}

// Call to backend (Python MCP)
const generateResponse = async (botMsgDiv) => {
    const textElement = botMsgDiv.querySelector(".message-text")
    controller = new AbortController()

    // Add user message to history
    chatHistory.push({
        role: "user",
        parts: [{ text: userData.message }]
    })

    try {
        const backendUrl = `http://localhost:8000/api/chat`

        const requestBody = {
            message: userData.message,
            isUsingChatGPT: isUsingChatGPT.value
        }

        const response = await fetch(backendUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestBody),
            signal: controller.signal
        })

        const data = await response.json()
        console.log('📦 [Frontend] Respuesta del backend:', JSON.stringify(data, null, 2))

        if (!response.ok || data.error) {
            console.error('❌ [Frontend] Error en la respuesta:', data.error)
            throw new Error(data.error || "Error en el backend")
        }

        console.log('🔍 [Frontend] Tipo de respuesta:', data.type)

        if (data.type === 'file' && data.url) {
            console.log('📄 [Frontend] ¡Archivo detectado!')
            console.log('📄 [Frontend] Filename:', data.filename)
            console.log('📄 [Frontend] URL:', data.url)

            const filename = data.filename || 'download.pdf'
            const downloadUrl = data.url

            console.log('🔗 [Frontend] Creando enlace de descarga...')
            const link = document.createElement('a')
            link.href = downloadUrl
            link.download = filename
            link.target = '_blank'
            document.body.appendChild(link)
            console.log('👆 [Frontend] Haciendo click en el enlace...')
            link.click()
            console.log('🗑️ [Frontend] Eliminando enlace del DOM...')
            document.body.removeChild(link)
            console.log('✅ [Frontend] Descarga iniciada!')

            const successMessage = '✅ PDF Generado!'
            typingEffect(successMessage, textElement, botMsgDiv)

            chatHistory.push({
                role: "assistant",
                parts: [{ text: successMessage }]
            })
            return
        }

        console.log('💬 [Frontend] Procesando respuesta de texto...')
        const botResponse = data.response.trim()

        typingEffect(botResponse, textElement, botMsgDiv)

        chatHistory.push({
            role: "model",
            parts: [{ text: botResponse }]
        })
    } catch (error) {
        console.error('❌ [Frontend] Error capturado:', error)
        textElement.style.color = "#d62939"
        textElement.textContent = error.name === "AbortError" ? "Response generation stopped." : error.message
        botMsgDiv.classList.remove("loading")
        document.body.classList.remove("bot-responding")
    }
}

// Send prompt
const handleFormSubmit = (e) => {
    e.preventDefault()

    const userMessage = promptInput.value.trim()

    if (!userMessage || document.body.classList.contains("bot-responding")) {
        console.warn('⚠️ [Frontend] Mensaje vacío o bot ya respondiendo')
        return
    }

    promptInput.value = ""
    userData.message = userMessage
    document.body.classList.add("bot-responding", "chats-active")

    const userMsgHTML = `<p class="message-text"></p>`
    const userMsgDiv = createMsgElement(userMsgHTML, "user-message")
    userMsgDiv.querySelector(".message-text").textContent = userMessage
    chatsContainer.appendChild(userMsgDiv)
    scrollToBottom()

    setTimeout(() => {
        const botMsgHTML = `<img src="atom.svg" alt="" class="avatar"><p class="message-text">Procesando...</p>`
        const botMsgDiv = createMsgElement(botMsgHTML, "bot-message", "loading")
        chatsContainer.appendChild(botMsgDiv)
        scrollToBottom()
        generateResponse(botMsgDiv)
    }, 600)
}

// Lifecycle
onMounted(() => {
    container = document.querySelector(".container")
    chatsContainer = document.querySelector(".chats-container")
    promptForm = document.querySelector(".prompt-form")
    promptInput = document.querySelector(".prompt-input")
    themeToggle = document.querySelector("#theme-toggle-btn")
    modelToggleBtn = document.querySelector("#model-toggle-btn")

    // Toggle model between ChatGPT and local
    modelToggleBtn.addEventListener("click", () => {
        isUsingChatGPT.value = !isUsingChatGPT.value

        modelToggleBtn.classList.toggle("active", isUsingChatGPT.value)
        modelToggleBtn.querySelector("span").textContent = isUsingChatGPT.value ? "cloud" : "computer"
        modelToggleBtn.title = isUsingChatGPT.value
            ? "ChatGPT (modo abierto)"
            : "Modelo Local (modo privado)"
    })

    // Stop response generation
    document.querySelector("#stop-response-btn").addEventListener("click", () => {
        controller?.abort()
        clearInterval(typingInterval)
        const loadingBot = chatsContainer?.querySelector(".bot-message.loading")
        if (loadingBot) loadingBot.classList.remove("loading")
        document.body.classList.remove("bot-responding")
    })

    // Delete chats
    document.querySelector("#delete-chats-btn").addEventListener("click", () => {
        chatHistory.length = 0
        chatsContainer.innerHTML = ""
        document.body.classList.remove("bot-responding", "chats-active")
    })

    // Suggestions click events
    document.querySelectorAll(".suggestions-item").forEach(item => {
        item.addEventListener("click", () => {
            promptInput.value = item.querySelector(".text").textContent
            promptForm.dispatchEvent(new Event("submit"))
        })
    })

    // Toggle theme
    themeToggle.addEventListener("click", () => {
        const isLightTheme = document.body.classList.toggle("light-theme")
        localStorage.setItem("themeColor", isLightTheme ? "light_mode" : "dark_mode")
        themeToggle.textContent = isLightTheme ? "dark_mode" : "light_mode"
    })

    // Apply saved theme
    const isLightTheme = localStorage.getItem("themeColor") === "light_mode"
    document.body.classList.toggle("light-theme", isLightTheme)
    themeToggle.textContent = isLightTheme ? "dark_mode" : "light_mode"

    promptForm.addEventListener("submit", handleFormSubmit)
})
</script>