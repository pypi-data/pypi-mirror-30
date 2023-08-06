from termplanner.planner_cli import PlannerRunner


def cli():
    """Creates and calls Planner."""
    planner_runner = PlannerRunner()
    planner_runner.cli()


if __name__ == "__main__":
    cli()
