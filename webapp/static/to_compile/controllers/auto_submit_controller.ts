import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["loading"]

  declare loadingTarget: HTMLElement

  handleChange(event: Event) {
    const target = event.target as HTMLFormElement
    const form = target.form
    if (!form) return

    // Show loading indicator
    this.loadingTarget.classList.remove("hidden")
    // Submit the form when any form element value changes
    form.submit()
  }
}
