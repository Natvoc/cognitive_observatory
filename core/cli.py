"""Command-line entry point for Cognitive Observatory."""

import argparse
from datetime import date
from pathlib import Path

from core.experiments.loader import load_experiment

__version__ = "0.1.0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cognitive-observatory")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")
    run_parser = subparsers.add_parser("run", help="Run an experiment from a YAML config file")
    run_parser.add_argument("config_path", type=Path)

    args = parser.parse_args(argv)

    if args.command == "run":
        return _run(args.config_path)

    return 0


def _run(config_path: Path) -> int:
    experiment = load_experiment(config_path)
    result = experiment.run()

    run_id = f"{date.today().isoformat()}_{experiment.name}_{experiment.seed}"
    output_dir = Path("experiments") / run_id
    result.save(output_dir)

    print(f"Experiment '{experiment.name}' (seed={experiment.seed}) done -> {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
