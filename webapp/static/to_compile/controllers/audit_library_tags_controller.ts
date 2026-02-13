import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["select", "input", "hidden"]

  declare selectTarget: HTMLSelectElement
  declare inputTarget: HTMLInputElement
  declare hiddenTarget: HTMLInputElement

  connect() {
    this.syncSelected()
  }

  syncSelected() {
    const selectedOptions = Array.from(this.selectTarget.selectedOptions)
    const names = selectedOptions
      .map((option) => option.textContent?.trim() || "")
      .filter((name) => name.length > 0)

    this.hiddenTarget.value = JSON.stringify(names)
  }

  addTag() {
    const rawValue = this.inputTarget.value.trim()
    if (!rawValue) {
      return
    }

    // Avoid creating duplicate options with the same label
    const existingOption = Array.from(this.selectTarget.options).find(
      (option) => option.textContent?.trim().toLowerCase() === rawValue.toLowerCase(),
    )

    let option: HTMLOptionElement
    if (existingOption) {
      option = existingOption
    } else {
      option = document.createElement("option")
      option.textContent = rawValue
      option.value = rawValue
      this.selectTarget.appendChild(option)
    }

    option.selected = true
    this.inputTarget.value = ""
    this.syncSelected()
  }
}
