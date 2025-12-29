import unittest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class CalculatorUITests(unittest.TestCase):

    def setUp(self):
        """Настройка браузера перед каждым тестом."""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        self.driver.get("https://x-calculator.ru/")

        self.wait = WebDriverWait(self.driver, 10)
        # Ждем загрузки экрана калькулятора
        self.wait.until(EC.presence_of_element_located((By.ID, "input")))

    def tearDown(self):
        self.driver.quit()

    # Вспомогательные методы

    def click_btn_by_text(self, text):
        """Нажимает кнопку цифр"""
        xpath = f"//div[contains(@class, 'round_btn') and normalize-space(text())='{text}']"
        self._safe_click(xpath)

    def click_btn_by_id(self, elem_id):
        """Нажимает функциональную кнопку по ID"""
        self._safe_click(f"//*[@id='{elem_id}']")

    def _safe_click(self, xpath):
        """Универсальный клик: скролл, ожидание, JS-клик при неудаче."""
        try:
            elem = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
            WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            elem.click()
        except:
            elem = self.driver.find_element(By.XPATH, xpath)
            self.driver.execute_script("arguments[0].click();", elem)
        time.sleep(0.2)

    def get_display_value(self):
        """Возвращает значение с экрана без пробелов."""
        display = self.driver.find_element(By.ID, "input")
        val = display.get_attribute("value")
        return val.replace(" ", "")

    def input_number(self, number_str):
        """Вводит длинное число посимвольно."""
        for digit in number_str:
            self.click_btn_by_text(digit)

    # ТЕСТЫ

    def test_01_all_digits_input(self):
        """1. Проверка ввода всех цифр (0-9)."""
        print("\nЗапуск теста: Ввод всех цифр")
        digits = "1234567890"
        self.input_number(digits)

        self.assertEqual(self.get_display_value(), digits, "Не все цифры корректно вводятся")

    def test_02_negative_numbers(self):
        """2. Операции с отрицательными числами."""
        print("\nЗапуск теста: Отрицательные числа")

        # 10 - 25 = -15
        self.input_number("10")
        self.click_btn_by_id("symbolMinus")
        self.input_number("25")
        self.click_btn_by_id("symbolEqual")

        self.assertEqual(self.get_display_value(), "-15", "Ошибка при вычитании в минус")

        self.click_btn_by_id("symbolClear")

        # 0 - 5 * 3 = -15
        self.click_btn_by_text("0")
        self.click_btn_by_id("symbolMinus")
        self.click_btn_by_text("5")
        self.click_btn_by_id("symbolMultiply")
        self.click_btn_by_text("3")
        self.click_btn_by_id("symbolEqual")

        self.assertEqual(self.get_display_value(), "-15", "Ошибка умножения отрицательного числа")

    def test_03_advanced_functions(self):
        """3. Корень, Факториал, Процент, Степень."""
        print("\nЗапуск теста: Сложные функции (√, !, %, ^)")

        # √16 = 4
        self.click_btn_by_id("symbolRoot")
        self.input_number("16")
        self.click_btn_by_id("symbolEqual")
        self.assertEqual(self.get_display_value(), "4", "Ошибка вычисления корня")

        self.click_btn_by_id("symbolClear")

        # 5! = 120
        self.input_number("5")
        self.click_btn_by_id("symbolExclamation")
        self.click_btn_by_id("symbolEqual")
        self.assertEqual(self.get_display_value(), "120", "Ошибка факториала")

        self.click_btn_by_id("symbolClear")

        # 200 * 50% = 100
        self.input_number("200")
        self.click_btn_by_id("symbolMultiply")
        self.input_number("50")
        self.click_btn_by_id("symbolPercent")
        self.click_btn_by_id("symbolEqual")
        self.assertEqual(self.get_display_value(), "100", "Ошибка процентов")

        self.click_btn_by_id("symbolClear")

        # 2^3 = 8
        self.input_number("2")
        self.click_btn_by_id("symbolExponent")

        # Обработка всплывающей клавиатуры степеней
        #exponent_keyboard = self.wait.until(EC.visibility_of_element_located((By.ID, "keyboardExponent")))

        # Находим цифру 3 (класс btnKeyboardExponent)
        exp_btn_xpath = "//div[contains(@class, 'btnKeyboardExponent') and normalize-space(text())='3']"

        self._safe_click(exp_btn_xpath)
        self.click_btn_by_id("buttonOK")
        self.click_btn_by_id("symbolEqual")
        self.assertEqual(self.get_display_value(), "8", "Ошибка возведения в степень")

if __name__ == "__main__":
    unittest.main(verbosity=2)