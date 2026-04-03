import requests
import time
import statistics
from datetime import datetime
import json
import os
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor
import colorama
from colorama import Fore, Style

# 初始化colorama
colorama.init()

class PerformanceTest:
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results: Dict[str, List[float]] = {}
        # 区分需要认证和不需要认证的路由
        self.public_routes = {
            "首页": "/",
            "社区": "/community",
        }
        self.auth_routes = {
            "创作": "/create",
            "成就": "/achievements",
            "我的故事": "/my_stories",
            "个人主页": "/profile"
        }
        
        # 创建results目录（如果不存在）
        self.results_dir = "test_results"
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

    def measure_load_time(self, route: str, name: str) -> Tuple[float, int]:
        """测量单个页面的加载时间"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}{route}")
            load_time = time.time() - start_time
            return load_time, response.status_code
        except Exception as e:
            print(f"{Fore.RED}测试 {name} 失败: {e}{Style.RESET_ALL}")
            return -1, -1

    def run_single_test(self, name: str, route: str, iterations: int = 5) -> None:
        """对单个页面进行多次测试"""
        print(f"\n{Fore.CYAN}测试页面: {name}{Style.RESET_ALL}")
        times = []
        
        for i in range(iterations):
            load_time, status_code = self.measure_load_time(route, name)
            if load_time > 0:
                times.append(load_time)
                status = f"{Fore.GREEN}成功{Style.RESET_ALL}" if status_code == 200 else f"{Fore.RED}失败 ({status_code}){Style.RESET_ALL}"
                print(f"  测试 #{i+1}: {load_time:.3f}秒 - {status}")
            time.sleep(1)  # 避免请求过于频繁
        
        if times:
            self.test_results[name] = times

    def run_tests(self, iterations: int = 5) -> None:
        """运行所有页面的测试"""
        print(f"{Fore.YELLOW}开始性能测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        print(f"基础URL: {self.base_url}")
        print(f"每个页面测试次数: {iterations}")
        
        # 测试公开页面
        print(f"\n{Fore.CYAN}测试公开页面:{Style.RESET_ALL}")
        with ThreadPoolExecutor(max_workers=3) as executor:
            for name, route in self.public_routes.items():
                executor.submit(self.run_single_test, name, route, iterations)
        
        # 显示需要认证的页面已跳过
        print(f"\n{Fore.YELLOW}以下需要认证的页面已跳过:{Style.RESET_ALL}")
        for name in self.auth_routes.keys():
            print(f"  - {name}")
        
        self.generate_report()

    def generate_report(self) -> None:
        """生成测试报告"""
        print(f"\n{Fore.YELLOW}测试报告{Style.RESET_ALL}")
        print("-" * 50)
        
        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "results": {}
        }
        
        for name, times in self.test_results.items():
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            
            results["results"][name] = {
                "average": avg_time,
                "min": min_time,
                "max": max_time,
                "std_dev": std_dev,
                "samples": len(times)
            }
            
            print(f"\n{Fore.CYAN}{name}:{Style.RESET_ALL}")
            print(f"  平均加载时间: {Fore.GREEN}{avg_time:.3f}秒{Style.RESET_ALL}")
            print(f"  最短加载时间: {min_time:.3f}秒")
            print(f"  最长加载时间: {max_time:.3f}秒")
            print(f"  标准差: {std_dev:.3f}秒")
            print(f"  样本数: {len(times)}")
        
        # 保存结果到JSON文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.results_dir, f"performance_test_{timestamp}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n{Fore.GREEN}测试报告已保存到: {filename}{Style.RESET_ALL}")

def main():
    # 创建测试实例并运行测试
    tester = PerformanceTest()
    tester.run_tests(iterations=5)  # 每个页面测试5次

if __name__ == "__main__":
    main() 