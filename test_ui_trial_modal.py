"""
自动化测试：验证 trial-courses 页面“录入新学员”模态框是否能正常弹出。

前置条件：
- 本地已启动 Flask 应用，地址 http://localhost:5000
- 若开启了登录保护，默认账户：用户名 17844540733，密码 yuan971035088

运行方式：
  pip install selenium webdriver-manager
  python test_ui_trial_modal.py
"""

from __future__ import annotations

import sys
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/login"
TRIAL_URL = f"{BASE_URL}/trial-courses"

DEFAULT_USERNAME = "17844540733"
DEFAULT_PASSWORD = "yuan971035088"


def create_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    # 无头模式可选：取消注释即可
    # options.add_argument("--headless=new")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  # 降噪

    # 1) 优先尝试使用本地 chromedriver，避免联网下载
    import os
    candidate_paths = [
        os.path.join(os.getcwd(), "chromedriver.exe"),
        os.path.join(os.getcwd(), "drivers", "chromedriver.exe"),
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            service = ChromeService(executable_path=path)
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_window_size(1400, 1000)
            return driver

    # 2) 找不到本地驱动时，退回 webdriver-manager（需要外网）
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1400, 1000)
    return driver


def ensure_logged_in(driver: webdriver.Chrome) -> None:
    """如果页面需要登录，则执行登录流程。"""
    driver.get(TRIAL_URL)
    time.sleep(0.5)
    current_url = driver.current_url
    if "/login" in current_url:
        # 执行登录
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        username_input.clear()
        username_input.send_keys(DEFAULT_USERNAME)
        password_input.clear()
        password_input.send_keys(DEFAULT_PASSWORD)
        # 提交表单
        password_input.submit()
        # 等待跳转
        WebDriverWait(driver, 10).until(lambda d: "/login" not in d.current_url)
        # 再次进入目标页
        driver.get(TRIAL_URL)


def click_and_assert_modal(driver: webdriver.Chrome) -> None:
    """点击按钮并断言模态框显示。"""
    # 等待按钮出现
    add_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "addTrialBtn"))
    )

    # 点击前先滚动到视图
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
    time.sleep(0.2)
    add_btn.click()

    # 等待模态框 display != 'none'
    def modal_is_visible(d) -> bool:
        try:
            modal = d.find_element(By.ID, "addTrialModal")
            display = d.execute_script(
                "return window.getComputedStyle(arguments[0]).display;", modal
            )
            return display != "none"
        except NoSuchElementException:
            return False

    try:
        WebDriverWait(driver, 5).until(modal_is_visible)
    except TimeoutException as exc:
        # 采集更多诊断信息
        try:
            modal = driver.find_element(By.ID, "addTrialModal")
            z_index = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).zIndex;", modal
            )
            display = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).display;", modal
            )
            print(f"[诊断] modal z-index={z_index}, display={display}")
        except Exception as e:  # noqa: BLE001
            print(f"[诊断] 获取 modal 样式失败: {e}")
        raise TimeoutException("点击后 5s 内未检测到模态框显示") from exc


def main() -> int:
    driver: Optional[webdriver.Chrome] = None
    try:
        driver = create_driver()
        ensure_logged_in(driver)
        click_and_assert_modal(driver)
        print("✅ 测试通过：点击‘录入新学员’后，模态框成功显示。")
        return 0
    except Exception as e:  # noqa: BLE001
        print("❌ 测试失败：", e)
        return 1
    finally:
        if driver is not None:
            driver.quit()


if __name__ == "__main__":
    sys.exit(main())


