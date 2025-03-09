# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MafengwoDistributedItem(scrapy.Item):
    """
    马蜂窝分布式爬虫的Item定义
    包含景点的各种信息字段
    """
    # 景点ID
    poi_id = scrapy.Field()
    # 景点名称
    name = scrapy.Field()
    # 景点链接
    link = scrapy.Field()
    # 城市
    city = scrapy.Field()
    # 景点图片
    image = scrapy.Field()
    # 景点简介
    summary = scrapy.Field()
    # 交通信息
    transport = scrapy.Field()
    # 门票信息
    ticket = scrapy.Field()
    # 开放时间
    opening_hours = scrapy.Field()
    # 位置信息
    location = scrapy.Field()
    # 用户评论
    comments = scrapy.Field()
    # 爬取时间戳
    crawl_time = scrapy.Field()
    # 爬取节点标识
    node_id = scrapy.Field()
    
    # 元数据字段，用于分布式爬虫的任务分配和状态跟踪
    # 任务ID
    task_id = scrapy.Field()
    # 任务类型（列表页/详情页）
    task_type = scrapy.Field()
    # 任务状态
    task_status = scrapy.Field()
    # 重试次数
    retry_times = scrapy.Field()
    # 处理时间
    process_time = scrapy.Field() 