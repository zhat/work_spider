from AmazonManagerOrderCrawlFromOrderID import get_profile
from datetime import datetime
if __name__=='__main__':
    print(datetime.now())
    get_profile('DE',0,'Pending')
    get_profile('US',0,'Pending')
    get_profile('CA',0,'Pending')
    get_profile('JP',0,'Pending')
