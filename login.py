from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
import time

class LoginBase():
    """
    amazon 商家后台基类 包括获取登录信息和网址
    打开chrome浏览器
    登录商家后台账号
    切换语言显示
    关闭浏览器
    """

    def __init__(self,url,username,password,user_data_dir=""):
        self.url = url
        self.username = username
        self.password = password
        self.user_data_dir = user_data_dir

    def login(self,driver):
        driver.get(self.url)
        WebDriverWait(driver, 120).until(
            lambda driver: driver.execute_script("return document.readyState") == 'complete')
        if driver.find_elements_by_xpath("//*[@id='gw-lefty']"):
            return True
        try:
            if driver.find_elements_by_xpath("//*[@id='merchant-picker-auth-status']"):
                driver.find_elements_by_xpath(
                    "//*[@id='merchant-picker-auth-status']//input[@name='not_authorized_sso_action' and @value='DIFFERENT_USER']")[
                    0].click()
                driver.find_elements_by_xpath("//*[@id='merchant-link-btn-continue']/span/input")[0].click()
            driver.implicitly_wait(10)
            driver.find_element_by_id("ap_email").clear()
            driver.implicitly_wait(10)
            driver.find_element_by_id("ap_email").send_keys(self.username)
            driver.implicitly_wait(10)
            driver.find_element_by_id("ap_password").send_keys(self.password)
            driver.implicitly_wait(10)
            driver.find_element_by_id("signInSubmit").click()
            driver.implicitly_wait(10)
            WebDriverWait(driver, 120).until(
                lambda driver: driver.execute_script("return document.readyState") == 'complete')
            return True
        except Exception as e:
            print(e)
            return False

    def open_chrome(self):
        """打开浏览器"""
        chrome_options = Options()
        chrome_options.add_experimental_option('prefs', {
            'credentials_enable_service': False,
            'profile': {
                'password_manager_enabled': False
            }
        })
        chrome_options.add_argument(
            '--user-data-dir=' + self.user_data_dir)
        return webdriver.Chrome(chrome_options=chrome_options)
    #切换显示语言
    def switch_language(self,driver,language="English"):
        try:
            selector = driver.find_element_by_id('sc-lang-switcher-header-select')
            Select(selector).select_by_visible_text(language)
            WebDriverWait(driver, 120).until(
                lambda driver: driver.execute_script("return document.readyState") == 'complete')
            return True
        except Exception as e:
            print(e)
            return False

    def close_brower(self):
        driver.close()

if __name__=='__main__':
    amazon=LoginBase('DE','','','')
    driver = amazon.open_chrome()
    amazon.login(driver)
    amazon.switch_language(driver,'English')
    time.sleep(60)
    amazon.close_brower(driver)