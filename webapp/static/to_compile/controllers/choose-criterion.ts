import { Controller } from "@hotwired/stimulus"

class ChooseCriterionController extends Controller<HTMLElement> {
  static targets = ["organization"]
  declare readonly organizationTarget: HTMLSelectElement

  connect() {
    console.log("choose-criterion controller connected")
  }

  getChooseCriterion(event: Event) {
    event.preventDefault()
    // Le contrôleur est sur le form, on peut le soumettre directement
    console.log("this.element", this.element)
    console.log("event.target", event.target)
    if (this.element instanceof HTMLFormElement) {
      this.element.requestSubmit()
    } else {
      console.error("Controller element is not a form")
    }
  }
}

export default ChooseCriterionController
