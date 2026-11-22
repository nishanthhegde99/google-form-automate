# Google Form Automation (Unlimited Responses)

Automates submitting responses to Google Forms with randomized options, varied Indian details, and continuous submission support.

## Features

- **Unlimited Responses Mode**: Runs continuously until stopped (`TOTAL_RESPONSES = None`).
- **Clean Interrupt**: Stop anytime with `Ctrl + C` in the terminal without losing submitted data or breaking Chrome.
- **Configurable Limit**: Set `TOTAL_RESPONSES = 50`, `100`, etc. if you ever want a fixed number.
- **Randomized Survey Logic**: Each response selects distinct combinations of checkboxes, varied radio options, and rating values (4 or 5).
- **Indian Identity Details**: Generates authentic Indian names, emails, and hostel blocks (1–6).

## Quick Start

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Run the script**:
   ```bash
   python form_automation.py
   ```

3. **Stop anytime**:
   Press `Ctrl + C` in your terminal. The script will safely close the browser and show the total number of responses submitted.
