import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["menu", "toggle"]

  declare menuTarget: HTMLElement
  declare toggleTarget: HTMLElement

  connect() {
    // Close the dropdown if clicked elsewhere
    document.addEventListener("click", this.handleClickOutside.bind(this))
  }

  disconnect() {
    document.removeEventListener("click", this.handleClickOutside.bind(this))
  }

  toggle() {
    this.menuTarget.classList.toggle("hidden")
    const isExpanded = !this.menuTarget.classList.contains("hidden")
    this.toggleTarget.setAttribute("aria-expanded", String(isExpanded))
  }

  handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement
    if (
      !this.element.contains(target) &&
      !this.menuTarget.classList.contains("hidden")
    ) {
      this.menuTarget.classList.add("hidden")
      this.toggleTarget.setAttribute("aria-expanded", "false")
    }
  }
}
