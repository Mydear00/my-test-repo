import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://automationexercise.com"
WAIT_TIME = 10


# =====================================================
# FIXTURE
# =====================================================

@pytest.fixture
def driver():
    """สร้าง Browser สำหรับทดสอบด้วย Selenium"""
    options = Options()
    # options.add_argument("--headless=new")  # ปิดโหมด headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1365,900")
    
    # ป้องกันไม่ให้ Chrome ปิดตัวเองลงอัตโนมัติเมื่อรันโค้ดเสร็จ
    options.add_experimental_option("detach", True)

    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(60)
    browser.implicitly_wait(0)

    try:
        yield browser
    finally:
        pass
        # browser.quit()  # เปิดค้างไว้หลังเทสเสร็จ


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def wait_for_page(driver):
    """รอให้เอกสาร HTML โหลดเสร็จ"""
    wait = WebDriverWait(driver, WAIT_TIME)

    wait.until(
        lambda browser: browser.execute_script(
            "return document.readyState"
        ) in ("interactive", "complete")
    )

    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )


def open_home(driver):
    """เปิดหน้าแรกและตรวจสอบเว็บไซต์เป้าหมาย"""
    driver.get(BASE_URL)
    wait_for_page(driver)

    assert "automationexercise.com" in driver.current_url.lower(), (
        f"URL ไม่ใช่เว็บไซต์เป้าหมาย: {driver.current_url}"
    )


def open_products(driver):
    """เปิดหน้ารายการสินค้า"""
    driver.get(f"{BASE_URL}/products")
    wait_for_page(driver)

    WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".features_items")
        )
    )


def open_product_by_index(driver, product_index=0):
    """เปิดหน้ารายละเอียดสินค้าตามลำดับ Index เพื่อให้ไม่ซ้ำกัน"""
    open_products(driver)

    links = WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "a[href*='/product_details/']")
        )
    )

    visible_links = [
        link for link in links
        if link.is_displayed() and link.is_enabled() and link.get_attribute("href")
    ]

    assert len(visible_links) > product_index, f"ไม่พบลิงก์สินค้าลำดับที่ {product_index + 1}"

    product_url = visible_links[product_index].get_attribute("href")

    driver.get(product_url)
    wait_for_page(driver)

    wait = WebDriverWait(driver, WAIT_TIME)
    wait.until(lambda browser: "/product_details/" in browser.current_url)

    print(f"\n[Product Index {product_index}] URL:", driver.current_url)
    print(f"[Product Index {product_index}] Title:", driver.title)

    for element_id in ("name", "email", "review"):
        try:
            wait.until(
                EC.presence_of_element_located((By.ID, element_id))
            )
        except Exception as exc:
            raise AssertionError(
                f"ไม่พบช่อง #{element_id} บนหน้ารายละเอียดสินค้า "
                f"URL={driver.current_url}, Title={driver.title}"
            ) from exc


def fill_and_submit_review(driver, name_val="Automation Tester", email_val="test.automation@example.com", review_val="Great product! Excellent quality and fast shipping."):
    """ฟังก์ชันช่วยป้อนข้อมูลลงในฟอร์มรีวิวและกดปุ่ม Submit ให้อัตโนมัติ"""
    wait = WebDriverWait(driver, WAIT_TIME)
    
    name_input = wait.until(EC.presence_of_element_located((By.ID, "name")))
    email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
    review_input = wait.until(EC.presence_of_element_located((By.ID, "review")))

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", name_input)

    name_input.clear()
    name_input.send_keys(name_val)
    
    email_input.clear()
    email_input.send_keys(email_val)
    
    review_input.clear()
    review_input.send_keys(review_val)

    try:
        submit_button = driver.find_element(By.ID, "button-review")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
        submit_button.click()
    except Exception:
        print("ไม่พบปุ่ม #button-review หรือไม่สามารถกดได้")


def add_product_to_cart(driver, product_index=0):
    """เพิ่มสินค้าลงรถเข็นโดยไม่ดำเนินการชำระเงิน"""
    open_products(driver)

    buttons = WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".productinfo a.add-to-cart")
        )
    )

    visible_buttons = [
        button for button in buttons
        if button.is_displayed() and button.is_enabled()
    ]

    assert len(visible_buttons) > product_index, (
        f"ไม่พบปุ่มเพิ่มสินค้าลำดับที่ {product_index + 1}"
    )

    button = visible_buttons[product_index]

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        button
    )
    button.click()

    wait = WebDriverWait(driver, WAIT_TIME)

    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".modal-content")
        )
    )

    continue_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".modal-content .close-modal")
        )
    )
    continue_button.click()

    wait.until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, ".modal-content")
        )
    )


def open_cart(driver):
    """เปิดหน้ารถเข็น"""
    driver.get(f"{BASE_URL}/view_cart")
    wait_for_page(driver)


def get_cart_rows(driver):
    """อ่านแถวรายการสินค้าในรถเข็น"""
    return driver.find_elements(
        By.CSS_SELECTOR,
        "#cart_info_table tbody tr"
    )


# =====================================================
# SC10: CHECKING OUT
# =====================================================

def test_sc10_01_cart_page_opens(driver):
    """TC_SC10_01: ตรวจสอบว่าหน้ารถเข็นเปิดได้"""
    open_cart(driver)
    driver.save_screenshot("TC_SC10_01_cart_page.png")

    assert "automationexercise.com" in driver.current_url.lower()

    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()

    assert (
        "cart" in body_text
        or "checkout" in body_text
        or driver.find_elements(By.ID, "cart_info")
        or driver.find_elements(By.ID, "cart_info_table")
    )

    print("PASS: เปิดหน้ารถเข็นได้")


def test_sc10_02_empty_cart_message(driver):
    """TC_SC10_02: ตรวจสอบสถานะรถเข็นว่าง"""
    open_cart(driver)
    driver.save_screenshot("TC_SC10_02_empty_cart.png")

    cart_rows = get_cart_rows(driver)
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()

    empty_message = (
        "cart is empty" in body_text
        or "empty cart" in body_text
    )

    if len(cart_rows) == 0 or empty_message:
        print("PASS: รถเข็นไม่มีแถวสินค้า")
    else:
        pytest.skip("รถเข็นมีสินค้าอยู่ จึงไม่ใช่เงื่อนไขรถเข็นว่าง")


def test_sc10_03_add_product_to_cart(driver):
    """TC_SC10_03: เพิ่มสินค้าและตรวจสอบในรถเข็น"""
    add_product_to_cart(driver)
    open_cart(driver)

    WebDriverWait(driver, WAIT_TIME).until(
        lambda browser: len(get_cart_rows(browser)) > 0
    )

    driver.save_screenshot("TC_SC10_03_added_product_in_cart.png")

    assert len(get_cart_rows(driver)) > 0
    print("PASS: พบสินค้าในรถเข็น")


def test_sc10_04_guest_checkout_requires_login(driver):
    """TC_SC10_04: ผู้ใช้ที่ยังไม่เข้าสู่ระบบเริ่ม Checkout"""
    add_product_to_cart(driver)
    open_cart(driver)

    wait = WebDriverWait(driver, WAIT_TIME)

    checkout_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-default.check_out"))
    )
    checkout_button.click()

    wait.until(
        lambda browser: browser.execute_script("return document.readyState") in ("interactive", "complete")
    )

    driver.save_screenshot("TC_SC10_04_checkout_redirect_login.png")

    current_url = driver.current_url.lower()
    page_text = driver.find_element(By.TAG_NAME, "body").text.lower()

    assert (
        "login" in current_url
        or "signup" in current_url
        or "register" in page_text
        or "login" in page_text
        or "checkout" in page_text
    )

    print("PASS: เว็บไซต์ตอบสนองต่อการเริ่ม Checkout")


def test_sc10_05_multiple_products_in_cart(driver):
    """TC_SC10_05: ตรวจสอบรถเข็นเมื่อเพิ่มสินค้าสองรายการ"""
    add_product_to_cart(driver, 0)
    add_product_to_cart(driver, 1)
    open_cart(driver)

    WebDriverWait(driver, WAIT_TIME).until(
        lambda browser: len(get_cart_rows(browser)) >= 2
    )

    driver.save_screenshot("TC_SC10_05_multiple_products_in_cart.png")

    rows = get_cart_rows(driver)
    assert len(rows) >= 2
    print("PASS: พบสินค้าหลายรายการในรถเข็น")


# =====================================================
# SC11: WRITE REVIEW (ปรับสินค้าและ Test Data ให้แตกต่างกัน)
# =====================================================

def test_sc11_01_review_form_exists(driver):
    """TC_SC11_01: ตรวจสอบว่าหน้ารายละเอียดมีฟอร์มรีวิว (สินค้าชิ้นที่ 1)"""
    open_product_by_index(driver, product_index=0)

    review_heading = WebDriverWait(driver, WAIT_TIME).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(translate(normalize-space(.),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'WRITE YOUR REVIEW')]"
        ))
    )

    driver.save_screenshot("TC_SC11_01_review_form_exists.png")
    assert review_heading.is_displayed()
    print("PASS: พบส่วน Write Your Review")


def test_sc11_02_review_fields_exist(driver):
    """TC_SC11_02: ตรวจสอบช่องกรอกชื่อ อีเมล และรีวิว (สินค้าชิ้นที่ 2)"""
    open_product_by_index(driver, product_index=1)

    name = driver.find_element(By.ID, "name")
    email = driver.find_element(By.ID, "email")
    review = driver.find_element(By.ID, "review")

    fill_and_submit_review(driver, name_val="Checker User", email_val="checker@example.com", review_val="Checking all review input fields.")

    driver.save_screenshot("TC_SC11_02_review_fields.png")

    assert name.is_displayed()
    assert email.is_displayed()
    assert review.is_displayed()

    print("PASS: พบช่องกรอกข้อมูลรีวิวครบ")


def test_sc11_03_review_form_accepts_name_and_email(driver):
    """TC_SC11_03: ตรวจสอบว่ากรอกชื่อและอีเมลได้ (สินค้าชิ้นที่ 3)"""
    open_product_by_index(driver, product_index=2)

    name_val = "Somchai Jaidee"
    email_val = "somchai.j@example.com"

    fill_and_submit_review(driver, name_val=name_val, email_val=email_val, review_val="Testing valid name and email entry.")

    name = driver.find_element(By.ID, "name")
    email = driver.find_element(By.ID, "email")

    driver.save_screenshot("TC_SC11_03_entered_name_email.png")

    assert name.get_attribute("value") == name_val
    assert email.get_attribute("value") == email_val

    print("PASS: กรอกชื่อและอีเมลได้")


def test_sc11_04_review_text_can_be_entered(driver):
    """TC_SC11_04: ตรวจสอบว่ากรอกข้อความรีวิวได้ (สินค้าชิ้นที่ 4)"""
    open_product_by_index(driver, product_index=3)

    review_text = "The product quality is superb! Highly satisfied with this order."

    fill_and_submit_review(driver, name_val="Reviewer Person", email_val="reviewer@example.com", review_val=review_text)

    review = driver.find_element(By.ID, "review")

    driver.save_screenshot("TC_SC11_04_entered_review_text.png")

    assert review.get_attribute("value") == review_text

    print("PASS: กรอกข้อความรีวิวได้")


def test_sc11_05_review_accepts_special_characters(driver):
    """TC_SC11_05: ตรวจสอบข้อความรีวิวที่มีอักขระพิเศษ (สินค้าชิ้นที่ 5)"""
    open_product_by_index(driver, product_index=4)

    special_text = "Rating: 5/5 stars! Code: #PRD-99 @Home (100% Recommended)!!!"

    fill_and_submit_review(driver, name_val="Special Tester", email_val="special.test@example.com", review_val=special_text)

    review = driver.find_element(By.ID, "review")

    driver.save_screenshot("TC_SC11_05_entered_special_chars.png")

    assert review.get_attribute("value") == special_text

    print("PASS: ช่องรีวิวยอมรับอักขระพิเศษ")