#!/usr/bin/env python3
"""
测试文件迁移和重构脚本
用于将根目录下的测试文件移动到tests目录并转换为pytest格式
"""

import shutil
from pathlib import Path
from typing import List, Dict

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"


class TestMigrator:
    """测试文件迁移器"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.tests_dir = TESTS_DIR
        self.migrated_files = []
        self.migration_log = []
    
    def find_root_test_files(self) -> List[Path]:
        """查找根目录下的测试文件"""
        test_files = []
        
        # 搜索模式
        patterns = [
            "*test*.py",
            "test_*.py",
            "*_test.py"
        ]
        
        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                # 排除已经在tests目录下的文件
                if not file_path.is_relative_to(self.tests_dir):
                    test_files.append(file_path)
        
        return list(set(test_files))  # 去重
    
    def analyze_test_file(self, file_path: Path) -> Dict[str, any]:
        """分析测试文件结构"""
        analysis = {
            'uses_pytest': False,
            'uses_unittest': False,
            'has_main_block': False,
            'has_async_functions': False,
            'imports': [],
            'functions': [],
            'classes': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # 检查pytest使用
                if 'import pytest' in line or 'from pytest' in line:
                    analysis['uses_pytest'] = True
                
                # 检查unittest使用
                if 'import unittest' in line or 'from unittest' in line:
                    analysis['uses_unittest'] = True
                
                # 检查主函数块
                if line.startswith('if __name__ == "__main__"'):
                    analysis['has_main_block'] = True
                
                # 检查异步函数
                if line.startswith('async def'):
                    analysis['has_async_functions'] = True
                
                # 收集导入
                if line.startswith('import ') or line.startswith('from '):
                    analysis['imports'].append(line)
                
                # 收集函数
                if line.startswith('def '):
                    func_name = line.split('(')[0].replace('def ', '')
                    analysis['functions'].append(func_name)
                
                # 收集类
                if line.startswith('class '):
                    class_name = line.split('(')[0].replace('class ', '').replace(':', '')
                    analysis['classes'].append(class_name)
        
        except Exception as e:
            print(f"分析文件失败 {file_path}: {e}")
        
        return analysis
    
    def generate_pytest_template(self, original_file: Path, analysis: Dict) -> str:
        """生成pytest测试模板"""
        file_name = original_file.stem
        
        template = f'''"""
{file_name}的pytest版本
从根目录迁移并转换为标准pytest测试
"""

import pytest
from unittest.mock import Mock, patch'''
        
        if analysis['has_async_functions']:
            template += ', AsyncMock'
        
        template += '''

from tests.test_utils import TestDataGenerator, TestAssertions
from tests.memory import test_memory, get_project_root


class Test{class_name}:
    """测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.test_data_gen = TestDataGenerator()
        self.assertions = TestAssertions()
        self.test_memory = test_memory
    
    def teardown_method(self):
        """测试后清理"""
        pass
'''.format(class_name=file_name.replace('_', '').replace('test', '').title())
        
        # 添加基本测试方法
        for func_name in analysis['functions']:
            if func_name.startswith('test'):
                template += f'''
    def {func_name}_pytest(self):
        """pytest版本的{func_name}"""
        # TODO: 实现pytest版本的测试逻辑
        pass
'''
        
        # 如果有异步函数，添加异步测试示例
        if analysis['has_async_functions']:
            template += '''
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """异步功能测试"""
        # TODO: 实现异步测试逻辑
        pass
'''
        
        template += '''

# 可以用于手动测试的函数
def manual_test():
    """手动测试函数"""
    print("运行手动测试...")
    # TODO: 实现手动测试逻辑
    print("手动测试完成！")


if __name__ == "__main__":
    manual_test()
'''
        
        return template
    
    def migrate_file(self, file_path: Path, backup: bool = True) -> bool:
        """迁移单个文件"""
        try:
            # 分析文件
            analysis = self.analyze_test_file(file_path)
            
            # 如果已经使用pytest，只需移动
            if analysis['uses_pytest']:
                new_path = self.tests_dir / file_path.name
                if backup:
                    backup_path = self.project_root / f"{file_path.name}.backup"
                    shutil.copy2(file_path, backup_path)
                
                shutil.move(str(file_path), str(new_path))
                self.migration_log.append(f"移动pytest文件: {file_path.name} -> tests/{file_path.name}")
                
            else:
                # 生成新的pytest版本
                pytest_content = self.generate_pytest_template(file_path, analysis)
                
                # 创建新文件名
                new_name = f"test_{file_path.stem.replace('test_', '').replace('_test', '')}_migrated.py"
                new_path = self.tests_dir / new_name
                
                # 写入新文件
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(pytest_content)
                
                # 备份原文件
                if backup:
                    backup_path = self.project_root / f"{file_path.name}.backup"
                    shutil.copy2(file_path, backup_path)
                
                # 删除原文件（可选）
                # file_path.unlink()
                
                self.migration_log.append(f"转换文件: {file_path.name} -> tests/{new_name}")
            
            self.migrated_files.append(new_path)
            return True
            
        except Exception as e:
            print(f"迁移文件失败 {file_path}: {e}")
            return False
    
    def run_migration(self, backup: bool = True) -> None:
        """运行完整迁移"""
        print("开始测试文件迁移...")
        print(f"项目根目录: {self.project_root}")
        print(f"测试目录: {self.tests_dir}")
        
        # 确保tests目录存在
        self.tests_dir.mkdir(exist_ok=True)
        
        # 查找需要迁移的文件
        test_files = self.find_root_test_files()
        print(f"找到 {len(test_files)} 个测试文件需要迁移:")
        
        for file_path in test_files:
            print(f"  - {file_path.name}")
        
        # 执行迁移
        success_count = 0
        for file_path in test_files:
            print(f"\\n迁移文件: {file_path.name}")
            if self.migrate_file(file_path, backup):
                success_count += 1
                print("✅ 迁移成功")
            else:
                print("❌ 迁移失败")
        
        # 输出结果
        print("\\n迁移完成！")
        print(f"成功迁移: {success_count}/{len(test_files)} 个文件")
        
        print("\\n迁移日志:")
        for log_entry in self.migration_log:
            print(f"  - {log_entry}")
        
        if backup:
            print("\\n原文件已备份，备份文件以.backup结尾")
        
        print("\\n建议下一步:")
        print("1. 检查迁移后的测试文件")
        print("2. 运行 pytest tests/ 验证测试")
        print("3. 如果测试通过，可以删除备份文件")
        print("4. 更新CI/CD配置以使用新的测试结构")


def main():
    """主函数"""
    migrator = TestMigrator()
    
    # 显示当前状态
    test_files = migrator.find_root_test_files()
    
    if not test_files:
        print("没有找到需要迁移的测试文件。")
        return
    
    print(f"找到 {len(test_files)} 个测试文件:")
    for file_path in test_files:
        analysis = migrator.analyze_test_file(file_path)
        status = "✅ pytest" if analysis['uses_pytest'] else "❌ 非pytest"
        print(f"  {file_path.name}: {status}")
    
    # 询问是否执行迁移
    response = input("\\n是否执行迁移？(y/N): ").lower().strip()
    if response == 'y':
        migrator.run_migration(backup=True)
    else:
        print("取消迁移。")


if __name__ == "__main__":
    main()
