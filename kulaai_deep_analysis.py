import requests
import re
import json

requests.packages.urllib3.disable_warnings()

import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

proxies = {"http": None, "https": None}

base_url = "https://kulaai.cn"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

print("=" * 60)
print("[1] 下载并深度分析JS文件")
print("=" * 60)

js_url = base_url + "/assets/index-CMjn12iu.js"
r = requests.get(js_url, headers=headers, timeout=15, proxies=proxies, verify=False)
content = r.text
print(f"JS文件大小: {len(content)} 字符")

patterns = [
    (r'["\'](/[a-zA-Z0-9_/\-]+api[a-zA-Z0-9_/\-]*)["\']', "API路径"),
    (r'https?://[a-zA-Z0-9._\-]+/[a-zA-Z0-9_/\-]+', "URL"),
    (r'model["\s:]+["\']([^"\']{3,60})["\']', "model值"),
    (r'["\']model["\']\s*:\s*["\']([^"\']+)["\']', "model键值"),
    (r'["\']baseURL["\']\s*:\s*["\']([^"\']+)["\']', "baseURL"),
    (r'["\']baseUrl["\']\s*:\s*["\']([^"\']+)["\']', "baseUrl"),
    (r'["\']api["\']\s*:\s*["\']([^"\']+)["\']', "api值"),
    (r'/api/[a-zA-Z0-9_/\-]+', "/api/路径"),
    (r'["\']chat["\']\s*:\s*["\']([^"\']+)["\']', "chat值"),
    (r'["\']stream["\']\s*:\s*["\']([^"\']+)["\']', "stream值"),
    (r'["\']completion["\']\s*:\s*["\']([^"\']+)["\']', "completion值"),
]

for pat, desc in patterns:
    matches = re.findall(pat, content, re.IGNORECASE)
    if matches:
        unique = list(set(matches))[:15]
        print(f"\n{desc} ({len(unique)}个):")
        for m in unique:
            print(f"  - {m}")

print()
print("=" * 60)
print("[2] 搜索常见模型名称")
print("=" * 60)

model_keywords = [
    'gpt', 'claude', 'gemini', 'gork', 'qwen', 'deepseek', 
    'glm', 'spark', 'llama', 'mistral', 'doubao', 'ernie',
    'yi-', 'kimi', 'moonshot', 'stepfun', 'xuniu',
    'doubao', 'xinghuo', 'qwen-long', 'qwen-max', 'qwen-plus',
    'gpt-4', 'gpt-3.5', 'claude-3', 'gemini-1', 'gemini-2',
]

found_models = set()
for kw in model_keywords:
    if kw.lower() in content.lower():
        found_models.add(kw)

if found_models:
    print(f"找到 {len(found_models)} 个模型关键词:")
    for m in sorted(found_models):
        print(f"  - {m}")
else:
    print("未找到明显的模型关键词")

print()
print("=" * 60)
print("[3] 搜索AI功能关键词")
print("=" * 60)

ai_keywords = [
    'Gemini', 'GPT', 'Claude', 'Gork', 'DeepSeek',
    '通义', '千问', '文心', '星火', '智谱',
    '免费', '对话', '聊天', '绘画', '图片生成',
    'AI', 'AIGC', 'ChatBot', 'ChatGPT',
]

found_ai = set()
for kw in ai_keywords:
    if kw in content:
        found_ai.add(kw)

if found_ai:
    print(f"找到 {len(found_ai)} 个AI关键词:")
    for m in sorted(found_ai):
        print(f"  - {m}")

print()
print("=" * 60)
print("[4] 提取所有URL路径")
print("=" * 60)

url_paths = re.findall(r'["\'](/[a-zA-Z0-9_/\-]+)["\']', content)
unique_paths = sorted(set(url_paths))
print(f"找到 {len(unique_paths)} 个URL路径:")
for p in unique_paths[:30]:
    if len(p) > 3 and len(p) < 80:
        print(f"  - {p}")

print()
print("=" * 60)
print("[5] 搜索fetch/axios调用")
print("=" * 60)

fetch_calls = re.findall(r'fetch\(([^)]+)\)', content)
print(f"找到 {len(fetch_calls)} 个fetch调用")
for call in fetch_calls[:10]:
    print(f"  - {call[:100]}")

print()
print("=" * 60)
print("[6] 搜索配置对象中的字符串")
print("=" * 60)

strings = re.findall(r'["\']([a-zA-Z_][a-zA-Z0-9_/\-]{5,60})["\']', content)
str_count = {}
for s in strings:
    if any(kw in s.lower() for kw in ['api', 'chat', 'model', 'ai', 'gpt', 'gemini', 'claude', 'gork', 'deepseek', 'qwen', 'glm', 'spark']):
        str_count[s] = str_count.get(s, 0) + 1

sorted_strs = sorted(str_count.items(), key=lambda x: -x[1])[:20]
print(f"找到 {len(sorted_strs)} 个相关字符串:")
for s, c in sorted_strs:
    print(f"  - {s} ({c}次)")
