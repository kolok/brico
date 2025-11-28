import { Application } from "@hotwired/stimulus"
import * as Turbo from "@hotwired/turbo"

import ChatController from "../controllers/chat"
import ChooseCriterionController from "../controllers/choose-criterion"

declare global {
  interface Window {
    stimulus: Application
  }
}

window.stimulus = Application.start()

window.stimulus.register("choose-criterion", ChooseCriterionController)
window.stimulus.register("chat", ChatController)

// Turbo Drive est désactivé, mais Turbo Frames fonctionne toujours
Turbo.session.drive = false
