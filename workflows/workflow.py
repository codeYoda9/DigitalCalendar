"""Deterministic household workflow meal planning and grocery generation."""
from __future__ import annotations

import html
import json
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - local fallback for JSON-compatible YAML.
    yaml = None


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DEFAULT_TASKS = [
    {"id": "generate-meal-plan", "label": "Generate meal plan", "done": False},
    {"id": "review-meal-plan", "label": "Review meal plan", "done": False},
    {"id": "generate-grocery-list", "label": "Generate grocery list", "done": False},
    {"id": "review-grocery-list", "label": "Review grocery list", "done": False},
    {"id": "shop-groceries", "label": "Shop groceries", "done": False},
]


@dataclass
class WorkflowPaths:
    root: Path
    data_dir: Path
    diet_plan: Path
    legacy_diet_plan: Path
    recipes: Path
    legacy_recipes: Path
    tasks: Path
    legacy_tasks: Path
    generated_dir: Path


class WorkflowsWorkflow:
    """Local file workflow for household meal planning."""

    def __init__(self, root: Path | None = None):
        repo_root = root or Path(__file__).resolve().parents[1]
        data_dir = repo_root / "data" / "workflows"
        self.paths = WorkflowPaths(
            root=repo_root,
            data_dir=data_dir,
            diet_plan=data_dir / "diet-plan.yaml",
            legacy_diet_plan=data_dir / "diet-plan.yaml",
            recipes=data_dir / "recipes.yaml",
            legacy_recipes=data_dir / "recipes.yaml",
            tasks=data_dir / "tasks.json",
            legacy_tasks=data_dir / "tasks.json",
            generated_dir=repo_root / "frontend" / "public" / "generated",
        )

    def generate_all(self) -> dict[str, Any]:
        meal_result = self.generate_meal_plan()
        grocery_result = self.generate_grocery_list()
        status = self.read_status()
        return {
            "ok": bool(meal_result.get("ok") and grocery_result.get("ok")),
            "meal_plan": meal_result,
            "grocery_list": grocery_result,
            "status": status,
        }

    def generate_meal_plan(self) -> dict[str, Any]:
        self.paths.generated_dir.mkdir(parents=True, exist_ok=True)
        errors: list[str] = []
        warnings: list[str] = []

        diet_plan = self._read_structured(
            self.paths.diet_plan,
            errors,
            "diet plan",
            {},
            legacy_path=self.paths.legacy_diet_plan,
        )
        recipes = self._read_structured(
            self.paths.recipes,
            errors,
            "recipes",
            [],
            legacy_path=self.paths.legacy_recipes,
        )
        recipes = normalize_recipe_source(recipes, warnings)
        if not recipes and not errors:
            errors.append(f"Empty recipes file: {self.paths.recipes}")
        if errors:
            status = self._write_status(None, None, warnings, errors)
            return {"ok": False, "errors": errors, "warnings": warnings, "status": status}

        plan = self.build_meal_plan(diet_plan, recipes, warnings)
        meal_html = render_html_document("Meal Plan", render_meal_plan_html(plan))
        self._write_json(self.paths.generated_dir / "meal-plan.json", plan)
        self._write_text(self.paths.generated_dir / "meal-plan.md", render_meal_plan_markdown(plan))
        self._write_text(self.paths.generated_dir / "meal-plan.html", meal_html)
        self._write_text(self.paths.generated_dir / "meal-plan" / "index.html", meal_html)
        self._mark_task("generate-meal-plan", True)
        status = self._write_status(plan, None, warnings, errors)
        return {"ok": True, "warnings": warnings, "meal_count": count_selected_meals(plan), "status": status}

    def generate_grocery_list(self) -> dict[str, Any]:
        self.paths.generated_dir.mkdir(parents=True, exist_ok=True)
        errors: list[str] = []
        warnings: list[str] = []

        meal_plan = self._read_json(self.paths.generated_dir / "meal-plan.json", errors, "generated meal plan")
        recipes = self._read_structured(
            self.paths.recipes,
            errors,
            "recipes",
            [],
            legacy_path=self.paths.legacy_recipes,
        )
        recipes = normalize_recipe_source(recipes, warnings)
        if not recipes and not errors:
            errors.append(f"Empty recipes file: {self.paths.recipes}")
        if errors:
            status = self._write_status(meal_plan if isinstance(meal_plan, dict) else None, None, warnings, errors)
            return {"ok": False, "errors": errors, "warnings": warnings, "status": status}

        grocery_list = self.build_grocery_list(meal_plan, recipes, warnings)
        grocery_html = render_html_document("Grocery List", render_grocery_html(grocery_list))
        self._write_json(self.paths.generated_dir / "grocery-list.json", grocery_list)
        self._write_text(self.paths.generated_dir / "grocery-list.md", render_grocery_markdown(grocery_list))
        self._write_text(self.paths.generated_dir / "grocery-list.html", grocery_html)
        self._write_text(self.paths.generated_dir / "grocery-list" / "index.html", grocery_html)
        self._mark_task("generate-grocery-list", True)
        status = self._write_status(meal_plan, grocery_list, warnings, errors)
        return {"ok": True, "warnings": unique_list(warnings), "item_count": grocery_list["item_count"], "status": status}

    def reset_week(self) -> dict[str, Any]:
        self.paths.data_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(self.paths.tasks, {"tasks": deepcopy(DEFAULT_TASKS)})
        status = self._write_status(
            self._read_optional_json(self.paths.generated_dir / "meal-plan.json"),
            self._read_optional_json(self.paths.generated_dir / "grocery-list.json"),
            ["Weekly task checklist reset."],
            [],
        )
        return {"ok": True, "status": status}

    def read_status(self) -> dict[str, Any]:
        status_path = self.paths.generated_dir / "workflow-status.json"
        if status_path.exists():
            return self._read_optional_json(status_path) or {"ok": False, "errors": ["Status file could not be read."]}
        status = self._write_status(None, None, ["Workflows have not been generated yet."], [])
        return status

    def build_meal_plan(self, diet_plan: dict[str, Any], recipes: list[dict[str, Any]], warnings: list[str]) -> dict[str, Any]:
        if not diet_plan.get("days"):
            warnings.append("Diet plan has no days configured.")

        global_excluded = normalize_words(diet_plan.get("excluded_ingredients", []))
        week: dict[str, Any] = {"generated_at": utc_now(), "days": []}

        for day_config in diet_plan.get("days", []):
            day_name = day_config.get("day", "Unknown")
            excluded = global_excluded | normalize_words(day_config.get("excluded_ingredients", []))
            slots = day_config.get("slots", {})
            day_result = {"day": day_name, "notes": day_config.get("notes", ""), "meals": []}

            for slot_name, slot_config in slots.items():
                slot = normalize_slot(slot_name, slot_config)
                recipe = choose_recipe(slot, recipes, excluded)
                if recipe:
                    day_result["meals"].append(
                        {
                            "slot": slot_name,
                            "recipe": recipe["name"],
                            "servings": recipe.get("servings"),
                            "tags": recipe.get("tags", []),
                            "source": recipe.get("source", ""),
                        }
                    )
                else:
                    warning = f"No matching recipe for {day_name} {slot_name}."
                    warnings.append(warning)
                    day_result["meals"].append({"slot": slot_name, "recipe": None, "warning": warning})

            week["days"].append(day_result)

        return week

    def build_grocery_list(
        self, meal_plan: dict[str, Any], recipes: list[dict[str, Any]], warnings: list[str]
    ) -> dict[str, Any]:
        recipes_by_name = {recipe.get("name"): recipe for recipe in recipes}
        grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)

        for day in meal_plan.get("days", []):
            for meal in day.get("meals", []):
                recipe_name = meal.get("recipe")
                if not recipe_name:
                    continue
                recipe = recipes_by_name.get(recipe_name)
                if not recipe:
                    warnings.append(f"Recipe '{recipe_name}' from meal plan is missing from recipe source.")
                    continue
                for ingredient in recipe.get("ingredients", []):
                    normalized = normalize_ingredient(ingredient)
                    if normalized["quantity"] is None:
                        warnings.append(f"Ingredient '{normalized['item']}' in '{recipe_name}' has no quantity.")
                    category = normalized["category"] or "Other"
                    key = normalized["item"].lower()
                    existing = grouped[category].get(key)
                    if existing and can_combine(existing, normalized):
                        existing["quantity"] += normalized["quantity"]
                        existing["recipes"].append(recipe_name)
                    elif existing and can_group_ambiguous(existing, normalized):
                        existing["recipes"].append(recipe_name)
                    elif existing:
                        warnings.append(f"Ingredient '{normalized['item']}' has incompatible units; keeping entries separate.")
                        grouped[category][f"{key}:{normalized['unit'] or 'unitless'}:{len(grouped[category])}"] = normalized
                    else:
                        grouped[category][key] = normalized
                        normalized["recipes"] = [recipe_name]

        categories = []
        for category in sorted(grouped.keys(), key=lambda value: (value == "Other", value)):
            items = sorted(grouped[category].values(), key=lambda value: value["item"].lower())
            categories.append({"category": category, "items": items})

        return {
            "generated_at": utc_now(),
            "item_count": sum(len(category["items"]) for category in categories),
            "categories": categories,
        }

    def _read_structured(
        self,
        path: Path,
        errors: list[str],
        label: str,
        empty_value: Any,
        legacy_path: Path | None = None,
    ):
        read_path = path
        if not read_path.exists() and legacy_path and legacy_path.exists():
            read_path = legacy_path
        if not read_path.exists() and legacy_path:
            legacy_json = legacy_path.with_suffix(".json")
            if legacy_json.exists():
                read_path = legacy_json
        if not read_path.exists():
            errors.append(f"Missing {label} file: {path}")
            return empty_value
        try:
            text = read_path.read_text(encoding="utf-8")
            if read_path.suffix == ".json":
                data = json.loads(text)
            elif yaml is not None:
                data = yaml.safe_load(text)
            else:
                data = json.loads(text)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {label} file: {exc}")
            return empty_value
        except Exception as exc:
            errors.append(f"Invalid YAML in {label} file: {exc}")
            return empty_value
        if data in ({}, [], None):
            errors.append(f"Empty {label} file: {read_path}")
            return empty_value
        return data

    def _read_json(self, path: Path, errors: list[str], label: str):
        if not path.exists():
            errors.append(f"Missing {label} file: {path}")
            return {} if label == "diet plan" else []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {label} file: {exc}")
            return {} if label == "diet plan" else []
        if data in ({}, []):
            errors.append(f"Empty {label} file: {path}")
        return data

    def _read_optional_json(self, path: Path):
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def _write_json(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def _write_text(self, path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _read_tasks(self) -> list[dict[str, Any]]:
        data = (
            self._read_optional_json(self.paths.tasks)
            or self._read_optional_json(self.paths.legacy_tasks)
            or self._read_optional_json(self.paths.legacy_tasks.with_name("task-status.json"))
        )
        if not data or not isinstance(data.get("tasks"), list):
            return deepcopy(DEFAULT_TASKS)
        known = {task["id"]: task for task in data["tasks"]}
        return [known.get(task["id"], deepcopy(task)) for task in DEFAULT_TASKS]

    def _mark_task(self, task_id: str, done: bool):
        tasks = self._read_tasks()
        for task in tasks:
            if task["id"] == task_id:
                task["done"] = done
        self.paths.data_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(self.paths.tasks, {"tasks": tasks})

    def _write_status(
        self,
        meal_plan: dict[str, Any] | None,
        grocery_list: dict[str, Any] | None,
        warnings: list[str],
        errors: list[str],
    ) -> dict[str, Any]:
        if meal_plan is None:
            meal_plan = self._read_optional_json(self.paths.generated_dir / "meal-plan.json")
        if grocery_list is None:
            grocery_list = self._read_optional_json(self.paths.generated_dir / "grocery-list.json")

        missing_meals = extract_missing_meals(meal_plan)
        meal_plan_html_exists = (self.paths.generated_dir / "meal-plan.html").exists()
        grocery_list_html_exists = (self.paths.generated_dir / "grocery-list.html").exists()
        meal_plan_index_exists = (self.paths.generated_dir / "meal-plan" / "index.html").exists()
        grocery_list_index_exists = (self.paths.generated_dir / "grocery-list" / "index.html").exists()
        meal_plan_generated = bool(meal_plan) and meal_plan_html_exists
        grocery_list_generated = bool(grocery_list) and grocery_list_html_exists
        status = {
            "ok": not errors,
            "last_generated_at": utc_now() if not errors else None,
            "meal_plan_generated": meal_plan_generated,
            "grocery_list_generated": grocery_list_generated,
            "grocery_item_count": grocery_list.get("item_count", 0) if grocery_list else 0,
            "missing_meals": missing_meals,
            "warnings": unique_list(warnings),
            "warning_count": len(unique_list(warnings)) + len(errors) + len(missing_meals),
            "errors": errors,
            "tasks": self._read_tasks(),
            "artifacts": {
                "meal_plan_html": "/generated/meal-plan.html" if meal_plan_html_exists else ("/generated/meal-plan/" if meal_plan_index_exists else None),
                "meal_plan_md": "/generated/meal-plan.md",
                "grocery_list_html": "/generated/grocery-list.html" if grocery_list_html_exists else ("/generated/grocery-list/" if grocery_list_index_exists else None),
                "grocery_list_md": "/generated/grocery-list.md",
            },
            "notification_extension": "Add future local notification hooks after workflows:generate succeeds.",
        }
        self.paths.generated_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(self.paths.generated_dir / "workflow-status.json", status)
        return status


def normalize_slot(slot_name: str, slot_config: Any) -> dict[str, Any]:
    if isinstance(slot_config, str):
        return {"meal_type": slot_name, "tags": [slot_config], "preferred_meals": []}
    return {
        "meal_type": slot_config.get("meal_type", slot_name),
        "tags": [tag.lower() for tag in slot_config.get("tags", [])],
        "preferred_meals": slot_config.get("preferred_meals", []),
        "notes": slot_config.get("notes", ""),
    }


def normalize_recipe_source(recipe_source: Any, warnings: list[str]) -> list[dict[str, Any]]:
    recipes = recipe_source.get("recipes", []) if isinstance(recipe_source, dict) else recipe_source
    if not isinstance(recipes, list):
        warnings.append("Recipe source did not contain a recipe list.")
        return []
    normalized = []
    for recipe in recipes:
        if not isinstance(recipe, dict):
            warnings.append("Recipe source contains a non-object recipe entry.")
            continue
        copy = dict(recipe)
        if "meal_types" not in copy:
            meal_type = copy.get("meal_type")
            copy["meal_types"] = [meal_type] if meal_type else []
        normalized.append(copy)
    return normalized


def choose_recipe(slot: dict[str, Any], recipes: list[dict[str, Any]], excluded: set[str]) -> dict[str, Any] | None:
    candidates = []
    meal_type = slot["meal_type"].lower()
    tags = set(slot.get("tags", []))
    preferred = [name.lower() for name in slot.get("preferred_meals", [])]

    for recipe in recipes:
        meal_types = [value.lower() for value in recipe.get("meal_types", [])]
        recipe_tags = set(tag.lower() for tag in recipe.get("tags", []))
        ingredients = normalize_words([ingredient.get("item", "") for ingredient in recipe.get("ingredients", [])])
        if meal_type not in meal_types:
            continue
        if excluded & ingredients:
            continue
        tag_score = len(tags & recipe_tags)
        preferred_score = 1 if recipe.get("name", "").lower() in preferred else 0
        if tags and tag_score == 0 and not preferred_score:
            continue
        candidates.append((preferred_score, tag_score, recipe.get("name", ""), recipe))

    if not candidates:
        return None
    return sorted(candidates, key=lambda item: (-item[0], -item[1], item[2].lower()))[0][3]


def normalize_ingredient(ingredient: dict[str, Any]) -> dict[str, Any]:
    quantity = ingredient.get("quantity")
    try:
        quantity = float(quantity) if quantity not in (None, "") else None
    except (TypeError, ValueError):
        quantity = None
    return {
        "item": ingredient.get("item", "Unknown item"),
        "quantity": quantity,
        "unit": ingredient.get("unit") or "",
        "category": ingredient.get("category") or "Other",
    }


def can_combine(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return left["quantity"] is not None and right["quantity"] is not None and left["unit"] == right["unit"]


def can_group_ambiguous(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return left["quantity"] is None and right["quantity"] is None and left["unit"] == right["unit"]


def normalize_words(values: list[str]) -> set[str]:
    return {str(value).strip().lower() for value in values if str(value).strip()}


def count_selected_meals(plan: dict[str, Any]) -> int:
    return sum(1 for day in plan.get("days", []) for meal in day.get("meals", []) if meal.get("recipe"))


def extract_missing_meals(plan: dict[str, Any] | None) -> list[str]:
    if not plan:
        return []
    return [
        f"{day.get('day')} {meal.get('slot')}"
        for day in plan.get("days", [])
        for meal in day.get("meals", [])
        if not meal.get("recipe")
    ]


def unique_list(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def quantity_label(item: dict[str, Any]) -> str:
    quantity = item.get("quantity")
    if quantity is None:
        return ""
    if float(quantity).is_integer():
        quantity = int(quantity)
    return f"{quantity} {item.get('unit', '')}".strip()


def render_meal_plan_markdown(plan: dict[str, Any]) -> str:
    lines = ["# Weekly Meal Plan", "", f"Generated: {plan.get('generated_at', '')}", ""]
    for day in plan.get("days", []):
        lines.extend([f"## {day['day']}", ""])
        for meal in day.get("meals", []):
            recipe = meal.get("recipe") or f"Missing ({meal.get('warning')})"
            lines.append(f"- {meal['slot'].title()}: {recipe}")
        lines.append("")
    return "\n".join(lines)


def render_grocery_markdown(grocery_list: dict[str, Any]) -> str:
    lines = ["# Grocery List", "", f"Generated: {grocery_list.get('generated_at', '')}", ""]
    for category in grocery_list.get("categories", []):
        lines.extend([f"## {category['category']}", ""])
        for item in category.get("items", []):
            qty = quantity_label(item)
            label = f"{qty} {item['item']}".strip()
            lines.append(f"- [ ] {label}")
        lines.append("")
    return "\n".join(lines)


def render_meal_plan_html(plan: dict[str, Any]) -> str:
    chunks = [f"<p class='generated'>Generated {html.escape(plan.get('generated_at', ''))}</p>"]
    for day in plan.get("days", []):
        chunks.append(f"<section><h2>{html.escape(day['day'])}</h2><ul>")
        for meal in day.get("meals", []):
            recipe = meal.get("recipe") or meal.get("warning", "Missing meal")
            chunks.append(f"<li><strong>{html.escape(meal['slot'].title())}</strong>: {html.escape(recipe)}</li>")
        chunks.append("</ul></section>")
    return "\n".join(chunks)


def render_grocery_html(grocery_list: dict[str, Any]) -> str:
    chunks = [f"<p class='generated'>Generated {html.escape(grocery_list.get('generated_at', ''))}</p>"]
    for category in grocery_list.get("categories", []):
        chunks.append(f"<section><h2>{html.escape(category['category'])}</h2><ul>")
        for item in category.get("items", []):
            label = f"{quantity_label(item)} {item['item']}".strip()
            chunks.append(f"<li><label><input type='checkbox'> {html.escape(label)}</label></li>")
        chunks.append("</ul></section>")
    return "\n".join(chunks)


def render_html_document(title: str, body: str) -> str:
    safe_title = html.escape(title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
    h1 {{ margin-bottom: .25rem; }}
    h2 {{ border-bottom: 1px solid #ddd; padding-bottom: .25rem; }}
    li {{ margin: .45rem 0; }}
    .generated {{ color: #666; }}
  </style>
</head>
<body>
  <h1>{safe_title}</h1>
  {body}
</body>
</html>
"""
