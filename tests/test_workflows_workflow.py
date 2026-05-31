import tempfile
import unittest
from pathlib import Path

from workflows.workflow import WorkflowsWorkflow, normalize_recipe_source


class WorkflowsWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.workflow = WorkflowsWorkflow(self.root)
        self.workflow.paths.data_dir.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write_inputs(self, diet_plan=None, recipes=None):
        diet_plan = diet_plan or {
            "days": [
                {
                    "day": "Monday",
                    "slots": {
                        "breakfast": {"meal_type": "breakfast", "tags": ["quick"]},
                        "dinner": {"meal_type": "dinner", "tags": ["family"]},
                    },
                }
            ]
        }
        if recipes is None:
            recipes = [
                {
                    "name": "Yogurt Bowl",
                    "meal_types": ["breakfast"],
                    "tags": ["quick"],
                    "servings": 2,
                    "ingredients": [
                        {"item": "Yogurt", "quantity": 2, "unit": "cups", "category": "Dairy"},
                        {"item": "Berries", "quantity": 1, "unit": "cup", "category": "Produce"},
                    ],
                },
                {
                    "name": "Rice Bowls",
                    "meal_types": ["dinner"],
                    "tags": ["family"],
                    "servings": 4,
                    "ingredients": [
                        {"item": "Rice", "quantity": 2, "unit": "cups", "category": "Pantry"},
                        {"item": "Yogurt", "quantity": 1, "unit": "cups", "category": "Dairy"},
                    ],
                },
            ]
        self.workflow._write_text(self.workflow.paths.diet_plan, self.to_yaml(diet_plan))
        self.workflow._write_text(self.workflow.paths.recipes, self.to_yaml({"recipes": recipes}))

    def to_yaml(self, value):
        import yaml

        return yaml.safe_dump(value, sort_keys=False)

    def test_diet_plan_parsing_and_recipe_matching(self):
        self.write_inputs()

        result = self.workflow.generate_meal_plan()

        self.assertTrue(result["ok"])
        meal_plan = self.workflow._read_optional_json(self.workflow.paths.generated_dir / "meal-plan.json")
        meals = meal_plan["days"][0]["meals"]
        self.assertEqual(meals[0]["recipe"], "Yogurt Bowl")
        self.assertEqual(meals[1]["recipe"], "Rice Bowls")

    def test_yaml_recipe_file_supports_single_meal_type(self):
        recipes = normalize_recipe_source(
            {
                "recipes": [
                    {
                        "name": "Toast",
                        "meal_type": "breakfast",
                        "tags": ["quick"],
                        "ingredients": [],
                    }
                ]
            },
            [],
        )

        self.assertEqual(recipes[0]["meal_types"], ["breakfast"])

    def test_excluded_ingredient_blocks_recipe(self):
        self.write_inputs(
            diet_plan={
                "excluded_ingredients": ["peanuts"],
                "days": [
                    {
                        "day": "Monday",
                        "slots": {"breakfast": {"meal_type": "breakfast", "tags": ["quick"]}},
                    }
                ],
            },
            recipes=[
                {
                    "name": "Peanut Oats",
                    "meal_types": ["breakfast"],
                    "tags": ["quick"],
                    "ingredients": [{"item": "peanuts", "quantity": 1, "unit": "cup", "category": "Pantry"}],
                }
            ],
        )

        result = self.workflow.generate_meal_plan()

        self.assertTrue(result["ok"])
        self.assertIn("No matching recipe for Monday breakfast.", result["warnings"])

    def test_grocery_ingredient_deduplication(self):
        self.write_inputs()
        self.workflow.generate_meal_plan()

        result = self.workflow.generate_grocery_list()

        self.assertTrue(result["ok"])
        grocery_list = self.workflow._read_optional_json(self.workflow.paths.generated_dir / "grocery-list.json")
        dairy = next(category for category in grocery_list["categories"] if category["category"] == "Dairy")
        yogurt = next(item for item in dairy["items"] if item["item"] == "Yogurt")
        self.assertEqual(yogurt["quantity"], 3)

    def test_grocery_category_grouping_and_other_fallback(self):
        self.write_inputs(
            recipes=[
                {
                    "name": "Yogurt Bowl",
                    "meal_types": ["breakfast"],
                    "tags": ["quick"],
                    "servings": 2,
                    "ingredients": [
                        {"item": "Yogurt", "quantity": 2, "unit": "cups", "category": "Dairy"},
                    ],
                },
                {
                    "name": "Rice Bowls",
                    "meal_types": ["dinner"],
                    "tags": ["family"],
                    "servings": 4,
                    "ingredients": [
                        {"item": "Seasoning", "quantity": 1, "unit": "packet"},
                    ],
                },
            ]
        )
        self.workflow.generate_meal_plan()

        result = self.workflow.generate_grocery_list()

        self.assertTrue(result["ok"])
        grocery_list = self.workflow._read_optional_json(self.workflow.paths.generated_dir / "grocery-list.json")
        categories = [category["category"] for category in grocery_list["categories"]]
        self.assertIn("Dairy", categories)
        self.assertEqual(categories[-1], "Other")

    def test_empty_recipe_source_is_an_error(self):
        self.write_inputs(recipes=[])

        result = self.workflow.generate_meal_plan()

        self.assertFalse(result["ok"])
        self.assertIn("Empty recipes file", result["errors"][0])

    def test_no_matching_recipe_warning_is_visible(self):
        self.write_inputs(
            recipes=[
                {
                    "name": "Dinner Only",
                    "meal_types": ["dinner"],
                    "tags": ["family"],
                    "ingredients": [],
                }
            ]
        )

        result = self.workflow.generate_meal_plan()

        self.assertTrue(result["ok"])
        self.assertIn("No matching recipe for Monday breakfast.", result["warnings"])
        status = self.workflow._read_optional_json(self.workflow.paths.generated_dir / "workflow-status.json")
        self.assertEqual(status["missing_meals"], ["Monday breakfast"])

    def test_generated_outputs_and_status_json_exist(self):
        self.write_inputs()

        self.workflow.generate_all()

        expected = [
            "meal-plan.json",
            "meal-plan.md",
            "meal-plan.html",
            "grocery-list.json",
            "grocery-list.md",
            "grocery-list.html",
            "workflow-status.json",
        ]
        for filename in expected:
            self.assertTrue((self.workflow.paths.generated_dir / filename).exists(), filename)
        status = self.workflow._read_optional_json(self.workflow.paths.generated_dir / "workflow-status.json")
        self.assertIn("last_generated_at", status)
        self.assertEqual(status["grocery_item_count"], 3)
        self.assertTrue(status["meal_plan_generated"])
        self.assertTrue(status["grocery_list_generated"])


if __name__ == "__main__":
    unittest.main()
