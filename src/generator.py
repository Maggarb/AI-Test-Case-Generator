"""
AI Test Case Generator
=======================

Takes a feature requirement (plain English) and generates structured
test cases using Google Gemini (free API) — covering positive,
negative, and edge cases. Exports to CSV for Jira/TestRail import.
"""

import os
import json
import csv
import argparse
import google.generativeai as genai

# Configure Gemini with your free API key
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY not set.\n"
        "Get a free key at: https://aistudio.google.com\n"
        "Then run: export GEMINI_API_KEY='your-key-here'"
    )

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # free tier model

PROMPT_TEMPLATE = """You are a senior QA engineer writing manual test cases for a software feature.

Given the feature requirement below, generate a comprehensive set of test cases covering:
1. Positive (happy path) scenarios
2. Negative scenarios (invalid input, error handling)
3. Edge cases (boundary values, unusual but valid inputs)
4. Regression risks — what existing functionality might break

Respond ONLY with valid JSON matching this exact structure, no markdown, no code fences, no other text:

{{
  "feature": "short feature name",
  "test_cases": [
    {{
      "id": "TC-001",
      "category": "positive|negative|edge_case",
      "title": "short test case title",
      "preconditions": "what must be true before this test runs",
      "steps": ["step 1", "step 2", "step 3"],
      "expected_result": "what should happen",
      "priority": "high|medium|low"
    }}
  ],
  "regression_risks": ["risk 1", "risk 2"]
}}

Feature requirement:
{requirement}"""


def generate_test_cases(requirement: str) -> dict:
    """
    Send a requirement to Gemini and return structured test case data.
    Raises ValueError if the response is not valid JSON.
    """
    prompt = PROMPT_TEMPLATE.format(requirement=requirement)
    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Defensive: strip markdown code fences if model adds them anyway
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1])

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model did not return valid JSON.\nError: {e}\nRaw response:\n{raw_text}"
        )


def print_test_cases(data: dict) -> None:
    """Pretty-print test cases to the terminal."""
    print(f"\n{'='*70}")
    print(f"FEATURE: {data['feature']}")
    print(f"{'='*70}\n")

    for tc in data["test_cases"]:
        print(f"[{tc['id']}] {tc['title']}  ({tc['category']}, priority: {tc['priority']})")
        print(f"  Preconditions : {tc['preconditions']}")
        print(f"  Steps:")
        for i, step in enumerate(tc["steps"], 1):
            print(f"    {i}. {step}")
        print(f"  Expected result: {tc['expected_result']}")
        print()

    if data.get("regression_risks"):
        print("REGRESSION RISKS:")
        for risk in data["regression_risks"]:
            print(f"  - {risk}")
        print()


def export_to_csv(data: dict, filepath: str) -> None:
    """Export test cases to CSV for import into Jira, TestRail, or Xray."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ID", "Category", "Title", "Preconditions",
            "Steps", "Expected Result", "Priority"
        ])
        for tc in data["test_cases"]:
            writer.writerow([
                tc["id"],
                tc["category"],
                tc["title"],
                tc["preconditions"],
                " | ".join(tc["steps"]),
                tc["expected_result"],
                tc["priority"],
            ])
    print(f"Exported {len(data['test_cases'])} test cases to {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate manual test cases from a feature requirement using Gemini AI (free)."
    )
    parser.add_argument("requirement", nargs="?", help="Feature requirement text.")
    parser.add_argument("--file", "-f", help="Path to a text file containing the requirement.")
    parser.add_argument("--csv", "-o", help="Export results to this CSV file path.")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            requirement = f.read()
    elif args.requirement:
        requirement = args.requirement
    else:
        parser.error("Provide a requirement as an argument or via --file.")

    print("Generating test cases...")
    data = generate_test_cases(requirement)
    print_test_cases(data)

    if args.csv:
        export_to_csv(data, args.csv)


if __name__ == "__main__":
    main()
