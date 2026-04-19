"""
examples/llm/anthropic_example.py
Use SUMD.md as system context for an Anthropic Claude API call.

Prerequisites:
    pip install anthropic sumd
    export ANTHROPIC_API_KEY=sk-ant-...

Usage:
    python examples/llm/anthropic_example.py
    python examples/llm/anthropic_example.py --file /path/to/SUMD.md
    python examples/llm/anthropic_example.py --question "What testql scenarios are missing?"
"""
from __future__ import annotations

import argparse
from pathlib import Path

import anthropic

from sumd import parse_file


def ask(sumd_path: Path, question: str, model: str = "claude-opus-4-5") -> str:
    doc = parse_file(sumd_path)
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=f"You are an expert on the {doc.project_name} project.\n\n{doc.raw_content}",
        messages=[{"role": "user", "content": question}],
    )
    return message.content[0].text


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask Claude about your project using SUMD context")
    parser.add_argument("--file", default="SUMD.md", help="Path to SUMD.md")
    parser.add_argument(
        "--question",
        default="What testql test scenarios should I add based on the API spec?",
    )
    parser.add_argument("--model", default="claude-opus-4-5")
    args = parser.parse_args()

    sumd_path = Path(args.file)
    if not sumd_path.exists():
        print(f"Error: {sumd_path} not found. Run 'sumd scan . --fix' first.")
        raise SystemExit(1)

    print(f"Context: {sumd_path}")
    print(f"Question: {args.question}")
    print("-" * 60)
    answer = ask(sumd_path, args.question, args.model)
    print(answer)


if __name__ == "__main__":
    main()
