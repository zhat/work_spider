from AmazonManagerOrderCrawlFromOrderID import get_profile
from datetime import datetime
if __name__=='__main__':
    print(datetime.now())
    get_profile('JP', 48)
    get_profile('CA', 48)
    get_profile('DE', 48)
    get_profile('US', 48)