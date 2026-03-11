#!/usr/bin/env python3
import argparse
import os
import sys
from fix_engine import FixEngine

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description="AI Agent for automatically fixing open source issues")
    parser.add_argument(
        "--config", 
        default="config.yaml", 
        help="Path to configuration file"
    )
    parser.add_argument(
        "--max-prs", 
        type=int, 
        help="Maximum number of PRs to create (overrides config)"
    )
    
    args = parser.parse_args()
    
    # 检查配置文件是否存在
    if not os.path.exists(args.config):
        print(f"Configuration file not found: {args.config}")
        return 1
    
    # 不需要检查OpenAI API密钥，使用trae cli
    
    # 初始化修复引擎
    engine = FixEngine(args.config)
    
    # 运行修复引擎
    try:
        print("Starting fix engine...")
        pr_count = engine.run(args.max_prs)
        print(f"Fix engine completed successfully. Created {pr_count} PRs.")
        return 0
    except Exception as e:
        print(f"Error running fix engine: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
