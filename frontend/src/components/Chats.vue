<script setup>
import { ref } from "vue"

const props = defineProps({
    conversations: Array,
    activeId: String
})
const emit = defineEmits(["select", "new", "delete", "rename"])

const editingId = ref(null)
const newTitle = ref("")
</script>

<template>
    <div class="panel">
        <h2>Chats</h2>
        <hr />
        <br>
        <button class="button" @click="emit('new')">+ Nueva conversación</button>

        <ul class="chat-list">
            <li v-for="c in conversations" :key="c.id" :class="{ active: c.id === activeId }"
                @click="emit('select', c.id)">
                <!-- Modo edición -->
                <template v-if="editingId === c.id">
                    <input v-model="newTitle" @keyup.enter="emit('rename', c.id, newTitle); editingId = null"
                        @blur="emit('rename', c.id, newTitle); editingId = null" class="rename-input" @click.stop />
                </template>

                <!-- Vista normal -->
                <template v-else>
                    <span>{{ c.title }}</span>
                    <div class="actions">
                        <button @click.stop="editingId = c.id; newTitle = c.title">✏️</button>
                        <button @click.stop="emit('delete', c.id)">🗑️</button>
                    </div>
                </template>
            </li>
        </ul>
    </div>
</template>

<style scoped>
.chat-list {
    list-style: none;
    padding: 0;
    margin: 12px 0 0 0;
}

.chat-list li {
    padding: 0px 12px;
    border-radius: 18px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.chat-list li:hover {
    background: #33363a;
    /* hover gris más claro */
}

.chat-list li.active {
    background: #2a2d31;
    /* activo gris oscuro */
    font-weight: bold;
}

.actions {
    display: flex;
    gap: 6px;
}

.actions button {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 14px;
}

.rename-input {
    flex: 1;
    padding: 4px 6px;
    border-radius: 4px;
    border: 1px solid #374151;
    background: #111827;
    color: #e5e7eb;
}
</style>
