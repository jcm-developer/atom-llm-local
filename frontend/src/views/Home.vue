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
                <p class="text">Haz un diseño de oficina para trabajo remoto con un presupuesto de 500€</p>
                <span class="material-symbols-outlined">
                    draw
                </span>
            </li>
            <li class="suggestions-item">
                <p class="text">Crea un plan de negocio para un negocio de ventas online</p>
                <span class="material-symbols-outlined">
                    lightbulb
                </span>
            </li>
            <li class="suggestions-item">
                <p class="text">Proporciona una lista de recursos para aprender sobre el desarrollo web</p>
                <span class="material-symbols-outlined">
                    explore
                </span>
            </li>
            <li class="suggestions-item">
                <p class="text">Proporciona un tutorial sobre cómo crear un sitio web de inicio</p>
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
const isUsingChatGPT = ref(false) // false = Local Model, true = ChatGPT

// Function to create message elements
const createMsgElement = (content, ...classes) => {
    const div = document.createElement("div")
    div.classList.add("message", ...classes)
    div.innerHTML = content
    return div
}

// Scroll to the bottom of the container
const scrollToBottom = () => container.scrollTo({ top: container.scrollHeight, behavior: "smooth" })

// Simulate typing effect for bot responses
const typingEffect = (text, textElement, botMsgDiv) => {
    textElement.textContent = ""
    const words = text.split(" ")
    let wordIndex = 0

    // Set an interval to type each word
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

// Make the API call and generate the bot's response
const generateResponse = async (botMsgDiv) => {
    const textElement = botMsgDiv.querySelector(".message-text")
    controller = new AbortController()

    // Add user message to the chat history
    chatHistory.push({
        role: "user",
        parts: [{ text: userData.message }]
    })

    try {
        let response, data

        if (isUsingChatGPT.value) {
            // Use ChatGPT API
            response = await fetch(`https://api.openai.com/v1/chat/completions`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${import.meta.env.VITE_OPENAI_API_KEY}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    model: "gpt-3.5-turbo",
                    messages: [
                        { role: "system", content: "Answer always in the user language" },
                        { role: "user", content: userData.message }
                    ]
                }),
                signal: controller.signal
            })

            data = await response.json()
            if (!response.ok) throw new Error(data.error?.message || "Error en la API de ChatGPT")

            const textResponse = data.choices[0].message.content.trim()
            typingEffect(textResponse, textElement, botMsgDiv)

            chatHistory.push({
                role: "model",
                parts: [{ text: textResponse }]
            })
        } else {
            // Use Local Model (Anything LLM)
            response = await fetch(`${import.meta.env.VITE_ANYTHING_LLM_URL}/api/v1/workspace/rag/chat`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${import.meta.env.VITE_ANYTHING_LLM_API_KEY}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: userData.message, rules: "Answer always in the user language" }),
                signal: controller.signal
            })

            data = await response.json()
            if (!response.ok) throw new Error(data.error.message)

            // Process the response text and display with typing effect
            const textResponse = data.textResponse.replace(/\*\*([^*]+)\*\*/g, "$1").trim()
            typingEffect(textResponse, textElement, botMsgDiv)

            chatHistory.push({
                role: "model",
                parts: [{ text: textResponse }]
            })
        }
    } catch (error) {
        textElement.style.color = "#d62939"
        textElement.textContent = error.name === "AbortError" ? "Response generation stopped." : error.message
        botMsgDiv.classList.remove("loading")
        document.body.classList.remove("bot-responding")
    }
}

// Handle the form submission
const handleFormSubmit = (e) => {
    e.preventDefault()
    const userMessage = promptInput.value.trim()
    if (!userMessage || document.body.classList.contains("bot-responding")) return

    promptInput.value = ""
    userData.message = userMessage
    document.body.classList.add("bot-responding", "chats-active")

    // Generate user message HTML
    const userMsgHTML = `<p class="message-text"></p>`
    const userMsgDiv = createMsgElement(userMsgHTML, "user-message")

    userMsgDiv.querySelector(".message-text").textContent = userMessage
    chatsContainer.appendChild(userMsgDiv)
    scrollToBottom()

    setTimeout(() => {
        // Generate bot message HTML and add in the chats container after 600ms
        const botMsgHTML = `<img src="atom.svg" alt="" class="avatar"><p class="message-text">Procesando...</p>`
        const botMsgDiv = createMsgElement(botMsgHTML, "bot-message", "loading")
        chatsContainer.appendChild(botMsgDiv)
        scrollToBottom()
        generateResponse(botMsgDiv)
    }, 600)
}

onMounted(() => {
    container = document.querySelector(".container")
    chatsContainer = document.querySelector(".chats-container")
    promptForm = document.querySelector(".prompt-form")
    promptInput = document.querySelector(".prompt-input")
    themeToggle = document.querySelector("#theme-toggle-btn")
    modelToggleBtn = document.querySelector("#model-toggle-btn")

    // Toggle between ChatGPT and Local Model
    modelToggleBtn.addEventListener("click", () => {
        isUsingChatGPT.value = !isUsingChatGPT.value
        modelToggleBtn.classList.toggle("active", isUsingChatGPT.value)
        modelToggleBtn.querySelector("span").textContent = isUsingChatGPT.value ? "cloud" : "computer"
        modelToggleBtn.title = isUsingChatGPT.value ? "ChatGPT (Abierto)" : "Modelo Local (Privado)"
    })

    // Stop ongoing bot response
    document.querySelector("#stop-response-btn").addEventListener("click", () => {
        controller?.abort()
        clearInterval(typingInterval)
        // The loading bot element may not exist — guard before calling classList
        const loadingBot = chatsContainer?.querySelector(".bot-message.loading")
        if (loadingBot) loadingBot.classList.remove("loading")
        document.body.classList.remove("bot-responding")
    })

    // Delete all chats
    document.querySelector("#delete-chats-btn").addEventListener("click", () => {
        chatHistory.length = 0
        chatsContainer.innerHTML = ""
        document.body.classList.remove("bot-responding", "chats-active")
    })

    // Handle suggestions click
    document.querySelectorAll(".suggestions-item").forEach(item => {
        item.addEventListener("click", () => {
            promptInput.value = item.querySelector(".text").textContent
            promptForm.dispatchEvent(new Event("submit"))
        })
    })

    // Show/hide controls for mobile on prompt input focus
    document.addEventListener("click", ({ target }) => {
        const wrapper = document.querySelector(".prompt-wrapper")
        const shouldHide = target.classList.contains("prompt-input") || (wrapper.classList.contains("hide-controls") && target.id === "stop-response-btn")
        wrapper.classList.toggle("hide-controls", shouldHide)
    })

    // Toggle dark/light theme
    themeToggle.addEventListener("click", () => {
        const isLightTheme = document.body.classList.toggle("light-theme")
        localStorage.setItem("themeColor", isLightTheme ? "light_mode" : "dark_mode")
        themeToggle.textContent = isLightTheme ? "dark_mode" : "light_mode"
    })

    // Set initial theme from local storage
    const isLightTheme = localStorage.getItem("themeColor") === "light_mode"
    document.body.classList.toggle("light-theme", isLightTheme)
    themeToggle.textContent = isLightTheme ? "dark_mode" : "light_mode"

    promptForm.addEventListener("submit", handleFormSubmit)
})
</script>
