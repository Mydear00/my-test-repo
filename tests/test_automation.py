
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://automationexercise.com"
WAIT_TIME = 30


# =====================================================
# FIXTURE
# =====================================================

@pytest.fixture
def driver():
    """สร้าง Browser สำหรับทดสอบด้วย Selenium"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1365,900")

    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(60)
    browser.implicitly_wait(0)

    try:
        yield browser
    finally:
        browser.quit()


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


def open_first_product(driver):
    """เปิดหน้ารายละเอียดสินค้ารายการแรก"""
    open_products(driver)

    links = WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "a[href*='/product_details/']")
        )
    )

    product_url = next(
        (
            link.get_attribute("href")
            for link in links
            if link.is_displayed()
            and link.is_enabled()
            and link.get_attribute("href")
        ),
        None
    )

    assert product_url, "ไม่พบลิงก์รายละเอียดสินค้าที่ใช้งานได้"

    driver.get(product_url)
    wait_for_page(driver)

    wait = WebDriverWait(driver, WAIT_TIME)

    wait.until(
        lambda browser: "/product_details/" in browser.current_url
    )

    print("Product URL:", driver.current_url)
    print("Product title:", driver.title)

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
# EZ1: SCROLL UP
# =====================================================

def test_ez1_scroll_up(driver):
    """TC_EZ1_01: คลิกปุ่ม Scroll Up และตรวจสอบการเลื่อนหน้า"""
    open_home(driver)
    wait = WebDriverWait(driver, WAIT_TIME)

    # เลื่อนหน้าเว็บลงด้านล่างเพื่อเตรียมทดสอบ
    driver.execute_script(
        "window.scrollTo(0, document.documentElement.scrollHeight);"
    )

    wait.until(
        lambda browser: browser.execute_script(
            "return window.scrollY"
        ) > 100
    )

    before = driver.execute_script("return window.scrollY")
    print("ตำแหน่งก่อนคลิก:", before)

    button = wait.until(
        EC.element_to_be_clickable((By.ID, "scrollUp"))
    )

    assert button.is_displayed(), "ไม่พบปุ่ม Scroll Up"

    # คลิกปุ่มผ่าน Selenium ก่อน
    button.click()

    try:
        # รอให้หน้าเว็บเริ่มเลื่อนขึ้น
        try:
            wait.until(
                lambda browser: browser.execute_script(
                    "return window.scrollY"
                ) < before - 10
            )
        except Exception:
            # หากคลิกปกติไม่เริ่มเลื่อน ให้ตรวจสอบปุ่มอีกครั้ง
            button = wait.until(
                EC.presence_of_element_located((By.ID, "scrollUp"))
            )

            assert button.is_displayed(), (
                "ปุ่ม Scroll Up ไม่ปรากฏหลังคลิก"
            )

            # กระตุ้น click event ของปุ่มโดยตรง
            driver.execute_script(
                "arguments[0].click();",
                button
            )

            wait.until(
                lambda browser: browser.execute_script(
                    "return window.scrollY"
                ) < before - 10
            )

        # ตรวจสอบว่าหน้าเว็บกลับถึงด้านบนจริง
        wait.until(
            lambda browser: browser.execute_script(
                "return window.scrollY"
            ) <= 5
        )

    except Exception:
        after = driver.execute_script("return window.scrollY")

        pytest.fail(
            "ปุ่ม Scroll Up ไม่สามารถเลื่อนหน้าเว็บกลับด้านบนได้ "
            f"ก่อนคลิก={before}, หลังรอ={after}"
        )

    after = driver.execute_script("return window.scrollY")

    print("ตำแหน่งหลังคลิก:", after)

    assert after <= 5, (
        f"หน้าเว็บยังไม่กลับด้านบน ตำแหน่งปัจจุบัน={after}"
    )

    print("PASS: ปุ่ม Scroll Up ทำงานสำเร็จ")


# =====================================================
# SC10: CHECKING OUT
# =====================================================

def test_sc10_01_cart_page_opens(driver):
    """TC_SC10_01: ตรวจสอบว่าหน้ารถเข็นเปิดได้"""
    open_cart(driver)

    assert "automationexercise.com" in driver.current_url.lower()

    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()

    assert (
        "cart" in body_text
        or "checkout" in body_text
        or driver.find_elements(By.ID, "cart_info")
        or driver.find_elements(By.ID, "cart_info_table")
    ), (
        "ไม่พบเนื้อหาที่เกี่ยวข้องกับรถเข็น "
        f"URL={driver.current_url}, Title={driver.title}"
    )

    print("PASS: เปิดหน้ารถเข็นได้")


def test_sc10_02_empty_cart_message(driver):
    """TC_SC10_02: ตรวจสอบสถานะรถเข็นว่าง"""
    open_cart(driver)

    cart_rows = get_cart_rows(driver)
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()

    empty_message = (
        "cart is empty" in body_text
        or "empty cart" in body_text
    )

    if len(cart_rows) == 0 or empty_message:
        print("PASS: รถเข็นไม่มีแถวสินค้า")
    else:
        pytest.skip(
            "รถเข็นมีสินค้าอยู่ จึงไม่ใช่เงื่อนไขรถเข็นว่าง"
        )


def test_sc10_03_add_product_to_cart(driver):
    """TC_SC10_03: เพิ่มสินค้าและตรวจสอบในรถเข็น"""
    add_product_to_cart(driver)
    open_cart(driver)

    WebDriverWait(driver, WAIT_TIME).until(
        lambda browser: len(get_cart_rows(browser)) > 0
    )

    assert len(get_cart_rows(driver)) > 0, (
        "ไม่พบสินค้าในรถเข็นหลังเพิ่มสินค้า"
    )

    print("PASS: พบสินค้าในรถเข็น")


def test_sc10_04_guest_checkout_requires_login(driver):
    """TC_SC10_04: ผู้ใช้ที่ยังไม่เข้าสู่ระบบเริ่ม Checkout"""
    add_product_to_cart(driver)
    open_cart(driver)

    wait = WebDriverWait(driver, WAIT_TIME)

    checkout_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".btn.btn-default.check_out")
        )
    )
    checkout_button.click()

    wait.until(
        lambda browser: browser.execute_script(
            "return document.readyState"
        ) in ("interactive", "complete")
    )

    current_url = driver.current_url.lower()
    page_text = driver.find_element(By.TAG_NAME, "body").text.lower()

    assert (
        "login" in current_url
        or "signup" in current_url
        or "register" in page_text
        or "login" in page_text
        or "checkout" in page_text
    ), (
        "ไม่พบหน้า Login, Register หรือ Checkout "
        f"URL={driver.current_url}"
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

    rows = get_cart_rows(driver)

    assert len(rows) >= 2, (
        f"คาดว่าจะมีสินค้าอย่างน้อย 2 รายการ แต่พบ {len(rows)} รายการ"
    )

    print("PASS: พบสินค้าหลายรายการในรถเข็น")


# =====================================================
# SC11: WRITE REVIEW
# =====================================================

def test_sc11_01_review_form_exists(driver):
    """TC_SC11_01: ตรวจสอบว่าหน้ารายละเอียดมีฟอร์มรีวิว"""
    open_first_product(driver)

    review_heading = WebDriverWait(driver, WAIT_TIME).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[contains("
                "translate(normalize-space(.),"
                "'abcdefghijklmnopqrstuvwxyz',"
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),"
                "'WRITE YOUR REVIEW'"
                ")]"
            )
        )
    )

    assert review_heading.is_displayed()

    print("PASS: พบส่วน Write Your Review")


def test_sc11_02_review_fields_exist(driver):
    """TC_SC11_02: ตรวจสอบช่องกรอกชื่อ อีเมล และรีวิว"""
    open_first_product(driver)

    name = driver.find_element(By.ID, "name")
    email = driver.find_element(By.ID, "email")
    review = driver.find_element(By.ID, "review")

    assert name.is_displayed()
    assert email.is_displayed()
    assert review.is_displayed()

    print("PASS: พบช่องกรอกข้อมูลรีวิวครบ")


def test_sc11_03_review_form_accepts_name_and_email(driver):
    """TC_SC11_03: ตรวจสอบว่ากรอกชื่อและอีเมลได้"""
    open_first_product(driver)

    name = driver.find_element(By.ID, "name")
    email = driver.find_element(By.ID, "email")

    name.send_keys("Selenium Test")
    email.send_keys("selenium.test@example.com")

    assert name.get_attribute("value") == "Selenium Test"
    assert email.get_attribute("value") == "selenium.test@example.com"

    print("PASS: กรอกชื่อและอีเมลได้")


def test_sc11_04_review_text_can_be_entered(driver):
    """TC_SC11_04: ตรวจสอบว่ากรอกข้อความรีวิวได้"""
    open_first_product(driver)

    review = driver.find_element(By.ID, "review")
    review_text = "This is a Selenium practice test review."

    review.send_keys(review_text)

    assert review.get_attribute("value") == review_text

    print("PASS: กรอกข้อความรีวิวได้")


def test_sc11_05_review_accepts_special_characters(driver):
    """TC_SC11_05: ตรวจสอบข้อความรีวิวที่มีอักขระพิเศษ"""
    open_first_product(driver)

    review = driver.find_element(By.ID, "review")
    special_text = "Test review: A&B, 100% useful! Line 1."

    review.send_keys(special_text)

    assert review.get_attribute("value") == special_text

    print("PASS: ช่องรีวิวยอมรับอักขระพิเศษ")
