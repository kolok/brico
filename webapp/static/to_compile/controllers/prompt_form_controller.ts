import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["submitButton", "loadingMessage", "emptyStateMessage"]

  declare submitButtonTarget: HTMLButtonElement
  declare loadingMessageTarget: HTMLElement
  declare emptyStateMessageTarget: HTMLElement

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
