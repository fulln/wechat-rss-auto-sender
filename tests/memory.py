"""
测试内存记录文件
用于存储测试过程中的临时数据和避免路径问题
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class TestMemory:
    """测试内存管理类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.memory_file = self.project_root / "tests" / "test_memory.json"
        self.temp_files = []
        self.test_data = {}
        self.load_memory()
    
    def load_memory(self):
        """加载内存数据"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.test_data = data.get('test_data', {})
                    self.temp_files = data.get('temp_files', [])
            except Exception as e:
                print(f"加载测试内存失败: {e}")
                self.test_data = {}
                self.temp_files = []
    
    def save_memory(self):
        """保存内存数据"""
        try:
            data = {
                'test_data': self.test_data,
                'temp_files': self.temp_files,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存测试内存失败: {e}")
    
    def add_test_data(self, test_name: str, data: Dict[str, Any]):
        """添加测试数据"""
        self.test_data[test_name] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.save_memory()
    
    def get_test_data(self, test_name: str) -> Dict[str, Any]:
        """获取测试数据"""
        return self.test_data.get(test_name, {}).get('data', {})
    
    def add_temp_file(self, file_path: str):
        """添加临时文件路径"""
        if file_path not in self.temp_files:
            self.temp_files.append(file_path)
            self.save_memory()
    
    def get_project_root(self) -> Path:
        """获取项目根目录"""
        return self.project_root
    
    def get_src_path(self) -> Path:
        """获取src目录路径"""
        return self.project_root / "src"
    
    def get_tests_path(self) -> Path:
        """获取tests目录路径"""
        return self.project_root / "tests"
    
    def get_cache_path(self) -> Path:
        """获取cache目录路径"""
        cache_path = self.project_root / "cache"
        cache_path.mkdir(exist_ok=True)
        return cache_path
    
    def get_logs_path(self) -> Path:
        """获取logs目录路径"""
        logs_path = self.project_root / "logs"
        logs_path.mkdir(exist_ok=True)
        return logs_path
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"删除临时文件失败 {file_path}: {e}")
        self.temp_files = []
        self.save_memory()
    
    def clear_test_data(self):
        """清除所有测试数据"""
        self.test_data = {}
        self.save_memory()


# 全局测试内存实例
test_memory = TestMemory()

# 常用路径快捷函数
def get_project_root() -> Path:
    """获取项目根目录"""
    return test_memory.get_project_root()

def get_src_path() -> Path:
    """获取src目录路径"""
    return test_memory.get_src_path()

def get_tests_path() -> Path:
    """获取tests目录路径"""
    return test_memory.get_tests_path()

def get_cache_path() -> Path:
    """获取cache目录路径"""
    return test_memory.get_cache_path()

def get_logs_path() -> Path:
    """获取logs目录路径"""
    return test_memory.get_logs_path()
