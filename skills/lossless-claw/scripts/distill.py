#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lossless Claw - 无损回忆技能
功能：对话记录蒸馏、提取重要信息、保留长期记忆
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 配置
CONFIG = {
    'memory_dir': '/Users/zhuxiaolei/.openclaw/workspace/memory',
    'memory_file': '/Users/zhuxiaolei/.openclaw/workspace/MEMORY.md',
    'output_dir': '/Users/zhuxiaolei/.openclaw/workspace/logs/memory-distill',
}

# 提取模式
EXTRACTION_PATTERNS = {
    'identity': [
        r'名字 [是叫]?[:：]?\s*(.+?)(?:\n|$)',
        r'称呼 [是叫]?[:：]?\s*(.+?)(?:\n|$)',
        r'职业 [是叫]?[:：]?\s*(.+?)(?:\n|$)',
        r'公司 [是叫]?[:：]?\s*(.+?)(?:\n|$)',
        r'我是做 (.+?)(?:的|，|。|\n|$)',
    ],
    'preference': [
        r'喜欢 [爱]?[:：]?\s*(.+?)(?:\n|$)',
        r'偏好 [是叫]?[:：]?\s*(.+?)(?:\n|$)',
        r'想要 [需要]?[:：]?\s*(.+?)(?:\n|$)',
        r'爱好 [是叫]?[:：]?\s*(.+?)(?:\n|$)',
    ],
    'task': [
        r'任务 [是叫]?[:：]?\s*(.+?)(?:\n|$)',
        r'目标 [是叫]?[:：]?\s*(.+?)(?:\n|$)',
        r'计划 [是叫]?[:：]?\s*(.+?)(?:\n|$)',
        r'待办 [是叫]?[:：]?\s*(.+?)(?:\n|$)',
    ],
    'knowledge': [
        r'记住 [记下]?[:：]?\s*(.+?)(?:\n|$)',
        r'知识 [是叫]?[:：]?\s*(.+?)(?:\n|$)',
        r'信息 [是叫]?[:：]?\s*(.+?)(?:\n|$)',
        r'记得 [住下]?[:：]?\s*(.+?)(?:\n|$)',
    ],
}

def extract_info(text: str, category: str) -> List[str]:
    """提取特定类别的信息"""
    results = []
    patterns = EXTRACTION_PATTERNS.get(category, [])
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        results.extend(matches)
    
    return list(set(results))

def distill_session(input_file: str, output_dir: str = None):
    """蒸馏会话记录"""
    if not output_dir:
        output_dir = CONFIG['output_dir']
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取信息
    extracted = {
        'identity': extract_info(content, 'identity'),
        'preference': extract_info(content, 'preference'),
        'task': extract_info(content, 'task'),
        'knowledge': extract_info(content, 'knowledge'),
    }
    
    # 生成摘要
    summary = []
    summary.append(f"# 会话蒸馏报告\n")
    summary.append(f"**时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    summary.append(f"**源文件：** {input_file}\n\n")
    
    for category, items in extracted.items():
        if items:
            summary.append(f"## {category.upper()}\n")
            for item in items:
                summary.append(f"- {item}\n")
            summary.append("\n")
    
    # 保存摘要
    summary_file = output_path / f'distill-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.writelines(summary)
    
    print(f"✅ 蒸馏完成：{summary_file}")
    print(f"\n📊 提取结果：")
    for category, items in extracted.items():
        if items:
            print(f"   {category}: {len(items)} 条")
    
    return extracted

def promote_to_memory(extracted: Dict, memory_file: str = None):
    """提升重要信息到长期记忆"""
    if not memory_file:
        memory_file = CONFIG['memory_file']
    
    memory_path = Path(memory_file)
    
    # 读取现有记忆
    if memory_path.exists():
        with open(memory_path, 'r', encoding='utf-8') as f:
            existing = f.read()
    else:
        existing = "# MEMORY.md - 长期记忆\n\n"
    
    # 添加新信息
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_section = f"\n## 蒸馏提升 ({timestamp})\n\n"
    
    for category, items in extracted.items():
        if items:
            new_section += f"### {category.upper()}\n"
            for item in items:
                new_section += f"- {item}\n"
            new_section += "\n"
    
    # 保存
    with open(memory_path, 'w', encoding='utf-8') as f:
        f.write(existing + new_section)
    
    print(f"✅ 已提升到长期记忆：{memory_file}")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 distill.py <输入文件> [--apply]")
        print("示例：python3 distill.py session.md")
        print("      python3 distill.py session.md --apply")
        return
    
    input_file = sys.argv[1]
    apply = '--apply' in sys.argv
    
    # 蒸馏
    extracted = distill_session(input_file)
    
    # 提升到长期记忆
    if apply:
        promote_to_memory(extracted)

if __name__ == '__main__':
    main()
