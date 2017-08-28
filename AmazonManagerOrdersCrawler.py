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
from AutoUpdateData import AutoUpdateData
import argparse

"""
    模拟登录下载订单管理页面数据
"""

current_path = os.path.abspath('.')

parser = argparse.ArgumentParser()
parser.add_argument('--zone', type=str, default="nothing", help='default value')
args = parser.parse_args()
zone = args.zone
zone_lower_case = zone.lower()
zone_upper_case = zone.upper()

logfilename = 'AmazonManagerOrdersCrawl{}.log'.format(zone_upper_case)

logging.basicConfig(level=logging.ERROR,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %Y-%m-%d  %H:%M:%S',
                filename= logfilename,
                filemode='w')

filename = 'AmazonManagerOrdersCrawl{}.py'.format(zone_upper_case)
_LOGGING = logging.getLogger(filename)

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

class AmazonOrderManagerCrawl():
    def __init__(self, zone, tryCnt, data_crawl_type, crawl_days):
        self.crawl_days = crawl_days
        self.data_crawl_type = data_crawl_type

        self.dbconn = pymysql.connect(
            host="192.168.2.23",
            database="leamazon",
            user="ama_account",
            password="T89ZY#UQWS",
            port=3306,
            charset='utf8'
        )
        self.cur = self.dbconn.cursor()
        self.zone = zone
        self.now_order_cnt = 0
        self.now_date_str = ''
        self.tryCnt = tryCnt
        self.crawlWrongDate = False
        self.now_sub_zone = ''
        self.need_to_crawl_date_list = []

    def handle_abnormal_date_format(self, date_str):
        if self.zone_upper_case in ['US', 'CA', 'JP']:
            dt = datetime.datetime.strptime(date_str, zone_date_format_dict[self.zone_upper_case])
            dt_str = '{}/{}/{}'.format(dt.month, dt.day, dt.year % 1000)
            return dt_str

    def need_to_crawl(self):
        try:
            today_str = datetime.date.today().strftime('%Y-%m-%d')
            sqlcmd = "select distinct substr(order_date,1,10) as order_date from amazon_report_manager_orders_%s a where zone = '%s' and substr(create_date,1,10) = '%s'" % (
                zone_lower_case, self.zone, today_str)
            order_date_max = pd.read_sql(sqlcmd, self.dbconn)

            order_date_list = order_date_max['order_date'].tolist()
            order_date_list_len = order_date_list.__len__()

            # 生成一个日期列表，包含从今天开始的crawl_days天数
            a = datetime.datetime.today()
            numdays = self.crawl_days
            dateList = []
            for x in range(0, numdays):
                dateList.append((a - datetime.timedelta(days=x)).strftime('%Y-%m-%d'))

            # 生成日期列表的差集，作为返回结果
            self.need_to_crawl_date_list = list(set(dateList) ^ set(order_date_list) & set(dateList) )
            self.need_to_crawl_date_list.sort()
            self.need_to_crawl_date_list.reverse()
            self.need_to_crawl_date_list = self.need_to_crawl_date_list[:self.tryCnt]
            print(self.need_to_crawl_date_list)
        except Exception as e:
            _LOGGING.error(e)

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
            "--user-data-dir=" + r'C:\Users\yaoxuzhao\AppData\Local\Google\Chrome\User Data')
        # driver = webdriver.Chrome(current_path + os.path.sep + 'drive' + os.path.sep + 'chromedriver.exe')
        return webdriver.Chrome(chrome_options=chrome_options)

    # 登录亚马逊后台
    def login(self, driver):
        try:

            # open driver and get url
            driver.set_page_load_timeout(200)

            driver.get(self.url)
            driver.implicitly_wait(10)
            driver.find_element_by_id("ap_email").clear()
            driver.implicitly_wait(5)
            driver.find_element_by_id("ap_email").send_keys(self.username)
            driver.implicitly_wait(5)
            driver.find_element_by_id("ap_password").send_keys(self.password)
            driver.implicitly_wait(5)
            driver.find_element_by_id("signInSubmit").click()
            # login in complete
            WebDriverWait(driver, 120).until(
                lambda driver: driver.execute_script("return document.readyState") == 'complete')
            selector = driver.find_element_by_id('sc-lang-switcher-header-select')
            Select(selector).select_by_visible_text("English")
            WebDriverWait(driver, 120).until(
                lambda driver: driver.execute_script("return document.readyState") == 'complete')
            driver.maximize_window()
            return True
        except Exception as e:
            _LOGGING(e)
            return False


            # sub_zone_url = '/merchant-picker/change-merchant?url=%2F&marketplaceId=' + marketplaceid_dict[self.zone.lower()] + '&merchantId=' +  merchantId_dict[self.zone.lower()]
            sub_zone_url = ''
            sub_zone = ''

            # if have wrong data, then recrawl them
            if self.crawlWrongDate:
                try:

                    insert_exists_date = "insert into amazon_report_total_orders_source_"+zone_lower_case+"(zone, order_date, total_cnt) " \
                                         "select '" + self.zone + "', order_date, total_cnt " \
                                                                  "  from amazon_report_order_manager_recrawl_"+zone_lower_case+" a " \
                                                                  " where not exists (select 1 from (select zone,order_date,sum(total_cnt) as total_cnt from amazon_report_total_orders_source_"+zone_lower_case+" group by 1,2 order by 1,2) b" \
                                                                  "  where a.zone = b.zone" \
                                                                  "    and a.order_date = b.order_date)"
                    self.cur.execute(insert_exists_date)
                    self.dbconn.commit()

                    clear_wrong_data = "delete from amazon_report_order_manager_recrawl_"+zone_lower_case+""
                    self.cur.execute(clear_wrong_data)
                    self.dbconn.commit()

                    create_recrawl_list = "insert into amazon_report_order_manager_recrawl_"+zone_lower_case+"(order_date, zone, cnt, total_cnt) " \
                                          "select a.order_date , a.zone , case when b.cnt is not null then a.total_cnt - b.cnt else a.total_cnt end as cnt, a.total_cnt" \
                                          "  from (select zone,order_date,sum(total_cnt) as total_cnt from amazon_report_total_orders_source_"+zone_lower_case+" group by 1,2 order by 1,2) a" \
                                          "  left join (select order_date,zone,count(distinct order_id) as cnt from amazon_report_manager_orders_"+zone_lower_case+" group by 1,2) b" \
                                          " on a.order_date = b.order_date " \
                                          "   and a.zone = b.zone" \
                                          "   where b.order_date is NULL or a.total_cnt <> b.cnt"
                    self.cur.execute(create_recrawl_list)
                    self.dbconn.commit()

                    delete_exists_data_1 = "delete from amazon_report_manager_orders_"+zone_lower_case+" " \
                                           " where order_date in (select distinct order_date from amazon_report_order_manager_recrawl_"+zone_lower_case+")" \
                                           "   and zone = '"+self.zone+"'"
                    self.cur.execute(delete_exists_data_1)
                    self.dbconn.commit()

                    delete_exists_data_2 = "delete from amazon_report_total_orders_source_"+zone_lower_case+" " \
                                           " where order_date in (select distinct order_date from amazon_report_order_manager_recrawl_"+zone_lower_case+")" \
                                           "   and zone = '"+self.zone+"'"
                    self.cur.execute(delete_exists_data_2)
                    self.dbconn.commit()

                    select_recrawl_list_query = "select distinct order_date from amazon_report_order_manager_recrawl_"+zone_lower_case+""
                    select_recrawl_list = pd.read_sql(select_recrawl_list_query, self.dbconn)

                    date_list = select_recrawl_list['order_date'].tolist()
                    date_list_len = date_list.__len__()
                    while date_list_len > 0:

                        startDate = self.handle_abnormal_date_format(date_list[date_list_len - 1].to_pydatetime().date().strftime(zone_date_format_dict[zone_upper_case]))
                        endDate = startDate

                        order_date_str = date_list[date_list_len-1].to_pydatetime().date().strftime('%Y-%m-%d %H:%M:%S')
                        self.crawlByExactDateAndZone(driver, startDate, endDate, sub_zone_url, sub_zone, order_date_str)

                        date_list_len -= 1
                except Exception as e:
                    _LOGGING.error(e)

            # crawl data day by day
            if self.data_crawl_type == 'CL':  # 存量数据抓取
                try:
                    sqlcmd = "select min(order_date) as order_date from amazon_report_manager_orders_"+zone_lower_case+" a where zone = '" + self.zone + "'"
                    order_date_max = pd.read_sql(sqlcmd, self.dbconn)
                    if (len(order_date_max) > 0 and order_date_max is not None and order_date_max['order_date'][
                        0] is not None):
                        begin = order_date_max['order_date'][0].to_pydatetime().date() - datetime.timedelta(days=1)
                    else:
                        begin = datetime.date.today()
                except Exception as e:
                    _LOGGING.error(e)
            elif self.data_crawl_type == "ZL":  # 增量数据抓取
                try:
                    today_str = datetime.date.today().strftime('%Y-%m-%d')
                    sqlcmd = "select min(order_date) as order_date from amazon_report_manager_orders_"+zone_lower_case+" a where zone = '%s' and substr(create_date,1,10) = '%s'" % (self.zone, today_str )
                    order_date_max = pd.read_sql(sqlcmd, self.dbconn)
                    if (len(order_date_max) > 0 and order_date_max is not None and order_date_max['order_date'][
                        0] is not None):
                        begin = order_date_max['order_date'][0].to_pydatetime().date() - datetime.timedelta(days=1)
                    else:
                        begin = datetime.date.today()
                except Exception as e:
                    _LOGGING.error(e)
            else:
                begin = datetime.date.today()

            if self.data_crawl_type == 'CL':
                end = datetime.date.today() - datetime.timedelta(days=self.crawl_days)

                d = begin
                days = 1

                while d >= end and self.tryCnt > 0:
                    # print(d.strftime('%Y-%m-%d %H:%M:%S'))
                    order_date_str = d.strftime('%Y-%m-%d %H:%M:%S')

                    startDate = self.handle_abnormal_date_format(d.strftime(zone_date_format_dict[zone_upper_case]))
                    endDate = startDate

                    self.now_order_cnt = 0
                    self.crawlByExactDateAndZone(driver, startDate, endDate, sub_zone_url, sub_zone, order_date_str)

                    begin = d - datetime.timedelta(days=1)
                    delta = datetime.timedelta(days=days)
                    d -= delta

                    self.tryCnt -= 1
            elif self.data_crawl_type == 'ZL':
                for date_str in self.need_to_crawl_date_list:

                    startDate = self.handle_abnormal_date_format(datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime(
                        zone_date_format_dict[zone_upper_case]))
                    endDate = startDate

                    order_date_str = datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
                    self.crawlByExactDateAndZone(driver, startDate, endDate, sub_zone_url, sub_zone, order_date_str)

        except Exception as e:
            _LOGGING.error(e)
            self.deleteAll(driver)

    def crawlByExactDateAndZone(self, driver, startDate, endDate, sub_zone_url, sub_zone, order_date_str):

        # chose english language
        try:
            selector = driver.find_element_by_id('sc-lang-switcher-header-select')
            Select(selector).select_by_visible_text("English")
            WebDriverWait(driver, 120).until(
                lambda driver: driver.execute_script("return document.readyState") == 'complete')
            time.sleep(2)
        except Exception as e:
            _LOGGING.error(e)
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
            _LOGGING.error(e)
            pass

        # change the begin and end date
        try:
            exactDateBeginStr = startDate
            exactDateEndStr = endDate

            # driver.find_element_by_id('_myoSO_SearchOption_exactDates').click()
            _myoLO_SearchTypeSelect = driver.find_element_by_id('_myoLO_SearchTypeSelect')
            Select(_myoLO_SearchTypeSelect).select_by_value('DateRange')

            _myoLO_preSelectedRangeSelect = driver.find_element_by_id('_myoLO_preSelectedRangeSelect')
            Select(_myoLO_preSelectedRangeSelect).select_by_value('exactDates')

            # 如果上面的Advanced Search部分有使用的话，这里才会需要，通过JS来修改日历控件中的日期
            js = "document.getElementById(\'exactDateBegin\').removeAttribute('readonly');document.getElementById(\'exactDateBegin\').setAttribute('value','" + exactDateBeginStr + "');"
            driver.execute_script(js)
            js = "document.getElementById(\'exactDateEnd\').removeAttribute('readonly');document.getElementById(\'exactDateEnd\').setAttribute('value','" + exactDateEndStr + "');"
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

            if 'Too Many Orders Found' in search_result_str and (style is None or len(style) == 0 or 'display' not in style[0]):
                _myoLO_SearchTypeSelect = driver.find_element_by_id('_myoLO_SearchTypeSelect')
                Select(_myoLO_SearchTypeSelect).select_by_value('Marketplace')
                salesChannels = tree.xpath('//*[@id="_myoLO_marketplaceFilterSelect"]/option/@value')
                for salesChannel in salesChannels:
                    if salesChannel != 'sitesall':
                        _myoLO_marketplaceFilterSelect = driver.find_element_by_id('_myoLO_marketplaceFilterSelect')
                        Select(_myoLO_marketplaceFilterSelect).select_by_value(salesChannel)

                        _myoLO_preSelectedRangeSelect = driver.find_element_by_id('_myoLO_preSelectedRangeSelect')
                        Select(_myoLO_preSelectedRangeSelect).select_by_value('exactDates')

                        # 如果上面的Advanced Search部分有使用的话，这里才会需要，通过JS来修改日历控件中的日期
                        js = "document.getElementById(\'exactDateBegin\').removeAttribute('readonly');document.getElementById(\'exactDateBegin\').setAttribute('value','" + exactDateBeginStr + "');"
                        driver.execute_script(js)
                        js = "document.getElementById(\'exactDateEnd\').removeAttribute('readonly');document.getElementById(\'exactDateEnd\').setAttribute('value','" + exactDateEndStr + "');"
                        driver.execute_script(js)

                        driver.find_element_by_id('SearchID').click()

                        # handle system error
                        self.systemErrorHandle(driver, 5)

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

                        if 'No Order Found' in search_result_str and (style is None or len(style) == 0 or 'display' not in style[0]):
                            continue

                        sub_zone = amzid_marketplace_dict[salesChannel]
                        self.crawlBySalesChannel(driver, startDate, endDate, sub_zone_url, sub_zone, order_date_str, salesChannel)
            elif 'No Order Found' in search_result_str and (style is None or len(style) == 0 or 'display' not in style[0]):
                return
            else:
                pass

        except Exception as e:
            _LOGGING.error(e)
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
            _LOGGING.error(e)
            pass

        # parse driver.page_source in cycs
        try:
            self.parsePageInfo(driver, sub_zone, startDate, order_date_str)
        except Exception as e:
            _LOGGING.error(e)

    def crawlBySalesChannel(self, driver, startDate, endDate, sub_zone_url, sub_zone, order_date_str, salesChannel):
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
                    while times > 0:
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

            self.parsePageInfo(driver, sub_zone, startDate, order_date_str)
        except Exception as e:
            _LOGGING.error(e)


    def parsePageInfo(self, driver, sub_zone, startDate, order_date_str):
        content = driver.page_source
        tree = etree.HTML(content)

        try:
            if sub_zone != self.now_sub_zone:
                dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                now_order_cnt_str = tree.xpath(
                    '//*[@id="myo-table"]/table/tbody/tr[1]/td/table/tbody/tr/td[1]/strong[2]/text()')
                now_order_cnt = int(now_order_cnt_str[0])

                total_cnt_del_query = "delete from amazon_report_total_orders_source_"+zone_lower_case+" where zone = '%s' and sub_zone = '%s' and order_date = '%s'" % (self.zone, sub_zone, order_date_str)
                self.cur.execute(total_cnt_del_query)

                total_cnt_query = "insert into amazon_report_total_orders_source_"+zone_lower_case+"(zone, sub_zone, order_date, total_cnt, create_date) values(%s, %s, %s, %s, %s)"
                self.cur.execute(total_cnt_query, (self.zone, sub_zone, order_date_str, now_order_cnt, dt))

                self.now_date_str = order_date_str
                self.now_sub_zone = sub_zone
            elif order_date_str != self.now_date_str:
                dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                now_order_cnt_str = tree.xpath(
                    '//*[@id="myo-table"]/table/tbody/tr[1]/td/table/tbody/tr/td[1]/strong[2]/text()')
                now_order_cnt = int(now_order_cnt_str[0])

                total_cnt_del_query = "delete from amazon_report_total_orders_source_"+zone_lower_case+" where zone = '%s' and sub_zone = '%s' and order_date = '%s'" % (
                self.zone, sub_zone, order_date_str)
                self.cur.execute(total_cnt_del_query)

                total_cnt_query = "insert into amazon_report_total_orders_source_"+zone_lower_case+"(zone, order_date, total_cnt, create_date) values(%s, %s, %s, %s)"
                self.cur.execute(total_cnt_query, (self.zone, order_date_str, now_order_cnt, dt))
                self.now_date_str = order_date_str
            else:
                pass

        except Exception as e:
            _LOGGING.error(e)


        orders = tree.xpath("//tr[contains(@id,'row-')]")
        self.now_order_cnt += len(orders)
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

            sqli = "insert into amazon_report_manager_orders_"+zone_lower_case+"(order_id, cust_id, zone, order_date, create_date) values(%s, %s, %s, %s, %s)"
            self.cur.execute(sqli, (order_id, cust_id, self.zone, order_date_str, dt))
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
            _LOGGING.error(e)

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
            _LOGGING(e)

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
            _LOGGING(e)


    def deleteAll(self, driver):
        try:
            self.cur.close()
            self.dbconn.close()
            driver.quit()
            sys.exit(0)
        except Exception as e:
            _LOGGING.error(e)



executor = AutoUpdateData()
executor._update_data(zone_lower_case)
executor._exit()

amzCrawl = AmazonOrderManagerCrawl(zone_upper_case, 16, "ZL", 48) # 每次启动跑16天的数据，截至到当天往前推62天
amzCrawl.crawlWrongDate = True

if amzCrawl.data_crawl_type == 'ZL':
    amzCrawl.need_to_crawl()
    if len(amzCrawl.need_to_crawl_date_list) == 0:
        sys.exit(0)

amzCrawl.getOrderInfo()

executor = AutoUpdateData()
executor._update_data(zone_lower_case)
executor._exit()

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--zone', type=str, default="nothing",help='default value')
#     args = parser.parse_args()
#
#     print(args.zone)
#     zone = args.zone
#     print(type(zone))
#
# if __name__ == '__main__':
#     main()
