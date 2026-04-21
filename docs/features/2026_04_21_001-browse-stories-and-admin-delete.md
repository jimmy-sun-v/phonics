# Browse Previously Created Stories & Admin Delete

## Description

Add the ability for users to browse their previously created stories within the Story Builder game, and allow administrators to permanently delete stories from the Django admin page. Currently, each visit to the Story Builder starts a fresh session with no way to revisit past stories. This feature improves engagement by letting children re-read and celebrate their past creations, and gives admins moderation control over stored content.

## Requirements

### User-Facing: Browse Stories

1. **Story History Page** – A new page (e.g. `/games/story_builder/history/`) that lists all completed stories for the current browser session.
2. **Story Card Display** – Each story is shown as a card containing:
   - The story summary (from `StorySession.summary`).
   - The creation date (`StorySession.created_at`), formatted in a child-friendly way (e.g. "April 16, 2026").
   - The number of rounds played.
3. **Story Detail View** – Tapping a story card opens a read-only view (`/games/story_builder/history/<story_session_id>/`) that replays the full dialogue trail (child and storyteller turns) in the same bubble UI used during live play.
4. **Navigation** – The Story Builder landing area should include a visible "My Stories" button/link that navigates to the history page.
5. **Empty State** – When no completed stories exist, show a friendly message encouraging the user to create their first story.
6. **Session Scoping** – Stories are scoped to the browser session (via Django session). Only stories whose related `LearningSession.session_id` has been stored in the current session are visible. No authentication is required.

### Admin-Facing: Delete Stories

7. **Register StorySession in Admin** – `StorySession` must be registered in `apps/games/admin.py` so it appears in the Django admin panel.
8. **Admin List Display** – The admin list view should display: story session ID, related learning session, `is_complete`, `created_at`, and a truncated summary (first 80 characters).
9. **Admin Filters** – Filterable by `is_complete` and `created_at`.
10. **Permanent Delete** – Admins can select one or more stories and use the built-in Django admin "Delete selected" action to permanently remove them from the database.
11. **No Soft Delete** – Deletion is permanent (hard delete). No soft-delete or archiving is required for this iteration.

## Solution Options

### Option A: Thin Server + JS-Fetched History

Add a new API endpoint (`GET /api/games/story/history/`) that returns completed stories for the current session. Build the history page and detail view as lightweight Django templates that fetch data via JavaScript (similar to the existing story builder pattern).

| Aspect   | Detail                                                                                                                                                     |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Pros** | Consistent with the existing Story Builder architecture (Django template + JS fetch). Easy to add loading states and future features (pagination, search). |
| **Cons** | Requires both a page view and an API endpoint per feature. Slightly more JS to maintain.                                                                   |

### Option B: Server-Rendered Templates Only

Add Django page views that query `StorySession` and pass the data directly to templates via context. No new API endpoints needed.

| Aspect   | Detail                                                                                                                          |
| -------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Pros** | Simpler implementation; fewer moving parts. No JavaScript required for data loading. Works immediately even if JS is disabled.  |
| **Cons** | Breaks pattern with the existing story builder JS-driven approach. Harder to add dynamic features later (e.g. infinite scroll). |

### Option C: Full REST API + SPA-like Frontend

Build a comprehensive REST API for stories (list, detail, delete) and a JavaScript-heavy single-page-like experience for browsing.

| Aspect   | Detail                                                                                                                                  |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Pros** | Most flexible and reusable. Could support future mobile clients.                                                                        |
| **Cons** | Over-engineered for current needs. Significantly more frontend code. Inconsistent with the rest of the app which uses Django templates. |

## Recommended Solution

**Option A: Thin Server + JS-Fetched History** is recommended.

**Justification:**

1. **Consistency** – The existing Story Builder page already uses the pattern of a Django template that fetches data from an API endpoint via JavaScript. Following the same pattern keeps the codebase uniform and reduces cognitive load for contributors.
2. **Right-Sized Complexity** – It avoids the over-engineering of Option C while still enabling progressive enhancement (pagination, loading spinners) that pure server-rendering (Option B) would make harder.
3. **Admin Delete is Built-In** – Registering `StorySession` in `admin.py` with `ModelAdmin` gives admins full CRUD capability with zero custom code, since Django's admin already provides a "Delete selected" bulk action.

### Implementation Outline

**Backend:**

- Add `GET /api/games/story/history/` – returns list of completed `StorySession` objects scoped to session IDs stored in `request.session`.
- Add `GET /api/games/story/history/<story_session_id>/` – returns full turns for a single story.
- Add `StorySessionAdmin` to `apps/games/admin.py` with `list_display`, `list_filter`, and `search_fields`.

**Frontend:**

- New template `templates/games/story_history.html` – renders the story card grid, fetches data from the history API.
- New template `templates/games/story_detail.html` – renders the read-only bubble trail, fetches turn data from the detail API.
- Add "My Stories" button to the story builder landing area.

**URLs:**

- Page routes: `/games/story_builder/history/`, `/games/story_builder/history/<id>/`.
- API routes: `/api/games/story/history/`, `/api/games/story/history/<id>/`.
