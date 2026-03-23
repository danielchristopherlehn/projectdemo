# Project Audit: Assignment + Proposal Alignment

## Source of truth

- Use the **new database design** you added recently.
- Ignore the **provisional structure** in the proposal unless you need it for historical reference.

## Assignment requirements

From the assignment sheet, the app must include:

- At least **five database models** with meaningful relationships.
- Admin interface support for managing database content.
- At least **five distinct views**, each with a specific purpose.
- Django **templates** for rendering HTML.
- At least **two forms** with validation and feedback.
- Django **authentication** for registration/login/logout and access control where needed.
- **Static assets** such as CSS, images, or JavaScript.
- Git/GitHub collaboration and visible teamwork.

## Proposal direction

From the proposal, the project direction is:

- Household finance and real-estate simulation platform.
- Secure onboarding and authentication.
- Personalized dashboard for each user.
- Active project management.
- Report generation and delivery.
- Data should be private and tied to the logged-in user.

## Current project status

### What already exists

- Django project structure is set up and runs as a multi-app project.
- One real model exists: `Project`.
- Admin registration exists for `Project`.
- Existing views already cover:
  - home
  - dashboard
  - create project
  - delete project
  - project detail / calculator page
- Templates already exist for:
  - dashboard
  - project creation
  - project detail
  - loan calculator
  - mortgage calculator
  - rent-vs-own calculator
  - budget calculator
- One form already exists: `ProjectForm`.
- Calculator logic already works at a basic level inside `projects/views.py`.

### What is missing or weak

- Only **one real database model** exists right now, but the assignment needs at least five.
- Authentication app files exist, but login/register/logout flows are **not implemented**.
- There is only **one proper Django form** so far, but the assignment needs at least two.
- Static styling is basically missing right now.
- The personalized dashboard is still simple and does not yet reflect the richer proposal/database design.
- Report generation and delivery are not implemented.
- Most of the new ER diagram entities are not yet represented as Django models.
- Some logic is too centralized in `projects/views.py` and should be split more cleanly as the app grows.

## Recommended model plan

To satisfy both the assignment and your new ER diagram, this is a practical first set of models:

- `UserProfile`
  - One-to-one with Django `User`
  - Stores currency, country, occupation
- `Project`
  - Already exists
  - Should remain linked to `User`
- `Budget`
  - Linked to `User`
  - Optionally linked to `Project`
- `Income`
  - Linked to `Budget`
- `Expense`
  - Linked to `Budget`
- `Report`
  - Linked to `User` and `Project`

That already gives you **six meaningful models**, which satisfies the assignment and matches the new design well.

## Recommended implementation order

### Phase 1: satisfy the assignment baseline

1. Add the core models:
   - `UserProfile`
   - `Budget`
   - `Income`
   - `Expense`
   - `Report`
2. Register those models in Django admin.
3. Add authentication routes and templates:
   - register
   - login
   - logout
4. Protect dashboard and project pages so they are user-specific.
5. Add at least one more real Django form:
   - budget form
   - or profile form
6. Add a base stylesheet and basic layout.

### Phase 2: align with the proposal

1. Make the dashboard truly personalized.
2. Let users save budget/project data to the database.
3. Add report generation metadata and downloadable output later.
4. Expand into assets, portfolio, calculations, and forecast once the baseline is stable.

## Best next coding task

The highest-value next step is:

1. Implement authentication
2. Add `UserProfile`, `Budget`, `Income`, `Expense`, and `Report` models
3. Wire the dashboard to authenticated users only

That gives your group a stronger foundation for nearly every other required feature.

## Current risk areas

- `dashboard/views.py` already has local uncommitted changes, so edits there should be made carefully.
- `projects/views.py` contains several calculators in one file, which is okay for now but will become harder to maintain as more models are added.
- The project is currently using SQLite and UTC defaults, which is fine for coursework, but user-facing time fields may need clearer handling later.
