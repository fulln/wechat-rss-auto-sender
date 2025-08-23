#!/usr/bin/env python3
"""
清理脚本
清理根目录下的旧测试文件和修复编码问题
"""

import shutil
from pathlib import Path
from typing import List

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"


class TestCleaner:
    """测试清理器"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.tests_dir = TESTS_DIR
        self.cleaned_files = []
        
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
    
    def backup_and_remove_root_tests(self) -> None:
        """备份并移除根目录下的测试文件"""
        test_files = self.find_root_test_files()
        
        if not test_files:
            print("没有找到需要清理的根目录测试文件。")
            return
        
        # 创建备份目录
        backup_dir = self.project_root / "backup_old_tests"
        backup_dir.mkdir(exist_ok=True)
        
        print(f"备份并清理 {len(test_files)} 个根目录测试文件:")
        
        for file_path in test_files:
            try:
                # 备份到backup目录
                backup_path = backup_dir / file_path.name
                shutil.copy2(file_path, backup_path)
                
                # 删除原文件
                file_path.unlink()
                
                self.cleaned_files.append(file_path.name)
                print(f"  ✅ 清理: {file_path.name}")
                
            except Exception as e:
                print(f"  ❌ 清理失败 {file_path.name}: {e}")
    
    def fix_encoding_issues(self) -> None:
        """修复编码问题"""
        problematic_files = [
            self.tests_dir / "test_rss_fetcher.py",
            self.tests_dir / "test_scheduler_service.py", 
            self.tests_dir / "test_send_service.py",
            self.tests_dir / "test_summarizer.py",
            self.tests_dir / "test_wechat_sender.py"
        ]
        
        print("\\n修复编码问题的文件:")
        
        for file_path in problematic_files:
            if file_path.exists():
                try:
                    # 尝试不同的编码读取文件
                    content = None
                    for encoding in ['utf-8', 'gbk', 'cp1252', 'latin1']:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.read()
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if content:
                        # 重新保存为UTF-8编码
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"  ✅ 修复编码: {file_path.name}")
                    else:
                        print(f"  ❌ 无法读取: {file_path.name}")
                        
                except Exception as e:
                    print(f"  ❌ 修复失败 {file_path.name}: {e}")
    
    def remove_duplicate_migrated_tests(self) -> None:
        """移除重复的迁移测试"""
        # 检查是否有同名的原始测试和迁移测试
        migrated_files = list(self.tests_dir.glob("*_migrated.py"))
        
        print(f"\\n检查 {len(migrated_files)} 个迁移测试文件:")
        
        for migrated_file in migrated_files:
            # 查找对应的原始文件名
            base_name = migrated_file.stem.replace('_migrated', '')
            original_file = self.tests_dir / f"{base_name}.py"
            
            if original_file.exists():
                print(f"  发现重复: {original_file.name} 和 {migrated_file.name}")
                # 可以选择保留哪个版本
    
    def clean_cache_and_pycache(self) -> None:
        """清理缓存文件"""
        print("\\n清理缓存文件:")
        
        # 清理__pycache__目录
        for pycache_dir in self.project_root.rglob("__pycache__"):
            try:
                shutil.rmtree(pycache_dir)
                print(f"  ✅ 清理: {pycache_dir.relative_to(self.project_root)}")
            except Exception as e:
                print(f"  ❌ 清理失败 {pycache_dir}: {e}")
        
        # 清理.pyc文件
        for pyc_file in self.project_root.rglob("*.pyc"):
            try:
                pyc_file.unlink()
                print(f"  ✅ 清理: {pyc_file.relative_to(self.project_root)}")
            except Exception as e:
                print(f"  ❌ 清理失败 {pyc_file}: {e}")
    
    def run_cleanup(self) -> None:
        """运行完整清理"""
        print("开始测试环境清理...")
        print(f"项目根目录: {self.project_root}")
        print(f"测试目录: {self.tests_dir}")
        
        # 1. 备份并移除根目录测试文件
        self.backup_and_remove_root_tests()
        
        # 2. 修复编码问题
        self.fix_encoding_issues()
        
        # 3. 检查重复文件
        self.remove_duplicate_migrated_tests()
        
        # 4. 清理缓存
        self.clean_cache_and_pycache()
        
        print("\\n清理完成！")
        print(f"已清理 {len(self.cleaned_files)} 个文件")
        
        if self.cleaned_files:
            print("\\n清理的文件:")
            for filename in self.cleaned_files:
                print(f"  - {filename}")
        
        print("\\n建议下一步:")
        print("1. 运行 pytest tests/ 验证测试")
        print("2. 检查备份文件是否需要")
        print("3. 更新README文档")


def main():
    """主函数"""
    cleaner = TestCleaner()
    
    # 显示当前状态
    root_test_files = cleaner.find_root_test_files()
    
    print(f"找到 {len(root_test_files)} 个根目录测试文件需要清理:")
    for file_path in root_test_files:
        print(f"  - {file_path.name}")
    
    # 询问是否执行清理
    if root_test_files:
        response = input("\\n是否执行清理？(y/N): ").lower().strip()
        if response == 'y':
            cleaner.run_cleanup()
        else:
            print("取消清理。")
    else:
        # 如果没有根目录测试文件，仍然可以修复编码问题
        response = input("\\n是否修复编码问题和清理缓存？(y/N): ").lower().strip()
        if response == 'y':
            cleaner.fix_encoding_issues()
            cleaner.clean_cache_and_pycache()
            print("编码修复和缓存清理完成！")


if __name__ == "__main__":
    main()
