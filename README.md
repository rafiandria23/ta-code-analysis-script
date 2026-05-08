# GitHub Gemini CLI Analyzer

A powerful CLI tool that uses the **GitHub GraphQL API** to fetch your recent activity and **Gemini AI** to analyze your code quality and development trends.

## 🚀 Features
- **7-Day Activity Report**: Automatically fetches all commits across all your repositories from the last week.
- **AI-Powered Analysis**: Uses Gemini 2.0 Flash to evaluate your development focus and provide constructive feedback on your code quality.
- **Productivity Stats**: Calculates "Total Commits" and "Average Time Between Pushes" to help you understand your coding rhythm.
- **High Efficiency**: Migrated to the GitHub GraphQL API to minimize network requests and stay well under rate limits.

## 📋 Prerequisites
- Python 3.11+
- [Conda](https://docs.conda.io/en/latest/) (recommended)
- A **Google Gemini API Key** (Get it from [Google AI Studio](https://aistudio.google.com/))
- A **GitHub Personal Access Token (PAT)** (Get it from [GitHub Settings](https://github.com/settings/tokens))

## ⚙️ Installation

1. **Set up the Conda environment**:
   ```bash
   conda create -n code-analysis-script python=3.11 -y
   conda activate code-analysis-script
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🔐 Configuration

1. **Environment Variables**:
   Copy the example environment file and add your Gemini API key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and replace `your_gemini_api_key_here` with your actual key.

2. **GitHub Credentials**:
   The app will securely prompt you for your **GitHub Username** and **Personal Access Token** every time it runs. This ensures your credentials remain private and are only used for the current session.

## 🛠 Usage

To run the default 7-day activity report:
```bash
python main.py
```

### Advanced Commands

**Generate a report for a specific user or timeframe:**
```bash
python main.py report --username someuser --days 14
```

**Summarize a specific repository's purpose and README:**
```bash
python main.py summarize google/generative-ai-python
```

## 🏗 Project Structure
- `main.py`: CLI entry point using `Typer` and `Rich`.
- `services/`:
  - `github_service.py`: Handles complex GraphQL queries to GitHub.
  - `gemini_service.py`: Interfaces with the Google Generative AI SDK.
- `config.py`: Centralized configuration and environment loader.

---
Built with ❤️ using Gemini AI and GitHub GraphQL.
