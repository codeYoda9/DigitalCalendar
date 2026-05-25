You are working in the existing DigitalCalendar project.

Goal:
Implement Workflows as a household planning workflow focused on meal planning, grocery list updates, shopping reminders, and task follow-through.

Current project context:
- The project is a local self-hosted Digital Calendar / household command center.
- Existing deployment uses Docker Compose.
- Existing homepage/dashboard already exists.
- Obsidian-exported HTML files are available under public/obsidian.
- Previous files included:
  - public/obsidian/Grocery List.html
  - public/obsidian/Personal/Home Dashboard.html
  - public/obsidian/Weekly Todo.html
- Phase 1 already established the base dashboard structure.
- Workflows must build on the existing codebase, not replace it.

Workflows user intent:
The system is for the whole household.
The main desired outcomes are:
- Less missed planning
- Less mental load
- Better meal and grocery execution
- Better task completion

Core workflow:
Diet plan → meal plan → grocery list → shopping reminder → task follow-through

Real-world success test:
On Saturday, the system should help parse a diet plan, pick meals, update the grocery list, and remind the household to shop.

Hard exclusions:
Do NOT implement:
- New hardware support
- Mobile app
- Voice assistant
- Receipt parsing
- AI automation
- Cloud-only dependencies
- Paid third-party services
- Complex user accounts
- Internet recipe scraping

Important constraint:
Do not assume the system should become a general-purpose calendar app.
Workflows is about household execution, especially meals, groceries, and weekly tasks.

Implementation approach:
Make the simplest useful local workflow first.
Prefer predictable rules, editable files, and transparent output over clever automation.
The system should be easy to debug and operate from a home server.

Required features:

1. Diet plan input
Implement a local diet plan input mechanism.

Accept at least one simple local source:
- A markdown file, JSON file, YAML file, or plain text file stored in the repo or mounted data directory.

Create a clear example diet plan file.

The diet plan should support:
- Days of week
- Meal slots, such as breakfast, lunch, dinner, snack
- Dietary constraints or notes
- Optional preferred meals
- Optional excluded ingredients

Do not require AI parsing.
Use deterministic parsing.

2. Meal planning engine
Implement a meal planning script or service that reads the diet plan and generates a weekly meal plan.

Meal source should be local.
Support one or more of:
- A local recipes JSON/YAML/markdown directory
- Existing Obsidian recipe notes if available
- A simple seed recipe file created as part of this implementation

Each recipe should include:
- Name
- Meal type
- Ingredients
- Servings
- Tags
- Optional dietary notes
- Optional prep time
- Optional source link or source filename

Meal selection behavior:
- Match recipes to meal slots using meal type and tags.
- Respect excluded ingredients where possible.
- Prefer predictable repeatable output.
- Avoid random behavior unless seeded.
- If no recipe matches, emit a visible warning.
- Do not silently skip missing meals.

Output:
Generate a weekly meal plan file.
Use a human-readable format such as markdown and a machine-readable format such as JSON if useful.

3. Grocery list generation
Implement grocery list generation from the weekly meal plan.

The grocery list should:
- Combine duplicate ingredients.
- Group items by category if categories are available.
- Keep unmatched or uncategorized items in an “Other” section.
- Preserve warnings for ambiguous quantities.
- Produce a human-readable grocery list.

Output destination:
Create or update a local grocery list artifact that can be shown on the dashboard.

Preferred outputs:
- public/generated/grocery-list.html
- public/generated/grocery-list.md
- public/generated/meal-plan.html
- public/generated/meal-plan.md
- public/generated/workflow-status.json

Do not overwrite user-authored Obsidian files directly unless the existing project already does this safely.
Generated files should live in a generated output directory.

4. Dashboard integration
Update the homepage/dashboard to include Workflows panels.

Add panels for:
- This week’s meal plan
- Grocery list
- Saturday shopping reminder
- Task follow-through status
- Warnings or missing data

The dashboard should clearly show:
- Whether the meal plan was generated successfully
- Last generated timestamp
- Number of grocery items
- Any missing meals
- Any recipe or ingredient parsing warnings

If generated files are missing, the dashboard should show a useful empty state instead of a broken link or 404.

5. Shopping reminder
Implement a Saturday shopping reminder in the local dashboard.

Minimum viable reminder:
- A visible dashboard reminder on Saturday.
- It should say that the grocery list should be reviewed and shopping completed.
- It should link to the generated grocery list.

Do not implement phone push notifications in this phase unless the project already has a simple notification mechanism.
If no notification mechanism exists, create a clear extension point for future notifications.

6. Task follow-through
Add a lightweight weekly task checklist.

The checklist should support at least:
- Generate meal plan
- Review meal plan
- Generate grocery list
- Review grocery list
- Shop groceries

Store state locally, preferably in JSON.

The dashboard should show completed versus pending tasks.

Implement a simple way to mark tasks done if the current app has interactivity.
If the dashboard is static-only, generate task status from a local JSON file and document how to edit it.

7. CLI commands
Add commands to run Workflows manually.

Examples:
- npm run workflows:generate
- npm run workflows:meal-plan
- npm run workflows:grocery-list
- npm run workflows:reset-week
- npm run workflows:status

Use the project’s existing package manager and language conventions.
Do not introduce a new runtime unless necessary.

8. Docker integration
Ensure Workflows works inside the existing Docker Compose setup.

Requirements:
- Generated files should persist across container restarts if the project has a data volume.
- Containers should auto-start as they did before.
- Document any new volume or environment variable.
- Do not break existing services.

9. Error handling
Handle these cases cleanly:
- Missing diet plan file
- Empty diet plan
- Missing recipe source
- No matching recipe for a meal slot
- Ingredient without quantity
- Duplicate ingredient with incompatible units
- Generated file directory missing
- Dashboard loaded before generation has run

Errors should be visible in:
- CLI output
- workflow-status.json
- Dashboard warning panel

10. Documentation
Update or create documentation for Workflows.

Include:
- What Workflows does
- What it does not do
- File locations
- How to edit the diet plan
- How to add recipes
- How to generate the meal plan
- How to generate the grocery list
- How to view results on the dashboard
- How to reset for a new week
- Known limitations
- Future extension points

11. Tests
Add basic tests for:
- Diet plan parsing
- Recipe matching
- Grocery ingredient deduplication
- Missing recipe warnings
- Generated output existence
- Status JSON output

Use the project’s existing test framework if present.
If no test framework exists, add a minimal test approach that fits the existing stack.

Implementation rules:
- Inspect the repo before changing files.
- Preserve existing behavior.
- Avoid large rewrites.
- Use small, reviewable commits or patches.
- Prefer local files and deterministic scripts.
- Keep UI simple and readable on a wall display.
- Avoid clever abstractions.
- Make failures obvious.

Expected deliverables:
- Working Workflows generation workflow
- Sample diet plan file
- Sample recipe data
- Generated meal plan output
- Generated grocery list output
- Dashboard panels
- Saturday reminder
- Weekly task checklist
- CLI commands
- Docker compatibility
- Documentation
- Tests

After implementation:
Run the full local validation:
- Install dependencies if needed
- Run tests
- Run the Workflows generation command
- Start the app using the project’s normal Docker flow
- Verify generated files exist
- Verify dashboard does not show 404s
- Verify warnings appear when expected

Report:
- Files changed
- Commands added
- How to run Workflows
- How to verify it worked
- Any assumptions made
- Any limitations left unresolved

## Coarse Correction Implemented

This correction converts Workflows from a manual dashboard shell into a local deterministic planning pipeline:

- `data/workflows/diet-plan.yaml` defines the household diet plan, days, meal slots, dietary notes, preferred tags, and excluded ingredients.
- `data/workflows/recipes.yaml` defines local recipes, meal types, tags, servings, categorized ingredients, quantities, and units.
- `data/workflows/tasks.json` stores the weekly follow-through checklist.
- `python3 -m workflows.cli generate` produces meal plan, grocery list, HTML, Markdown, JSON, and status artifacts under `frontend/public/generated`.
- The dashboard reads generated Workflows files first. Manual meals, groceries, and tasks remain only as secondary override controls.
- Generated warnings and missing meals are surfaced in `workflow-status.json` and the dashboard instead of becoming blank panels.

Intentionally not implemented: hardware changes, mobile app, voice assistant, receipt parsing, AI automation, internet recipe scraping, paid services, complex accounts, or cloud-only dependencies.
