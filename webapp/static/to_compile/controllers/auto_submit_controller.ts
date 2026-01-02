import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  handleChange(event: Event) {
    const target = event.target as HTMLFormElement
    // Submit the form when any form element value changes
    target.form?.submit()
  }
}
