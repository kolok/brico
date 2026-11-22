import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["option", "tagSet", "tag", "input", "tagsContainer", "error"]
  static values = {
    name: String,
    max: { type: Number, default: 5 },
  }

  declare optionTargets: HTMLElement[]
  declare tagSetTarget: HTMLElement
  declare tagTargets: HTMLInputElement[]
  declare inputTarget: HTMLInputElement
  declare tagsContainerTarget: HTMLElement
  declare errorTarget: HTMLElement
  declare nameValue: string
  declare maxValue: number

  private tags: string[] = []

  connect() {
    this.loadInitialTags()
    this.render()
  }

  handleKeydown(event: KeyboardEvent) {
    if (event.key === "Enter") {
      event.preventDefault()
      this.addTag()
    } else if (event.key === "Backspace" && this.inputTarget.value === "") {
      this.removeLastTag()
    }
  }

  private addTag() {
    const value = this.inputTarget.value.trim()
    if (!value) return

    if (this.tags.length >= this.maxValue) {
      this.errorTarget.classList.remove("hidden")
      return
    }
    this.errorTarget.classList.add("hidden")

    if (!this.tags.includes(value)) {
      this.tags.push(value)
      this.render()
    }
    this.inputTarget.value = ""
  }

  private removeLastTag() {
    if (this.tags.length === 0) return
    this.tags.pop()
    this.render()
    this.errorTarget.classList.add("hidden")
  }

  removeTag(event: Event) {
    const button = event.currentTarget as HTMLElement
    const index = Number(button.dataset.index)
    this.tags.splice(index, 1)
    this.render()
    this.errorTarget.classList.add("hidden")
  }

  private loadInitialTags() {
    this.tags = this.optionTargets
      .filter((el) => el.dataset.selected === "True")
      .map((el) => el.dataset.label ?? "")
      .filter((label) => label.length > 0)
  }

  private render() {
    this.renderVisualTags()
    this.syncHiddenInputs()
  }

  private renderVisualTags() {
    this.tagsContainerTarget.replaceChildren()
    this.tags.forEach((tag, index) => {
      const el = document.createElement("div")
      el.className = "tag-element"

      const span = document.createElement("span")
      span.textContent = tag

      const button = document.createElement("button")
      button.type = "button"
      button.className = "tag-button"
      button.dataset.index = String(index)
      button.dataset.action = "click->tag-select#removeTag"
      button.textContent = "×"

      el.appendChild(span)
      el.appendChild(button)
      this.tagsContainerTarget.appendChild(el)
    })
  }

  private syncHiddenInputs() {
    this.tagSetTarget.innerHTML = ""
    this.tags.forEach((tag) => {
      const input = document.createElement("input")
      input.type = "hidden"
      input.name = this.nameValue
      input.value = tag
      input.setAttribute("data-tag-select-target", "tag")
      this.tagSetTarget.appendChild(input)
    })
  }
}
