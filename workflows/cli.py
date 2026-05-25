"""CLI entry points for household workflows."""
import argparse
import json
import sys

from .workflow import WorkflowsWorkflow


def main(argv=None):
    parser = argparse.ArgumentParser(description="Digital Calendar workflows")
    parser.add_argument(
        "command",
        choices=["generate", "meal-plan", "grocery-list", "reset-week", "status"],
        help="Workflow command to run",
    )
    args = parser.parse_args(argv)

    workflow = WorkflowsWorkflow()

    if args.command == "generate":
        result = workflow.generate_all()
    elif args.command == "meal-plan":
        result = workflow.generate_meal_plan()
    elif args.command == "grocery-list":
        result = workflow.generate_grocery_list()
    elif args.command == "reset-week":
        result = workflow.reset_week()
    else:
        result = workflow.read_status()

    print(json.dumps(result, indent=2))
    return 1 if result.get("ok") is False else 0


if __name__ == "__main__":
    sys.exit(main())
