<script setup>
import { ref, nextTick, watch, onMounted } from "vue"

const props = defineProps({
    conversation: Object
})
const inputText = ref("")
const isTyping = ref(false)
const chatBody = ref(null)   // 👈 ref al contenedor

const sendMessage = async () => {
    if (!inputText.value.trim()) return

    props.conversation.messages.push({ role: "user", content: inputText.value })
    const myMessage = inputText.value
    inputText.value = ""

    isTyping.value = true

    try {
        const formData = new FormData()
        formData.append("question", myMessage)

        const res = await fetch("http://localhost:8001/query", {
            method: "POST",
            body: formData,
        })
        const data = await res.json()

        props.conversation.messages.push({ role: "assistant", content: data.answer })

        if (
            props.conversation.title.startsWith("Conversación") &&
            props.conversation.messages.length === 2
        ) {
            props.conversation.title = myMessage.slice(0, 30) + "..."
        }
    } catch (err) {
        props.conversation.messages.push({
            role: "assistant",
            content: "⚠️ Error al consultar el LLM",
        })
    } finally {
        isTyping.value = false
    }
}

// 👉 Formateo básico Markdown
function formatText(text) {
    let html = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    html = html.replace(/\*(.*?)\*/g, "<em>$1</em>")
    return html
}

// 👉 Función de scroll
const scrollToBottom = async () => {
    await nextTick()
    if (chatBody.value) {
        chatBody.value.lastElementChild?.scrollIntoView({ behavior: "smooth" })
    }
}

// 👀 Auto-scroll al cambiar mensajes o typing
watch(
    () => [props.conversation.messages.length, isTyping.value],
    scrollToBottom
)

// 👀 Auto-scroll al cargar la primera vez
onMounted(scrollToBottom)
</script>

<template>
    <div class="panel chat-panel">
        <h2>Chat</h2>
        <hr />

        <!-- cuerpo de chat -->
        <div class="chat-body" ref="chatBody">
            <div v-for="(msg, i) in conversation.messages" :key="i" class="chat-message" :class="msg.role">
                <p style="font-size: 14px;" v-html="formatText(msg.content)"></p>
            </div>

            <!-- indicador de escribiendo -->
            <div v-if="isTyping" class="chat-message assistant">
                <div class="typing">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </div>
            </div>
        </div>

        <!-- barra de entrada -->
        <div class="buttons">
            <input v-model="inputText" type="text" class="chat-input" placeholder="Escribe un mensaje..."
                @keyup.enter="sendMessage" />
            <button class="button" @click="sendMessage">Enviar</button>
        </div>
    </div>
</template>

<style scoped>
.chat-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.chat-body {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.chat-message {
    max-width: 70%;
    padding: 10px 14px;
    border-radius: 8px;
    word-wrap: break-word;
    white-space: pre-wrap;
    line-height: 1.4;
}

.chat-message.user {
    align-self: flex-end;
    background: #272c31;
    color: #e5e7eb;
    border-radius: 18px;
}

.chat-message.assistant {
    align-self: flex-start;
    background: transparent;
    color: #e5e7eb;
}

/* barra input */
.buttons {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px;
}

.buttons input {
    flex: 1;
    padding: 16px;
}

.buttons button {
    width: 15%;
    padding: 16px;
}

/* animación typing */
.typing {
    display: flex;
    gap: 4px;
    align-items: center;
    padding: 4px 0;
}

.dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #e5e7eb;
    opacity: 0.5;
    animation: blink 1.2s infinite;
}

.dot:nth-child(2) {
    animation-delay: .2s;
}

.dot:nth-child(3) {
    animation-delay: .4s;
}

@keyframes blink {

    0%,
    100% {
        opacity: .2
    }

    50% {
        opacity: 1
    }
}
</style>
