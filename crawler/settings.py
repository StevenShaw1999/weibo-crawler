# Scrapy settings for weibo project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
import datetime
from pathlib import Path

to_day = datetime.datetime.now()
log_path = f"/home/vipl/workspace/Crawler/weibo/logs/{to_day.year}_{to_day.month}_{to_day.day}"
#print(Path(log_path))
Path(log_path).mkdir(exist_ok = True)

LOG_FILE = f"{log_path}/scrapy_{to_day.hour}_{to_day.minute}_{to_day.second}.log"
LOG_LEVEL = 'INFO'

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWORD = ""

MYSQL_HOST = "127.0.0.1"
#MYSQL_HOST = "10.10.10.26"
MYSQL_USER = "root"
MYSQL_PORT = 3306
MYSQL_PASSWORD = "matrix666"
MYSQL_DBNAME = "spider"

XDAILI_ORDERNO = "ZF201912255648Jkkwbe"
XDAILI_SECRET  = "565ee6cc50a1437fb684e0bc64807f85"


BOT_NAME = 'weibo'

SPIDER_MODULES = ['weibo.spiders']
NEWSPIDER_MODULE = 'weibo.spiders'

RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 301, 302, 403, 418]

RETRY_ENABLED = True
RETRY_TIMES = 12
DOWNLOAD_TIMEOUT = 20
CONCURRENT_REQUESTS = 20

#DOWNLOAD_DELAY =0.25
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 20
#CONCURRENT_REQUESTS_PER_IP = 20

LOWER = 1200
UPPER = 1400


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'weibo (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    'host':    'm.weibo.cn',
#    'accept':    'application/json, text/plain, */*',
#    'user-agent':    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
#    'accept-encoding':    'gzip, deflate, br',
#    'accept-language':    'zh-CN,zh;q=0.9',
#    'cookie':    "SUB=_2A25OSiSkDeRhGeRH61YR-CbKwj2IHXVttUzsrDV6PUJbkdANLXLmkW1NTfjLwiuD_7lkbE482wP7AthjLIHsuDZx;"
#}


# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'weibo.middlewares.WeiboSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'weibo.middlewares.WeiboDownloaderMiddleware': 543,
    'weibo.middlewares.RetryMiddleware': 550,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    #'weibo.pipelines.WeiboPipeline': 300,
    'weibo.pipelines.WeiboTwistedPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Set settings whose default value is deprecated to a future-proof value
#REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
#TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
