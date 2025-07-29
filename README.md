# Git Issue Responder

This project automates the process of responding to GitHub issues and updating code based on issue descriptions using Gemini AI. It also provides a simple Flask API for demonstration purposes.

## Features
- **GitHub Actions Integration:** Automatically processes and closes issues via workflows in `.github/workflows/`.
- **AI-Powered Automation:** Uses Gemini API to analyze issues and update relevant files.
- **Flask API:** Includes a sample Flask app with authentication and a circle area calculation endpoint.
- **Command-Line Automation:** Run `automation.py` to process issues and update codebase automatically.

## File Structure
- `ai_agent.py`: Handles Gemini API requests and response management.
- `automation.py`: Main automation script for processing issues and updating files.
- `requirements.txt`: Python dependencies.
- `project/main.py`: Flask web application with authentication and endpoints.
- `.github/workflows/`: GitHub Actions workflows for automation and testing.

## Usage

### 1. Setup
- Install dependencies:
  ```powershell
  pip install -r requirements.txt
  ```
- Set your Gemini API key in a `.env` file:
  ```env
  GEMINI_API_KEY=your_api_key_here
  ```

### 2. Run Flask App
- Start the server:
  ```powershell
  python project/main.py
  ```
- Access endpoints:
  - `/` (GET): Home page (requires `X-API-Key` header)
  - `/area` (POST): Calculate area of a circle (requires `X-API-Key` header and JSON body with `radius`)

### 3. Automate Issue Response
- Run automation script:
  ```powershell
  python automation.py "<issue title>" "<issue description>"
  ```
- The script will:
  1. Scan project files
  2. Identify files to update
  3. Update files using Gemini AI
  4. Commit and push changes

### 4. GitHub Actions
- Workflows automatically process and close issues when triggered by new or edited issues.

## Authentication
- API endpoints require an `X-API-Key` header. Example keys: `mysecretkey`, `anotherkey` (see `main.py`).

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT
