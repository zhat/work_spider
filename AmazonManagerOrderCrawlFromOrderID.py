# coding = utf-8
from datetime import datetime,timedelta
import pandas as pd
import pymysql
from selenium import webdriver  # selenium 需要自己安装此模块
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urljoin,urlparse,urlunparse
from selenium.webdriver.chrome.options import Options

DATABASE = {
            'host':"192.168.2.97",
            'database':"bi_system",
            'user':"lepython",
            'password':"qaz123456",
            'port':3306,
            'charset':'utf8'
}

USER_DATA_DIR= r'C:\Users\yaoxuzhao\AppData\Local\Google\Chrome\User Data'


"""
    模拟登录下载订单管理页面数据
"""

# for example
# /merchant-picker/change-merchant?url=%2F&marketplaceId=A1F83G8C2ARO7P&merchantId=AV7KSH7XB8RNM
# '/merchant-picker/change-merchant?url=%2F&marketplaceId=' + marketplaceid_dict[zone] + '&merchantId=' +  merchantId_dict[zone]
# change key and value
# url = 'https://sellercentral.amazon.es/gp/homepage.html?'

class AmazonOrderManagerCrawlFromOrderId():
    def __init__(self, zone,last_day_str, crawl_number=100):

        self.zone = zone
        self.start_time = datetime.now()
        self.crawl_number = crawl_number
        self.not_find_profile_num = 0
        self.last_day_str = last_day_str
        self.dbconn = pymysql.connect(**DATABASE)
        self.url, self.username, self.password = self.get_login_info()
        self.short_url = urlunparse(urlparse(self.url)[0:2] + ('',) * 4)
    # 打开浏览器
    def get_login_info(self):
        sqlcmd = "select username as un, AES_DECRYPT(password_encrypt,'andy') as pw, login_url as url from core_amazon_account a where department = '技术部' and platform = '" + self.zone + "'"
        a = pd.read_sql(sqlcmd, self.dbconn)
        if (len(a) > 0):
            username = a["un"][0]
            password = str(a["pw"][0], encoding="utf-8")
            url = a["url"][0]
            return (url,username,password)

    def open_browser(self):

        chrome_options = Options()
        chrome_options.add_experimental_option('prefs', {
            'credentials_enable_service': False,
            'profile': {
                'password_manager_enabled': False
            }
        })
        chrome_options.add_argument(
            '--user-data-dir=' + USER_DATA_DIR)
        return webdriver.Chrome(chrome_options=chrome_options)
    #登录亚马逊后台
    def login(self,driver):
        try:
            if driver.find_elements_by_xpath("//*[@id='merchant-picker-auth-status']"):
                try:
                    driver.find_elements_by_xpath(
                        "//*[@id='merchant-picker-auth-status']//input[@name='not_authorized_sso_action' and @value='DIFFERENT_USER']")[
                        0].click()
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

            return True
        except Exception as e:
            print(e)
            return False

    def get_order_id_list(self):
        cur = self.dbconn.cursor()
        sqlcmd = r'SELECT order_id FROM order_orderdata WHERE zone="%s" and `profile` is null  and `status`!="Canceled" and order_time<"%s" limit %d,%d;'%(self.zone,self.last_day_str,self.not_find_profile_num, self.crawl_number)
        cur.execute(sqlcmd)
        order_id_list = cur.fetchall()
        cur.close()
        order_id_list = [x for j in order_id_list for x in j]
        return order_id_list

    def getOrderInfo(self,order_id_list):

        driver = self.open_browser()
        sqlcmds = []
        try:
            # open driver and get url
            #driver.set_page_load_timeout(200)

            driver.get(self.url)
            driver.implicitly_wait(30)

            if not driver.find_elements_by_xpath("//*[@id='gw-lefty']"):
                self.login(driver)
            driver.maximize_window()

            #driver.refresh()
            #driver.implicitly_wait(10)

            # sub_zone_url = '/merchant-picker/change-merchant?url=%2F&marketplaceId=' + marketplaceid_dict[self.zone.lower()] + '&merchantId=' +  merchantId_dict[self.zone.lower()]
            order_number=1
            for order_id in order_id_list:
                profile=self.parseProfileInfo(driver,order_id)
                if profile:
                    sqlcmd = 'update `order_orderdata` set `profile`="%s" where `order_id`="%s";' % (profile, order_id)
                    sqlcmds.append(sqlcmd)
                    print("%03d:%s找到profile"%(order_number,order_id))
                else:
                    print("%03d:%s未找到profile" % (order_number, order_id))
                    self.not_find_profile_num+=1
                order_number+=1
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())
            cur = self.dbconn.cursor()
            try:
                for sqlcmd in sqlcmds:
                    cur.execute(sqlcmd)
                print(datetime.now())
                self.dbconn.commit()
            except:
                pass
            finally:
                cur.close()
            print(datetime.now())
            self.deleteAll(driver)

    def parseProfileInfo(self,driver,order_id):
        sub_order_id_url = "hz/orders/details?_encoding=UTF8&orderId=%s" % order_id
        order_url = urljoin(self.short_url,sub_order_id_url)
        driver.get(order_url)
        driver.implicitly_wait(3)
        try:
            if not driver.find_elements_by_id('myo-set-merchant-order-id-labelText'):
                self.login(driver)
                driver.get(order_url)
                driver.implicitly_wait(3)
            profile = driver.find_element_by_id('buyerId').get_attribute('value')
            return profile
        except Exception as e:
            print(e)
            print('未找到profile')
            return ''

    def deleteAll(self, driver):
        try:
            driver.quit()
        except Exception as e:
            print(e)

def get_profile(zone,days):
    now_time = datetime.now()
    last_day = now_time - timedelta(days=days)
    last_day_str = last_day.strftime('%Y-%m-%d')
    amzCrawl = AmazonOrderManagerCrawlFromOrderId(zone, last_day_str, 200)
    while True:
        try:
            order_id_list=amzCrawl.get_order_id_list()
            if order_id_list:
                amzCrawl.getOrderInfo(order_id_list)
            else:
                break
        except Exception as e:
            print(e)
if __name__=='__main__':
    print(datetime.now())
    get_profile('DE',8)