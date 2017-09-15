from selenium import webdriver
import urllib.request
from urllib.parse import urlunparse,urlparse
import urllib.error
import time
import json

USER_DATA_DIR = r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data"
BASE_URL = "https://www.amazon.com"

def get_email(driver):
    """
    :param driver: webdriver.Chrome
    :return:email or ""
    """
    if not isinstance(driver,webdriver.Chrome):
        raise TypeError
    if not driver.find_elements_by_class_name("user-links-email"):
        return ""
    #time.sleep(5)
    cookie = driver.get_cookies()
    cookie = [item["name"] + "=" + item["value"] for item in cookie]
    cookiestr = ';'.join(item for item in cookie)
    current_url = driver.current_url
    url_parse = urlparse(current_url)
    host = url_parse.netloc
    print(host)
    short_url = urlunparse(url_parse[:3] + ('',) * 3)
    target_url = short_url+'/customer_email'
    user_agent = r'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 r'Chrome/60.0.3112.113 Safari/537.36'
    headers = {'cookie':cookiestr,
               'User-Agent':user_agent,
               'Referer':current_url,
               'Host':host,
               'X-Requested-With':'XMLHttpRequest',
               }
    req = urllib.request.Request(target_url, headers=headers)
    try:
        result = urllib.request.urlopen(req).read()
    except urllib.error.HTTPError as e:
        print(e)
        return ""
    result = json.loads(result.decode('utf-8'))
    if result['status']=='ok':
        return result['data']['email']

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
    driver = webdriver.Chrome(executable_path='E:\\softwares\\drive\\chromedriver.exe', chrome_options=chrome_options)

    # driver.get(BASE_URL)
    # time.sleep(5)
    driver.get(
        "https://www.amazon.com/gp/profile/amzn1.account.AHABWD7YYEVMBMZBIZIZDUXBHQRA?ie=UTF8&ref_=cm_cr_dp_d_pdp")
    time.sleep(5)
    driver.find_elements_by_class_name("a-expander-prompt")[0].click()
    time.sleep(5)
    email=get_email(driver)
    print(email)