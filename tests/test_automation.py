
import pytest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@pytest.fixture
def driver():
    """สร้าง Browser สำหรับทดสอบด้วย Selenium"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1365,900")

    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(3)

    yield browser

    browser.quit()


def test_homepage_opens(driver):
    """TC_SETUP_01: ตรวจสอบว่าเปิดหน้าแรกได้"""
    driver.get("https://automationexercise.com/")

    wait = WebDriverWait(driver, 20)

    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert "Automation Exercise" in driver.title

    print("PASS: เปิดหน้าแรกสำเร็จ")
    print("Page title:", driver.title)


def test_ez1_scroll_up(driver):
    """TC_EZ1_01: ตรวจสอบปุ่มเลื่อนหน้าเว็บขึ้นด้านบน"""
    wait = WebDriverWait(driver, 20)

    driver.get("https://automationexercise.com/")

    # รอให้หน้าเว็บโหลด
    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # เลื่อนลงไปด้านล่างด้วย JavaScript
    driver.execute_script(
        "window.scrollTo(0, document.documentElement.scrollHeight);"
    )

    # รอให้หน้าเว็บเลื่อนลงจริง
    wait.until(
        lambda browser: browser.execute_script(
            "return window.scrollY"
        ) > 0
    )

    scroll_before = driver.execute_script(
        "return window.scrollY"
    )
    print("ตำแหน่งก่อนคลิก:", scroll_before)

    # รอให้ปุ่ม Scroll Up ปรากฏและคลิกได้
    button = wait.until(
        EC.element_to_be_clickable((By.ID, "scrollUp"))
    )

    # คลิกปุ่มบนหน้าเว็บจริง
    button.click()

    # รอจนหน้าเว็บเลื่อนกลับไปด้านบน
    try:
        wait.until(
            lambda browser: browser.execute_script(
                "return window.scrollY"
            ) <= 5
        )

    except TimeoutException:
        scroll_after = driver.execute_script(
            "return window.scrollY"
        )

        # บันทึกภาพหน้าจอเมื่อทดสอบไม่ผ่าน
        result_dir = Path("test-results")
        result_dir.mkdir(parents=True, exist_ok=True)

        driver.save_screenshot(
            str(result_dir / "ez1-scroll-up-failed.png")
        )

        pytest.fail(
            "ปุ่ม Scroll Up ไม่สามารถเลื่อนหน้าเว็บกลับด้านบนได้ "
            f"ตำแหน่งก่อนคลิก={scroll_before}, "
            f"ตำแหน่งหลังคลิก={scroll_after}. "
            "บันทึกภาพหน้าจอไว้ที่ "
            "test-results/ez1-scroll-up-failed.png"
        )

    # ตรวจสอบผลลัพธ์สุดท้าย
    scroll_after = driver.execute_script(
        "return window.scrollY"
    )

    print("ตำแหน่งหลังคลิก:", scroll_after)

    assert scroll_after <= 5, (
        f"หน้าเว็บยังไม่กลับด้านบน ตำแหน่ง={scroll_after}"
    )

    print("PASS: ปุ่ม Scroll Up ทำงานได้จริง")
