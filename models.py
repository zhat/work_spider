# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Index, Integer, Numeric, SmallInteger, String, Text, VARBINARY, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class AmazonOrder(Base):
    __tablename__ = 'amazon_order'
    __table_args__ = (
        Index('UNIQUE_ORDER_ID', 'channel', 'order_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    platform = Column(String(32), nullable=False, index=True)
    channel = Column(String(40), nullable=False)
    order_id = Column(String(80), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    payment_method = Column(String(40), nullable=False)
    purchase_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    created_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    updated_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    amazon_updated_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    lastest_ship_date = Column(DateTime, nullable=False, server_default=text("'0000-00-00 00:00:00'"))
    lastest_delivery_date = Column(DateTime, nullable=False, server_default=text("'0000-00-00 00:00:00'"))
    customer_name = Column(String(40), nullable=False)
    email = Column(String(255), nullable=False)
    amount = Column(Numeric(12, 4))
    currency_code = Column(String(20))
    country_code = Column(String(20))
    name = Column(String(255))
    state_or_region = Column(String(40), nullable=False)
    postal_code = Column(String(40))
    phone = Column(String(60))
    city = Column(String(255))
    street = Column(Text)


class AmazonOrderItem(Base):
    __tablename__ = 'amazon_order_item'

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, nullable=False, index=True)
    amazon_item_id = Column(String(40), nullable=False)
    title = Column(String(255), nullable=False)
    ASIN = Column(String(120), nullable=False, index=True)
    sku = Column(String(255), index=True)
    price = Column(Numeric(12, 4))
    qty = Column(Numeric(12, 4))
    shipping_amount = Column(Numeric(12, 4))
    shipping_discount = Column(Numeric(12, 4))
    tax = Column(Numeric(12, 0))
    gift_price = Column(Numeric(12, 4))
    promotion_id = Column(String(256))
    promotion_discount = Column(Numeric(12, 4))
    shipping_tax = Column(Numeric(12, 4))
    condition_id = Column(String(20))
    created_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    updated_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    push_status = Column(SmallInteger, nullable=False, server_default=text("'0'"))


class AmazonOrderSearchDatum(Base):
    __tablename__ = 'amazon_order_search_data'

    id = Column(Integer, primary_key=True)
    profile = Column(String(50), nullable=False, index=True)
    zone = Column(String(50), nullable=False)
    order_id = Column(String(50), nullable=False, index=True)
    order_time = Column(String(50), nullable=False)


class AuthGroup(Base):
    __tablename__ = 'auth_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)


class AuthGroupPermission(Base):
    __tablename__ = 'auth_group_permissions'
    __table_args__ = (
        Index('auth_group_permissions_group_id_permission_id_0cd325b0_uniq', 'group_id', 'permission_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey('auth_group.id'), nullable=False)
    permission_id = Column(ForeignKey('auth_permission.id'), nullable=False, index=True)

    group = relationship('AuthGroup')
    permission = relationship('AuthPermission')


class AuthPermission(Base):
    __tablename__ = 'auth_permission'
    __table_args__ = (
        Index('auth_permission_content_type_id_codename_01ab375a_uniq', 'content_type_id', 'codename', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    content_type_id = Column(ForeignKey('django_content_type.id'), nullable=False)
    codename = Column(String(100), nullable=False)

    content_type = relationship('DjangoContentType')


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(Integer, primary_key=True)
    password = Column(String(128), nullable=False)
    last_login = Column(DateTime)
    is_superuser = Column(Integer, nullable=False)
    username = Column(String(150), nullable=False, unique=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    email = Column(String(254), nullable=False)
    is_staff = Column(Integer, nullable=False)
    is_active = Column(Integer, nullable=False)
    date_joined = Column(DateTime, nullable=False)


class AuthUserGroup(Base):
    __tablename__ = 'auth_user_groups'
    __table_args__ = (
        Index('auth_user_groups_user_id_group_id_94350c0c_uniq', 'user_id', 'group_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False)
    group_id = Column(ForeignKey('auth_group.id'), nullable=False, index=True)

    group = relationship('AuthGroup')
    user = relationship('AuthUser')


class AuthUserUserPermission(Base):
    __tablename__ = 'auth_user_user_permissions'
    __table_args__ = (
        Index('auth_user_user_permissions_user_id_permission_id_14a6b632_uniq', 'user_id', 'permission_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False)
    permission_id = Column(ForeignKey('auth_permission.id'), nullable=False, index=True)

    permission = relationship('AuthPermission')
    user = relationship('AuthUser')


class CeleryTaskmeta(Base):
    __tablename__ = 'celery_taskmeta'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), nullable=False)
    result = Column(String)
    date_done = Column(DateTime, nullable=False)
    traceback = Column(String)
    hidden = Column(Integer, nullable=False, index=True)
    meta = Column(String)


class CeleryTasksetmeta(Base):
    __tablename__ = 'celery_tasksetmeta'

    id = Column(Integer, primary_key=True)
    taskset_id = Column(String(255), nullable=False, unique=True)
    result = Column(String, nullable=False)
    date_done = Column(DateTime, nullable=False)
    hidden = Column(Integer, nullable=False, index=True)


class CoreAmazonAccount(Base):
    __tablename__ = 'core_amazon_account'

    id = Column(Integer, primary_key=True)
    platform = Column(String(40), nullable=False)
    department = Column(String(20))
    username = Column(String(40), nullable=False)
    password_encrypt = Column(VARBINARY(100), nullable=False)
    login_url = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime, nullable=False, server_default=text("'0000-00-00 00:00:00'"))


class DjangoAdminLog(Base):
    __tablename__ = 'django_admin_log'

    id = Column(Integer, primary_key=True)
    action_time = Column(DateTime, nullable=False)
    object_id = Column(String)
    object_repr = Column(String(200), nullable=False)
    action_flag = Column(SmallInteger, nullable=False)
    change_message = Column(String, nullable=False)
    content_type_id = Column(ForeignKey('django_content_type.id'), index=True)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False, index=True)

    content_type = relationship('DjangoContentType')
    user = relationship('AuthUser')


class DjangoContentType(Base):
    __tablename__ = 'django_content_type'
    __table_args__ = (
        Index('django_content_type_app_label_model_76bd3d3b_uniq', 'app_label', 'model', unique=True),
    )

    id = Column(Integer, primary_key=True)
    app_label = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)


class DjangoMigration(Base):
    __tablename__ = 'django_migrations'

    id = Column(Integer, primary_key=True)
    app = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    applied = Column(DateTime, nullable=False)


class DjangoSession(Base):
    __tablename__ = 'django_session'

    session_key = Column(String(40), primary_key=True)
    session_data = Column(String, nullable=False)
    expire_date = Column(DateTime, nullable=False, index=True)


class DjceleryCrontabschedule(Base):
    __tablename__ = 'djcelery_crontabschedule'

    id = Column(Integer, primary_key=True)
    minute = Column(String(64), nullable=False)
    hour = Column(String(64), nullable=False)
    day_of_week = Column(String(64), nullable=False)
    day_of_month = Column(String(64), nullable=False)
    month_of_year = Column(String(64), nullable=False)


class DjceleryIntervalschedule(Base):
    __tablename__ = 'djcelery_intervalschedule'

    id = Column(Integer, primary_key=True)
    every = Column(Integer, nullable=False)
    period = Column(String(24), nullable=False)


class DjceleryPeriodictask(Base):
    __tablename__ = 'djcelery_periodictask'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    task = Column(String(200), nullable=False)
    args = Column(String, nullable=False)
    kwargs = Column(String, nullable=False)
    queue = Column(String(200))
    exchange = Column(String(200))
    routing_key = Column(String(200))
    expires = Column(DateTime)
    enabled = Column(Integer, nullable=False)
    last_run_at = Column(DateTime)
    total_run_count = Column(Integer, nullable=False)
    date_changed = Column(DateTime, nullable=False)
    description = Column(String, nullable=False)
    crontab_id = Column(ForeignKey('djcelery_crontabschedule.id'), index=True)
    interval_id = Column(ForeignKey('djcelery_intervalschedule.id'), index=True)

    crontab = relationship('DjceleryCrontabschedule')
    interval = relationship('DjceleryIntervalschedule')


class DjceleryPeriodictask(Base):
    __tablename__ = 'djcelery_periodictasks'

    ident = Column(SmallInteger, primary_key=True)
    last_update = Column(DateTime, nullable=False)


class DjceleryTaskstate(Base):
    __tablename__ = 'djcelery_taskstate'

    id = Column(Integer, primary_key=True)
    state = Column(String(64), nullable=False, index=True)
    task_id = Column(String(36), nullable=False, unique=True)
    name = Column(String(200), index=True)
    tstamp = Column(DateTime, nullable=False, index=True)
    args = Column(String)
    kwargs = Column(String)
    eta = Column(DateTime)
    expires = Column(DateTime)
    result = Column(String)
    traceback = Column(String)
    runtime = Column(Float(asdecimal=True))
    retries = Column(Integer, nullable=False)
    hidden = Column(Integer, nullable=False, index=True)
    worker_id = Column(ForeignKey('djcelery_workerstate.id'), index=True)

    worker = relationship('DjceleryWorkerstate')


class DjceleryWorkerstate(Base):
    __tablename__ = 'djcelery_workerstate'

    id = Column(Integer, primary_key=True)
    hostname = Column(String(255), nullable=False, unique=True)
    last_heartbeat = Column(DateTime, index=True)


class DjkombuMessage(Base):
    __tablename__ = 'djkombu_message'

    id = Column(Integer, primary_key=True)
    visible = Column(Integer, nullable=False, index=True)
    sent_at = Column(DateTime, index=True)
    payload = Column(String, nullable=False)
    queue_id = Column(ForeignKey('djkombu_queue.id'), nullable=False, index=True)

    queue = relationship('DjkombuQueue')


class DjkombuQueue(Base):
    __tablename__ = 'djkombu_queue'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)


class EbayOrderFull(Base):
    __tablename__ = 'ebay_order_full'

    id = Column(BigInteger, primary_key=True)
    account = Column(String(50), nullable=False, index=True)
    order_id = Column(String(255), nullable=False, index=True)
    record_number = Column(BigInteger, nullable=False, index=True)
    order_status = Column(String(50), nullable=False, index=True)
    adjustment_amount = Column(String(50), nullable=False)
    amount_paid = Column(String(50), nullable=False)
    amount_saved = Column(String(50), nullable=False)
    created_time = Column(DateTime, nullable=False, server_default=text("'0000-00-00 00:00:00'"))
    payment_methods = Column(String(50), nullable=False)
    seller_email = Column(String(255), nullable=False)
    sub_total = Column(String(50), nullable=False)
    total = Column(String(50), nullable=False)
    buyer_user_id = Column(String(255), nullable=False)
    paid_time = Column(DateTime, nullable=False, server_default=text("'0000-00-00 00:00:00'"))
    shipped_time = Column(DateTime, nullable=False, server_default=text("'0000-00-00 00:00:00'"))
    integrated_merchant_credit_card_enabled = Column(Integer, nullable=False)
    eias_token = Column(String(255), nullable=False)
    payment_hold_status = Column(String(50), nullable=False)
    is_multi_leg_shipping = Column(Integer, nullable=False)
    seller_user_id = Column(String(255), nullable=False)
    seller_eias_token = Column(String(255))
    cancel_status = Column(String(50))
    extended_order_id = Column(String(255))
    contains_ebay_plus_transaction = Column(Integer)
    checkout_status_s = Column(String(40), index=True)
    checkout_status = Column(Text)
    shipping_country = Column(String(60), index=True)
    shipping_region = Column(String(60), index=True)
    shipping_postcode = Column(String(40), index=True)
    shipping_details = Column(Text)
    shipping_address = Column(Text)
    shipping_service_selected = Column(Text)
    external_transaction = Column(Text)
    transaction_array = Column(Text)
    monetary_details = Column(Text)
    last_modified_time = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    last_fetch_time = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    has_pushed = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    process_status = Column(Integer, nullable=False, index=True, server_default=text("'0'"))


class EbayOrderFullItem(Base):
    __tablename__ = 'ebay_order_full_item'

    id = Column(Integer, primary_key=True)
    order_id = Column(String(255), nullable=False, index=True, server_default=text("'0'"))
    transaction_id = Column(String(255), nullable=False, server_default=text("'0'"))
    transaction_site_id = Column(String(50), nullable=False, server_default=text("'0'"))
    email = Column(String(80))
    item_id = Column(String(255))
    item_sku = Column(String(50))
    item_title = Column(String(50))
    quantity_purchased = Column(String(50))
    transaction_price = Column(String(50))


class LightOrder(Base):
    __tablename__ = 'light_order'
    __table_args__ = (
        Index('IDX_ORDER_PLATFORM', 'platform', 'order_id', unique=True),
    )

    entity_id = Column(Integer, primary_key=True)
    platform = Column(String(60), nullable=False, index=True)
    order_id = Column(String(50), nullable=False)
    light_order_id = Column(String(50), nullable=False, index=True)
    state = Column(String(32), nullable=False, index=True)
    status = Column(String(32), nullable=False, index=True)
    discount_amount = Column(Numeric(12, 4), nullable=False)
    subtotal = Column(Numeric(12, 4), nullable=False)
    grand_total = Column(Numeric(12, 4), nullable=False)
    shipping_amount = Column(Numeric(12, 4), nullable=False)
    tax_amount = Column(Numeric(12, 4), nullable=False)
    total_canceled = Column(Numeric(12, 4), nullable=False)
    total_invoiced = Column(Numeric(12, 4), nullable=False)
    total_paid = Column(Numeric(12, 4), nullable=False)
    total_qty_ordered = Column(Numeric(12, 4), nullable=False)
    total_refunded = Column(Numeric(12, 4), nullable=False)
    gift_message = Column(String(255), nullable=False)
    weight = Column(Numeric(12, 4), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_firstname = Column(String(255), nullable=False)
    customer_lastname = Column(String(255), nullable=False)
    customer_middlename = Column(String(255), nullable=False)
    global_currency_code = Column(String(3), nullable=False)
    order_currency_code = Column(String(255), nullable=False)
    remote_ip = Column(String(255), nullable=False)
    shipping_method = Column(String(255), nullable=False)
    country_id = Column(String(20), nullable=False, index=True)
    region_id = Column(Integer, nullable=False, index=True)
    region = Column(String(40), nullable=False)
    city = Column(String(40), nullable=False)
    postcode = Column(String(40), nullable=False)
    street = Column(Text, nullable=False)
    shipping_firstname = Column(String(255), nullable=False)
    shipping_middlename = Column(String(255), nullable=False)
    shipping_lastname = Column(String(255), nullable=False)
    telephone = Column(String(40), nullable=False)
    customer_note = Column(Text)
    avs = Column(String(4), nullable=False, index=True)
    payment_method = Column(String(40), nullable=False)
    light_created_at = Column(DateTime, nullable=False, index=True, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    paid_time = Column(DateTime, nullable=False, server_default=text("'0000-00-00 00:00:00'"))
    light_updated_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    process_status = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    created_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    updated_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))


class LightOrderItem(Base):
    __tablename__ = 'light_order_item'

    entity_id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, nullable=False, index=True)
    light_item_id = Column(Integer, nullable=False, index=True)
    weight = Column(Numeric(12, 4), nullable=False)
    sku = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    free_shipping = Column(SmallInteger, nullable=False)
    is_qty_decimal = Column(SmallInteger, nullable=False)
    no_discount = Column(SmallInteger, nullable=False)
    qty_canceled = Column(Numeric(12, 4), nullable=False)
    qty_invoiced = Column(Numeric(12, 4), nullable=False)
    qty_ordered = Column(Numeric(12, 4), nullable=False)
    qty_refunded = Column(Numeric(12, 4), nullable=False)
    qty_shipped = Column(Numeric(12, 4), nullable=False)
    price = Column(Numeric(12, 4), nullable=False)
    base_price = Column(Numeric(12, 4), nullable=False)
    original_price = Column(Numeric(12, 4), nullable=False)
    tax_percent = Column(Numeric(12, 4), nullable=False)
    tax_amount = Column(Numeric(12, 4), nullable=False)
    tax_invoiced = Column(Numeric(12, 4), nullable=False)
    discount_percent = Column(Numeric(12, 4), nullable=False)
    discount_amount = Column(Numeric(12, 4), nullable=False)
    amount_refunded = Column(Numeric(12, 4), nullable=False)
    row_total = Column(Numeric(12, 4), nullable=False)
    gift_message_id = Column(Integer, nullable=False)
    postcode = Column(String(40), nullable=False)
    region = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    street = Column(Text, nullable=False)
    gift_message = Column(Integer, nullable=False)
    light_created_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    light_updated_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    ship_at = Column(DateTime, nullable=False, server_default=text("'0000-00-00 00:00:00'"))
    push_status = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))
    updated_at = Column(DateTime, nullable=False, index=True, server_default=text("'0000-00-00 00:00:00'"))


class OrderAdvise(Base):
    __tablename__ = 'order_advise'

    id = Column(Integer, primary_key=True)
    summary = Column(String(255))
    content = Column(String)
    add_time = Column(DateTime)
    reply = Column(String)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False, index=True)

    user = relationship('AuthUser')


class OrderOrderdatum(Base):
    __tablename__ = 'order_orderdata'

    id = Column(Integer, primary_key=True)
    profile = Column(String(255), index=True)
    zone = Column(String(16), nullable=False)
    order_id = Column(String(255), nullable=False, index=True)
    order_time = Column(DateTime)
    create_time = Column(DateTime)
    update_time = Column(DateTime)
    status = Column(String(50))


class SpiderCountofday(Base):
    __tablename__ = 'spider_countofday'

    id = Column(Integer, primary_key=True)
    order_day = Column(String(64), nullable=False)
    total = Column(Integer, nullable=False)
    success = Column(Integer)


class SpiderOrdercrawl(Base):
    __tablename__ = 'spider_ordercrawl'

    id = Column(Integer, primary_key=True)
    asin = Column(String(255), nullable=False)
    zone = Column(String(16), nullable=False)
    add_time = Column(DateTime)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    days = Column(Integer)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False, index=True)
    profile = Column(String(255), nullable=False)
    name = Column(String(255))

    user = relationship('AuthUser')


class SpiderPermission(Base):
    __tablename__ = 'spider_permission'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    url = Column(String(255), nullable=False)
    per_method = Column(SmallInteger, nullable=False)
    argument_list = Column(String(255))
    describe = Column(String(255), nullable=False)


class SpiderStudent(Base):
    __tablename__ = 'spider_student'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    age = Column(SmallInteger, nullable=False)
    sex = Column(SmallInteger, nullable=False)
