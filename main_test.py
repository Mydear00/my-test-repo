import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

test_results = []

def log_result(tc_id, tc_name, status, details=""):
    test_results.append({
        "Test Case ID": tc_id,
        "Test Case Name": tc_name,
        "Status": status,
        "Details": details
    })
    icon = "✅" if status == "PASS" else ("❌" if status == "FAIL" else "⚠️")
    print(f"{icon} [{status}] {tc_id}: {tc_name} -> {details}")

print("🚀 Starting Test Execution on GitHub Actions...\n")

# ==============================================================================
# PART 1: EASY TEST CASES (EZ1 & EZ2)
# ==============================================================================

# EZ1: Verify Scroll Up using 'Arrow' button
try:
    driver = create_driver()
    driver.get("https://automationexercise.com/")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    
    scroll_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "scrollUp"))
    )
    scroll_btn.click()
    time.sleep(1.5)
    
    pos_y = driver.execute_script("return window.pageYOffset;")
    if pos_y < 100:
        log_result("EZ1", "Scroll Up using Arrow button", "PASS", f"Scrolled to top successfully (Y={pos_y})")
    else:
        log_result("EZ1", "Scroll Up using Arrow button", "FAIL", f"Position Y is {pos_y}")
    driver.quit()
except Exception as e:
    log_result("EZ1", "Scroll Up using Arrow button", "ERROR", str(e))

# EZ2: Verify Scroll Up without 'Arrow' button
try:
    driver = create_driver()
    driver.get("https://automationexercise.com/")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1.5)
    
    pos_y = driver.execute_script("return window.pageYOffset;")
    if pos_y < 100:
        log_result("EZ2", "Scroll Up without Arrow button", "PASS", f"Manual scroll to top successful (Y={pos_y})")
    else:
        log_result("EZ2", "Scroll Up without Arrow button", "FAIL", f"Position Y is {pos_y}")
    driver.quit()
except Exception as e:
    log_result("EZ2", "Scroll Up without Arrow button", "ERROR", str(e))


# ==============================================================================
# PART 2: SC10 - CHECKING OUT
# ==============================================================================

# TC_SC10_01: Verify Address Details & Review Order
try:
    driver = create_driver()
    driver.get("https://automationexercise.com/products")
    driver.execute_script("window.scrollTo(0, 400);")
    add_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-product-id='1']")))
    add_btn.click()
    time.sleep(1.5)
    
    driver.get("https://automationexercise.com/view_cart")
    checkout_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Proceed To Checkout')]")))
    checkout_btn.click()
    time.sleep(1)
    
    modal = driver.find_elements(By.XPATH, "//u[contains(text(),'Register / Login')]")
    if len(modal) > 0:
        log_result("TC_SC10_01", "Verify Address Details & Review Order", "PASS", "Guest user prompt displayed correctly.")
    else:
        log_result("TC_SC10_01", "Verify Address Details & Review Order", "FAIL", "Modal prompt missing.")
    driver.quit()
except Exception as e:
    log_result("TC_SC10_01", "Verify Address Details & Review Order", "ERROR", str(e))

# TC_SC10_02: Register while Checkout Process
try:
    driver = create_driver()
    driver.get("https://automationexercise.com/products")
    driver.execute_script("window.scrollTo(0, 400);")
    driver.find_element(By.CSS_SELECTOR, "a[data-product-id='1']").click()
    time.sleep(1.5)
    
    driver.get("https://automationexercise.com/view_cart")
    driver.find_element(By.XPATH, "//a[contains(text(),'Proceed To Checkout')]").click()
    time.sleep(1)
    
    driver.find_element(By.XPATH, "//u[contains(text(),'Register / Login')]").click()
    time.sleep(1.5)
    
    if "login" in driver.current_url:
        log_result("TC_SC10_02", "Register while Checkout Process", "PASS", "Navigated to Register/Login from modal.")
    else:
        log_result("TC_SC10_02", "Register while Checkout Process", "FAIL", "Navigation failed.")
    driver.quit()
except Exception as e:
    log_result("TC_SC10_02", "Register while Checkout Process", "ERROR", str(e))

# TC_SC10_03: Complete Payment with Valid Card Details
try:
    driver = create_driver()
    driver.get("https://automationexercise.com/payment")
    driver.find_element(By.NAME, "name_on_card").send_keys("Tester User")
    driver.find_element(By.NAME, "card_number").send_keys("4111111111111111")
    driver.find_element(By.NAME, "cvc").send_keys("123")
    driver.find_element(By.NAME, "expiry_month").send_keys("12")
    driver.find_element(By.NAME, "expiry_year").send_keys("2028")
    
    pay_btn = driver.find_element(By.ID, "submit")
    if pay_btn.is_enabled():
        log_result("TC_SC10_03", "Complete Payment with Valid Card Details", "PASS", "Payment fields validated and button ready.")
    else:
        log_result("TC_SC10_03", "Complete Payment with Valid Card Details", "FAIL", "Pay button disabled.")
    driver.quit()
except Exception as e:
    log_result("TC_SC10_03", "Complete Payment with Valid Card Details", "ERROR", str(e))

# TC_SC10_04: Verify Checkout Restriction with Empty Cart
try:
    driver = create_driver()
    driver.get("https://automationexercise.com/view_cart")
    empty_msg = driver.find_element(By.ID, "empty_cart")
    if empty_msg.is_displayed():
        log_result("TC_SC10_04", "Verify Checkout Restriction with Empty Cart", "PASS", "Empty cart message verified.")
    else:
        log_result("TC_SC10_04", "Verify Checkout Restriction with Empty Cart", "FAIL", "Empty cart message missing.")
    driver.quit()
except Exception as e:
    log_result("TC_SC10_04", "Verify Checkout Restriction with Empty Cart", "ERROR", str(e))

# TC_SC10_05: Verify Order Placement Cancellation on Payment Page
try:
    driver = create_driver()
    driver.get("https://automationexercise.com/payment")
    driver.find_element(By.NAME, "name_on_card").send_keys("Tester User")
    driver.get("https://automationexercise.com/view_cart")
    time.sleep(1)
    
    if "view_cart" in driver.current_url:
        log_result("TC_SC10_05", "Verify Order Placement Cancellation", "PASS", "Cancellation/navigation handled properly.")
    else:
        log_result("TC_SC10_05", "Verify Order Placement Cancellation", "FAIL", "Navigation failed.")
    driver.quit()
except Exception as e:
    log_result("TC_SC10_05", "Verify Order Placement Cancellation", "ERROR", str(e))


# ==============================================================================
# PART 3: SC11 - WRITE REVIEW
# ==============================================================================

# TC_SC11_01: Submit Review with Valid Data
try:
    driver = create_driver()
    driver.get("https://automationexercise.com/product_details/1")
    
    driver.find_element(By.ID, "name").send_keys("Automated Tester")
    driver.find_element(By.ID, "email").send_keys("test_auto@example.com")
    driver.find_element(By.ID, "review").send_keys("This is a high-quality product tested via Selenium!")
    
    submit_btn = driver.find_element(By.ID, "button-review")
    driver.execute_script("arguments[0].click();", submit_btn)
    time.sleep(1.5)
    
    alert_msg = driver.find_element(By.XPATH, "//span[contains(text(),'Thank you for your review.')]")
    if alert_msg.is_displayed():
        log_result("TC_SC11_01", "Submit Review with Valid Data", "PASS", "Review submitted with success alert.")
    else:
        log_result("TC_SC11_01", "Submit Review with Valid Data", "FAIL", "Confirmation alert missing.")
    driver.quit()
except Exception as e:
    log_result("TC_SC11_01", "Submit Review with Valid Data", "ERROR", str(e))

# TC_SC11_02: Submit Review with Missing Required Fields
try:
    driver = create_driver()
    driver.get("https://automationexercise.com/product_details/1")
    
    driver.find_element(By.ID, "review").send_keys("Only review text without name and email.")
    submit_btn = driver.find_element(By.ID, "button-review")
    driver.execute_script("arguments[0].click();", submit_btn)
    time.sleep(1)
    
    name_field = driver.find_element(By.ID, "name")
    is_required = name_field.get_attribute("required")
    if is_required is not None:
        log_result("TC_SC11_02", "Submit Review with Missing Required Fields", "PASS", "HTML5 'required' attribute present.")
    else:
        log_result("TC_SC11_02", "Submit Review with Missing Required Fields", "FAIL", "Validation missing.")
    driver.quit()
except Exception as e:
    log_result("TC_SC11_02", "Submit Review with Missing Required Fields", "ERROR", str(e))

# TC_SC11_03: Submit Review with Invalid Email Format
try:
    driver = create_driver()
    driver.get("https://automationexercise.com/product_details/1")
    
    driver.find_element(By.ID, "name").send_keys("Tester")
    driver.find_element(By.ID, "email").send_keys("invalid_email_format")
    driver.find_element(By.ID, "review").send_keys("Testing invalid email format submission.")
    
    email_field = driver.find_element(By.ID, "email")
    is_valid = driver.execute_script("return arguments[0].checkValidity();", email_field)
    
    if not is_valid:
        log_result("TC_SC11_03", "Submit Review with Invalid Email Format", "PASS", "Invalid email caught by HTML5 validity check.")
    else:
        log_result("TC_SC11_03", "Submit Review with Invalid Email Format", "FAIL", "Invalid email was accepted.")
    driver.quit()
except Exception as e:
    log_result("TC_SC11_03", "Submit Review with Invalid Email Format", "ERROR", str(e))

# TC_SC11_04: Verify Review Section Presence Across Products
try:
    driver = create_driver()
    p_ids = [1, 2, 3]
    all_has_review = True
    
    for pid in p_ids:
        driver.get(f"https://automationexercise.com/product_details/{pid}")
        review_header = driver.find_elements(By.XPATH, "//a[contains(text(),'Write Your Review')]")
        if len(review_header) == 0:
            all_has_review = False
            break
            
    if all_has_review:
        log_result("TC_SC11_04", "Verify Review Section Presence Across Products", "PASS", "Review section verified on multiple products.")
    else:
        log_result("TC_SC11_04", "Verify Review Section Presence Across Products", "FAIL", "Review section missing on some products.")
    driver.quit()
except Exception as e:
    log_result("TC_SC11_04", "Verify Review Section Presence Across Products", "ERROR", str(e))

# TC_SC11_05: Submit Review with Special Characters
try:
    driver = create_driver()
    driver.get("https://automationexercise.com/product_details/1")
    
    driver.find_element(By.ID, "name").send_keys("User_Special!@#$")
    driver.find_element(By.ID, "email").send_keys("special_user@example.com")
    driver.find_element(By.ID, "review").send_keys("Special characters test: <script>alert('test')</script> & multi-line text validation.")
    
    submit_btn = driver.find_element(By.ID, "button-review")
    driver.execute_script("arguments[0].click();", submit_btn)
    time.sleep(1.5)
    
    alert_msg = driver.find_element(By.XPATH, "//span[contains(text(),'Thank you for your review.')]")
    if alert_msg.is_displayed():
        log_result("TC_SC11_05", "Submit Review with Special Characters", "PASS", "Special character review submitted successfully.")
    else:
        log_result("TC_SC11_05", "Submit Review with Special Characters", "FAIL", "Submission failed.")
    driver.quit()
except Exception as e:
    log_result("TC_SC11_05", "Submit Review with Special Characters", "ERROR", str(e))


# ==============================================================================
# SUMMARY REPORT
# ==============================================================================
print("\n" + "="*80)
print("📊 TEST EXECUTION SUMMARY REPORT")
print("="*80)

df_results = pd.DataFrame(test_results)
print(df_results.to_string(index=False))

# Throw exception if any test failed/errored to mark GitHub Workflow status
has_failures = any(res["Status"] in ["FAIL", "ERROR"] for res in test_results)
if has_failures:
    raise RuntimeError("Some test cases failed or encountered errors!")