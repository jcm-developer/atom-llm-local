<script setup>
const uploadFile = async () => {
    const input = document.createElement("input")
    input.type = "file"
    input.accept = ".pdf"
    input.onchange = async () => {
        const file = input.files[0]
        if (!file) return
        const formData = new FormData()
        formData.append("file", file)

        try {
            const res = await fetch("http://localhost:8001/upload", {
                method: "POST",
                body: formData,
            })
            const data = await res.json()
            alert(`Archivo subido: ${data.file}`)
        } catch (err) {
            console.error(err)
            alert("Error al subir archivo")
        }
    }
    input.click()
}
</script>

<template>
    <div class="panel">
        <h2>Fonts</h2>
        <hr />
        <br>
        <div class="buttons">
            <button class="button" @click="uploadFile">+ Añadir</button>
        </div>
    </div>
</template>

<style scoped>
.button {
    width: 100%;
}
</style>
