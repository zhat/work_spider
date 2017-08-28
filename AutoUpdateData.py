# coding = utf-8

import pymysql

"""
    每天进行一次数据的增量插入
"""


class AutoUpdateData():

    def __init__(self):

        self.dbconn = pymysql.connect(
            host="192.168.2.23",
            database="leamazon",
            user="ama_account",
            password="T89ZY#UQWS",
            port=3306,
            charset='utf8'
        )
        self.cur = self.dbconn.cursor()

    def _update_data(self, zone_or_asin):
        insert_data_sql_str = "insert into amazon_order_search_data(profile, zone, order_id, order_time) " \
                          " select distinct cust_id, zone, order_id, substr(order_date,1,10) as order_time " \
                          " from amazon_report_manager_orders_{0} a "  \
                          " where not exists (select 1 from amazon_order_search_data b where a.zone = b.zone and a.order_id = b.order_id) "
        insert_data_sql = insert_data_sql_str.format(zone_or_asin)
        self.cur.execute(insert_data_sql)
        self.dbconn.commit()

    def _update_data_by_asin(self, zone_or_asin):
        insert_data_sql_str = "insert into amazon_order_search_data(profile, zone, order_id, order_time) " \
                              " select distinct cust_id, zone, order_id, substr(order_date,1,10) as order_time " \
                              " from amazon_asin_manager_orders_{0} a " \
                              " where not exists (select 1 from amazon_order_search_data b where a.zone = b.zone and a.order_id = b.order_id) "
        insert_data_sql = insert_data_sql_str.format(zone_or_asin)
        self.cur.execute(insert_data_sql)
        self.dbconn.commit()

        # insert_data_sql_de = "insert into amazon_order_search_data(profile, zone, order_id, order_time) " \
        #                      " select cust_id, zone, order_id, substr(order_date,1,10) as order_time " \
        #                      " from amazon_report_manager_orders_de a " \
        #                      " where not exists (select 1 from amazon_order_search_data b where a.zone = b.zone and a.order_id = b.order_id) "
        # self.cur.execute(insert_data_sql_de)
        # self.dbconn.commit()
        #
        # insert_data_sql_jp = "insert into amazon_order_search_data(profile, zone, order_id, order_time) " \
        #                      " select cust_id, zone, order_id, substr(order_date,1,10) as order_time " \
        #                      " from amazon_report_manager_orders_jp a " \
        #                      " where not exists (select 1 from amazon_order_search_data b where a.zone = b.zone and a.order_id = b.order_id) "
        # self.cur.execute(insert_data_sql_jp)
        # self.dbconn.commit()
        #
        # insert_data_sql_ca = "insert into amazon_order_search_data(profile, zone, order_id, order_time) " \
        #                      " select cust_id, zone, order_id, substr(order_date,1,10) as order_time " \
        #                      " from amazon_report_manager_orders_ca a " \
        #                      " where not exists (select 1 from amazon_order_search_data b where a.zone = b.zone and a.order_id = b.order_id) "
        # self.cur.execute(insert_data_sql_ca)
        # self.dbconn.commit()

    def _exit(self):
        self.cur.close()
        self.dbconn.close()

if __name__ == "__main__":
    executor = AutoUpdateData()
    # executor._update_data('de')
    executor._update_data_by_asin('us')
    executor._exit()



