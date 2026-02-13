import { Application } from "@hotwired/stimulus"
import * as Turbo from "@hotwired/turbo"
import AutoSubmitController from "../controllers/auto_submit_controller"
import DropdownController from "../controllers/dropdown_controller"
import PromptFormController from "../controllers/prompt_form_controller"
import AuditLibraryTagsController from "../controllers/audit_library_tags_controller"

declare global {
  interface Window {
    stimulus: Application
  }
}

// Let's keep Stimulus even if we don't use it yet
window.stimulus = Application.start()
window.stimulus.register("dropdown", DropdownController)
window.stimulus.register("auto-submit", AutoSubmitController)
window.stimulus.register("prompt-form", PromptFormController)
window.stimulus.register("audit-library-tags", AuditLibraryTagsController)

// Turbo Drive is disabled, but Turbo Frames still works
Turbo.session.drive = false
