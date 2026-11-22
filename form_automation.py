import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeHnKuQnHaLZVL-TTXCjLIZUQMmYnoB--Kr_LINtTzuk1Z-MA/viewform?usp=header"

# Set to None for UNLIMITED responses (press Ctrl + C in terminal to stop anytime),
# or specify a number (e.g., 50, 100, 500)
TOTAL_RESPONSES = None

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


def safe_click(driver, element):
    """Scrolls element to center of screen and clicks it safely."""
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)
    time.sleep(0.2)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def get_label(el):
    """Extracts text or data-value from a form element."""
    val = el.get_attribute("data-value") or el.get_attribute("aria-label") or el.text
    return (val or "").strip()


def match_options_by_keywords(elements, keywords):
    """Filters element list by matching lowercase label against keywords."""
    matched = []
    for el in elements:
        lbl = get_label(el).lower()
        if any(kw.lower() in lbl for kw in keywords):
            matched.append(el)
    return matched if matched else elements


def answer_survey_question(driver, q, title, index):
    """
    Answers each of the 12 survey questions according to the specified options,
    introducing realistic random variation between responses.
    """
    lower = title.lower()
    radios = q.find_elements(By.XPATH, './/div[@role="radio"]')
    checkboxes = q.find_elements(By.XPATH, './/div[@role="checkbox"]')
    text_inputs = q.find_elements(By.XPATH, './/input[@type="text"]')
    textareas = q.find_elements(By.XPATH, './/textarea')

    # --- 1. Have you ever purchased a second-hand product? (Yes) ---
    if "purchased a second-hand" in lower or ("purchased" in lower and "second-hand" in lower):
        if radios:
            candidates = match_options_by_keywords(radios, ["yes"])
            choice = random.choice(candidates)
            safe_click(driver, choice)
            print(f"  Q1: Selected '{get_label(choice)}'")
            return

    # --- 2. Which second-hand products would you consider purchasing? ---
    # (Textbooks, clothing, electronics, hostel essentials)
    if "which second-hand products" in lower or "consider purchasing" in lower:
        if checkboxes:
            targets = ["textbook", "academic", "cloth", "accessor", "electronic", "hostel"]
            matched = match_options_by_keywords(checkboxes, targets)
            pick_k = random.randint(max(1, len(matched) - 2), len(matched))
            selected = random.sample(matched, pick_k)
            for c in selected:
                safe_click(driver, c)
            print(f"  Q2: Checked {[get_label(c) for c in selected]}")
            return

    # --- 3. Where would you normally look for second-hand products? ---
    # (WhatsApp groups, friends and classmates, Instagram)
    if "where would you normally look" in lower:
        targets = ["whatsapp", "friend", "classmate", "instagram"]
        if checkboxes:
            matched = match_options_by_keywords(checkboxes, targets)
            pick_k = random.randint(1, len(matched))
            selected = random.sample(matched, pick_k)
            for c in selected:
                safe_click(driver, c)
            print(f"  Q3: Checked {[get_label(c) for c in selected]}")
            return
        elif radios:
            candidates = match_options_by_keywords(radios, targets)
            choice = random.choice(candidates)
            safe_click(driver, choice)
            print(f"  Q3: Selected '{get_label(choice)}'")
            return

    # --- 4. Main reason for purchasing second-hand products? ---
    # (Lower cost / Better affordability)
    if "main reason" in lower and ("purchas" in lower or "second-hand" in lower):
        if radios:
            candidates = match_options_by_keywords(radios, ["lower cost", "affordab", "cost", "price", "cheap"])
            choice = random.choice(candidates)
            safe_click(driver, choice)
            print(f"  Q4: Selected '{get_label(choice)}'")
            return

    # --- 5. Do you currently own products that you no longer use but are still usable? ---
    # (Yes)
    if "currently own products" in lower or ("own" in lower and "usable" in lower):
        if radios:
            candidates = match_options_by_keywords(radios, ["yes"])
            choice = random.choice(candidates)
            safe_click(driver, choice)
            print(f"  Q5: Selected '{get_label(choice)}'")
            return

    # --- 6. Have you ever sold, exchanged or given away an unused product? ---
    # (Sold / Exchanged / Given away / More than one of these)
    if "sold, exchanged or given away" in lower or ("sold" in lower and "exchanged" in lower):
        if radios:
            choice = random.choice(radios)
            safe_click(driver, choice)
            print(f"  Q6: Selected '{get_label(choice)}'")
            return
        elif checkboxes:
            pick_k = random.randint(1, min(2, len(checkboxes)))
            selected = random.sample(checkboxes, pick_k)
            for c in selected:
                safe_click(driver, c)
            print(f"  Q6: Checked {[get_label(c) for c in selected]}")
            return

    # --- 7. What difficulties might you face when selling or exchanging? ---
    # (Finding buyers, someone willing to exchange, pricing, communication, location, trusting buyers)
    if "difficulties might you face" in lower or "selling or exchanging" in lower:
        targets = ["finding", "buyer", "exchange", "price", "communicat", "location", "trust"]
        if checkboxes:
            matched = match_options_by_keywords(checkboxes, targets)
            pick_k = random.randint(2, min(4, len(matched)))
            selected = random.sample(matched, pick_k)
            for c in selected:
                safe_click(driver, c)
            print(f"  Q7: Checked {[get_label(c) for c in selected]}")
            return
        elif radios:
            choice = random.choice(radios)
            safe_click(driver, choice)
            print(f"  Q7: Selected '{get_label(choice)}'")
            return

    # --- 8. Biggest concern when purchasing a second-hand product? ---
    # (Product quality and condition / Seller reliability / Fake or misleading listings)
    if "biggest concern" in lower or "concern" in lower:
        targets = ["quality", "condition", "reliab", "fake", "misleading", "trust"]
        if radios:
            candidates = match_options_by_keywords(radios, targets)
            choice = random.choice(candidates)
            safe_click(driver, choice)
            print(f"  Q8: Selected '{get_label(choice)}'")
            return
        elif checkboxes:
            choice = random.choice(checkboxes)
            safe_click(driver, choice)
            print(f"  Q8: Checked '{get_label(choice)}'")
            return

    # --- 9. Prefer a marketplace specifically for verified university students? ---
    # (Yes)
    if "verified university students" in lower or ("marketplace" in lower and "verified" in lower):
        if radios:
            candidates = match_options_by_keywords(radios, ["yes"])
            choice = random.choice(candidates)
            safe_click(driver, choice)
            print(f"  Q9: Selected '{get_label(choice)}'")
            return

    # --- 10. Platform connecting buyers and sellers across all six hostel blocks? ---
    # (Definitely / Probably)
    if "six hostel blocks" in lower or "hostel blocks" in lower:
        if radios:
            candidates = match_options_by_keywords(radios, ["definitely", "probably", "yes"])
            choice = random.choice(candidates)
            safe_click(driver, choice)
            print(f"  Q10: Selected '{get_label(choice)}'")
            return

    # --- 11. Which features would be most useful in such a platform? ---
    # (Student verification, search and filters, category browsing, condition/images, chat, hostel filter, exchange)
    if "features would be most useful" in lower or ("features" in lower and "useful" in lower):
        targets = ["verificat", "search", "filter", "category", "condition", "image", "communicat", "hostel", "exchange"]
        if checkboxes:
            matched = match_options_by_keywords(checkboxes, targets)
            pick_k = random.randint(3, len(matched))
            selected = random.sample(matched, pick_k)
            for c in selected:
                safe_click(driver, c)
            print(f"  Q11: Checked {[get_label(c) for c in selected]}")
            return
        elif radios:
            choice = random.choice(radios)
            safe_click(driver, choice)
            print(f"  Q11: Selected '{get_label(choice)}'")
            return

    # --- 12. How important is reducing waste and reusing products? ---
    # (4 or 5 / Important or Very important)
    if "reducing waste" in lower or "reusing products" in lower or "waste" in lower:
        if radios:
            candidates = match_options_by_keywords(radios, ["5", "4", "very important", "important"])
            choice = random.choice(candidates)
            safe_click(driver, choice)
            print(f"  Q12: Selected '{get_label(choice)}'")
            return

    # --- GENERIC FIELDS: Names, Emails, Hostel Block, or Fallback ---
    if any(k in lower for k in ["name", "full name"]):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name_val = f"{first} {last}"
        if text_inputs:
            text_inputs[0].clear()
            text_inputs[0].send_keys(name_val)
            print(f"  Name: '{name_val}'")
            return

    if any(k in lower for k in ["email", "e-mail"]):
        first = random.choice(FIRST_NAMES).lower()
        last = random.choice(LAST_NAMES).lower()
        email_val = f"{first}.{last}{random.randint(10, 99)}@gmail.com"
        if text_inputs:
            text_inputs[0].clear()
            text_inputs[0].send_keys(email_val)
            print(f"  Email: '{email_val}'")
            return

    if any(k in lower for k in ["hostel", "block"]):
        if radios:
            choice = random.choice(radios)
            safe_click(driver, choice)
            print(f"  Hostel Block: Selected '{get_label(choice)}'")
            return
        elif text_inputs:
            blk = random.choice(HOSTEL_BLOCKS)
            text_inputs[0].clear()
            text_inputs[0].send_keys(blk)
            print(f"  Hostel Block: '{blk}'")
            return

    # Fallbacks if an unlisted question is encountered
    if radios:
        choice = random.choice(radios)
        safe_click(driver, choice)
        print(f"  Radio -> Selected '{get_label(choice)}'")
    elif checkboxes:
        num = random.randint(1, max(1, len(checkboxes) // 2))
        selected = random.sample(checkboxes, num)
        for c in selected:
            safe_click(driver, c)
        print(f"  Checkboxes -> Selected {[get_label(c) for c in selected]}")
    elif text_inputs:
        text_inputs[0].clear()
        text_inputs[0].send_keys("Useful initiative for campus students")
        print("  Short text -> filled")
    elif textareas:
        textareas[0].clear()
        textareas[0].send_keys("A dedicated platform for our hostel blocks would really help students buy and sell easily.")
        print("  Paragraph -> filled")


def fill_and_submit(driver, response_num):
    """Processes all questions and submits."""
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="listitem"]')))
    questions = driver.find_elements(By.XPATH, '//div[@role="listitem"]')

    target_str = str(TOTAL_RESPONSES) if TOTAL_RESPONSES is not None else "∞ (Unlimited)"
    print(f"\n==========================================")
    print(f" [Response #{response_num} / {target_str}] Filling {len(questions)} survey questions")
    print(f"==========================================")

    for i, q in enumerate(questions, 1):
        try:
            title_el = q.find_element(By.XPATH, './/div[@role="heading"]')
            title = title_el.text.strip().replace("\n", " ")
        except Exception:
            title = f"Question {i}"

        answer_survey_question(driver, q, title, i)

    # Click Submit
    print("\nSubmitting response...")
    submit_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//div[@role="button"]//span[text()="Submit" or text()="Send"]')
    ))
    safe_click(driver, submit_button)

    # Allow confirmation to register
    time.sleep(1.5)
    print(f"[✓] Response #{response_num} successfully submitted!\n")


def main():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment if you prefer running silently without UI
    driver = webdriver.Chrome(options=options)

    submitted_count = 0
    target_info = f"{TOTAL_RESPONSES}" if TOTAL_RESPONSES is not None else "Unlimited (Press Ctrl+C to stop)"
    print(f"Starting Google Form automation...")
    print(f"Target submissions: {target_info}\n")

    try:
        resp_num = 1
        while TOTAL_RESPONSES is None or resp_num <= TOTAL_RESPONSES:
            driver.get(FORM_URL)
            fill_and_submit(driver, resp_num)
            submitted_count += 1

            # Random 1-2.5s jitter between submissions
            if TOTAL_RESPONSES is None or resp_num < TOTAL_RESPONSES:
                jitter = round(random.uniform(1.0, 2.5), 1)
                print(f"Waiting {jitter}s before next entry... (Ctrl+C to stop)")
                time.sleep(jitter)

            resp_num += 1

        print("\n" + "*" * 55)
        print(f"COMPLETED! Total submitted: {submitted_count} responses.")
        print("*" * 55)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 55)
        print(f"PAUSED / STOPPED by user (Ctrl+C).")
        print(f"Successfully submitted: {submitted_count} responses.")
        print("=" * 55)

    except Exception as e:
        print(f"\n[ERROR] Automation stopped: {e}")
        print(f"Total successfully submitted before error: {submitted_count}")

    finally:
        time.sleep(1)
        print("Closing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
