import { Application } from "@hotwired/stimulus"
import * as Turbo from "@hotwired/turbo"

import ChooseCriterionController from "../controllers/choose-criterion"
import ChatController from "../controllers/chat"

declare global {
  interface Window {
    stimulus: Application
  }
}

window.stimulus = Application.start()

window.stimulus.register("choose-criterion", ChooseCriterionController)
window.stimulus.register("chat", ChatController)

Turbo.session.drive = false
