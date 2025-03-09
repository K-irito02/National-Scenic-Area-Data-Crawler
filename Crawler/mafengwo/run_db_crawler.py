#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
马蜂窝景点爬虫启动脚本（数据库存储URL版本）
用于初始化Redis数据库并启动爬虫
支持全国景点爬虫
"""

import os
import sys
import time
import redis
import argparse
import subprocess
import glob
import json
from datetime import datetime

def check_redis_connection(host='localhost', port=6379, db=0, password=None):
    """检查Redis连接是否正常"""
    try:
        r = redis.Redis(host=host, port=port, db=db, password=password)
        r.ping()
        print(f"[+] Redis连接成功: {host}:{port}")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"[-] Redis连接失败: {str(e)}")
        return None

def clear_redis_data(r, spider_name, clear_all=False):
    """清空Redis中的爬虫数据"""
    # 清空URL队列
    if spider_name == "china_attractions_db":
        # 注意：不要删除cities_urls队列，否则爬虫将无法启动
        r.delete(f"{spider_name}:cities_urls")  # 现在我们删除cities_urls队列，然后重新初始化
        r.delete(f"{spider_name}:list_urls")
        r.delete(f"{spider_name}:detail_urls")
        
        # 重新初始化cities_urls队列
        r.lpush(f"{spider_name}:cities_urls", "https://www.mafengwo.cn/mdd/")
        print(f"[+] 已重新初始化城市URL队列: https://www.mafengwo.cn/mdd/")
        
        if clear_all:
            # 清空所有景点数据
            keys = r.keys("china:attraction:*")
            if keys:
                r.delete(*keys)
            # 清空城市数据
            city_keys = r.keys("china:city:*")
            if city_keys:
                r.delete(*city_keys)
            # 清空索引
            r.delete("china:attractions:all")
            # 清空去重过滤器
            r.delete(f"{spider_name}:cities:dupefilter")
            r.delete(f"{spider_name}:list:dupefilter")
            r.delete(f"{spider_name}:detail:dupefilter")
            print("[+] 已清空所有全国爬虫数据")
        else:
            print("[+] 已清空全国爬虫队列数据")

def start_crawler(spider_name, settings_file=None, log_file=None, job_dir=None, node_id=None, is_master=False, task_type=None, redis_host=None, checkpoint_interval=300):
    """启动爬虫"""
    cmd = ["scrapy", "crawl", spider_name]
    
    if settings_file:
        cmd.extend(["-s", f"SETTINGS_MODULE={settings_file}"])
    
    if job_dir:
        # 创建job_dir目录
        os.makedirs(job_dir, exist_ok=True)
        cmd.extend(["-s", f"JOBDIR={job_dir}"])
    
    if log_file:
        # 创建logs目录
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        cmd.extend(["--logfile", log_file])
    
    if node_id:
        cmd.extend(["-s", f"NODE_ID={node_id}"])
    
    if is_master:
        cmd.extend(["-a", "is_master=True"])
    
    if task_type:
        cmd.extend(["-a", f"task_type={task_type}"])
    
    if redis_host:
        cmd.extend(["-a", f"redis_host={redis_host}"])
    
    # 添加检查点间隔参数
    cmd.extend(["-s", f"CHECKPOINT_INTERVAL={checkpoint_interval}"])
    
    print(f"[+] 启动爬虫: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(cmd)
        return process
    except Exception as e:
        print(f"[-] 启动爬虫失败: {str(e)}")
        return None

def monitor_redis(r, spider_name, interval=10):
    """监控Redis数据库状态"""
    try:
        while True:
            if spider_name == "beijing_attractions_db":
                # 获取列表页URL队列长度
                list_urls_count = r.llen(f"{spider_name}:list_urls")
                # 获取详情页URL队列长度
                detail_urls_count = r.llen(f"{spider_name}:detail_urls")
                # 获取已保存的景点数量
                attraction_count = r.scard("beijing:attractions:all")
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"列表页URL队列: {list_urls_count}, "
                      f"详情页URL队列: {detail_urls_count}, "
                      f"已保存的景点: {attraction_count}")
            elif spider_name == "china_attractions_db":
                # 获取城市列表页URL队列长度
                cities_urls_count = r.llen(f"{spider_name}:cities_urls")
                # 获取列表页URL队列长度
                list_urls_count = r.llen(f"{spider_name}:list_urls")
                # 获取详情页URL队列长度
                detail_urls_count = r.llen(f"{spider_name}:detail_urls")
                # 获取已保存的景点数量
                attraction_count = r.scard("china:attractions:all")
                # 获取已保存的城市数量
                city_count = len(r.keys("china:city:info:*"))
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"城市列表页URL队列: {cities_urls_count}, "
                      f"景点列表页URL队列: {list_urls_count}, "
                      f"详情页URL队列: {detail_urls_count}, "
                      f"已保存的城市: {city_count}, "
                      f"已保存的景点: {attraction_count}")
            
            # 如果所有队列都为空且已经有景点数据，可能爬虫已经完成
            if spider_name == "beijing_attractions_db":
                if list_urls_count == 0 and detail_urls_count == 0 and attraction_count > 0:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 所有队列为空，爬虫可能已完成")
            elif spider_name == "china_attractions_db":
                if cities_urls_count == 0 and list_urls_count == 0 and detail_urls_count == 0 and attraction_count > 0:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 所有队列为空，爬虫可能已完成")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[!] 监控已停止")

def run_python_script(script_path):
    """运行Python脚本"""
    try:
        process = subprocess.Popen([sys.executable, script_path])
        return process
    except Exception as e:
        print(f"[-] 运行脚本失败: {str(e)}")
        return None

def check_data_consistency(r, spider_name):
    """检查数据一致性"""
    print("[+] 开始检查数据一致性")
    
    if spider_name == "china_attractions_db":
        # 获取所有景点的键
        attraction_keys = r.smembers("china:attractions:all")
        
        if not attraction_keys:
            print("[-] 未找到任何全国景点数据")
            return
        
        print(f"[+] 找到 {len(attraction_keys)} 个全国景点数据")
        
        # 检查每个景点数据是否完整
        incomplete_count = 0
        for key in attraction_keys:
            data = r.get(key)
            if data:
                try:
                    attraction = json.loads(data)
                    # 检查必要字段是否存在
                    required_fields = ['name', 'poi_id', 'link', 'city']
                    missing_fields = [field for field in required_fields if field not in attraction]
                    if missing_fields:
                        print(f"[-] 景点数据不完整: {key}, 缺少字段: {', '.join(missing_fields)}")
                        incomplete_count += 1
                except json.JSONDecodeError as e:
                    print(f"[-] 景点数据格式错误: {key}, 错误: {str(e)}")
                    incomplete_count += 1
            else:
                print(f"[-] 景点数据不存在: {key}")
                incomplete_count += 1
        
        if incomplete_count > 0:
            print(f"[-] 发现 {incomplete_count} 个不完整的景点数据")
        else:
            print("[+] 所有景点数据完整")

def list_checkpoints(spider_name, node_id=None):
    """列出所有检查点"""
    checkpoint_dir = f'crawls/{spider_name}'
    if node_id:
        checkpoint_dir = f'{checkpoint_dir}_{node_id}'
    checkpoint_dir = f'{checkpoint_dir}/checkpoints'
    
    if not os.path.exists(checkpoint_dir):
        print(f"[-] 未找到检查点目录: {checkpoint_dir}")
        return
    
    checkpoint_files = glob.glob(f"{checkpoint_dir}/checkpoint_*.json")
    if not checkpoint_files:
        print(f"[-] 未找到任何检查点文件")
        return
    
    # 按时间排序
    checkpoint_files.sort(key=os.path.getmtime, reverse=True)
    
    print(f"[+] 找到 {len(checkpoint_files)} 个检查点文件:")
    for i, file in enumerate(checkpoint_files):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                timestamp = data.get('timestamp', '未知时间')
                node = data.get('node_id', '未知节点')
                task = data.get('task_type', '未知任务')
                
                # 获取数据统计
                cities = data.get('data_status', {}).get('cities', 0)
                attractions = data.get('data_status', {}).get('attractions', 0)
                
                print(f"  {i+1}. [{timestamp}] 节点: {node}, 任务: {task}, 城市: {cities}, 景点: {attractions}")
        except Exception as e:
            print(f"  {i+1}. {os.path.basename(file)} (读取失败: {str(e)})")

def save_checkpoint_status(r, spider_name, node_id, status_data):
    """保存检查点状态到Redis"""
    try:
        r.set(
            f"{spider_name}:checkpoint:{node_id}", 
            json.dumps(status_data, ensure_ascii=False)
        )
        print(f"[+] 已保存检查点状态到Redis")
        return True
    except Exception as e:
        print(f"[-] 保存检查点状态到Redis失败: {str(e)}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="马蜂窝景点爬虫启动脚本")
    parser.add_argument("--spider", type=str, default="china_attractions_db", 
                        choices=["beijing_attractions_db", "china_attractions_db"],
                        help="要运行的爬虫名称")
    parser.add_argument("--redis-host", type=str, default="localhost", help="Redis服务器地址")
    parser.add_argument("--redis-port", type=int, default=6379, help="Redis服务器端口")
    parser.add_argument("--redis-db", type=int, default=0, help="Redis数据库编号")
    parser.add_argument("--redis-password", type=str, default="3143285505", help="Redis密码")
    parser.add_argument("--clear", action="store_true", help="清空Redis中的爬虫队列数据")
    parser.add_argument("--clear-all", action="store_true", help="清空Redis中的所有爬虫数据")
    parser.add_argument("--monitor", action="store_true", help="监控Redis数据库状态")
    parser.add_argument("--node-id", type=str, default="node1", help="节点ID")
    parser.add_argument("--master", action="store_true", help="是否为主节点")
    parser.add_argument("--task-type", type=str, default="all", 
                        choices=["all", "cities", "list", "detail"],
                        help="任务类型")
    parser.add_argument("--settings", type=str, default="settings_distributed", help="设置文件名")
    parser.add_argument("--log-file", type=str, help="日志文件路径")
    parser.add_argument("--job-dir", type=str, help="任务目录路径")
    parser.add_argument("--export", action="store_true", help="导出数据")
    parser.add_argument("--check-consistency", action="store_true", help="检查数据一致性")
    # 添加断点续爬相关参数
    parser.add_argument("--resume", action="store_true", help="从断点恢复爬虫")
    parser.add_argument("--list-checkpoints", action="store_true", help="列出所有检查点")
    parser.add_argument("--checkpoint-interval", type=int, default=300, help="检查点保存间隔（秒）")
    parser.add_argument("--auto-resume", action="store_true", help="自动从最新检查点恢复")
    
    args = parser.parse_args()
    
    # 检查Redis连接
    r = check_redis_connection(
        host=args.redis_host,
        port=args.redis_port,
        db=args.redis_db,
        password=args.redis_password
    )
    
    if not r:
        print("[-] 无法连接到Redis，请检查配置")
        return
    
    # 列出检查点
    if args.list_checkpoints:
        list_checkpoints(args.spider, args.node_id)
        return
    
    # 清空Redis数据
    if args.clear or args.clear_all:
        clear_redis_data(r, args.spider, args.clear_all)
        if not args.monitor and not args.resume:  # 如果不需要监控或恢复，则退出
            return
    
    # 检查数据一致性
    if args.check_consistency:
        check_data_consistency(r, args.spider)
        return
    
    # 导出数据
    if args.export:
        export_script = os.path.join(os.path.dirname(__file__), "export_data.py")
        if os.path.exists(export_script):
            print(f"[+] 运行数据导出脚本: {export_script}")
            run_python_script(export_script)
        else:
            print(f"[-] 数据导出脚本不存在: {export_script}")
        return
    
    # 设置日志文件
    if not args.log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.log_file = f"logs/{args.spider}_{args.node_id}_{timestamp}.log"
    
    # 设置任务目录
    if not args.job_dir:
        args.job_dir = f"crawls/{args.spider}_{args.node_id}"
    
    # 如果是恢复模式，设置相关参数
    if args.resume or args.auto_resume:
        # 检查是否存在检查点
        checkpoint_dir = f'{args.job_dir}/checkpoints'
        latest_checkpoint_file = f"{checkpoint_dir}/checkpoint_{args.node_id}_latest.json"
        
        if os.path.exists(latest_checkpoint_file):
            try:
                with open(latest_checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
                print(f"[+] 找到最新检查点: {checkpoint_data['timestamp']}")
                
                # 保存检查点状态到Redis
                save_checkpoint_status(r, args.spider, args.node_id, checkpoint_data)
                
                print(f"[+] 将从断点恢复爬虫")
            except Exception as e:
                print(f"[-] 读取检查点文件失败: {str(e)}")
                if not args.auto_resume:  # 如果不是自动恢复模式，则退出
                    return
        else:
            print(f"[-] 未找到检查点文件: {latest_checkpoint_file}")
            if not args.auto_resume:  # 如果不是自动恢复模式，则退出
                return

    # 启动爬虫
    process = start_crawler(
        spider_name=args.spider,
        settings_file=args.settings,
        log_file=args.log_file,
        job_dir=args.job_dir,
        node_id=args.node_id,
        is_master=args.master,
        task_type=args.task_type,
        redis_host=args.redis_host,
        checkpoint_interval=args.checkpoint_interval
    )
    
    # 监控Redis状态
    if args.monitor and process:
        try:
            print("[!] 正在运行爬虫，按 Ctrl+C 停止")
            print("[!] 注意：可能需要多按几次 Ctrl+C 才能完全停止所有浏览器窗口")
            monitor_redis(r, args.spider)
        except KeyboardInterrupt:
            print("\n[!] 收到终止信号，正在停止爬虫...")
            if process:
                try:
                    # 发送SIGTERM信号
                    import signal
                    process.send_signal(signal.SIGTERM)
                    print("[!] 已发送终止信号")
                    
                    # 等待最多30秒
                    print("[!] 等待爬虫关闭...")
                    for _ in range(30):
                        if process.poll() is not None:  # 进程已结束
                            print("[!] 爬虫已正常关闭")
                            break
                        time.sleep(1)
                    
                    # 如果30秒后进程仍未结束，强制终止
                    if process.poll() is None:
                        print("[!] 爬虫未能正常关闭，强制终止")
                        process.terminate()
                        time.sleep(2)
                        if process.poll() is None:
                            print("[!] 强制终止失败，尝试使用SIGKILL信号")
                            try:
                                # 在Windows上可能不支持SIGKILL
                                import os
                                os.kill(process.pid, 9)  # SIGKILL
                            except:
                                print("[!] 无法使用SIGKILL信号，请手动关闭浏览器窗口")
                except Exception as e:
                    print(f"[!] 终止爬虫时出错: {str(e)}")
                    try:
                        process.terminate()
                    except:
                        pass
            print("[!] 程序已停止")

if __name__ == "__main__":
    main() 