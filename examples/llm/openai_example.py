"""
examples/llm/openai_example.py
Use SUMD.md as system context for an OpenAI GPT-4o API call.

Prerequisites:
    pip install openai sumd
    export OPENAI_API_KEY=sk-...

Usage:
    python examples/llm/openai_example.py
    python examples/llm/openai_example.py --file /path/to/project/SUMD.md
    python examples/llm/openai_example.py --question "What endpoints exist?"
"""
from __future__ import annotations

import argparse
from pathlib import Path

import openai

from sumd import parse_file


def build_context(sumd_path: Path) -> str:
    """Return a focused context string from SUMD.md."""
    doc = parse_file(sumd_path)

    sections = {}
    for s in doc.sections:
        sections[s.name.lower()] = s.content

    parts = [f"# {doc.project_name}", ""]
    if doc.description:
        parts.append(doc.description)
        parts.append("")

    for name in ("intent", "architecture", "interfaces", "workflows", "dependencies"):
        if name in sections:
            parts.append(f"## {name.title()}")
            parts.append(sections[name])
            parts.append("")

    return "\n".join(parts)


def ask(sumd_path: Path, question: str, model: str = "gpt-4o") -> str:
    context = build_context(sumd_path)
    client = openai.OpenAI()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"You are an expert on the project described below.\n\n{context}",
            },
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask a question about your project using SUMD context")
    parser.add_argument("--file", default="SUMD.md", help="Path to SUMD.md (default: ./SUMD.md)")
    parser.add_argument(
        "--question",
        default="Summarise this project and list its main API endpoints.",
        help="Question to ask",
    )
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model (default: gpt-4o)")
    args = parser.parse_args()

    sumd_path = Path(args.file)
    if not sumd_path.exists():
        print(f"Error: {sumd_path} not found. Run 'sumd scan . --fix' first.")
        raise SystemExit(1)

    print(f"Context: {sumd_path}")
    print(f"Question: {args.question}")
    print(f"Model: {args.model}")
    print("-" * 60)
    answer = ask(sumd_path, args.question, args.model)
    print(answer)


if __name__ == "__main__":
    main()
