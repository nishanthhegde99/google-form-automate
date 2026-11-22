import json
import random
import threading
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Diverse Indian First Names
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishan",
    "Shaurya", "Atharv", "Advik", "Pranav", "Dhruv", "Kabir", "Ritvik", "Rohan", "Nikhil", "Rahul",
    "Varun", "Karthik", "Harish", "Suresh", "Rajesh", "Amit", "Manoj", "Chetan", "Vikram", "Gautam",
    "Ananya", "Diya", "Saanvi", "Aadhya", "Pari", "Kiara", "Myra", "Riya", "Anika", "Ishita",
    "Sneha", "Pooja", "Priya", "Neha", "Tanvi", "Kavya", "Shreya", "Meera", "Swati", "Divya",
    "Aditi", "Niharika", "Deepika", "Bhavya", "Shruti", "Akanksha", "Rashmi", "Pallavi", "Anjali"
]

# Diverse Indian Surnames
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Patel", "Mehta", "Shah", "Reddy", "Nair", "Rao", "Iyer",
    "Kulkarni", "Deshmukh", "Joshi", "Bhat", "Hegde", "Shenoy", "Shetty", "Prasad", "Kumar", "Singh",
    "Mishra", "Chatterjee", "Banerjee", "Mukherjee", "Das", "Ghosh", "Pillai", "Menon", "Nambiar", "Gowda",
    "Patil", "More", "Shinde", "Yadav", "Chauhan", "Agarwal", "Bansal", "Goel", "Jain", "Saxena"
]

HOSTEL_BLOCKS = ["Block 1", "Block 2", "Block 3", "Block 4", "Block 5", "Block 6"]

FEEDBACK_TEMPLATES = [
    "Overall experience was quite satisfactory and met my expectations.",
    "Very well organized and smooth process. Appreciate the effort.",
    "Good initiative, but there is definitely room for minor improvements.",
    "Found this very helpful and informative. Keep up the great work!",
    "Decent experience. The instructions could be slightly clearer.",
    "Excellent quality and timely execution. Highly recommended.",
    "It was an average experience, nothing extraordinary but fulfilled the purpose.",
    "Really liked the attention to detail. Would love to participate again.",
    "Great service and user-friendly interface. Very impressed.",
    "Everything worked seamlessly without any noticeable hurdles."
]

# Global Automation State
state = {
    "is_running": False,
    "current_response": 0,
    "target_responses": None,  # None means unlimited
    "url": "",
    "logs": [],
    "status": "Idle",  # "Idle", "Running", "Stopped", "Completed", "Error"
    "error": None
}
state_lock = threading.Lock()
stop_event = threading.Event()


def add_log(msg):
    with state_lock:
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {msg}"
        state["logs"].append(log_entry)
        if len(state["logs"]) > 300:
            state["logs"].pop(0)
    print(log_entry)


def safe_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)
    time.sleep(0.2)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def get_label(el):
    val = el.get_attribute("data-value") or el.get_attribute("aria-label") or el.text
    return (val or "").strip()


def match_options_by_keywords(elements, keywords):
    matched = []
    for el in elements:
        lbl = get_label(el).lower()
        if any(kw.lower() in lbl for kw in keywords):
            matched.append(el)
    return matched if matched else elements


def answer_survey_question(driver, q, title, index):
    lower = title.lower()
    radios = q.find_elements(By.XPATH, './/div[@role="radio"]')
    checkboxes = q.find_elements(By.XPATH, './/div[@role="checkbox"]')
    text_inputs = q.find_elements(By.XPATH, './/input[@type="text"]')
    textareas = q.find_elements(By.XPATH, './/textarea')

    # 1. Purchased second-hand before
    if "purchased a second-hand" in lower or ("purchased" in lower and "second-hand" in lower):
        if radios:
            candidates = match_options_by_keywords(radios, ["yes"])
            choice = random.choice(candidates)
            safe_click(driver, choice)
            add_log(f"  Q{index}: Selected '{get_label(choice)}'")
            return

    # 2. Second-hand products to purchase
    if "which second-hand products" in lower or "consider purchasing" in lower:
        if checkboxes:
            targets = ["textbook", "academic", "cloth", "accessor", "electronic", "hostel"]
            matched = match_options_by_keywords(checkboxes, targets)
            pick_k = random.randint(max(1, len(matched) - 2), len(matched))
            selected = random.sample(matched, pick_k)
            for c in selected:
                safe_click(driver, c)
            add_log(f"  Q{index}: Checked {[get_label(c) for c in selected]}")
            return

    # 3. Look for second-hand products
    if "where would you normally look" in lower:
        targets = ["whatsapp", "friend", "classmate", "instagram"]
        if checkboxes:
            matched = match_options_by_keywords(checkboxes, targets)
            pick_k = random.randint(1, len(matched))
            selected = random.sample(matched, pick_k)
            for c in selected:
                safe_click(driver, c)
            add_log(f"  Q{index}: Checked {[get_label(c) for c in selected]}")
            return
        elif radios:
            candidates = match_options_by_keywords(radios, targets)
            choice = random.choice(candidates)
            safe_click(driver, choice)
            add_log(f"  Q{index}: Selected '{get_label(choice)}'")
            return

    # 4. Main reason
    if "main reason" in lower and ("purchas" in lower or "second-hand" in lower):
        if radios:
            candidates = match_options_by_keywords(radios, ["lower cost", "affordab", "cost", "price", "cheap"])
            choice = random.choice(candidates)
            safe_click(driver, choice)
            add_log(f"  Q{index}: Selected '{get_label(choice)}'")
            return

    # 5. Own unused but usable products
    if "currently own products" in lower or ("own" in lower and "usable" in lower):
        if radios:
            candidates = match_options_by_keywords(radios, ["yes"])
            choice = random.choice(candidates)
            safe_click(driver, choice)
            add_log(f"  Q{index}: Selected '{get_label(choice)}'")
            return

    # 6. Sold, exchanged or given away
    if "sold, exchanged or given away" in lower or ("sold" in lower and "exchanged" in lower):
        if radios:
            choice = random.choice(radios)
            safe_click(driver, choice)
            add_log(f"  Q{index}: Selected '{get_label(choice)}'")
            return
        elif checkboxes:
            pick_k = random.randint(1, min(2, len(checkboxes)))
            selected = random.sample(checkboxes, pick_k)
            for c in selected:
                safe_click(driver, c)
            add_log(f"  Q{index}: Checked {[get_label(c) for c in selected]}")
            return

    # 7. Difficulties faced
    if "difficulties might you face" in lower or "selling or exchanging" in lower:
        targets = ["finding", "buyer", "exchange", "price", "communicat", "location", "trust"]
        if checkboxes:
            matched = match_options_by_keywords(checkboxes, targets)
            pick_k = random.randint(2, min(4, len(matched)))
            selected = random.sample(matched, pick_k)
            for c in selected:
                safe_click(driver, c)
            add_log(f"  Q{index}: Checked {[get_label(c) for c in selected]}")
            return
        elif radios:
            choice = random.choice(radios)
            safe_click(driver, choice)
            add_log(f"  Q{index}: Selected '{get_label(choice)}'")
            return

    # 8. Biggest concern
    if "biggest concern" in lower or "concern" in lower:
        targets = ["quality", "condition", "reliab", "fake", "misleading", "trust"]
        if radios:
            candidates = match_options_by_keywords(radios, targets)
            choice = random.choice(candidates)
            safe_click(driver, choice)
            add_log(f"  Q{index}: Selected '{get_label(choice)}'")
            return
        elif checkboxes:
            choice = random.choice(checkboxes)
            safe_click(driver, choice)
            add_log(f"  Q{index}: Checked '{get_label(choice)}'")
            return

    # 9. Verified student marketplace
    if "verified university students" in lower or ("marketplace" in lower and "verified" in lower):
        if radios:
            candidates = match_options_by_keywords(radios, ["yes"])
            choice = random.choice(candidates)
            safe_click(driver, choice)
            add_log(f"  Q{index}: Selected '{get_label(choice)}'")
            return

    # 10. Platform across 6 hostel blocks
    if "six hostel blocks" in lower or "hostel blocks" in lower:
        if radios:
            candidates = match_options_by_keywords(radios, ["definitely", "probably", "yes"])
            choice = random.choice(candidates)
            safe_click(driver, choice)
            add_log(f"  Q{index}: Selected '{get_label(choice)}'")
            return

    # 11. Useful features
    if "features would be most useful" in lower or ("features" in lower and "useful" in lower):
        targets = ["verificat", "search", "filter", "category", "condition", "image", "communicat", "hostel", "exchange"]
        if checkboxes:
            matched = match_options_by_keywords(checkboxes, targets)
            pick_k = random.randint(3, len(matched))
            selected = random.sample(matched, pick_k)
            for c in selected:
                safe_click(driver, c)
            add_log(f"  Q{index}: Checked {[get_label(c) for c in selected]}")
            return
        elif radios:
            choice = random.choice(radios)
            safe_click(driver, choice)
            add_log(f"  Q{index}: Selected '{get_label(choice)}'")
            return

    # 12. Reducing waste
    if "reducing waste" in lower or "reusing products" in lower or "waste" in lower:
        if radios:
            candidates = match_options_by_keywords(radios, ["5", "4", "very important", "important"])
            choice = random.choice(candidates)
            safe_click(driver, choice)
            add_log(f"  Q{index}: Selected '{get_label(choice)}'")
            return

    # Generic inputs: Name, Email, Hostel Block
    if any(k in lower for k in ["name", "full name"]):
        val = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if text_inputs:
            text_inputs[0].clear()
            text_inputs[0].send_keys(val)
            add_log(f"  Name: '{val}'")
            return

    if any(k in lower for k in ["email", "e-mail"]):
        val = f"{random.choice(FIRST_NAMES).lower()}.{random.choice(LAST_NAMES).lower()}{random.randint(10, 99)}@gmail.com"
        if text_inputs:
            text_inputs[0].clear()
            text_inputs[0].send_keys(val)
            add_log(f"  Email: '{val}'")
            return

    if any(k in lower for k in ["hostel", "block"]):
        if radios:
            choice = random.choice(radios)
            safe_click(driver, choice)
            add_log(f"  Hostel Block: Selected '{get_label(choice)}'")
            return
        elif text_inputs:
            blk = random.choice(HOSTEL_BLOCKS)
            text_inputs[0].clear()
            text_inputs[0].send_keys(blk)
            add_log(f"  Hostel Block: '{blk}'")
            return

    # Fallbacks
    if radios:
        choice = random.choice(radios)
        safe_click(driver, choice)
        add_log(f"  Radio -> '{get_label(choice)}'")
    elif checkboxes:
        num = random.randint(1, max(1, len(checkboxes) // 2))
        selected = random.sample(checkboxes, num)
        for c in selected:
            safe_click(driver, c)
        add_log(f"  Checkboxes -> {[get_label(c) for c in selected]}")
    elif text_inputs:
        text_inputs[0].clear()
        text_inputs[0].send_keys("Automated campus survey entry")
        add_log("  Short text -> filled")
    elif textareas:
        textareas[0].clear()
        textareas[0].send_keys("A dedicated platform for hostel students would be very beneficial.")
        add_log("  Paragraph -> filled")


def run_automation_worker(form_url, target_responses, headless):
    global state
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,800")

    driver = None
    try:
        add_log("Launching Chrome browser...")
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 15)

        resp_num = 1
        while not stop_event.is_set():
            if target_responses is not None and resp_num > target_responses:
                break

            target_display = target_responses if target_responses is not None else "Unlimited"
            add_log(f"=== Starting Response #{resp_num} / {target_display} ===")

            driver.get(form_url)
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="listitem"]')))
            questions = driver.find_elements(By.XPATH, '//div[@role="listitem"]')

            for i, q in enumerate(questions, 1):
                if stop_event.is_set():
                    break
                try:
                    title = q.find_element(By.XPATH, './/div[@role="heading"]').text.strip().replace("\n", " ")
                except Exception:
                    title = f"Question {i}"
                answer_survey_question(driver, q, title, i)

            if stop_event.is_set():
                break

            # Submit
            add_log("Submitting form...")
            submit_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//div[@role="button"]//span[text()="Submit" or text()="Send"]')
            ))
            safe_click(driver, submit_button)
            time.sleep(1.5)

            with state_lock:
                state["current_response"] = resp_num

            add_log(f"✓ Response #{resp_num} successfully submitted!")

            # Check stop or limit
            if target_responses is not None and resp_num >= target_responses:
                break

            # Delay
            pause = round(random.uniform(1.2, 2.5), 1)
            add_log(f"Waiting {pause}s before next entry...")
            time.sleep(pause)
            resp_num += 1

        with state_lock:
            if stop_event.is_set():
                state["status"] = "Stopped"
                add_log(f"Automation stopped by user. Total submitted: {state['current_response']}")
            else:
                state["status"] = "Completed"
                add_log(f"All {state['current_response']} responses completed successfully!")

    except Exception as e:
        with state_lock:
            state["status"] = "Error"
            state["error"] = str(e)
        add_log(f"ERROR: {e}")

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        with state_lock:
            state["is_running"] = False
        add_log("Browser closed.")


# HTML Dashboard
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Google Form Automation</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, sans-serif;
      background: #0f172a;
      color: #f1f5f9;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 30px 15px;
    }
    .container {
      width: 100%;
      max-width: 860px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .header {
      background: linear-gradient(135deg, #1e293b, #0f172a);
      border: 1px solid #334155;
      padding: 24px 28px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .header h1 {
      font-size: 1.5rem;
      font-weight: 700;
      color: #38bdf8;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .header p {
      font-size: 0.85rem;
      color: #94a3b8;
      margin-top: 4px;
    }
    .badge {
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .badge-idle { background: #334155; color: #cbd5e1; }
    .badge-running { background: #0369a1; color: #38bdf8; animation: pulse 1.5s infinite; }
    .badge-completed { background: #065f46; color: #34d399; }
    .badge-stopped { background: #991b1b; color: #f87171; }
    .badge-error { background: #7f1d1d; color: #fca5a5; }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.6; }
    }

    .card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 16px;
      padding: 24px 28px;
    }
    .form-group {
      margin-bottom: 18px;
    }
    label {
      display: block;
      font-size: 0.9rem;
      font-weight: 600;
      color: #e2e8f0;
      margin-bottom: 8px;
    }
    input[type="text"], input[type="number"] {
      width: 100%;
      background: #0f172a;
      border: 1px solid #334155;
      padding: 12px 16px;
      border-radius: 10px;
      color: #f1f5f9;
      font-size: 0.95rem;
      transition: all 0.2s;
    }
    input[type="text"]:focus, input[type="number"]:focus {
      outline: none;
      border-color: #38bdf8;
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
    }
    .row {
      display: flex;
      gap: 16px;
      align-items: center;
    }
    .checkbox-label {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.9rem;
      color: #cbd5e1;
      cursor: pointer;
      user-select: none;
    }
    .checkbox-label input {
      accent-color: #38bdf8;
      width: 18px;
      height: 18px;
    }
    .actions {
      display: flex;
      gap: 12px;
      margin-top: 20px;
    }
    button {
      flex: 1;
      padding: 14px 20px;
      border-radius: 10px;
      border: none;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    .btn-start {
      background: #0284c7;
      color: #ffffff;
    }
    .btn-start:hover:not(:disabled) {
      background: #0369a1;
      transform: translateY(-1px);
    }
    .btn-stop {
      background: #dc2626;
      color: #ffffff;
    }
    .btn-stop:hover:not(:disabled) {
      background: #b91c1c;
      transform: translateY(-1px);
    }
    button:disabled {
      opacity: 0.4;
      cursor: not-allowed;
      transform: none;
    }

    .counter-bar {
      display: flex;
      align-items: center;
      justify-content: space-around;
      background: #0f172a;
      border: 1px solid #334155;
      padding: 16px;
      border-radius: 12px;
      margin-bottom: 20px;
      text-align: center;
    }
    .counter-item .number {
      font-size: 2rem;
      font-weight: 700;
      color: #38bdf8;
    }
    .counter-item .label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #94a3b8;
      margin-top: 2px;
    }

    .logs-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }
    .logs-console {
      background: #090d16;
      border: 1px solid #1e293b;
      border-radius: 10px;
      padding: 14px 16px;
      height: 280px;
      overflow-y: auto;
      font-family: ui-monospace, Menlo, Monaco, Consolas, monospace;
      font-size: 0.8rem;
      line-height: 1.5;
      color: #94a3b8;
    }
    .log-line {
      margin-bottom: 4px;
      word-break: break-all;
    }
    .log-line.success { color: #34d399; font-weight: 600; }
    .log-line.error { color: #f87171; font-weight: 600; }
    .log-line.highlight { color: #38bdf8; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1>⚡ Google Form Automator</h1>
        <p>Automate submissions with varied Indian survey responses</p>
      </div>
      <div id="statusBadge" class="badge badge-idle">Idle</div>
    </div>

    <div class="card">
      <div class="form-group">
        <label for="formUrl">Google Form Link (URL)</label>
        <input type="text" id="formUrl" placeholder="https://docs.google.com/forms/d/e/.../viewform" value="https://docs.google.com/forms/d/e/1FAIpQLSeHnKuQnHaLZVL-TTXCjLIZUQMmYnoB--Kr_LINtTzuk1Z-MA/viewform?usp=header" />
      </div>

      <div class="row" style="margin-bottom: 16px;">
        <div style="flex: 1;">
          <label for="respCount">Number of Responses</label>
          <input type="number" id="respCount" min="1" value="50" />
        </div>
        <div style="flex: 1; padding-top: 28px; display: flex; flex-direction: column; gap: 10px;">
          <label class="checkbox-label">
            <input type="checkbox" id="unlimitedCheck" onchange="toggleUnlimited(this)">
            <span>Run Unlimited Responses</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" id="headlessCheck">
            <span>Run Chrome in Background (Headless)</span>
          </label>
        </div>
      </div>

      <div class="actions">
        <button id="startBtn" class="btn-start" onclick="startAutomation()">
          ▶ Start Automation
        </button>
        <button id="stopBtn" class="btn-stop" onclick="stopAutomation()" disabled>
          ⏹ Stop
        </button>
      </div>
    </div>

    <div class="card">
      <div class="counter-bar">
        <div class="counter-item">
          <div class="number" id="submittedCount">0</div>
          <div class="label">Responses Submitted</div>
        </div>
        <div class="counter-item">
          <div class="number" id="targetCount">50</div>
          <div class="label">Target Limit</div>
        </div>
      </div>

      <div class="logs-header">
        <label style="margin: 0;">Live Activity Console</label>
        <button onclick="clearLogs()" style="background: none; border: 1px solid #334155; padding: 4px 10px; font-size: 0.75rem; color: #94a3b8; border-radius: 6px; flex: none;">Clear Console</button>
      </div>
      <div class="logs-console" id="logConsole">
        <div class="log-line">Ready. Enter your form link and click 'Start Automation'.</div>
      </div>
    </div>
  </div>

  <script>
    function toggleUnlimited(cb) {
      const countInput = document.getElementById('respCount');
      if (cb.checked) {
        countInput.disabled = true;
        document.getElementById('targetCount').innerText = '∞';
      } else {
        countInput.disabled = false;
        document.getElementById('targetCount').innerText = countInput.value;
      }
    }

    document.getElementById('respCount').addEventListener('input', (e) => {
      if (!document.getElementById('unlimitedCheck').checked) {
        document.getElementById('targetCount').innerText = e.target.value || '0';
      }
    });

    async function startAutomation() {
      const url = document.getElementById('formUrl').value.trim();
      const isUnlimited = document.getElementById('unlimitedCheck').checked;
      const count = isUnlimited ? null : parseInt(document.getElementById('respCount').value, 10);
      const headless = document.getElementById('headlessCheck').checked;

      if (!url.startsWith('http')) {
        alert('Please enter a valid Google Form URL');
        return;
      }

      document.getElementById('startBtn').disabled = true;
      document.getElementById('stopBtn').disabled = false;

      await fetch('/api/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, count, headless })
      });
    }

    async function stopAutomation() {
      document.getElementById('stopBtn').disabled = true;
      await fetch('/api/stop', { method: 'POST' });
    }

    function clearLogs() {
      document.getElementById('logConsole').innerHTML = '';
    }

    async function updateStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();

        // Update badge
        const badge = document.getElementById('statusBadge');
        badge.innerText = data.status;
        badge.className = 'badge badge-' + data.status.toLowerCase();

        // Update buttons
        document.getElementById('startBtn').disabled = data.is_running;
        document.getElementById('stopBtn').disabled = !data.is_running;

        // Update counters
        document.getElementById('submittedCount').innerText = data.current_response;
        if (data.target_responses === null) {
          document.getElementById('targetCount').innerText = '∞';
        } else {
          document.getElementById('targetCount').innerText = data.target_responses;
        }

        // Update logs
        const logConsole = document.getElementById('logConsole');
        if (data.logs && data.logs.length > 0) {
          const atBottom = logConsole.scrollHeight - logConsole.scrollTop <= logConsole.clientHeight + 50;
          logConsole.innerHTML = data.logs.map(log => {
            let cls = 'log-line';
            if (log.includes('✓') || log.includes('successfully')) cls += ' success';
            else if (log.includes('ERROR') || log.includes('error')) cls += ' error';
            else if (log.includes('===')) cls += ' highlight';
            return `<div class="${cls}">${log}</div>`;
          }).join('');
          if (atBottom) {
            logConsole.scrollTop = logConsole.scrollHeight;
          }
        }
      } catch (e) {
        console.error(e);
      }
    }

    setInterval(updateStatus, 1000);
  </script>
</body>
</html>
"""


class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            self._set_headers(200, "text/html; charset=utf-8")
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path == "/api/status":
            self._set_headers(200, "application/json")
            with state_lock:
                data = json.dumps(state)
            self.wfile.write(data.encode("utf-8"))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_POST(self):
        global stop_event
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        if self.path == "/api/start":
            try:
                params = json.loads(body.decode("utf-8"))
                url = params.get("url", "")
                count = params.get("count", None)
                headless = params.get("headless", False)

                with state_lock:
                    if state["is_running"]:
                        self._set_headers(400)
                        self.wfile.write(json.dumps({"error": "Already running"}).encode("utf-8"))
                        return
                    state["is_running"] = True
                    state["current_response"] = 0
                    state["target_responses"] = count
                    state["url"] = url
                    state["status"] = "Running"
                    state["logs"] = []
                    stop_event.clear()

                thread = threading.Thread(
                    target=run_automation_worker,
                    args=(url, count, headless),
                    daemon=True
                )
                thread.start()

                self._set_headers(200)
                self.wfile.write(json.dumps({"status": "started"}).encode("utf-8"))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        elif self.path == "/api/stop":
            stop_event.set()
            with state_lock:
                state["status"] = "Stopping..."
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "stopping"}).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        # Silence default http.server access log clutter
        pass


def start_server(port=5000):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, RequestHandler)
    url = f"http://127.0.0.1:{port}"
    print("\n" + "=" * 55)
    print(f"🚀 Google Form Automator UI running at: {url}")
    print(f"👉 Opening browser automatically...")
    print("=" * 55 + "\n")

    # Open browser automatically
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping web dashboard server...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    start_server(5000)
