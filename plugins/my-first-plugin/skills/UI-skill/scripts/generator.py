#!/usr/bin/env python3
"""
UI Framework 代码生成器
根据 SKILL.md 规范生成 Python + Playwright + PO 框架
"""
import os
import sys
from pathlib import Path

# 基础目录
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent.parent
OUTPUT_DIR = BASE_DIR.parent / "pw_po_framework"

# 目录结构
DIRS = [
    "base",
    "pages",
    "testcases",
    "config",
    "utils",
    "logs",
    "reports",
]

# 代码模板
TEMPLATES = {
    "base/__init__.py": '',
    "base/base_page.py": '''from playwright.sync_api import Page


class BasePage:
    """页面对象基类"""

    def __init__(self, page: Page):
        self.page = page

    def goto(self, url: str):
        """打开URL"""
        self.page.goto(url)

    def click(self, locator: str):
        """点击元素"""
        self.page.locator(locator).click()

    def fill(self, locator: str, value: str):
        """填写输入框"""
        self.page.locator(locator).fill(value)

    def get_text(self, locator: str) -> str:
        """获取文本内容"""
        return self.page.locator(locator).text_content()

    def wait_for_selector(self, locator: str, timeout: int = 30000):
        """等待元素出现"""
        self.page.wait_for_selector(locator, timeout=timeout)

    def screenshot(self, path: str):
        """截图"""
        self.page.screenshot(path=path)
''',

    "base/browser.py": '''from playwright.sync_api import sync_playwright, Browser, Page


class Browser:
    """浏览器管理类"""

    def __init__(self, browser_type: str = "chromium", headless: bool = False):
        self.playwright = None
        self.browser = None
        self.browser_type = browser_type
        self.headless = headless

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = getattr(self.playwright, self.browser_type).launch(headless=self.headless)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def new_page(self) -> Page:
        """创建新页面"""
        context = self.browser.new_context()
        return context.new_page()
''',

    "pages/__init__.py": '',
    "pages/login_page.py": '''from base.base_page import BasePage


class LoginPage(BasePage):
    """登录页面"""

    # 元素定位器
    username_input = "input[name='username']"
    password_input = "input[name='password']"
    login_btn = "button[type='submit']"
    error_msg = ".error-message"

    def input_username(self, username: str):
        """输入用户名"""
        self.fill(self.username_input, username)

    def input_password(self, pwd: str):
        """输入密码"""
        self.fill(self.password_input, pwd)

    def click_login_btn(self):
        """点击登录按钮"""
        self.click(self.login_btn)

    def login(self, username: str, password: str):
        """登录流程"""
        self.input_username(username)
        self.input_password(password)
        self.click_login_btn()

    def get_error_message(self) -> str:
        """获取错误信息"""
        return self.get_text(self.error_msg)
''',

    "testcases/__init__.py": '',
    "testcases/conftest.py": '''import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def browser():
    """浏览器会话级 fixture"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """页面 fixture"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
''',

    "testcases/test_login.py": '''import pytest
from pages.login_page import LoginPage


def test_login_success(page):
    """登录成功用例"""
    login_page = LoginPage(page)
    login_page.goto("https://example.com/login")
    login_page.login("test_user", "123456")
    assert page.title() is not None


def test_login_failed(page):
    """登录失败用例"""
    login_page = LoginPage(page)
    login_page.goto("https://example.com/login")
    login_page.login("wrong_user", "wrong_pwd")
    assert login_page.get_error_message() is not None
''',

    "config/__init__.py": '',
    "config/config.py": '''import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 环境配置
ENV = os.getenv("ENV", "test")

# URL配置
URLS = {
    "dev": "https://dev.example.com",
    "test": "https://test.example.com",
    "prod": "https://prod.example.com",
}

# 浏览器配置
BROWSER_CONFIG = {
    "browser_type": "chromium",
    "headless": False,
    "viewport": {"width": 1920, "height": 1080},
}

# 超时配置
TIMEOUT = 30000

# 报告配置
REPORT_DIR = BASE_DIR / "reports"
LOG_DIR = BASE_DIR / "logs"
''',

    "utils/__init__.py": '',
    "utils/logger.py": '''import logging
import sys
from pathlib import Path


def setup_logger(name: str = "ui_framework", log_file: str = None):
    """日志配置"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()
''',

    "utils/path_util.py": '''from pathlib import Path
import os

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 各目录路径
BASE_DIR_PATH = BASE_DIR
PAGES_DIR = BASE_DIR / "pages"
TESTCASES_DIR = BASE_DIR / "testcases"
CONFIG_DIR = BASE_DIR / "config"
UTILS_DIR = BASE_DIR / "utils"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"


def ensure_dir(path: Path):
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)
    return path
''',

    "conftest.py": '''"""pytest全局配置"""
''',

    "pytest.ini": '''[pytest]
testpaths = testcases
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --alluredir=./reports/allure-results
''',

    "requirements.txt": '''playwright
pytest
pytest-html
allure-pytest
''',

    "run.py": '''#!/usr/bin/env python3
"""
UI Framework 运行入口
"""
import subprocess
import sys
from pathlib import Path


def run_tests():
    """运行测试"""
    subprocess.run([sys.executable, "-m", "pytest"])


def open_report():
    """打开测试报告"""
    report_path = Path(__file__).parent / "reports" / "html-report.html"
    if report_path.exists():
        subprocess.run(["open" if sys.platform == "darwin" else "start", str(report_path)])
    else:
        print("报告文件不存在，请先运行测试")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="UI Framework 运行工具")
    parser.add_argument("action", choices=["run", "report"], help="run: 运行测试, report: 打开报告")
    args = parser.parse_args()

    if args.action == "run":
        run_tests()
    elif args.action == "report":
        open_report()
''',

    "README.md": '''# Python Playwright PO Framework

## 目录结构

pw_po_framework/
├── base/                 # 底层基础封装
│   ├── base_page.py
│   └── browser.py
├── pages/                # PO页面对象层
│   └── login_page.py
├── testcases/            # 业务测试用例层
│   ├── conftest.py
│   └── test_login.py
├── config/               # 环境配置
│   └── config.py
├── utils/                # 工具类
│   ├── logger.py
│   └── path_util.py
├── logs/                 # 日志存放目录
├── reports/              # 测试报告存放目录
├── conftest.py           # pytest全局夹具
├── pytest.ini            # pytest配置文件
├── requirements.txt      # 依赖清单
└── run.py                # 一键运行入口

## 快速开始

1. 安装依赖:
   pip install -r requirements.txt
   playwright install

2. 运行测试:
   python run.py run

3. 查看报告:
   python run.py report
''',
}


def generate_framework():
    """生成框架"""
    print(f"Generating framework to: {OUTPUT_DIR}")

    # 创建目录
    for dir_name in DIRS:
        dir_path = OUTPUT_DIR / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Create dir: {dir_name}/")

    # 生成文件
    for file_path, content in TEMPLATES.items():
        full_path = OUTPUT_DIR / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        print(f"  Create file: {file_path}")

    print(f"\n[OK] Framework generated!")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"\nNext steps:")
    print(f"  cd {OUTPUT_DIR}")
    print(f"  pip install -r requirements.txt")
    print(f"  playwright install")
    print(f"  python run.py run")


if __name__ == "__main__":
    if OUTPUT_DIR.exists():
        response = input(f"Directory {OUTPUT_DIR} exists, overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled")
            sys.exit(0)

    generate_framework()