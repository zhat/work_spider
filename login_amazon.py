from AmazonManagerOrderCrawlFromOrderID import AmazonOrderManagerCrawlFromAsin_
from datetime import datetime
import pymysql
zone = 'US'
amzCrawl = AmazonOrderManagerCrawlFromAsin_(zone, 200)

amzCrawl.dbconn = pymysql.connect(
            host="192.168.2.97",
            database="bi_system",
            user="lepython",
            password="qaz123456",
            port=3306,
            charset='utf8'
        )
amzCrawl.cur = amzCrawl.dbconn.cursor()

amzCrawl.url,amzCrawl.username,amzCrawl.password=amzCrawl.get_login_info()
driver=amzCrawl.open_browser()
driver.get(amzCrawl.url)
amzCrawl.login(driver)