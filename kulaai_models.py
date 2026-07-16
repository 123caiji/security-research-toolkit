import requests
import json

requests.packages.urllib3.disable_warnings()

import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

proxies = {"http": None, "https": None}

api_base = "https://api.877ai.cn/api"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://kulaai.cn",
    "Referer": "https://kulaai.cn/",
}

print("=" * 60)
print("[1] 获取完整模型列表")
print("=" * 60)

try:
    r = requests.get(api_base + "/chat/models", headers=headers, timeout=15, proxies=proxies, verify=False)
    data = r.json()
    
    print(f"模型分组数: {len(data)}")
    print(f"\n{'='*60}")
    print("模型列表详情:")
    print(f"{'='*60}")
    
    total_models = 0
    for group in data:
        group_name = group.get('name', group.get('id', 'Unknown'))
        sub_models = group.get('subModels', [])
        default_model = group.get('defaultModel', 'N/A')
        print(f"\n【{group_name}】 (默认: {default_model})")
        print(f"  子模型数: {len(sub_models)}")
        total_models += len(sub_models)
        
        for m in sub_models[:5]:
            actual = m.get('actualModelId', 'N/A')
            display = m.get('displayModelId', 'N/A')
            provider = m.get('providerName', 'N/A')
            tier = m.get('tier', 'N/A')
            capability = m.get('capability', 'N/A')
            credits = m.get('creditsPerUse', 'N/A')
            print(f"    - {actual}")
            print(f"      显示ID: {display}")
            print(f"      提供商: {provider}, 等级: {tier}, 能力: {capability}, 积分: {credits}")
        
        if len(sub_models) > 5:
            print(f"    ... 还有 {len(sub_models) - 5} 个模型")
    
    print(f"\n{'='*60}")
    print(f"模型总数: {total_models}")
    print(f"{'='*60}")
    
    print(f"\n[2] 所有模型 actualModelId 列表")
    print(f"{'='*60}")
    all_models = []
    for group in data:
        for m in group.get('subModels', []):
            all_models.append(m.get('actualModelId', ''))
    
    for m in sorted(all_models):
        print(f"  - {m}")
        
    print(f"\n[3] 所有提供商")
    print(f"{'='*60}")
    providers = set()
    for group in data:
        for m in group.get('subModels', []):
            providers.add(m.get('providerName', 'unknown'))
    
    for p in sorted(providers):
        print(f"  - {p}")
        
except Exception as e:
    print(f"失败: {e}")
    import traceback
    traceback.print_exc()
