# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from random import choice
from .settings_distributed import USER_AGENT_LIST, PROXY_LIST
from selenium import webdriver
from selenium.webdriver.edge.service import Service
import time
from scrapy.http import HtmlResponse
from scrapy import signals
from selenium.webdriver.common.by import By
import random
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        request.headers['User-Agent'] = choice(USER_AGENT_LIST)

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        proxy = choice(PROXY_LIST)
        # 确保代理地址包含协议
        if not proxy['ip_port'].startswith(('http://', 'https://')):
            request.meta['proxy'] = f"http://{proxy['ip_port']}"
        else:
            request.meta['proxy'] = proxy['ip_port']

class RandomDelayMiddleware(object):
    def __init__(self, settings):
        self.delay_min = settings.getfloat('RANDOM_DELAY_MINIMUM', 3)
        self.delay_max = settings.getfloat('RANDOM_DELAY_MAXIMUM', 8)
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
        
    def process_request(self, request, spider):
        # 为每个请求设置随机延迟
        delay = random.uniform(self.delay_min, self.delay_max)
        spider.logger.debug(f"随机延迟: {delay:.2f}秒")
        time.sleep(delay)

class CustomRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        
        # 如果状态码在重试列表中，或者是被反爬机制拦截的页面
        if response.status in self.retry_http_codes or '访问验证' in response.text:
            reason = response_status_message(response.status)
            # 增加随机延迟，避免被反爬
            delay = random.uniform(10, 30)
            spider.logger.info(f"检测到需要重试，等待 {delay:.2f} 秒后重试")
            time.sleep(delay)
            return self._retry(request, reason, spider) or response
        
        return response

class SeleniumMiddleware(object):   
    def process_request(self, request, spider):
        url = request.url

        if "mdd" in url:
            # 使用 Service 类来指定驱动路径
            service = Service(executable_path=r"E:\\edgedriver\\msedgedriver.exe")
            driver = webdriver.Edge(service=service)
            driver.get(url)
            time.sleep(5)
            driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/a[1]").click()
            time.sleep(2)
            html = driver.page_source
            
            driver.close()
            # 创建响应对象
            res = HtmlResponse(url=url, body=html, encoding='utf-8', request=request)
            
            return res
        

