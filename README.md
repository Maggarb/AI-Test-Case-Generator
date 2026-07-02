# 🤖 AI Test Case Generator

A CLI tool that takes a plain-English feature requirement and uses Google Gemini (free API) to generate structured manual test cases — covering positive, negative, and edge-case scenarios, plus regression risk notes. Exports directly to CSV for import into Jira, TestRail, or Xray.

---

## Why I built this

As a QA professional, writing comprehensive test cases from a requirements doc is repetitive and easy to under-cover, especially edge cases under time pressure. This tool gives a fast, structured first draft to review, edit, and prioritise — so more time goes into actually testing rather than transcribing requirements into test case format.

---

## How it works

```
Requirement (text) → Gemini API → Structured JSON → Console output + CSV export
```

1. You provide a feature requirement (as a CLI argument or a text file)
2. The tool sends it to Gemini with a system prompt instructing it to act as a senior QA engineer and return structured JSON
3. The JSON is parsed and printed in a readable format
4. Optionally exported to CSV with one row per test case

---

## Design decisions

**Structured JSON output, not free text.** Instructing the model to return a strict JSON schema makes the output programmatically usable — it can be piped into a CSV, a test management tool, or a database — rather than something a human has to manually reformat.

**No agent framework.** This is a single-step task: read input, call the LLM once, structure the output. Wrapping it in LangChain or CrewAI would add complexity without benefit. I'd reach for an agent framework if this needed multiple coordinated steps — for example, an agent that fetches requirements from Jira, generates test cases, then creates the tickets automatically.

**Defensive JSON parsing.** LLMs sometimes wrap JSON in markdown code fences even when told not to. The parser strips these defensively rather than failing outright.

**CSV export matches real QA tooling.** Output columns (ID, Category, Title, Preconditions, Steps, Expected Result, Priority) mirror fields used in Jira/Xray/TestRail imports.

---

## What I'd change if I started over

- **Add a confidence/review flag** — flag test cases where requirements are ambiguous so reviewers know where to focus
- **Support batch processing** — process a list of user stories from a Jira export in one run
- **Add a lightweight eval step** — compare generated cases against human-written "gold standard" cases to measure coverage quality
- **Retry logic for malformed JSON** — retry once with a corrective follow-up prompt before failing

---

## Getting started

### 1. Get a free Gemini API key
- Go to **aistudio.google.com**
- Sign in with your Google account
- Click "Get API Key" → "Create API key"
- No credit card required

### 2. Install and run

```bash
git clone https://github.com/Maggarb/ai-test-case-generator.git
cd ai-test-case-generator
pip install -r requirements.txt

# Set your free API key
export GEMINI_API_KEY="your-key-here"

# Run from a string
python src/generator.py "Users can reset their password via email link..."

# Run from a file
python src/generator.py --file examples/sample_requirement.txt

# Export to CSV
python src/generator.py --file examples/sample_requirement.txt --csv output.csv
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| [Google Gemini API](https://aistudio.google.com) | Free LLM that generates the test cases |
| Python | CLI implementation |
| `argparse` | Command-line interface |
| `csv` (stdlib) | Export for test management tools |

---

*Part of my QA automation portfolio — see also [Playwright E2E Tests](https://github.com/Maggarb/Playwright-Saucedemo), [Cypress API Tests](https://github.com/Maggarb/Cypress-API-UI-Automation-Framework), and [Python API Framework](https://github.com/Maggarb/Pytest-API-Framework)*
