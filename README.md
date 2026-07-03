# AI Test Case Generator

Generate structured manual test cases from software requirements using **Groq AI**.

This tool takes a feature requirement (text or file), sends it to the Groq API, and generates comprehensive manual test cases covering:

* ✅ Positive (happy path) scenarios
* ✅ Negative scenarios
* ✅ Edge cases
* ✅ Regression risks

The generated test cases can be displayed in the terminal or exported to CSV for use with tools such as Jira, TestRail, or Xray.

---

## Features

```
Requirement (text) → Groq API → Structured JSON → Console output + CSV export
```

* Uses the **Groq API** (OpenAI-compatible API)
* No third-party Python dependencies required
* Accepts requirements from the command line or a text file
* Outputs structured JSON
* Exports test cases to CSV

---

## Requirements

* Python 3.10+
* A free Groq API key

Create a free account and generate an API key at:

https://console.groq.com

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Maggarb/AI-Test-Case-Generator.git
cd AI-Test-Case-Generator
```

No additional packages are required.

---

## Configure the API Key

### Windows PowerShell

```powershell
$env:GROQ_API_KEY="your-api-key"
```

### Windows Command Prompt

```cmd
set GROQ_API_KEY=your-api-key
```

### Linux / macOS

```bash
export GROQ_API_KEY="your-api-key"
```

---

## Usage

Generate test cases from a text file:

```bash
python src/generator.py --file examples/sample_requirement.txt
```

Generate test cases directly from the command line:

```bash
python src/generator.py "Users should be able to reset their password using email."
```

Export the results to CSV:

```bash
python src/generator.py --file examples/sample_requirement.txt --csv output.csv
```

---

## Example Output

```text
======================================================================
FEATURE: Password Reset
======================================================================

[TC-001] Reset password with valid email
Priority: High

Preconditions:
- User has a registered account

Steps:
1. Open the login page.
2. Click "Forgot Password".
3. Enter a registered email.
4. Submit the request.

Expected Result:
Password reset instructions are sent to the user's email.

Regression Risks:
- Email delivery
- Login functionality
```

---

## Project Structure

```
AI-Test-Case-Generator/
│
├── examples/
│   └── sample_requirement.txt
│
├── src/
│   └── generator.py
│
├── README.md
└── LICENSE
```

---

## AI Model

The project currently uses:

* **Provider:** Groq
* **Model:** `llama-3.3-70b-versatile`

You can easily switch to another Groq-supported model by changing the `MODEL` constant in `generator.py`.

---

