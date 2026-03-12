---
description: "Add or update UI elements after new API endpoints or features"
allowed-tools: ["Bash", "Read", "Write", "Edit", "Glob"]
---

## Your Task

Update the project's UI (web frontend, playground, dashboard) to expose a new or changed API endpoint.

### Steps

1. **Discover UI files** — Find the frontend code:
   ```bash
   # Check common locations
   ls -la src/ app/ pages/ static/ public/ api/static/ 2>/dev/null
   ```

2. **Read the endpoint** — Check the API route for request/response models.

3. **Read existing UI patterns** — Understand current structure, styles, and conventions before adding.

4. **Add UI section:**
   - Add a new tab/section/page for the endpoint
   - Input form matching the request model
   - Result display area with proper formatting
   - Use existing UI patterns (copy from similar endpoint sections)

5. **Test:**
   - Start the dev server
   - Verify the new UI element renders
   - Verify the API call works end-to-end
   - Verify existing functionality still works

### Guardrails
- Match existing UI style (fonts, colors, layout, framework)
- Include error handling in the UI (show error messages to user)
- Don't break existing endpoint UIs
- Use the same JS framework / approach already in the project (don't introduce React into a vanilla JS project, etc.)
