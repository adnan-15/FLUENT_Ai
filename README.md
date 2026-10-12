# Fluent AI

Fluent AI is a Django-based English-learning application. Its AI Tutor sends prompts to a locally running Ollama model, and the browser provides voice input/output through its speech APIs.

This guide follows the folder structure in this repository. Complete the initial setup once, then use the quick-start checklist whenever you want to run the application.

## 1. Project structure

The VS Code workspace is named `FluentAI`. The Django project folder inside it is `fluent_ai`. Run Django commands from the **inner `fluent_ai` folder**, the one containing `manage.py`.

```text
FluentAI/                     # VS Code workspace / repository root
└── fluent_ai/                # Django project root: run commands here
    ├── .venv/                # Python virtual environment (local to this computer)
    ├── fluent_ai/            # Django project configuration package
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── learning/             # Main Django app
    │   ├── migrations/
    │   ├── templates/        # Templates are directly in this folder
    │   │   ├── ai_tutor.html
    │   │   ├── assessment_result.html
    │   │   ├── assessment_writing.html
    │   │   ├── assessment.html
    │   │   ├── base.html
    │   │   ├── dashboard.html
    │   │   ├── game.html
    │   │   ├── games.html
    │   │   ├── landing.html
    │   │   ├── leaderboard.html
    │   │   ├── learning_path.html
    │   │   ├── lesson_detail.html
    │   │   ├── lesson_test.html
    │   │   ├── login.html
    │   │   ├── module_detail.html
    │   │   ├── practice_result.html
    │   │   ├── practice.html
    │   │   ├── profile.html
    │   │   ├── settings.html
    │   │   ├── signup.html
    │   │   ├── test_result.html
    │   │   └── vnotes.html
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── ai_service.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── db.sqlite3
    ├── manage.py
    ├── train_model.py
    └── requirements.txt
```

The list above highlights the items shown in the current project structure; your repository may contain additional files. Keep your templates directly under `learning/templates/`. For example, the AI Tutor template path is `learning/templates/ai_tutor.html`, not `learning/templates/learning/ai_tutor.html`.

> **Do not commit or share the `.venv` folder.** It is environment-specific and can be recreated from `requirements.txt`. Keep `db.sqlite3` if you need the existing local data; back it up before making database changes.

## 2. Prerequisites

Install the following:

- Python compatible with the project's dependencies.
- Ollama for running the local language model.
- A current browser. Chrome or Edge is recommended for speech recognition.
- Internet access for installing Python packages and downloading the model.

Open a terminal at the `FluentAI` workspace root, then enter the Django project folder:

```powershell
cd .\fluent_ai
```

If your terminal is already open in the inner `fluent_ai` folder, do not run `cd .\fluent_ai` again.

Confirm that you are in the correct directory:

```powershell
dir manage.py
dir requirements.txt
```

Both files should be found. If not, move to the folder that contains them.

Check Python:

```powershell
python --version
python -m pip --version
```

If `python` is not recognized, install Python, enable the option to add Python to PATH, and open a new terminal.

## 3. Set up the Python virtual environment

The project structure shows a `.venv` folder. If it is already configured on this computer, activate it.

### PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Command Prompt

```bat
.venv\Scripts\activate.bat
```

If `.venv` does **not** exist, create it first from the folder containing `manage.py`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, use Command Prompt or, if permitted by your computer's policy, run this for the current PowerShell process and then retry activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Once the environment is active, the terminal prompt commonly begins with `(.venv)`.

## 4. Install Python dependencies

With `.venv` active and the terminal in the folder containing `manage.py`, run:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The AI service calls Ollama using the Python `requests` package. If installation reports that `requests` is missing and it is not included in the requirements file, install it inside the active environment:

```powershell
python -m pip install requests
```

Use the same activated environment for `manage.py` commands. Otherwise, Django may appear to be missing packages that are installed in a different Python environment.

## 5. Install and configure Ollama

Ollama runs the language model locally. Django uses its local API to generate AI Tutor responses.

1. Install Ollama for Windows from the official website: https://ollama.com/download
2. Complete installation and open Ollama. Some installations start its service automatically.
3. Open a new terminal and check the command:

```powershell
ollama --version
```

If Windows cannot find `ollama`, finish installation or reopen the terminal so PATH changes can take effect.

### Download the model used by the application

The AI service configuration is expected to use:

```python
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:1b"
```

Pull the exact model:

```powershell
ollama pull llama3.2:1b
```

The download is normally required only once, unless you remove the model.

### Check the installed model

```powershell
ollama list
```

Confirm that `llama3.2:1b` appears in the list. You can test the model directly:

```powershell
ollama run llama3.2:1b
```

Enter a short prompt such as `Help me introduce myself in English.` and check that a response appears. Exit with `/bye` if supported, or press `Ctrl+C`.

### Check the local API

With Ollama running, execute this in PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get
```

The response should list the locally installed models.

**Keep Ollama running while using AI Tutor.** Django may still start when Ollama is stopped, but requests that need an AI response will fail. Do not expose the local Ollama API publicly.

## 6. Verify `learning/ai_service.py`

Open `learning/ai_service.py` and confirm that the configured model and endpoint match what you installed:

```python
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:1b"
```

If you intentionally use another model, pull that model first and update `MODEL_NAME` to the exact name reported by `ollama list`.

The service should send the user's message to Ollama and return the assistant's response. If it imports `requests`, that package must be installed in the active `.venv`.

## 7. Check Django configuration and database

The Django settings file is:

```text
fluent_ai/settings.py
```

Check that:

- `learning` is in `INSTALLED_APPS`.
- Django's template configuration discovers app templates. If using app template discovery, `APP_DIRS` should be enabled in the `TEMPLATES` setting.
- Database settings match the project.
- Your existing authentication, middleware, and URL configuration are preserved.
- Local development settings allow `localhost` and `127.0.0.1` when needed.

Do not replace `settings.py` with a generic example; it contains project-specific configuration.

### Apply migrations

From the inner `fluent_ai` folder, run:

```powershell
python manage.py migrate
```

This applies migrations already included with the app. If you have changed Django models and need to generate migrations, run:

```powershell
python manage.py makemigrations
python manage.py migrate
```

The repository contains `db.sqlite3`, so it may already have a local database. Back it up before making model or migration changes. Do not delete the database as a routine troubleshooting step.

The chat-history implementation expects the chat model and fields referenced in `learning/views.py` to exist and have migrations applied. Check the actual `ChatMessage` model and view code in your project if you encounter database-field or missing-table errors.

### Check the project

```powershell
python manage.py check
```

Fix reported configuration errors before starting the application.

### Create a user account if needed

If you do not already have a login, you can create an administrator account:

```powershell
python manage.py createsuperuser
```

Follow the prompts. Use the site's signup page if that is the normal registration flow for this app. The AI Tutor may require you to sign in first.

## 8. Run the application

You will normally use **two terminals**: one for Ollama and one for Django.

### Terminal 1: start Ollama

Open the Ollama application. If the service is not already running, open a terminal and execute:

```powershell
ollama serve
```

If you see a message that port `11434` is already in use, Ollama may already be running. Do not try to start a second server on the same port.

Keep Ollama running.

### Terminal 2: start Django

Open another terminal. If you are at the `FluentAI` workspace root:

```powershell
cd .\fluent_ai
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start Django:

```powershell
python manage.py runserver
```

Keep this terminal open, too. Django will print the local URL, usually:

- Main application: http://127.0.0.1:8000/
- AI Tutor: http://127.0.0.1:8000/ai-tutor/

Sign in first if required. The URL names are based on the expected route configuration; if you changed routes, use the address registered in `learning/urls.py`.

## 9. Test AI chat

1. Open the application and sign in.
2. Open the AI Tutor page.
3. Enter a message, for example: `Help me introduce myself in English.`
4. Send the message and wait for the response.
5. Send another message to confirm a second request works.
6. Refresh the page and check whether the conversation reloads from the database.

If the AI response fails, check the Django terminal for the error, then check that Ollama is running, the model is installed, and `learning/ai_service.py` points to the correct endpoint.

## 10. Test the voice assistant

The voice assistant relies on browser speech features. In this setup, browser speech recognition captures/transcribes the user's voice, Ollama generates the text response, and browser text-to-speech can read the response aloud. Ollama itself is not the microphone or speech-recognition engine.

1. Use a recent version of Chrome or Edge.
2. Open the application on `http://127.0.0.1:8000` or `http://localhost:8000`.
3. Open AI Tutor and activate voice mode.
4. Allow microphone access when the browser asks.
5. Start listening and speak a short English sentence.
6. Verify that the recognized text is submitted and an AI answer appears.
7. If voice replies are enabled, verify that the answer is spoken aloud.
8. Stop listening or close voice mode to return to the chat interface.

### Voice assistant notes

- Browser speech recognition support varies by browser, operating system, and installed speech services. Chrome or Edge is the recommended first test.
- Microphone access generally works on localhost. A deployed site should use HTTPS.
- Check the browser's microphone permissions and Windows privacy settings if recognition does not start.
- Check system volume and output device if responses appear but cannot be heard.
- Voice functions cannot be guaranteed on every browser just by installing Ollama; they depend on browser speech API support.

## 11. Test Clear Chat

1. Send a message and wait for the conversation to save.
2. Select **Clear Chat**.
3. Confirm that the displayed conversation disappears.
4. Refresh the page.
5. Confirm that cleared messages do not reappear.

For permanent deletion, the button must send a CSRF-protected `POST` request to the Django `clear_chat_history` route, and the view must delete records belonging to the signed-in user. If messages return after refreshing, check the route name in `learning/urls.py`, the JavaScript request, CSRF handling, and the delete query in `learning/views.py`.

## 12. Troubleshooting

### `Cannot connect to Ollama`

- Open the Ollama app or run `ollama serve`.
- Test `http://localhost:11434/api/tags`.
- Check `OLLAMA_URL` in `learning/ai_service.py`.
- Confirm that a local firewall or another process is not blocking the API.

### `model not found`

```powershell
ollama pull llama3.2:1b
ollama list
```

Make sure the `MODEL_NAME` value exactly matches the installed model.

### `No module named 'requests'`

Activate `.venv` and run:

```powershell
python -m pip install requests
```

### Missing database table or database error

```powershell
python manage.py showmigrations
python manage.py migrate
```

Check the database settings and the app's migrations. Back up `db.sqlite3` before any manual database changes.

### HTTP 403 or CSRF error in chat or Clear Chat

Check that:

- The user is signed in if the view requires authentication.
- The template includes `{% csrf_token %}` in its form.
- JavaScript includes the CSRF token in the `X-CSRFToken` header.
- The request uses `POST` where required.
- JavaScript posts to the URL generated by Django's URL name rather than an outdated hard-coded route.

### HTTP 404 for AI Tutor

Check that the main `fluent_ai/urls.py` includes the `learning` app's URL configuration and that `learning/urls.py` contains the AI Tutor route. The expected URL is `/ai-tutor/`.

### Microphone permission denied or voice recognition does not start

- Allow microphone access for localhost in the browser's site settings.
- Confirm the correct microphone is selected in Windows.
- Check Windows microphone privacy permissions.
- Try an updated version of Chrome or Edge.
- Reload the page after changing permissions.

### Voice reply is silent

- Check system volume and audio output.
- Check any voice-reply toggle in AI Tutor.
- Confirm browser `speechSynthesis` support.
- Test with a short response.

### Port 8000 is already in use

Run Django on a different port:

```powershell
python manage.py runserver 8001
```

Open http://127.0.0.1:8001/ instead.

## 13. Quick startup checklist

Every time you want to use Fluent AI:

- [ ] Start/open Ollama.
- [ ] Confirm `llama3.2:1b` is installed.
- [ ] Open a terminal in `FluentAI/fluent_ai/`, the folder containing `manage.py`.
- [ ] Activate `.venv`.
- [ ] Run `python manage.py runserver`.
- [ ] Open the website and sign in.
- [ ] Test AI chat.
- [ ] Test voice mode and microphone access when needed.

The first-time setup (installing Python packages, downloading the model, and applying existing migrations) normally only needs to be done once, unless dependencies, model configuration, or database models change.

## 14. Before deploying

This README is for local development. Before production deployment, configure secure environment-based secrets, `DEBUG=False`, correct `ALLOWED_HOSTS`, HTTPS, persistent database backups, and appropriate access controls for any AI service. Do not use Django's development server as a production web server.


## 15. Team collaboration with Git and GitHub

This section explains how teammates can get the project onto their own computers, run it locally, receive updates, create feature branches, push their work, and merge changes safely.

### 15.1 One-time setup for the project owner

The project owner should:

1. Create a repository on GitHub, or use the team's existing repository.
2. Push the project source code to that repository.
3. Add teammates as collaborators if the repository is private and the team is using a shared repository.
4. Share the GitHub repository URL with the team.

Do not commit the `.venv` folder, local secrets, or private credentials. Check that `.gitignore` excludes at least `.venv/`, `__pycache__/`, and local environment files such as `.env`. Decide as a team whether the existing `db.sqlite3` is sample data that should be shared or a local database that should remain untracked. Do not accidentally publish real user data.

A teammate needs Git installed and access to the GitHub repository. They do not need a copy of your `.venv`; each person creates their own environment.

### 15.2 If the project is not on a teammate's computer yet

There are two common ways to collaborate.

**Option A: Fork the repository (common for open-source contribution)**

1. Open the project repository on GitHub.
2. Click **Fork** to create a copy under the teammate's GitHub account.
3. Copy the URL of that fork.
4. Clone it locally:

```powershell
git clone https://github.com/TEAMMATE-USERNAME/REPOSITORY-NAME.git
cd REPOSITORY-NAME
```

5. If the Django project is inside a nested folder, enter the folder containing `manage.py`. For this project, that is expected to be the inner `fluent_ai` directory:

```powershell
cd .\fluent_ai
```

Use `dir manage.py` to verify you are in the right folder. If `manage.py` is at the repository root instead, do not run the extra `cd` command.

6. Add the original project repository as `upstream`, so the teammate can fetch updates from the team repository:

```powershell
git remote add upstream https://github.com/OWNER-USERNAME/REPOSITORY-NAME.git
git remote -v
```

Replace the example URLs and names with the real repository details.

**Option B: Clone the shared team repository**

If the owner has added the teammate as a collaborator, or the repository is public, the teammate can clone the shared repository directly:

```powershell
git clone https://github.com/OWNER-USERNAME/REPOSITORY-NAME.git
cd REPOSITORY-NAME
```

Then enter the folder containing `manage.py` if necessary. With a shared repository, `origin` normally points to the team repository. With a fork, `origin` points to the teammate's fork and `upstream` points to the original team repository.

> **Fork vs clone:** A fork is a GitHub-side copy under another account. A clone is a local copy on a computer. A teammate often forks first and then clones their fork, but members of a private team repository can usually clone the shared repository directly.

### 15.3 Set up the project on each teammate's computer

Run these steps after cloning. Use PowerShell commands below; use the equivalent activation command for Command Prompt if needed.

1. Open a terminal in the cloned repository.
2. Move into the Django folder containing `manage.py`.
3. Create a fresh virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If `.venv` already exists on that machine, just activate it. Do not copy another teammate's `.venv`.

4. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

5. Install Ollama from https://ollama.com/download.
6. Pull the model used by the project:

```powershell
ollama pull llama3.2:1b
```

7. Check `learning/ai_service.py` to ensure `OLLAMA_URL` and `MODEL_NAME` match the local Ollama installation and downloaded model.
8. Apply database migrations:

```powershell
python manage.py migrate
```

9. Check Django:

```powershell
python manage.py check
```

10. Create a login if needed:

```powershell
python manage.py createsuperuser
```

The project has a `db.sqlite3` file in the current structure, but a fresh clone may or may not include it, depending on the team's `.gitignore` and repository policy. If the database is not included, migrations create the schema; they do not recreate another developer's private database records. Use the team's approved seed-data instructions if the application needs example content.

### 15.4 Run AI chat and voice assistant on a teammate's computer

Each teammate must run their own local Ollama service and Django server. One person's `localhost` is not another person's computer.

**Terminal A: Ollama**

Open the Ollama app, or run:

```powershell
ollama serve
```

If it is already running, do not start a second server. Confirm the model is present:

```powershell
ollama list
```

Optional API test:

```powershell
Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get
```

**Terminal B: Django**

Open another terminal in the directory containing `manage.py`, activate `.venv`, and run:

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

Open http://127.0.0.1:8000/ and sign in. Open the AI Tutor at http://127.0.0.1:8000/ai-tutor/ if that route is registered in `learning/urls.py`.

To test the AI chat, send a message and wait for a response. To test voice assistance, use a current Chrome or Edge browser, allow microphone permission, open voice mode, and speak. Browser speech recognition support depends on the browser and operating system. Use localhost for development; use HTTPS for a deployed site.

If a teammate changes the application code, each developer still needs the dependencies, local Ollama model, database migrations, and running local services described above. A Git pull does not install Python packages, download the model, or start Ollama automatically.

### 15.5 Before starting a feature, update your local copy

First save or commit any work in progress. Then switch to the shared repository's default branch and pull the latest changes.

**For a shared repository clone:**

```powershell
git status
git switch main
git pull origin main
```

**For a forked repository:**

Fetch changes from the original team repository and update your local `main`:

```powershell
git status
git fetch upstream
git switch main
git merge upstream/main
git push origin main
```

This assumes the team's default branch is named `main`. If it is called `master` or something else, use that actual name. In a fork workflow, pushing `main` updates the teammate's fork, not the original team repository.

If `git status` shows uncommitted work, do not blindly switch branches or pull. Commit the work on its feature branch, or stash it first:

```powershell
git stash push -m "work in progress"
```

After updating `main`, you can restore the stash when appropriate:

```powershell
git stash pop
```

If the project uses a different default branch or team policy, follow that policy.

### 15.6 Create a feature branch before making changes

Do not develop directly on `main`. Create a descriptive branch from the updated `main`:

```powershell
git switch main
git switch -c feature/voice-assistant-fix
```

Other example branch names:

```text
feature/ai-chat-ui
feature/chat-history
fix/ollama-connection
fix/clear-chat
docs/team-setup
```

Use a branch name that describes one focused task. Make your code changes and test them locally. For this project, that may mean running `python manage.py check`, testing the page in the browser, testing AI chat with Ollama running, and checking voice behavior where supported.

### 15.7 Review and commit your changes

Check which files changed:

```powershell
git status
git diff
```

Stage only the files that belong to the feature. For example:

```powershell
git add learning/templates/ai_tutor.html learning/views.py
```

Use the paths that actually changed; do not copy this example blindly if you changed different files.

Commit the work:

```powershell
git commit -m "Improve AI tutor voice assistant"
```

A commit records your changes locally. It does not upload them to GitHub yet.

Before committing, make sure you are not adding `.venv/`, secrets, API keys, personal database contents, or unrelated files.

### 15.8 Push the feature branch to GitHub

For a shared team repository:

```powershell
git push -u origin feature/voice-assistant-fix
```

For a fork, the same command pushes to the teammate's fork, because `origin` points to that fork:

```powershell
git push -u origin feature/voice-assistant-fix
```

The `-u` option sets the upstream tracking branch, so later pushes can usually be done with:

```powershell
git push
```

### 15.9 Add the feature to the main project using a Pull Request

After pushing:

1. Open the repository on GitHub.
2. Create a **Pull Request (PR)** from `feature/voice-assistant-fix` into the team's default branch, usually `main`.
3. In a fork workflow, set the base repository to the original team repository and the compare/head repository to the teammate's fork.
4. Explain what changed, why it changed, and how it was tested.
5. Ask a teammate to review it.
6. Resolve review comments and push any further commits to the same branch.
7. Merge the PR only after the team agrees and any required checks pass.

A branch does not become part of `main` just because it was pushed. The PR review and merge are the normal way to integrate team work.

If you have direct permission and the team explicitly uses direct merges, follow the team's agreed process. For most collaborative projects, Pull Requests are safer.

### 15.10 Get updates after a teammate merges changes

Before pulling, commit or stash your own work so the update does not overwrite it.

**Shared repository clone:**

```powershell
git switch main
git pull origin main
```

**Fork workflow:**

```powershell
git fetch upstream
git switch main
git merge upstream/main
git push origin main
```

Then update your own feature branch with the latest `main` if necessary:

```powershell
git switch feature/voice-assistant-fix
git merge main
```

If Git reports conflicts, open the conflicted files, resolve the markers, test the result, then stage and commit the resolution:

```powershell
git add .
git commit -m "Merge latest main into voice assistant feature"
```

Only use `git add .` after reviewing `git status` and making sure you are not staging unrelated files. If the team prefers rebasing, follow the team's rebase policy instead of mixing merge and rebase workflows.

### 15.11 Common Git commands

| Task | Command |
|---|---|
| See current branch and changed files | `git status` |
| List local branches | `git branch` |
| List remotes | `git remote -v` |
| Download remote branch updates | `git fetch` |
| Switch branches | `git switch main` |
| Create and switch to a feature branch | `git switch -c feature/my-change` |
| Review unstaged changes | `git diff` |
| Stage a specific file | `git add path/to/file` |
| Commit staged changes | `git commit -m "Describe change"` |
| Push the current tracked branch | `git push` |
| Pull updates from the shared remote | `git pull origin main` |

### 15.12 Team workflow summary

Use this cycle for each feature:

```text
Clone the repository (first time only)
        ↓
Install Python dependencies and Ollama model (first time / when needed)
        ↓
Fetch and update main
        ↓
Create a feature branch
        ↓
Code and test locally
        ↓
Stage and commit the changes
        ↓
Push the feature branch
        ↓
Open a Pull Request
        ↓
Review and merge
        ↓
Everyone updates their local main
```

### Git safety rules for the team

- Never commit `.venv/`; each teammate creates their own environment.
- Never commit passwords, private keys, or local `.env` secrets.
- Agree whether `db.sqlite3` is shared sample data or local-only data. Do not publish real personal/user records.
- Do not use `git push --force` on shared branches unless the team explicitly agrees and understands the consequences.
- Pull or fetch updates before starting new work.
- Keep each feature branch focused and test it before opening a PR.
- Do not assume Git updates install dependencies or start Ollama. Re-read `requirements.txt`, run migrations when needed, and keep the local Ollama service running.

## Configuration reminder

This guide assumes `learning/ai_service.py` uses the Ollama endpoint `http://localhost:11434/api/chat` and model `llama3.2:1b`. If your current code uses different values, use the values from the actual code and ensure the matching model is installed. Always check the Django terminal and browser console when verifying features in your environment.
