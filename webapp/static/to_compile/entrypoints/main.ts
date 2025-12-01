import { Application } from "@hotwired/stimulus"
import * as Turbo from "@hotwired/turbo"

declare global {
  interface Window {
    stimulus: Application
  }
}

// Let's keep Stimulus even if we don't use it yet
window.stimulus = Application.start()

// Turbo Drive is disabled, but Turbo Frames still works
Turbo.session.drive = false
