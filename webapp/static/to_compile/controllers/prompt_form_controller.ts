import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["submitButton", "form", "loadingMessage", "emptyStateMessage"]

  declare submitButtonTarget: HTMLButtonElement
  declare formTarget: HTMLFormElement
  declare loadingMessageTarget: HTMLElement
  declare emptyStateMessageTarget: HTMLElement

  connect() {
    // Listen for form submission
    this.formTarget.addEventListener("submit", this.handleSubmit.bind(this))
  }

  disconnect() {
    this.formTarget.removeEventListener("submit", this.handleSubmit.bind(this))
  }

  handleSubmit(event: Event) {
    // Show loading message
    this.loadingMessageTarget.classList.remove("hidden")
    // Hide empty state message
    // @ts-expect-error - Stimulus generates hasEmptyStateMessageTarget dynamically
    if (this.hasEmptyStateMessageTarget) {
      this.emptyStateMessageTarget.classList.add("hidden")
    }
    // Disable submit button to prevent double submission
    this.submitButtonTarget.disabled = true
  }
}
