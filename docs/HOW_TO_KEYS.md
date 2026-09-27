# API keys — no chat paste

You do **not** put keys on GitHub.com.

## If you see the repo files (left / file viewer)

1. Open `.env.example`
2. Duplicate it as a new file named exactly `.env` in the **same folder as README.md**
3. Put the keys after `=`
4. Save
5. Run `python -m monarch keys` — should show `"gemini": true`

## If there is no edit button

That screen is probably **GitHub in the browser**, which will not give you a safe `.env` editor.

Do this instead:

- On your computer: clone the repo, create `.env` in VS Code / Notepad, never push it
- Or in Arena: open the **workspace file tree** (not github.com), new file `.env`

## If the only box you have is this chat

Do **not** paste live keys here. Keys in chat get logged.

Wait until you have a file you can save locally. Upload/OAuth can wait.

`.env` is gitignored. It will not go to GitHub if we did our job.
