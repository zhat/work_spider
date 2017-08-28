# coding = utf-8
import os
import sys
import time
import datetime
import pandas as pd
import pymysql
from lxml import etree
from selenium import webdriver  # selenium 需要自己安装此模块
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
import logging
from selenium.webdriver.chrome.options import Options
from .AutoUpdateData import AutoUpdateData
import argparse

"""
    模拟登录下载订单管理页面数据
"""

current_path = os.path.abspath('.')

marketplaceid_dict = {
	  'co.uk':'A1F83G8C2ARO7P'
	, 'de':'A1PA6795UKMFR9'
	, 'es':'A1RKKUPIHCS9HS'
	, 'fr':'A13V1IB3VIYZZH'
	, 'it':'APJ6JRA9NG5V4'
	, 'Non-Amazon CO.UK':'AZMDEXL2RVFNN'
	, 'Non-Amazon DE':'A38D8NSA03LJTC'
	, 'Non-Amazon ES':'AFQLKURYRPEL8'
	, 'Non-Amazon FR':'A1ZFFQZ3HTUKT9'
	, 'Non-Amazon IT':'A62U237T8HV6N'
}

merchantId_dict = {
    'de':'AV7KSH7XB8RNM'
}

zone_date_format_dict = {
    'US': '%m/%d/%y',
    'DE': '%d/%m/%Y',
    'JP': '%m/%d/%y',
    'CA': '%m/%d/%y',
}

# for example
# /merchant-picker/change-merchant?url=%2F&marketplaceId=A1F83G8C2ARO7P&merchantId=AV7KSH7XB8RNM
# '/merchant-picker/change-merchant?url=%2F&marketplaceId=' + marketplaceid_dict[zone] + '&merchantId=' +  merchantId_dict[zone]


# change key and value
amzid_marketplace_dict = {value:key for key,value in marketplaceid_dict.items()}

# url = 'https://sellercentral.amazon.es/gp/homepage.html?'

class AmazonOrderManagerCrawlFromAsin_():
    def __init__(self, zone, asin, start_date, end_date, crawl_days):

        self.zone = zone
        self.zone_lower_case = zone.lower()
        self.zone_upper_case = zone.upper()

        self.now_sub_zone = ''

        self.asin = asin
        self.start_date = start_date
        self.end_date = end_date
        self.crawl_days = crawl_days

        self.now_date_str = ''

        self.dbconn = pymysql.connect(
            host="192.168.2.23",
            database="leamazon",
            user="ama_account",
            password="T89ZY#UQWS",
            port=3306,
            charset='utf8'
        )
        self.cur = self.dbconn.cursor()

    def getOrderInfo(self):
        # get username and password
        sqlcmd = "select username as un, AES_DECRYPT(password_encrypt,'andy') as pw, login_url as url from core_amazon_account a where department = '技术部' and platform = '"+self.zone+"'"
        a = pd.read_sql(sqlcmd, self.dbconn)
        if (len(a) > 0):
            username = a["un"][0]
            password = str(a["pw"][0], encoding="utf-8")
            url = a["url"][0]
        else:
            sys.exit(0)

        chrome_options = Options()
        chrome_options.add_experimental_option('prefs', {
            'credentials_enable_service': False,
            'profile': {
                'password_manager_enabled': False
            }
        })
        chrome_options.add_argument(
            '--user-data-dir=' + r'C:\Users\yaoxuzhao\AppData\Local\Google\Chrome\User Data')
        # driver = webdriver.Chrome(current_path + os.path.sep + 'drive' + os.path.sep + 'chromedriver.exe')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        try:
            # open driver and get url
            driver.set_page_load_timeout(200)

            driver.get(url)
            time.sleep(5)

            if driver.find_elements_by_xpath("//*[@id='gw-lefty']"):
                pass
            else:
                driver.refresh()
                time.sleep(5)

                driver.find_element_by_id("ap_email").clear()
                time.sleep(2)
                driver.find_element_by_id("ap_email").send_keys(username)
                time.sleep(2)
                driver.find_element_by_id("ap_password").send_keys(password)
                time.sleep(2)
                driver.find_element_by_id("signInSubmit").click()
                time.sleep(4)

                # login in complete
                WebDriverWait(driver, 120).until(
                    lambda driver: driver.execute_script("return document.readyState") == 'complete')
                time.sleep(2)
            driver.maximize_window()
            driver.refresh()
            time.sleep(5)
            # sub_zone_url = '/merchant-picker/change-merchant?url=%2F&marketplaceId=' + marketplaceid_dict[self.zone.lower()] + '&merchantId=' +  merchantId_dict[self.zone.lower()]
            sub_zone_url = ''
            sub_zone = ''

            if self.asin != '':
                end = datetime.datetime.strptime(self.end_date, '%Y-%m-%d')
                start = datetime.datetime.strptime(self.start_date, '%Y-%m-%d')
                days = self.crawl_days
                delta = datetime.timedelta(days=days)
                temp_start = start
                temp_end = temp_start - delta
                while temp_start >= end :
                    if temp_end < end:
                        temp_end = end
                    order_date_str = temp_end.strftime('%Y-%m-%d') + ' ' + temp_start.strftime('%Y-%m-%d')

                    startDate = self.handle_abnormal_date_format(temp_start.strftime(zone_date_format_dict[self.zone_upper_case]))
                    endDate = self.handle_abnormal_date_format(temp_end.strftime(zone_date_format_dict[self.zone_upper_case]))

                    self.crawlByExactDateAndZone(driver, startDate, endDate, sub_zone_url, sub_zone, order_date_str)
                    # '2017-06-15 2017-06-22'
                    # '2017-06-07 2017-06-14'
                    temp_start = temp_end - datetime.timedelta(days=1)
                    temp_end = temp_start - delta

        except Exception as e:
            print(e)
        finally:
            self.deleteAll(driver)

    def handle_abnormal_date_format(self, date_str):
        if self.zone_upper_case in ['US', 'CA', 'JP']:
            dt = datetime.datetime.strptime(date_str, zone_date_format_dict[self.zone_upper_case])
            dt_str = '{}/{}/{}'.format(dt.month, dt.day, dt.year % 1000)
            return dt_str
        elif self.zone_upper_case in ['DE']:
            return date_str

    def crawlByExactDateAndZone(self, driver, startDate, endDate, sub_zone_url, sub_zone, order_date_str):

        # chose english language
        try:
            selector = driver.find_element_by_id('sc-lang-switcher-header-select')
            Select(selector).select_by_visible_text("English")
            WebDriverWait(driver, 120).until(
                lambda driver: driver.execute_script("return document.readyState") == 'complete')
            time.sleep(2)
        except Exception as e:
            print(e)
            pass

        # click to 'Manage Orders' menu
        try:
            target_menu = 'Manage Orders'
            target_link = driver.find_elements_by_link_text(target_menu)
            if target_link:
                target_link[0].click()
                WebDriverWait(driver, 120).until(
                    lambda driver: driver.execute_script("return document.readyState") == 'complete')
                time.sleep(2)
            else:
                pass
        except Exception as e:
            print(e)
            pass

        # change the begin and end date
        try:
            exactDateBeginStr = startDate
            exactDateEndStr = endDate

            # driver.find_element_by_id('_myoSO_SearchOption_exactDates').click()
            _myoLO_SearchTypeSelect = driver.find_element_by_id('_myoLO_SearchTypeSelect')
            Select(_myoLO_SearchTypeSelect).select_by_value('ASIN')

            driver.find_element_by_id("searchKeyword").clear()
            driver.find_element_by_id("searchKeyword").send_keys(self.asin)


            _myoLO_preSelectedRangeSelect = driver.find_element_by_id('_myoLO_preSelectedRangeSelect')
            Select(_myoLO_preSelectedRangeSelect).select_by_value('exactDates')

            # 如果上面的Advanced Search部分有使用的话，这里才会需要，通过JS来修改日历控件中的日期
            js = "document.getElementById(\'exactDateBegin\').removeAttribute('readonly');document.getElementById(\'exactDateBegin\').setAttribute('value','" + exactDateEndStr + "');"
            driver.execute_script(js)
            js = "document.getElementById(\'exactDateEnd\').removeAttribute('readonly');document.getElementById(\'exactDateEnd\').setAttribute('value','" + exactDateBeginStr + "');"
            driver.execute_script(js)

            driver.find_element_by_id('SearchID').click()

            # handle system error
            self.systemErrorHandle(driver, 5)
            self.waitForLoadData(driver, 5)

            time.sleep(15)

            WebDriverWait(driver, 120).until(
                lambda driver: driver.execute_script("return document.readyState") == 'complete')

            # handle searching error
            content = driver.page_source
            tree = etree.HTML(content)
            search_result = tree.xpath('//*[@id="_myoV2PageTopMessagePlaceholder"]//text()')
            style = tree.xpath('//*[@id="_myoV2PageTopMessagePlaceholder"]/@style')
            search_result_str = ''
            if search_result is not None and len(search_result) > 0:
                for str in search_result:
                    search_result_str += str
                print(search_result_str)

        except Exception as e:
            print(e)
            pass

        # change per page cnt to 100,as 100 is the max size
        try:
            driver.find_element_by_xpath("//select[@name='itemsPerPage']").send_keys(100)
            goList = driver.find_elements_by_xpath("//td/input[@type='image' and contains(@src,'go.')]")  # stop here
            if goList:
                goList[-1].click()  # use -1 index, because it's hard to chose the right 'go' input using xpath
                time.sleep(15)
                WebDriverWait(driver, 120).until(
                    lambda driver: driver.execute_script("return document.readyState") == 'complete')

                content = driver.page_source
                tree = etree.HTML(content)
                if (tree.xpath("//select[@name='itemsPerPage']/option[@selected]/@value")[0] != '100'):
                    times = 3
                    while times>0:
                        driver.find_element_by_xpath("//select[@name='itemsPerPage']").send_keys(100)
                        goList = driver.find_elements_by_xpath(
                            "//td/input[@type='image' and contains(@src,'go.')]")  # stop here
                        if goList:
                            goList[
                                -1].click()  # use -1 index, because it's hard to chose the right 'go' input using xpath
                            time.sleep(15)
                            WebDriverWait(driver, 120).until(
                                lambda driver: driver.execute_script("return document.readyState") == 'complete')

                        content = driver.page_source
                        tree = etree.HTML(content)
                        if (tree.xpath("//select[@name='itemsPerPage']/option[@selected]/@value")[0] == '100'):
                            break

                        times -= 1
            else:
                pass
        except Exception as e:
            print(e)
            pass

        # parse driver.page_source in cycs
        try:
            self.parsePageInfo(driver, sub_zone, startDate, order_date_str)
        except Exception as e:
            print(e)

    def parsePageInfo(self, driver, sub_zone, startDate, order_date_str):
        content = driver.page_source
        tree = etree.HTML(content)

        try:
            if order_date_str != self.now_date_str:
                dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                now_order_cnt_str = tree.xpath(
                    '//*[@id="myo-table"]/table/tbody/tr[1]/td/table/tbody/tr/td[1]/strong[2]/text()')
                now_order_cnt = int(now_order_cnt_str[0])

                total_cnt_del_query = "delete from amazon_asin_total_orders_source_"+self.zone_lower_case+" where zone = '%s' and asin = '%s' and order_date = '%s'" % (
                self.zone, self.asin, order_date_str)
                self.cur.execute(total_cnt_del_query)

                total_cnt_query = "insert into amazon_asin_total_orders_source_"+self.zone_lower_case+"(zone, asin, order_date, total_cnt, create_date) values(%s, %s, %s, %s, %s)"
                self.cur.execute(total_cnt_query, (self.zone, self.asin, order_date_str, now_order_cnt, dt))
                self.dbconn.commit()
                self.now_date_str = order_date_str
            else:
                pass
        except Exception as e:
            print(e)


        orders = tree.xpath("//tr[contains(@id,'row-')]")

        for order in orders:
            order_id = order.xpath("./@id")[0].replace('row-', '')

            cust_id = ''
            if order.xpath("./td/input[@class='cust-id']/@value"):
                cust_id = order.xpath("./td/input[@class='cust-id']/@value")[0]

            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


            latestShipDate_str = ''
            if order.xpath("./td/input[@class='latestShipDate']/@value"):
                latestShipDate_str = order.xpath("./td/input[@class='latestShipDate']/@value")[0]
            x = time.localtime(int(latestShipDate_str))
            latestShipDate = time.strftime('%Y-%m-%d %H:%M:%S', x)

            sqli = "insert into amazon_asin_manager_orders_"+self.zone_lower_case+"(asin, order_id, cust_id, zone, order_date, create_date) values(%s, %s, %s, %s, %s, %s)"
            self.cur.execute(sqli, (self.asin, order_id, cust_id, self.zone, order_date_str, dt))
            self.dbconn.commit()

        try:
            next_link = driver.find_element_by_xpath(
                "//*[@id='myo-table']//a[@class='myo_list_orders_link' and contains(text(),'Next')]")  #
            if next_link:
                next_link.click()
                WebDriverWait(driver, 120).until(
                    lambda driver: driver.execute_script("return document.readyState") == 'complete')
                time.sleep(15)

                self.waitForLoadData(driver, 5)

                self.parsePageInfo(driver, sub_zone, startDate, order_date_str)

            else:
                # self.deleteAll(driver)
                return
        except Exception as e:
            print(e)

    def waitForLoadData(self, driver, waitSeconds):
        try:
            content = driver.page_source
            tree = etree.HTML(content)
            _myoLO_pleaseWaitExtendedMessage = tree.xpath('//*[@id="_myoLO_pleaseWaitExtendedMessage"]//text()')
            style = tree.xpath('//*[@id="_myoLO_pleaseWaitExtendedMessage"]/@style')
            _myoLO_pleaseWaitExtendedMessage_str = ''
            if _myoLO_pleaseWaitExtendedMessage is not None and len(_myoLO_pleaseWaitExtendedMessage) > 0:
                for str in _myoLO_pleaseWaitExtendedMessage:
                    _myoLO_pleaseWaitExtendedMessage_str += str
                print(_myoLO_pleaseWaitExtendedMessage_str)

            if 'We apologize for the delay' in _myoLO_pleaseWaitExtendedMessage_str and (
                                style is None or len(style) == 0 or 'display' not in style[0]):
                time.sleep(waitSeconds)
        except Exception as e:
            print(e)

    def systemErrorHandle(self, driver, waitSeconds):
        try:
            content = driver.page_source
            tree = etree.HTML(content)
            _myoLO_pleaseWaitExtendedMessage = tree.xpath('//*[@id="_myoV2_AjaxGenericSysErrorMessagePlaceholder"]//text()')
            style = tree.xpath('//*[@id="_myoV2_AjaxGenericSysErrorMessagePlaceholder"]/@style')
            _myoLO_pleaseWaitExtendedMessage_str = ''
            if _myoLO_pleaseWaitExtendedMessage is not None and len(_myoLO_pleaseWaitExtendedMessage) > 0:
                for str in _myoLO_pleaseWaitExtendedMessage:
                    _myoLO_pleaseWaitExtendedMessage_str += str
                print(_myoLO_pleaseWaitExtendedMessage_str)

            if style is None or len(style) == 0 or 'display' not in style[0]:
                # time.sleep(waitSeconds)
                sys.exit(0)
        except Exception as e:
            print(e)

    def deleteAll(self, driver):
        try:
            self.cur.close()
            self.dbconn.close()
            driver.quit()
            sys.exit(0)
        except Exception as e:
            print(e)

if __name__=='__main__':
    asin = 'B0196JNQYC'
    zone = 'DE'
    zone_lower_case = zone.lower()

    amzCrawl = AmazonOrderManagerCrawlFromAsin_(zone, asin, '2017-08-02', '2017-01-01', 90) # 每次启动跑16天的数据，截至到当天往前推62天


    amzCrawl.getOrderInfo()

    executor = AutoUpdateData()
    executor._update_data_by_asin(zone_lower_case)
    executor._exit()
