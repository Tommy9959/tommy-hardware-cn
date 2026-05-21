#!/usr/bin/env python3
"""
修复 Hugo 模板中的三语言条件判断
Go template 不支持 else if，需要用嵌套格式

转换前: {{ if eq $lang "zh" }}中文{{ else if eq $lang "ar" }}عربي{{ else }}English{{ end }}
转换后: {{ if eq $lang "zh" }}中文{{ else }}{{ if eq $lang "ar" }}عربي{{ else }}English{{ end }}{{ end }}
"""
import re
import os

LAYOUTS_DIR = os.path.expanduser("~/Sites/hardware-site/layouts")
FIXED_COUNT = 0

def fix_else_if(content):
    """将 else if eq $lang 'ar' 转换为嵌套格式"""
    # 模式: {{ else if eq $lang "ar" }}...{{ else }}...{{ end }}
    # 需要递归处理，因为可能有多层嵌套
    
    # 先找到所有 {{ else if ... }} 模式
    # 使用函数闭包来计数
    counter = [0]
    
    pattern = re.compile(r'\{\{ else if eq \$lang "([^"]+)" \}\}(.*?)\{\{ end \}\}', re.DOTALL)
    
    def make_replacer(counter):
        def replacer(match):
            lang = match.group(1)
            inner = match.group(2).strip()
            
            # 检查内部是否还有 {{ else }}
            else_match = re.search(r'\{\{ else \}\}(.*?)$', inner, re.DOTALL)
            if else_match:
                if_content = re.sub(r'\{\{ else \}\}(.*?)$', '', inner, flags=re.DOTALL).strip()
                else_content = else_match.group(1).strip()
                counter[0] += 1
                return f'{{{{ else }}}}{{{{ if eq $lang "{lang}" }}}}{if_content}{{{{ else }}}}{else_content}{{{{ end }}}}{{{{ end }}}}'
            else:
                # 没有 else 分支，只有 if
                counter[0] += 1
                return f'{{{{ else }}}}{{{{ if eq $lang "{lang}" }}}}{inner}{{{{ end }}}}{{{{ end }}}}'
        return replacer
    
    new_content = pattern.sub(make_replacer(counter), content)
    return new_content, counter[0]

def fix_price_line(content):
    """修复价格行中的 中文$ 后跟 else if 的问题"""
    return content.replace('价格区间：${ else if eq $lang', '价格区间：${{ else if eq $lang')

def process_file(filepath):
    """处理单个文件"""
    global FIXED_COUNT
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 多次运行直到没有更多匹配
    for _ in range(5):  # 最大5次迭代（处理嵌套）
        new_content = fix_else_if(content)
        if new_content == content:
            break
        content = new_content
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    global FIXED_COUNT
    print(f"扫描目录: {LAYOUTS_DIR}")
    
    html_files = []
    for root, dirs, files in os.walk(LAYOUTS_DIR):
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))
    
    print(f"找到 {len(html_files)} 个 HTML 文件")
    
    for filepath in sorted(html_files):
        FIXED_COUNT = 0
        if process_file(filepath):
            rel = os.path.relpath(filepath, LAYOUTS_DIR)
            print(f"  ✅ 修复 {rel} ({FIXED_COUNT} 处)")

if __name__ == "__main__":
    main()
