import { Controller } from "@hotwired/stimulus"
import { marked } from "marked"

class ChatController extends Controller<HTMLElement> {
  static targets = ["messages", "input", "submitButton", "loading", "title", "markdown"]
  static values = {
    conversationId: Number,
  }

  declare readonly messagesTarget: HTMLDivElement
  declare readonly inputTarget: HTMLInputElement
  declare readonly submitButtonTarget: HTMLButtonElement
  declare readonly loadingTarget: HTMLDivElement
  declare readonly titleTarget: HTMLHeadingElement
  declare readonly markdownTargets: HTMLDivElement[]
  declare conversationIdValue: number

  connect() {
    console.log("Chat controller connected")

    // Configurer marked pour le rendu markdown
    marked.setOptions({
      breaks: true,
      gfm: true,
    })

    // Rendre le markdown pour les messages existants
    this.renderMarkdown()

    // Scroller vers le bas au chargement
    this.scrollToBottom()
  }

  renderMarkdown() {
    this.markdownTargets.forEach((target) => {
      const content = target.textContent || ""
      target.innerHTML = marked.parse(content) as string
    })
  }

  async sendMessage(event: Event) {
    event.preventDefault()

    const message = this.inputTarget.value.trim()
    if (!message) return

    // Désactiver le formulaire pendant l'envoi
    this.inputTarget.disabled = true
    this.submitButtonTarget.disabled = true

    // Ajouter le message de l'utilisateur à l'interface
    this.addUserMessage(message)

    // Vider l'input
    this.inputTarget.value = ""

    // Afficher le loader
    this.loadingTarget.classList.remove("hidden")
    this.scrollToBottom()

    try {
      // Envoyer le message au backend
      const response = await fetch(`/audits/chat/${this.conversationIdValue}/send/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.getCSRFToken(),
        },
        body: JSON.stringify({ message }),
      })

      if (!response.ok) {
        throw new Error("Erreur lors de l'envoi du message")
      }

      const data = await response.json()

      // Masquer le loader
      this.loadingTarget.classList.add("hidden")

      // Ajouter la réponse de l'assistant
      this.addAssistantMessage(data.message.content, data.message.created)

      // Mettre à jour le titre si disponible
      if (data.conversation_title) {
        this.titleTarget.textContent = data.conversation_title
      }

      this.scrollToBottom()
    } catch (error) {
      console.error("Erreur:", error)
      this.loadingTarget.classList.add("hidden")
      alert("Une erreur est survenue lors de l'envoi du message")
    } finally {
      // Réactiver le formulaire
      this.inputTarget.disabled = false
      this.submitButtonTarget.disabled = false
      this.inputTarget.focus()
    }
  }

  addUserMessage(content: string) {
    const messageDiv = document.createElement("div")
    messageDiv.className = "flex justify-end"

    const now = new Date()
    const timeString = now.toLocaleTimeString("fr-FR", {
      hour: "2-digit",
      minute: "2-digit",
    })

    messageDiv.innerHTML = `
      <div class="bg-blue-600 text-white rounded-lg px-4 py-2 max-w-2xl">
        <div class="whitespace-pre-wrap">${this.escapeHtml(content)}</div>
        <div class="text-xs text-blue-200 mt-1">${timeString}</div>
      </div>
    `

    this.messagesTarget.insertBefore(messageDiv, this.loadingTarget)
  }

  addAssistantMessage(content: string, created: string) {
    const messageDiv = document.createElement("div")
    messageDiv.className = "flex justify-start"

    const date = new Date(created)
    const timeString = date.toLocaleTimeString("fr-FR", {
      hour: "2-digit",
      minute: "2-digit",
    })

    // Rendre le markdown
    const htmlContent = marked.parse(content) as string

    messageDiv.innerHTML = `
      <div class="bg-gray-100 text-gray-800 rounded-lg px-4 py-2 max-w-2xl">
        <div class="prose prose-sm max-w-none">${htmlContent}</div>
        <div class="text-xs text-gray-500 mt-1">${timeString}</div>
      </div>
    `

    this.messagesTarget.insertBefore(messageDiv, this.loadingTarget)
  }

  scrollToBottom() {
    setTimeout(() => {
      this.messagesTarget.scrollTop = this.messagesTarget.scrollHeight
    }, 100)
  }

  escapeHtml(text: string): string {
    const div = document.createElement("div")
    div.textContent = text
    return div.innerHTML
  }

  getCSRFToken(): string {
    const token = document.querySelector<HTMLInputElement>(
      '[name="csrfmiddlewaretoken"]',
    )
    if (token) {
      return token.value
    }

    // Fallback: chercher dans les cookies
    const cookies = document.cookie.split(";")
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split("=")
      if (name === "csrftoken") {
        return value
      }
    }

    return ""
  }
}

export default ChatController
