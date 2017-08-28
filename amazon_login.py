from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
import time
import pandas as pd
import pymysql
from config import DATABASE,USER_DATA_DIR

class AmazonLogin():
    def __init__(self,url,username,password,user_data_dir=""):
        self.url = url
        self.username = username
        self.password = password
        self.user_data_dir = user_data_dir

    def open_browser(self):

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

    def close(self,driver):
        driver.close()

    def login(self):
        driver = self.open_browser()
        driver.get(self.url)
        WebDriverWait(driver, 120).until(
            lambda driver: driver.execute_script("return document.readyState") == 'complete')
        if driver.find_elements_by_xpath("//*[@id='gw-lefty']"):
            return driver
        if driver.find_elements_by_xpath("//*[@id='merchant-picker-auth-status']"):
            try:
                driver.find_elements_by_xpath(
                    "//*[@id='merchant-picker-auth-status']//input[@name='not_authorized_sso_action' and @value='DIFFERENT_USER']")[0].click()
                driver.find_elements_by_xpath("//*[@id='merchant-link-btn-continue']/span/input")[0].click()
            except Exception as e:
                    pass
        driver.implicitly_wait(10)
        driver.find_element_by_id("ap_email").clear()
        driver.implicitly_wait(10)
        driver.find_element_by_id("ap_email").send_keys(self.username)
        driver.implicitly_wait(10)
        driver.find_element_by_id("ap_password").send_keys(self.password)
        driver.implicitly_wait(10)
        driver.find_element_by_id("signInSubmit").click()
        driver.implicitly_wait(10)

        # login in complete
        WebDriverWait(driver, 120).until(
            lambda driver: driver.execute_script("return document.readyState") == 'complete')
        selector = driver.find_element_by_id('sc-lang-switcher-header-select')
        Select(selector).select_by_visible_text("English")
        WebDriverWait(driver, 120).until(
            lambda driver: driver.execute_script("return document.readyState") == 'complete')

        return driver

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

class GetInfoFromSQL():
    def __init__(self, zone):
        self.zone = zone
        self.dbconn = pymysql.connect(**DATABASE)

    def get_login_info(self):
        sqlcmd = "select username as un, AES_DECRYPT(password_encrypt,'andy') as pw, login_url as url from core_amazon_account a where department = '技术部' and platform = '" + self.zone + "'"
        a = pd.read_sql(sqlcmd, self.dbconn)
        if (len(a) > 0):
            username = a["un"][0]
            password = str(a["pw"][0], encoding="utf-8")
            url = a["url"][0]
            return (url, username, password)

if __name__=='__main__':
    sql_info=GetInfoFromSQL('DE')
    url,username,password = sql_info.get_login_info()
    amazon = AmazonLogin(url,username,password,USER_DATA_DIR)
    amazon.login()
    time.sleep(120)