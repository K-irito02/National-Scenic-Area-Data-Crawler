# Scrapy settings for mafengwo project (Distributed Version)
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "mafengwo"

SPIDER_MODULES = ["mafengwo.spiders"]
NEWSPIDER_MODULE = "mafengwo.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"

USER_AGENT_LIST = [
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/5.1)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/3.0)",
    "Mozilla/5.0 (compatible; MSIE 7.0; Windows 95; Trident/4.1)",
    "Mozilla/5.0 (Windows 98) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/30.0.850.0 Safari/535.2",
    "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 6.2; Trident/5.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.01; Trident/4.1)",
    "Mozilla/5.0 (compatible; MSIE 6.0; Windows 98; Trident/3.0)",
    "Mozilla/5.0 (Windows NT 5.0) AppleWebKit/535.0 (KHTML, like Gecko) Chrome/51.0.884.0 Safari/535.0",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows 98; Win 9x 4.90; Trident/4.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.1)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.2) AppleWebKit/535.23.6 (KHTML, like Gecko) Version/4.0.3 Safari/535.23.6",
]

PROXY_LIST = [
    {'ip_port': '127.0.0.1:8080'},
    {'ip_port': '192.168.1.1:8080'}
]

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 5
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "mafengwo.middlewares.MafengwoSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'mafengwo.middlewares.RandomUserAgentMiddleware': 400,
    'mafengwo.middlewares.RandomDelayMiddleware': 500,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "scrapy_redis.pipelines.RedisPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# 设置更长的超时时间
DOWNLOAD_TIMEOUT = 30

# 重试设置
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 202]

# 随机化下载延迟
RANDOMIZE_DOWNLOAD_DELAY = True

# 配置输出
FEED_FORMAT = 'json'
FEED_URI = 'attractions_distributed.json'
FEED_EXPORT_ENCODING = 'utf-8'
FEED_EXPORT_INDENT = 4

# 增加随机延迟范围，避免固定延迟被识别
RANDOM_DELAY_MINIMUM = 3
RANDOM_DELAY_MAXIMUM = 8

# ================ Scrapy-Redis 分布式爬虫配置 ================

# 使用Scrapy-Redis的调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 使用Scrapy-Redis的去重组件
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 在爬虫结束后不清空Redis队列
SCHEDULER_PERSIST = True

# 使用优先级队列
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'

# 配置去重持久化
DUPEFILTER_KEY = '%(spider)s:dupefilter'
DUPEFILTER_DEBUG = True

# 配置不同类型URL的去重键
CITIES_DUPEFILTER_KEY = '%(spider)s:cities:dupefilter'
LIST_DUPEFILTER_KEY = '%(spider)s:list:dupefilter'
DETAIL_DUPEFILTER_KEY = '%(spider)s:detail:dupefilter'

# Redis连接设置 - 这些设置已被弃用，请使用REDIS_PARAMS
# REDIS_HOST = 'localhost'  # 替换为您的Redis服务器地址
# REDIS_PORT = 6379
# REDIS_DB = 0
# REDIS_PASSWORD = '3143285505'  # 设置Redis密码

# 使用Redis作为Item Pipeline
ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 300,
}

# 设置Redis键的前缀，避免不同爬虫之间的冲突
REDIS_ITEMS_KEY = '%(spider)s:items'
REDIS_START_URLS_KEY = '%(name)s:start_urls'

# 设置Redis编码
REDIS_ENCODING = 'utf-8'

# 设置Redis连接参数 - 使用这个配置替代上面的单独配置
REDIS_PARAMS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': '3143285505',  # 添加Redis密码
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': 'utf-8',
}

# 设置日志级别
LOG_LEVEL = 'INFO'

# 设置日志文件
LOG_FILE = 'logs/mafengwo_distributed.log'

# 创建日志目录
import os
os.makedirs('logs', exist_ok=True)

# 全国景点爬虫起始URL
START_URLS = [
    'https://www.mafengwo.cn/mdd/'
]

# Redis键配置
REDIS_START_URLS_KEY = '%(name)s:start_urls'
CITIES_START_URLS_KEY = 'china_attractions_db:cities_start_urls'
LIST_START_URLS_KEY = 'china_attractions_db:list_start_urls'
DETAIL_START_URLS_KEY = 'china_attractions_db:detail_start_urls' 