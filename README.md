# ABI — First Contact (v0.1)

A responsive phone/desktop web app with a Python FastAPI backend and Ollama Cloud chat.

## Run locally
1. Install Python 3.11+.
2. Install dependencies: `pip install -r requirements.txt`
3. Set `OLLAMA_API_KEY` in your environment.
4. Optional: set `OLLAMA_MODEL` to a model available to your Ollama Cloud account. Default: `gemma4:31b`.
5. Run: `uvicorn main:app --host 0.0.0.0 --port 3000`

Open `http://localhost:3000`.

## Deploy on Replit
1. Create/open a Python Repl or add these files to a new folder in your existing Repl.
2. Add `OLLAMA_API_KEY` in Replit **Secrets** (lock icon). Never put the key in source code.
3. Optional: add `OLLAMA_MODEL` in Secrets if you want a different available model.
4. Run the app. For a public deployment, use Replit Deployments and select the web-server deployment option. The app listens on `0.0.0.0:3000`.
5. After deployment, Replit provides the public URL.

## Notes
- Chat history is stored in the browser's local storage in this first prototype.
- Voice input uses the browser's Web Speech API where supported; availability varies by browser.
- Speech output uses the browser's speech synthesis.
- The API key stays on the server and is never sent to the browser.
- This is a first-contact prototype, not yet a multi-user account system. Do not use it for sensitive conversations.
