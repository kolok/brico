import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["menu", "toggle"]

  declare menuTarget: HTMLElement
  declare toggleTarget: HTMLElement

  private currentIndex: number = -1
  private menuItems: HTMLElement[] = []

  connect() {
    // Close the dropdown if clicked elsewhere
    document.addEventListener("click", this.handleClickOutside.bind(this))
    // Handle keyboard events
    this.toggleTarget.addEventListener("keydown", this.handleToggleKeydown.bind(this))
    this.menuTarget.addEventListener("keydown", this.handleMenuKeydown.bind(this))
    this.updateMenuItems()
  }

  disconnect() {
    document.removeEventListener("click", this.handleClickOutside.bind(this))
    this.toggleTarget.removeEventListener(
      "keydown",
      this.handleToggleKeydown.bind(this),
    )
    this.menuTarget.removeEventListener("keydown", this.handleMenuKeydown.bind(this))
  }

  toggle() {
    this.menuTarget.classList.toggle("hidden")
    const isExpanded = !this.menuTarget.classList.contains("hidden")
    this.toggleTarget.setAttribute("aria-expanded", String(isExpanded))

    if (isExpanded) {
      this.updateMenuItems()
      this.currentIndex = -1
      // Focus first item if available
      if (this.menuItems.length > 0) {
        this.currentIndex = 0
        this.focusItem(this.currentIndex)
      }
    } else {
      this.currentIndex = -1
    }
  }

  close() {
    if (!this.menuTarget.classList.contains("hidden")) {
      this.menuTarget.classList.add("hidden")
      this.toggleTarget.setAttribute("aria-expanded", "false")
      this.toggleTarget.focus()
      this.currentIndex = -1
    }
  }

  updateMenuItems() {
    this.menuItems = Array.from(
      this.menuTarget.querySelectorAll('[role="menuitem"]'),
    ) as HTMLElement[]
  }

  focusItem(index: number) {
    if (index >= 0 && index < this.menuItems.length) {
      this.menuItems[index].focus()
      this.currentIndex = index
    }
  }

  handleToggleKeydown(event: KeyboardEvent) {
    if (event.key === "Enter" || event.key === " " || event.key === "ArrowDown") {
      event.preventDefault()
      if (this.menuTarget.classList.contains("hidden")) {
        this.toggle()
      } else if (event.key === "ArrowDown") {
        this.updateMenuItems()
        if (this.menuItems.length > 0) {
          this.currentIndex = 0
          this.focusItem(this.currentIndex)
        }
      }
    } else if (event.key === "Escape") {
      this.close()
    }
  }

  handleMenuKeydown(event: KeyboardEvent) {
    if (this.menuTarget.classList.contains("hidden")) {
      return
    }

    switch (event.key) {
      case "Escape":
        event.preventDefault()
        this.close()
        break

      case "ArrowDown":
        event.preventDefault()
        this.updateMenuItems()
        if (this.menuItems.length > 0) {
          this.currentIndex = (this.currentIndex + 1) % this.menuItems.length
          this.focusItem(this.currentIndex)
        }
        break

      case "ArrowUp":
        event.preventDefault()
        this.updateMenuItems()
        if (this.menuItems.length > 0) {
          this.currentIndex =
            this.currentIndex <= 0 ? this.menuItems.length - 1 : this.currentIndex - 1
          this.focusItem(this.currentIndex)
        }
        break

      case "Home":
        event.preventDefault()
        this.updateMenuItems()
        if (this.menuItems.length > 0) {
          this.currentIndex = 0
          this.focusItem(this.currentIndex)
        }
        break

      case "End":
        event.preventDefault()
        this.updateMenuItems()
        if (this.menuItems.length > 0) {
          this.currentIndex = this.menuItems.length - 1
          this.focusItem(this.currentIndex)
        }
        break

      case "Enter":
      case " ":
        // Let the default behavior handle the click on links
        // But prevent default if it's not a link
        const target = event.target as HTMLElement
        if (target.tagName !== "A") {
          event.preventDefault()
          target.click()
        }
        break
    }
  }

  handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement
    if (
      !this.element.contains(target) &&
      !this.menuTarget.classList.contains("hidden")
    ) {
      this.menuTarget.classList.add("hidden")
      this.toggleTarget.setAttribute("aria-expanded", "false")
      this.currentIndex = -1
    }
  }
}
