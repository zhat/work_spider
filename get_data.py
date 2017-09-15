from selenium import webdriver
import urllib.request
import urllib
from urllib.parse import urlunparse,urlparse,urlencode
import urllib.error
import time
import json
import pymysql
from datetime import datetime,timedelta
#from shibie import GetImageDate

USER_DATA_DIR = r"C:\Users\yaoxuzhao\AppData\Local\Google\Chrome\User Data"
BASE_URL = "http://192.168.2.99:9080/ocs/index"
DATABASE = {
            'host':"192.168.2.97",
            'database':"bi_system_dev",
            'user':"lepython",
            'password':"qaz123456",
            'port':3306,
            'charset':'utf8'
}

class GetStatisticsDataFromOMS():
    """
    从OMS系统上抓取每天统计信息
    """
    def __init__(self,date):
        self.dbconn = pymysql.connect(**DATABASE)
        self.date=date
    def get_data(self,driver):
        """
        :param driver: webdriver.Chrome
        :return:email or ""
        """
        if not isinstance(driver,webdriver.Chrome):
            raise TypeError
        #time.sleep(5)
        cookie = driver.get_cookies()
        cookie = [item["name"] + "=" + item["value"] for item in cookie]
        cookiestr = ';'.join(item for item in cookie)
        print(cookiestr)
        current_url = driver.current_url
        url_parse = urlparse(current_url)
        host = url_parse.netloc
        origin = urlunparse(url_parse[:2]+('',)*4)
        print(host)
        print(origin)
        page = 1
        short_url = urlunparse(url_parse[:3] + ('',) * 3)

        target_url = "http://192.168.2.99:9080/ocs/salesStatistics/findAll"
        user_agent = r'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 r'Chrome/60.0.3112.113 Safari/537.36'
        headers = {'cookie':cookiestr,
               'User-Agent':user_agent,
               'Referer':"http://192.168.2.99:9080/ocs/salesStatistics/tolist",
               'Host':host,
               'Origin':origin,
               'X-Requested-With':'XMLHttpRequest',
               }

        sql_insert = []
        while True:
            values = {'param[source]': 'amazon',
                      'param[sku]': '',
                      'param[platform]': 'US',
                      'param[status]': '',
                      'param[whichTime]': 'purchaseat',
                      'param[starttime]': self.date,
                      'param[endtime]': self.date,
                      'param[timeQuantum]': 0,
                      'param[asin]': '',
                      'param[station]': 'Amazon.com',
                      'page': page,
                      'rows': 50}
            # values=json.dumps(values)
            print(values)
            data = urlencode(values).encode()
            # data=b'param%5Bsource%5D=amazon&param%5Bsku%5D=&param%5Bplatform%5D=&param%5Bstatus%5D=&param%5BwhichTime%5D=purchaseat&param%5Bstarttime%5D=&param%5Bendtime%5D=&param%5BtimeQuantum%5D=-30&param%5Basin%5D=&param%5Bstation%5D=&page=1&rows=50'

            print(data)
            req = urllib.request.Request(target_url, data=data, headers=headers)
            try:
                result = urllib.request.urlopen(req).read()
            except urllib.error.HTTPError as e:
                print(e)
                return ""

            result = json.loads(result.decode('utf-8'))
            self.total = result['total']
            self.source = result['source']
            footer = result['footer']
            count_data = footer[1]
            rows = result['rows']
            print(self.total)
            print(self.source)
            for row in rows:
                # print(row['sku'], row['asin'], row['platform'], row['station'], row['qty'], row['currencycode'],
                #   row['deduction'],
                #   row['price'], row['count'], row['sametermrate'], row['weekrate'], row['monthrate'], row['status'])
                insert_url = r'INSERT INTO report_statisticsdata (`date`,sku,asin,platform,station,qty,currencycode,' \
                     r'deduction,price,`count`,sametermrate,weekrate,monthrate,status)' \
                     r' VALUES("%s","%s","%s","%s","%s",%d,"%s",%f,%f,%d,%f,%f,%f,"%s");'%(self.date,
                row['sku'],row['asin'],row['platform'],row['station'],row['qty'],row['currencycode'],row['deduction'],
                row['price'],row['count'],row['sametermrate'],row['weekrate'],row['monthrate'],row['status'])
                print(insert_url)
                sql_insert.append(insert_url)
            if self.total<page*50:
                # print(self.date,count_data['currencycode'],count_data['deduction'],count_data['taxrate'],
                #       float(count_data['weekrate']),float(count_data['monthrate']),float(count_data['status']),
                #       float(count_data['sametermrate'][:-1]),float(count_data['price'][:-1]),
                #       float(count_data['count'][:-1]))
                insert_url=r'INSERT INTO report_statisticsofplatform (`date`,station,qty,`count`,' \
                           r'site_price,dollar_price,RMB_price,sametermrate,weekrate,monthrate) ' \
                           r'VALUES("%s","%s",%d,%d,%f,%f,%f,%f,%f,%f);'%(self.date,
                            count_data['currencycode'],count_data['deduction'],count_data['taxrate'],
                            float(count_data['weekrate']),float(count_data['monthrate']),float(count_data['status']),
                            float(count_data['sametermrate'][:-1]),float(count_data['price'][:-1]),
                            float(count_data['count'][:-1]))
                print(insert_url)
                sql_insert.append(insert_url)
                break
            else:
                page+=1
        cur = self.dbconn.cursor()
        try:
            for sqlcmd in sql_insert:
                cur.execute(sqlcmd)
            print(datetime.now())
            self.dbconn.commit()
        except Exception as e:
            print(e)
        finally:
            cur.close()
        return result

    def clean_data(self):
        cur = self.dbconn.cursor()
        sqlcmd = r'INSERT INTO report_asininfo(`date`,`asin`,`platform`,station,sku) SELECT DISTINCT ' \
                 r'`date`,`asin`,`platform`,station,sku FROM report_statisticsdata WHERE date="%s";'%self.date
        try:
            cur.execute(sqlcmd)
            self.dbconn.commit()
        except Exception as e:
            print(e)
        finally:
            cur.close()

if __name__=="__main__":
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('prefs', {
        'credentials_enable_service': True,
        'profile': {
            'password_manager_enabled': True
        }
    })
    # 读取本地信息
    chrome_options.add_argument("--user-data-dir=" + USER_DATA_DIR)
    driver = webdriver.Chrome(chrome_options=chrome_options)

    # driver.get(BASE_URL)
    # time.sleep(5)
    driver.get(BASE_URL)
    time.sleep(10)
    now = datetime.now()
    days = 2
    while days<30:
        date = now-timedelta(days=days)
        date = date.strftime("%Y-%m-%d")
        gs = GetStatisticsDataFromOMS(date)
        result=gs.get_data(driver)
        gs.clean_data()
        days+=1
        time.sleep(5)
    driver.quit()
#汇率表；
#"cal_currency_rate"

