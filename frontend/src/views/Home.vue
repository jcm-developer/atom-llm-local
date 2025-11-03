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

        console.log('🔍 [Frontend] Response type:', data.type)

        if (data.type === 'image' && data.imageData) {
            console.log('🖼️ [Frontend] Image detected!')
            console.log('📄 [Frontend] Filename:', data.filename)

            // Create container with relative position for absolute button
            const imageContainer = document.createElement('div')
            imageContainer.style.position = 'relative'
            imageContainer.style.display = 'inline-block'
            imageContainer.style.maxWidth = '100%'
            imageContainer.style.marginTop = '10px'

            // Create image element
            const imgElement = document.createElement('img')
            imgElement.src = data.imageData
            imgElement.alt = data.filename
            imgElement.style.maxWidth = '90%'
            imgElement.style.borderRadius = '12px'
            imgElement.style.cursor = 'pointer'
            imgElement.style.display = 'block'
            imgElement.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'
            imgElement.style.transition = 'transform 0.3s ease'

            // Hover effect
            imgElement.onmouseover = () => {
                imgElement.style.transform = 'scale(1.02)'
            }
            imgElement.onmouseout = () => {
                imgElement.style.transform = 'scale(1)'
            }

            // Create styled download button positioned in the corner
            const downloadBtn = document.createElement('a')
            downloadBtn.href = data.imageData
            downloadBtn.download = data.filename
            downloadBtn.innerHTML = '<span class="material-symbols-outlined" style="margin-right: 8px;">download</span>Download chart'
            downloadBtn.style.position = 'absolute'
            downloadBtn.style.bottom = '16px'
            downloadBtn.style.left = '16px'
            downloadBtn.style.display = 'inline-flex'
            downloadBtn.style.alignItems = 'center'
            downloadBtn.style.justifyContent = 'center'
            downloadBtn.style.padding = '12px 24px'
            downloadBtn.style.background = 'linear-gradient(135deg, #1d7efd 0%, #8f6fff 100%)'
            downloadBtn.style.color = 'white'
            downloadBtn.style.borderRadius = '8px'
            downloadBtn.style.textDecoration = 'none'
            downloadBtn.style.fontSize = '14px'
            downloadBtn.style.fontWeight = '600'
            downloadBtn.style.cursor = 'pointer'
            downloadBtn.style.transition = 'all 0.3s ease'
            downloadBtn.style.boxShadow = '0 4px 12px rgba(29, 126, 253, 0.3)'

            // Button hover effect
            downloadBtn.onmouseover = () => {
                downloadBtn.style.transform = 'translateY(-2px)'
                downloadBtn.style.boxShadow = '0 6px 16px rgba(29, 126, 253, 0.4)'
                downloadBtn.style.background = 'linear-gradient(135deg, #0264e3 0%, #7a5ae8 100%)'
            }
            downloadBtn.onmouseout = () => {
                downloadBtn.style.transform = 'translateY(0)'
                downloadBtn.style.boxShadow = '0 4px 12px rgba(29, 126, 253, 0.3)'
                downloadBtn.style.background = 'linear-gradient(135deg, #1d7efd 0%, #8f6fff 100%)'
            }

            // Function to create full view modal
            const createImageModal = () => {
                // Create overlay
                const modal = document.createElement('div')
                modal.style.position = 'fixed'
                modal.style.top = '0'
                modal.style.left = '0'
                modal.style.width = '100%'
                modal.style.height = '100%'
                modal.style.backgroundColor = 'rgba(0, 0, 0, 0.9)'
                modal.style.display = 'flex'
                modal.style.alignItems = 'center'
                modal.style.justifyContent = 'center'
                modal.style.zIndex = '10000'
                modal.style.cursor = 'pointer'
                modal.style.animation = 'fadeIn 0.3s ease'

                // Create image in modal
                const modalImg = document.createElement('img')
                modalImg.src = data.imageData
                modalImg.alt = data.filename
                modalImg.style.maxWidth = '75%'
                modalImg.style.maxHeight = '75%'
                modalImg.style.borderRadius = '12px'
                modalImg.style.boxShadow = '0 8px 32px rgba(0,0,0,0.5)'
                modalImg.style.cursor = 'default'
                modalImg.style.animation = 'zoomIn 0.3s ease'

                // Close when clicking background
                modal.onclick = (e) => {
                    if (e.target === modal) {
                        modal.style.animation = 'fadeOut 0.3s ease'
                        setTimeout(() => modal.remove(), 300)
                    }
                }

                // Prevent image click from closing modal
                modalImg.onclick = (e) => {
                    e.stopPropagation()
                }

                modal.appendChild(modalImg)
                document.body.appendChild(modal)
            }

            // Click on image to view full size
            imgElement.onclick = createImageModal

            // Assemble elements
            imageContainer.appendChild(imgElement)
            imageContainer.appendChild(downloadBtn)

            // Clear text and add container
            textElement.textContent = ''
            botMsgDiv.appendChild(imageContainer)

            botMsgDiv.classList.remove("loading")
            document.body.classList.remove("bot-responding")
            scrollToBottom()

            chatHistory.push({
                role: "assistant",
                parts: [{ text: '✅ Chart generated', image: data.imageData }]
            })
            return
        }

        if (data.type === 'file' && data.url) {
            console.log('📄 [Frontend] File detected!')
            console.log('📄 [Frontend] Filename:', data.filename)
            console.log('📄 [Frontend] URL:', data.url)

            const filename = data.filename || 'download.pdf'
            const downloadUrl = data.url

            // Create container for message and button
            const pdfContainer = document.createElement('div')
            pdfContainer.style.display = 'flex'
            pdfContainer.style.flexDirection = 'column'
            pdfContainer.style.gap = '12px'
            pdfContainer.style.marginTop = '10px'

            // Create text message
            const messageText = document.createElement('p')
            messageText.textContent = 'Here is your PDF'
            messageText.style.margin = '0'
            messageText.style.fontSize = '15px'
            messageText.style.fontWeight = '500'
            messageText.style.color = 'var(--text-color)'

            // Create styled download button
            const downloadButton = document.createElement('a')
            downloadButton.href = downloadUrl
            downloadButton.download = filename
            downloadButton.target = '_blank'
            downloadButton.innerHTML = '<span class="material-symbols-outlined" style="margin-right: 8px;">download</span>Download PDF'
            downloadButton.style.display = 'inline-flex'
            downloadButton.style.alignItems = 'center'
            downloadButton.style.justifyContent = 'center'
            downloadButton.style.padding = '12px 24px'
            downloadButton.style.background = 'linear-gradient(135deg, #1d7efd 0%, #8f6fff 100%)'
            downloadButton.style.color = 'white'
            downloadButton.style.borderRadius = '8px'
            downloadButton.style.textDecoration = 'none'
            downloadButton.style.fontSize = '14px'
            downloadButton.style.fontWeight = '600'
            downloadButton.style.cursor = 'pointer'
            downloadButton.style.transition = 'all 0.3s ease'
            downloadButton.style.boxShadow = '0 4px 12px rgba(29, 126, 253, 0.3)'
            downloadButton.style.width = 'fit-content'

            // Button hover effect
            downloadButton.onmouseover = () => {
                downloadButton.style.transform = 'translateY(-2px)'
                downloadButton.style.boxShadow = '0 6px 16px rgba(29, 126, 253, 0.4)'
                downloadButton.style.background = 'linear-gradient(135deg, #0264e3 0%, #7a5ae8 100%)'
            }
            downloadButton.onmouseout = () => {
                downloadButton.style.transform = 'translateY(0)'
                downloadButton.style.boxShadow = '0 4px 12px rgba(29, 126, 253, 0.3)'
                downloadButton.style.background = 'linear-gradient(135deg, #1d7efd 0%, #8f6fff 100%)'
            }

            // Assemble elements
            pdfContainer.appendChild(messageText)
            pdfContainer.appendChild(downloadButton)

            // Clear text and add container
            textElement.textContent = ''
            botMsgDiv.appendChild(pdfContainer)

            botMsgDiv.classList.remove("loading")
            document.body.classList.remove("bot-responding")
            scrollToBottom()

            console.log('✅ [Frontend] Download button created!')

            chatHistory.push({
                role: "assistant",
                parts: [{ text: 'Here is your PDF' }]
            })
            return
        }

        console.log('💬 [Frontend] Processing text response...')
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