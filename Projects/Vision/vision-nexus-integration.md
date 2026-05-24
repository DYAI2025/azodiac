# Vision Nexus Integration Plan

## Goal
Fully integrate the "Nexus-UI" into the Vision project as a desktop-launchable application with real-time connections to WhatsOrga (radar-api), GBrain (EverMemOS), Obsidian Kanban, and Slack.

## Tasks
- [ ] **Setup**: Initialize a Vite + React + TypeScript project in `ai-sdlc-scaffold-main/3-code/vision-nexus` → Verify: `npm run dev` starts a local server.
- [ ] **Component Port**: Convert the `nexus-ui.html` mockup into modular React components (Sidebar, Tabs, Viewport, Kanban) → Verify: UI renders identical to mockup.
- [ ] **WhatsOrga Link**: Implement a WebSocket/Polling client to fetch live ingestion data from `radar-api` (Port 8000) → Verify: Real messages appear in the central feed.
- [ ] **GBrain Integration**: Connect the "Graph" tab to the `EverMemOS` retrieval API (Port 8001) → Verify: Semantic search returns real project artifacts.
- [ ] **Obsidian Sync**: Implement a local file-system bridge to read/write Obsidian Kanban markdown files → Verify: Changes in the UI reflect in Obsidian and vice-versa.
- [ ] **Slack Integration**: Setup a Slack Socket Mode or Webhook listener to display real-time team communication → Verify: Slack messages show up in the left sidebar.
- [ ] **Desktop Wrapper**: Create a `bin/vision-nexus` launch script and an Electron/Tauri scaffold for desktop execution → Verify: App opens as a standalone window.

## Done When
- [ ] Vision Nexus is a standalone application in the `3-code` directory.
- [ ] It displays real data from all four integrated systems (WhatsOrga, GBrain, Obsidian, Slack).
- [ ] Persistent memory and backlog updates are fully functional.

## Notes
- Adhere to the scaffold's `CLAUDE.md` rules: English code/comments only.
- Use the established `radar-api` and `EverMemOS` endpoints.
- Ensure the Obsidian bridge handles file locks/concurrency safely.
