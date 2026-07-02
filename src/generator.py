"""
AI Test Case Generator
=======================
Uses Groq API (free) via direct HTTP requests — no external libraries
needed beyond the Python standard library. Works on any Python version.
https://console.groq.com
"""

import os
import json
import csv
import argparse
import urllib.request
import urllib.error

API_KEY = os.environ.get("GROQ_API_KEY")
if not API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY not set.\n"
        "Get a free key at: https://console.groq.com\n"
        "On Windows PowerShell run:\n"
        '  $env:GROQ_API_KEY="your-key-here"'
    )

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"  # free, fast, high quality

SYSTEM_PROMPT = """You are a senior QA engineer writing manual test cases for a software feature.

Given a feature requirement, generate a comprehensive set of test cases covering:
1. Positive (happy path) scenarios
2. Negative scenarios (invalid input, error handling)
3. Edge cases (boundary values, unusual but valid inputs)
4. Regression risks — what existing functionality might break

Respond ONLY with valid JSON matching this exact structure, no markdown, no code fences, no other text:

{
  "feature": "short feature name",
  "test_cases": [
    {
      "id": "TC-001",
      "category": "positive|negative|edge_case",
      "title": "short test case title",
      "preconditions": "what must be true before this test runs",
      "steps": ["step 1", "step 2", "step 3"],
      "expected_result": "what should happen",
      "priority": "high|medium|low"
    }
  ],
  "regression_risks": ["risk 1", "risk 2"]
}"""


def generate_test_cases(requirement: str) -> dict:
    """Call Groq API via HTTP and return structured test case data."""
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Feature requirement:\n\n{requirement}"}
        ],
        "temperature": 0.3,
        "max_tokens": 4096,
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "ai-test-case-generator/1.0",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"API error {e.code}: {error_body}")

    # Extract text from Groq's OpenAI-compatible response format
    raw_text = result["choices"][0]["message"]["content"].strip()

    # Strip markdown code fences if model adds them anyway
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]


    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON.\nError: {e}\nRaw:\n{raw_text}")


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
        description="Generate manual test cases from a feature requirement using Groq AI (free)."
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
