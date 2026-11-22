# Google Form Automator

A tool to automate Google Form survey submissions with randomized Indian respondent profiles and varied choices. Includes both a **Modern Web User Interface** and a **CLI script**.

---

## 🚀 Running the Web User Interface

Launch the graphical dashboard with a single command:

```bash
source venv/bin/activate
python app.py
```

The app will open automatically in your browser at **`http://127.0.0.1:5000`**.

### UI Features:
- 🔗 **Google Form Link Input**: Paste any Google Form link directly into the input field.
- 🔢 **Custom or Unlimited Submissions**: Enter a fixed number (e.g. `50`) or check **"Run Unlimited Responses"**.
- 🕶️ **Headless Toggle**: Option to run Chrome invisibly in the background.
- ▶️ **Start & Stop Controls**: Start with one click, and stop cleanly whenever you want.
- 📊 **Live Dashboard**: Real-time counters showing submitted responses vs target.
- 📜 **Live Activity Console**: See each question, option chosen, and confirmation live as it happens.

---

## 💻 Alternative: Running via CLI

If you prefer running directly in the terminal without a web browser:

```bash
source venv/bin/activate
python form_automation.py
```
*(Press `Ctrl + C` anytime to safely halt and view total submissions).*
