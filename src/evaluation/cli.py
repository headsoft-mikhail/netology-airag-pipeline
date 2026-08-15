import argparse
import typing
from pathlib import Path

from evaluation.config import load_evaluator_config
from evaluation.evaluator import Evaluator


def main() -> None:
    parser: typing.Final = argparse.ArgumentParser(
        description="RAG data preparation pipeline",
    )

    subparsers: typing.Final = parser.add_subparsers(
        dest="command",
        required=True,
    )

    run_parser: typing.Final = subparsers.add_parser(
        "run",
        help="Send question to LLM using RAG",
    )
    run_parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/evaluate.yaml"),
        help="Path to evaluate configuration",
    )
    run_parser.add_argument(
        "-q",
        type=str,
        help="Question",
    )

    test_parser: typing.Final = subparsers.add_parser(
        "test",
        help="Send question to LLM using RAG",
    )
    test_parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/evaluate.yaml"),
        help="Path to evaluate configuration",
    )

    args: typing.Final = parser.parse_args()
    config: typing.Final = load_evaluator_config(args.config)
    evaluator: typing.Final = Evaluator(config)

    if args.command == "run":
        evaluator.evaluate(args.q)
    elif args.command == "test":
        evaluator.test()
    else:
        raise ValueError(f"Unknown command: {args.command}")
