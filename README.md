# 马蜂窝景点数据分布式爬虫

基于Scrapy-Redis架构的分布式景点数据采集系统，支持全国城市和景点信息的持续爬取。

## 目录

- [项目概述](#项目概述)
- [项目结构](#项目结构)
- [功能特点](#功能特点)
- [环境要求](#环境要求)
- [安装依赖](#安装依赖)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
  - [启动参数详解](#启动参数详解)
  - [基本爬虫启动](#基本爬虫启动)
  - [分布式爬虫启动](#分布式爬虫启动)
  - [断点续爬功能](#断点续爬功能)
  - [数据导出](#数据导出)
- [数据结构](#数据结构)
- [工作原理](#工作原理)
- [常见问题排解](#常见问题排解)
- [注意事项](#注意事项)
- [性能优化](#性能优化)
- [更新日志](#更新日志)

## 项目概述

这是一个基于Scrapy和Redis的马蜂窝景点爬虫系统，用于爬取马蜂窝网站上的全国各地景点信息。该系统采用分布式架构，支持多节点并行爬取，使用Redis作为核心数据存储和消息队列，能够实现高效稳定的大规模数据采集。

本项目特别适合需要获取全国旅游景点数据的研究人员、数据分析师和旅游行业从业者。通过本系统，您可以获取到景点名称、地址、门票信息、开放时间等详细数据，为旅游行业分析和决策提供数据支持。

## 项目结构

```
mafengwo/
├── spiders/                      # 爬虫文件目录
│   ├── __init__.py               # 初始化文件
│   └── china_attractions_db.py   # 中国景点爬虫
├── __init__.py                   # 包初始化文件
├── items_distributed.py          # 定义数据项结构
├── middlewares.py                # 中间件（随机UA、延迟等）
├── pipelines.py                  # 数据处理管道
├── settings_distributed.py       # 分布式爬虫配置文件
├── run_db_crawler.py             # 爬虫启动控制脚本
├── export_data.py                # 数据导出脚本
├── logs/                         # 日志文件目录
├── crawls/                       # 爬虫状态和断点续爬目录
└── results/                      # 结果输出目录
```

### 核心文件说明

- **china_attractions_db.py**: 爬虫主体实现，包含爬取逻辑和数据处理
- **run_db_crawler.py**: 爬虫启动脚本，提供命令行接口和参数处理
- **export_data.py**: 数据导出工具，支持多种格式和筛选条件
- **settings_distributed.py**: 分布式配置文件，包含Redis和爬虫行为设置
- **items_distributed.py**: 定义数据结构和字段映射

## 功能特点

- **全面数据采集**：支持爬取全国各省市的景点信息，包括景点名称、地址、门票信息、开放时间等详细数据
- **分布式架构**：基于Scrapy-Redis架构，支持多机器、多节点并行爬取
- **断点续爬**：自动保存爬取状态，支持中断后从断点恢复爬取
- **灵活配置**：提供丰富的配置选项，可根据需求调整爬虫行为
- **数据导出**：支持将爬取结果导出为JSON或CSV格式
- **监控功能**：实时监控爬虫状态和Redis队列
- **任务分类**：支持按城市列表、景点列表、景点详情分类爬取
- **反爬处理**：内置随机User-Agent、随机延迟等反爬策略
- **数据一致性检查**：提供数据完整性和一致性验证工具

## 环境要求

- Python 3.6+
- Redis 5.0+
- Scrapy 2.5+
- Scrapy-Redis 0.7.0+
- Selenium 4.0+
- Microsoft Edge浏览器及对应版本的EdgeDriver

## 安装依赖

### 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 安装所需包

```bash
# 安装基本依赖
pip install scrapy scrapy-redis selenium redis

# 安装其他依赖
pip install pandas requests lxml
```

### 安装EdgeDriver

1. 确认您的Edge浏览器版本
2. 从[Microsoft Edge WebDriver下载页面](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)下载对应版本的WebDriver
3. 将下载的EdgeDriver放置在系统PATH路径下或项目目录中

## 配置说明

### 核心配置文件

主要配置文件为`settings_distributed.py`，包含以下关键配置：

1. **基本爬虫配置**
   - `USER_AGENT`：浏览器标识
   - `CONCURRENT_REQUESTS`：并发请求数（默认为1）
   - `DOWNLOAD_DELAY`：下载延迟（默认为5秒）
   - `RANDOMIZE_DOWNLOAD_DELAY`：随机化下载延迟（默认开启）

2. **Redis连接配置**
   - `REDIS_PARAMS`：Redis连接参数
     ```python
     REDIS_PARAMS = {
         'host': 'localhost',
         'port': 6379,
         'db': 0,
         'password': '3143285505',  # 默认密码，请修改为您自己的密码
         'socket_timeout': 30,
         'socket_connect_timeout': 30,
         'retry_on_timeout': True,
         'encoding': 'utf-8',
     }
     ```

3. **分布式配置**
   - `SCHEDULER`：使用Redis调度器
   - `DUPEFILTER_CLASS`：使用Redis去重过滤器
   - `SCHEDULER_PERSIST`：爬虫结束后不清空Redis队列
   - `SCHEDULER_QUEUE_CLASS`：使用优先级队列

### 自定义配置

可以通过命令行参数修改默认配置，例如Redis连接信息：

```bash
python run_db_crawler.py --redis-host 192.168.1.100 --redis-port 6379 --redis-password yourpassword
```

## 使用方法

### 启动参数详解

`run_db_crawler.py`脚本支持以下参数：

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--spider` | 爬虫名称 | beijing_attractions_db | --spider china_attractions_db |
| `--redis-host` | Redis服务器地址 | localhost | --redis-host 192.168.1.100 |
| `--redis-port` | Redis服务器端口 | 6379 | --redis-port 6380 |
| `--redis-db` | Redis数据库编号 | 0 | --redis-db 1 |
| `--redis-password` | Redis密码 | 3143285505 | --redis-password yourpassword |
| `--clear` | 清空Redis中的爬虫队列数据 | - | --clear |
| `--clear-all` | 清空Redis中的所有爬虫数据 | - | --clear-all |
| `--monitor` | 监控Redis数据库状态 | - | --monitor |
| `--node-id` | 节点ID | node1 | --node-id worker2 |
| `--master` | 是否为主节点 | - | --master |
| `--task-type` | 任务类型 | all | --task-type cities |
| `--settings` | 设置文件名 | settings_distributed | --settings my_settings |
| `--log-file` | 日志文件路径 | 自动生成 | --log-file logs/my_log.log |
| `--job-dir` | 任务目录路径 | 自动生成 | --job-dir crawls/my_job |
| `--export` | 导出数据 | - | --export |
| `--check-consistency` | 检查数据一致性 | - | --check-consistency |
| `--resume` | 从断点恢复爬虫 | - | --resume |
| `--list-checkpoints` | 列出所有检查点 | - | --list-checkpoints |
| `--checkpoint-interval` | 检查点保存间隔（秒） | 300 | --checkpoint-interval 600 |
| `--auto-resume` | 自动从最新检查点恢复 | - | --auto-resume |

**关键参数说明**：

- **task-type**: 控制爬虫执行的任务类型
  - `all`: 执行所有任务（城市列表、景点列表、景点详情）
  - `cities`: 只爬取城市列表
  - `list`: 只爬取景点列表
  - `detail`: 只爬取景点详情

- **master**: 主节点标志，只有主节点会初始化URL队列，分布式部署时只需要一个主节点

- **node-id**: 节点标识，在分布式部署中用于区分不同节点，断点续爬也依赖此ID

- **resume/auto-resume**: 断点续爬功能，resume会严格检查断点文件存在才会继续，auto-resume则会在找不到断点时也继续执行

### 基本爬虫启动

启动单机爬虫（包含所有功能）：

```bash
python run_db_crawler.py --spider china_attractions_db --master --task-type all --redis-host localhost --monitor
```

此命令会：
1. 连接本地Redis服务器
2. 初始化URL队列（因为是主节点）
3. 开始爬取全国城市和景点数据
4. 开启监控显示爬虫状态

### 分布式爬虫启动

分布式部署需要先配置好Redis服务器，然后在不同机器上启动爬虫：

1. **主节点启动**（负责初始化URL队列 cities）：

```bash
python run_db_crawler.py --spider china_attractions_db --master --task-type cities --redis-host localhost --node-id master --monitor
```

2. **从节点启动**（多个工作节点 list\detail）：

```bash
# 工作节点1 - 负责爬取景点列表
python run_db_crawler.py --spider china_attractions_db --task-type list --redis-host localhost --node-id worker1 --monitor
```

```bash
# 工作节点2 - 负责爬取景点详情
python run_db_crawler.py --spider china_attractions_db --task-type detail --redis-host localhost --node-id worker2 --monitor
```

```bash
# 工作节点3 - 负责爬取景点详情
python run_db_crawler.py --spider china_attractions_db --task-type detail --redis-host localhost --node-id worker3 --monitor
```

**注意**：
- 所有节点必须连接到同一个Redis服务器
- 只需要一个主节点（--master），其他都是工作节点
- 每个节点需要设置不同的node-id
- 可以根据需要调整任务类型分配，例如多个节点都执行detail任务

### 断点续爬功能

爬虫支持在意外中断后从上次停止的地方继续爬取。断点保存在`crawls/{spider_name}_{node_id}/checkpoints/`目录下。

1. **列出所有断点**：

```bash
python run_db_crawler.py --spider china_attractions_db --list-checkpoints --node-id node1
```

2. **从指定断点恢复**：

```bash
python run_db_crawler.py --spider china_attractions_db --resume --node-id node1 --redis-host localhost --monitor
```

3. **自动从最新断点恢复**（即使找不到断点也会继续）：

```bash
python run_db_crawler.py --spider china_attractions_db --auto-resume --node-id node1 --redis-host localhost --monitor
```

4. **设置断点保存间隔**：

```bash
python run_db_crawler.py --spider china_attractions_db --master --checkpoint-interval 600 --redis-host localhost --monitor
```

断点续爬原理：
- 爬虫会定期（默认每300秒）保存当前状态到检查点文件
- 爬虫正常关闭或收到中断信号时会自动保存检查点
- Redis存储了所有队列和已处理的URL，确保不会重复爬取
- 恢复时会自动重新连接Redis并继续处理未完成的队列

### 数据导出

使用`export_data.py`脚本导出爬取的数据：

```bash
python export_data.py --data-type china --format json --output results/china_attractions.json
```

导出参数说明：

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--data-type` | 要导出的数据类型 | beijing | --data-type china |
| `--format` | 输出文件格式 | json | --format csv |
| `--output` | 输出文件路径 | 自动生成 | --output results/my_data.json |
| `--export-cities` | 是否导出城市数据 | - | --export-cities |
| `--city-id` | 要导出的城市ID | - | --city-id 10065 |
| `--city-name` | 要导出的城市名称 | - | --city-name 北京 |
| `--redis-host` | Redis服务器地址 | localhost | --redis-host 192.168.1.100 |
| `--redis-port` | Redis服务器端口 | 6379 | --redis-port 6380 |
| `--redis-password` | Redis密码 | 3143285505 | --redis-password yourpassword |

可用的数据类型：
- `beijing`: 北京景点数据
- `china`: 全国景点数据
- `city`: 指定城市的景点数据（需要提供--city-id）
- `city-name`: 指定城市名称的景点数据（需要提供--city-name）
- `all`: 所有城市的景点数据

### 使用示例（cd mafengwo）

1. **按城市ID导出**：

```bash
python export_data.py --data-type=city --city-id=10065
```

2. **按城市名称导出**：

```bash
python export_data.py --data-type=city-name --city-name=北京
```

3. **全部导出所有城市景点**：

```bash
python export_data.py --data-type=all
```

4. **导出为CSV格式**：

```bash
python export_data.py --data-type=china --format=csv --output=results/china_attractions.csv
```

5. **导出城市数据**：

```bash
python export_data.py --export-cities --output=results/china_cities.json
```

6. **导出北京景点到MongoDB**

```bash
python export_data.py --data-type beijing --format mongodb
```

7. **导出指定城市到MongoDB**

```bash
python export_data.py --data-type city --city-id 123 --format mongodb
```

8. **使用自定义MongoDB配置**
```bash
python export_data.py --data-type china --format mongodb --mongodb-host 192.168.1.100 --mongodb-port 27018
```

这些命令将根据指定的参数导出相应的景点数据，并保存到指定的文件或目录中。

## 数据结构

### 城市数据

```json
{
  "name": "城市名称",
  "link": "城市链接",
  "city_id": "城市ID",
  "attractions_list_url": "景点列表页URL",
  "province": "所属省份",
  "crawl_time": "爬取时间"
}
```

### 景点数据

```json
{
  "name": "景点名称",
  "poi_id": "景点ID",
  "link": "景点链接",
  "city": "所在城市",
  "city_id": "城市ID",
  "image": "图片URL",
  "summary": "简介",
  "transport": "交通信息",
  "ticket": "门票信息",
  "opening_hours": "开放时间",
  "location": "位置信息",
  "comments": ["评论1", "评论2", ...],
  "crawl_time": "爬取时间",
  "node_id": "爬取节点ID"
}
```

## 工作原理

### 爬虫工作流程

1. **初始化阶段**：
   - 主节点初始化Redis队列，添加起始URL（https://www.mafengwo.cn/mdd/）
   - 从节点连接到Redis服务器，等待URL任务

2. **城市爬取阶段**：
   - 爬取全国城市列表页面，提取城市信息
   - 将城市信息保存到Redis，同时添加景点列表URL到队列

3. **景点列表爬取阶段**：
   - 爬取城市景点列表页面，提取景点信息
   - 将景点基本信息保存到Redis，同时添加景点详情URL到队列

4. **景点详情爬取阶段**：
   - 爬取景点详情页面，提取详细信息
   - 将完整景点信息保存到Redis数据库

### 断点续爬工作原理

1. **状态保存**：
   - 爬虫在运行过程中会定期（默认300秒）保存状态到检查点文件
   - 检查点文件保存在`crawls/{spider_name}_{node_id}/checkpoints/`目录下
   - 包含当前爬取状态、队列信息和数据统计

2. **状态恢复**：
   - 爬虫启动时检查是否需要恢复（--resume或--auto-resume）
   - 加载最新的检查点文件，恢复爬取状态
   - 通过Redis队列继续处理未完成的URL

## 常见问题排解

1. **Redis连接失败**
   - 检查Redis服务器是否正常运行
   - 验证IP地址、端口和密码是否正确
   - 确认防火墙设置是否允许连接

   ```bash
   # 测试Redis连接
   redis-cli -h <host> -p <port> -a <password> ping
   ```

2. **爬虫无法启动**
   - 检查Python环境和依赖包是否正确安装
   - 查看日志文件中的错误信息
   - 确保EdgeDriver与Edge浏览器版本匹配

3. **爬虫运行缓慢**
   - 可能是网络问题或服务器限制
   - 尝试增加`DOWNLOAD_DELAY`参数值
   - 减少`CONCURRENT_REQUESTS`值降低并发数

4. **断点续爬失败**
   - 确保node-id与之前的爬取任务一致
   - 检查Redis服务器连接是否正常
   - 验证检查点文件是否存在且完整

5. **数据不完整**
   - 可能是页面结构变化导致解析失败
   - 查看日志文件中的警告和错误信息
   - 使用`--check-consistency`参数检查数据一致性

6. **Selenium相关问题**
   - 确保已安装正确版本的EdgeDriver
   - 检查浏览器是否能正常启动
   - 尝试禁用无头模式进行调试

## 注意事项

1. **反爬机制**：马蜂窝网站有反爬虫机制，爬虫设置了随机延迟和User-Agent轮换以减少被封风险。请合理设置并发数和延迟时间，避免频繁请求

2. **资源占用**：爬虫使用Selenium模拟浏览器，会占用较多系统资源。如果服务器资源有限，建议减少并发数

3. **Redis内存**：长时间运行可能会占用大量Redis内存，请确保Redis服务器有足够空间或设置合理的数据过期策略

4. **代码维护**：网站结构可能变化，如遇到爬取失败，可能需要更新爬虫代码中的选择器和解析逻辑

5. **数据备份**：定期导出和备份爬取的数据，避免Redis服务器意外重启导致数据丢失

6. **法律合规**：请遵守网站robots.txt规则和使用条款，合理使用爬虫

## 性能优化

为了提高爬虫性能和稳定性，可以考虑以下优化措施：

1. **调整并发数和延迟**：
   - 根据服务器性能和网络条件调整`CONCURRENT_REQUESTS`和`DOWNLOAD_DELAY`
   - 对于高性能服务器，可以适当增加并发数
   - 对于不稳定网络，可以增加延迟和重试次数

2. **使用代理IP**：
   - 在`settings_distributed.py`中配置代理IP池
   - 启用代理中间件轮换使用不同IP

3. **优化Redis配置**：
   - 调整Redis内存限制和过期策略
   - 定期清理不需要的数据
   - 考虑使用Redis集群提高性能

4. **分布式部署优化**：
   - 根据任务类型合理分配节点
   - 城市和列表页爬取节点可以少一些
   - 详情页爬取节点可以多一些

## 更新日志

### v1.0.0 (2024-03-05)
- 初始版本发布
- 支持全国景点数据爬取
- 实现分布式架构和断点续爬

### v0.9.0 (2024-02-22)
- 测试版本
- 实现基本爬虫功能
- 添加数据导出工具 