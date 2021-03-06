from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
import time
import easygui as g
import pandas as pd
import pymysql
import getpass

DATABASE = {
            'host':"192.168.2.97",
            'database':"bi_system",
            'user':"lepython",
            'password':"qaz123456",
            'port':3306,
            'charset':'utf8'
}


#USER_DATA_DIR= r'C:\Users\yaoxuzhao\AppData\Local\Google\Chrome\User Data'
USER_DATA_DIR = r'C:\Users\%s\AppData\Local\Google\Chrome\User Data'%(getpass.getuser())

class AmazonBase():
    """
    amazon 商家后台基类 包括获取登录信息和网址
    打开chrome浏览器
    登录商家后台账号
    切换语言显示
    关闭浏览器
    """

    def __init__(self,zone,database,user_data_dir):
        self.zone = zone
        self.user_data_dir = user_data_dir
        if isinstance(database,dict):
            self.conn = pymysql.connect(**database)
        else:
            raise TypeError
    # 获取登录信息 url username password
    def get_login_info(self):

        sqlcmd = "select username as un, AES_DECRYPT(password_encrypt,'andy') as pw, login_url as url" \
                 " from core_amazon_account a where department = '技术部' and platform = '" + self.zone + "'"
        a = pd.read_sql(sqlcmd, self.conn)
        if (len(a) > 0):
            username = a["un"][0]
            password = str(a["pw"][0], encoding="utf-8")
            url = a["url"][0]
            return (url, username, password)
        else:
            return ('','','')

    def login(self,driver, username, password):
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
            driver.find_element_by_id("ap_email").send_keys(username)
            driver.implicitly_wait(10)
            driver.find_element_by_id("ap_password").send_keys(password)
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

    def close_sql(self):
        self.conn.close()

if __name__=='__main__':
    reply = g.choicebox(msg="请选择你要登录的站点，默认为选择第一个站点！！！", title="选择登录站点", choices=['DE','US','JP','CA'])
    amazon=AmazonBase(reply,DATABASE,USER_DATA_DIR)
    url,username,password = amazon.get_login_info()
    driver = amazon.open_chrome()
    driver.get(url)
    amazon.login(driver,username,password)
    #amazon.switch_language(driver,'English')
    time.sleep(300)
    #amazon.close_brower(driver)
    #amazon.close_sql()