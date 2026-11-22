# Google Form Automation (50 Varied Responses)

Automates submitting 50 unique responses to Google Forms with randomized options and distinct text inputs.

## How it works

- **50 Iterations**: Automatically loops from response 1 to 50.
- **Randomized Multiple Choice / Radios**: Every iteration selects a different random radio choice (`random.choice`).
- **Randomized Checkboxes**: Selects a varied random combination of checkboxes (`random.sample`).
- **Randomized Dropdowns**: Picks random options from dropdown menus.
- **Context-aware Text Generation**: Generates unique names, emails, feedback comments, and suggestions so no two text responses are identical.
- **Human-like delays**: Random delay (1 to 2.5 seconds) between submissions to prevent rate limiting.

## Running

```bash
source venv/bin/activate
python form_automation.py
```
