from AmazonManagerOrderCrawlFromOrderID import get_profile
from datetime import datetime
if __name__=='__main__':
    print(datetime.now())
    get_profile('JP', 0)
    get_profile('CA', 0)
    get_profile('DE', 0)
    get_profile('US', 0)