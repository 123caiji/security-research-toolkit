# -*- coding: utf-8 -*-
"""
前端密码加密算法分析工具（纯本地）。

功能：
1. 分析 JS 文件中的密码加密逻辑
2. 搜索常见加密算法关键词
3. 提供前端加密算法的 Python 对照实现
4. 辅助定位加密函数位置
"""

import re
import os
import json
from datetime import datetime

class FrontendCryptoAnalyzer:
    """前端密码加密算法分析器"""
    
    def __init__(self):
        # 常见加密算法关键词
        self.crypto_keywords = {
            'md5': ['md5', 'MD5', 'CryptoJS.MD5'],
            'sha1': ['sha1', 'SHA1', 'CryptoJS.SHA1'],
            'sha256': ['sha256', 'SHA256', 'CryptoJS.SHA256'],
            'sha512': ['sha512', 'SHA512', 'CryptoJS.SHA512'],
            'base64': ['base64', 'Base64', 'btoa', 'atob', 'CryptoJS.enc.Base64'],
            'rsa': ['rsa', 'RSA', 'JSEncrypt', 'setPublicKey', 'publicKey'],
            'aes': ['aes', 'AES', 'CryptoJS.AES'],
            'des': ['des', 'DES', 'CryptoJS.DES'],
            'hmac': ['hmac', 'HMAC', 'CryptoJS.Hmac'],
            'encrypt': ['encrypt', 'Encrypt', 'encode'],
            'password': ['password', 'pwd', 'pass'],
            'submit_api': ['submit', '/api/submit', '/api/login', 'login'],
        }
        
        # 常见加密函数模式
        self.crypto_patterns = [
            # MD5模式
            r'(CryptoJS\.MD5\(|md5\()([^)]+)\)',
            # SHA256模式
            r'(CryptoJS\.SHA256\(|sha256\()([^)]+)\)',
            # Base64模式
            r'(btoa\(|encodeURIComponent\()([^)]+)\)',
            # RSA模式
            r'(setPublicKey|publicKey)\s*[=:]\s*["\']([^"\']+)',
            # 通用加密模式
            r'(encrypt|encode)\s*\(\s*([^,]+)',
        ]
    
    def analyze_js_file(self, file_path):
        """分析JS文件中的加密逻辑"""
        print(f"\n{'='*80}")
        print(f"分析文件: {file_path}")
        print('='*80)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            print(f"\n[文件信息]")
            print(f"  文件大小: {len(content):,} 字节")
            
            # 搜索关键词
            print(f"\n[加密关键词搜索]")
            found_keywords = {}
            
            for algo, keywords in self.crypto_keywords.items():
                matches = []
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        matches.append(keyword)
                if matches:
                    found_keywords[algo] = matches
                    print(f"  ✅ {algo}: {', '.join(matches)}")
            
            if not found_keywords:
                print("  ❌ 未发现常见加密关键词")
                return None
            
            # 搜索加密函数调用
            print(f"\n[加密函数调用分析]")
            crypto_calls = []
            
            for pattern in self.crypto_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches[:10]:  # 最多显示10个
                    if isinstance(match, tuple):
                        call_info = f"{match[0]}({match[1]})"
                    else:
                        call_info = match
                    if call_info not in crypto_calls:
                        crypto_calls.append(call_info)
            
            if crypto_calls:
                print("  发现的加密调用:")
                for call in crypto_calls[:10]:
                    print(f"    - {call}")
            
            # 搜索提交/登录相关代码
            print(f"\n[接口路径分析]")
            api_patterns = [
                r'["\']/api/submit["\']',
                r'["\']/api/login["\']',
                r'url\s*[=:]\s*["\'][^"\']+/api/',
            ]
            
            api_matches = []
            for pattern in api_patterns:
                matches = re.findall(pattern, content)
                api_matches.extend(matches)
            
            if api_matches:
                print("  发现的接口路径引用:")
                for match in list(set(api_matches))[:5]:
                    print(f"    - {match}")
            
            # 搜索密码处理代码
            print(f"\n[密码字段处理]")
            password_patterns = [
                r'password\s*[=:]\s*([^,;\n]+)',
                r'pwd\s*[=:]\s*([^,;\n]+)',
                r'data\.password\s*[=:]\s*([^,;\n]+)',
            ]
            
            password_matches = []
            for pattern in password_patterns:
                matches = re.findall(pattern, content)
                password_matches.extend(matches)
            
            if password_matches:
                print("  发现的密码赋值语句:")
                for match in list(set(password_matches))[:5]:
                    print(f"    - password = {match.strip()}")
            
            # 尝试识别具体算法
            print(f"\n[算法识别]")
            algorithm = self._identify_algorithm(content)
            if algorithm:
                print(f"  识别到可能的加密算法: {algorithm}")
            
            return {
                'file_path': file_path,
                'file_size': len(content),
                'found_keywords': found_keywords,
                'crypto_calls': crypto_calls,
                'api_references': list(set(api_matches)),
                'password_assignments': list(set(password_matches)),
                'identified_algorithm': algorithm,
            }
            
        except Exception as e:
            print(f"  ❌ 分析失败: {e}")
            return None
    
    def _identify_algorithm(self, content):
        """根据内容识别加密算法"""
        content_lower = content.lower()
        
        # 按优先级检测
        if 'cryptojs.aes' in content_lower:
            return 'AES (CryptoJS)'
        elif 'cryptojs.sha256' in content_lower:
            return 'SHA-256 (CryptoJS)'
        elif 'cryptojs.md5' in content_lower:
            return 'MD5 (CryptoJS)'
        elif 'jsencrypt' in content_lower or 'setpublickey' in content_lower:
            return 'RSA (JSEncrypt)'
        elif 'btoa' in content_lower:
            return 'Base64 (btoa)'
        elif 'sha256(' in content_lower:
            return 'SHA-256'
        elif 'md5(' in content_lower:
            return 'MD5'
        elif 'cryptojs.hmac' in content_lower:
            return 'HMAC (CryptoJS)'
        
        return None
    
    def scan_directory(self, directory):
        """扫描目录中的JS文件"""
        print(f"\n{'='*80}")
        print(f"扫描目录: {directory}")
        print('='*80)
        
        js_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.js'):
                    js_files.append(os.path.join(root, file))
        
        print(f"\n找到 {len(js_files)} 个JS文件")
        
        results = []
        for js_file in js_files:
            print(f"\n正在分析: {os.path.basename(js_file)}")
            result = self.analyze_js_file(js_file)
            if result:
                results.append(result)
        
        return results


class FrontendCryptoSimulator:
    """前端加密算法模拟器"""
    
    def __init__(self):
        import hashlib
        import base64
        self.hashlib = hashlib
        self.base64 = base64
    
    def simulate_crypto_js_md5(self, password):
        """模拟 CryptoJS.MD5 输出（小写十六进制）"""
        return self.hashlib.md5(password.encode('utf-8')).hexdigest()
    
    def simulate_crypto_js_sha256(self, password):
        """模拟 CryptoJS.SHA256 输出（小写十六进制）"""
        return self.hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def simulate_btoa(self, password):
        """模拟 JavaScript btoa 函数"""
        return self.base64.b64encode(password.encode('utf-8')).decode('utf-8')
    
    def simulate_double_md5(self, password):
        """模拟 MD5(MD5(password))"""
        first = self.hashlib.md5(password.encode('utf-8')).hexdigest()
        return self.hashlib.md5(first.encode('utf-8')).hexdigest()
    
    def simulate_md5_with_salt(self, password, salt=''):
        """模拟 MD5(password + salt)"""
        if not salt:
            salt = 'demo'
        return self.hashlib.md5((password + salt).encode('utf-8')).hexdigest()
    
    def simulate_sha256_with_salt(self, password, salt=''):
        """模拟 SHA256(password + salt)"""
        if not salt:
            salt = 'demo'
        return self.hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    
    def run_all_simulations(self, password):
        """运行所有加密模拟"""
        print(f"\n{'='*80}")
        print(f"前端加密算法模拟")
        print(f"原始密码: '{password}'")
        print('='*80)
        
        simulations = [
            ('MD5 (CryptoJS.MD5)', self.simulate_crypto_js_md5(password)),
            ('SHA-256 (CryptoJS.SHA256)', self.simulate_crypto_js_sha256(password)),
            ('Base64 (btoa)', self.simulate_btoa(password)),
            ('MD5(MD5(password))', self.simulate_double_md5(password)),
            ('MD5(password + "demo")', self.simulate_md5_with_salt(password)),
            ('SHA256(password + "demo")', self.simulate_sha256_with_salt(password)),
        ]
        
        for name, result in simulations:
            print(f"{name:35} -> {result}")
        
        return simulations


def main():
    """主函数"""
    print("="*80)
    print("前端密码加密算法分析工具")
    print("="*80)
    print("\n本工具用于分析本地保存的前端 JS 中的密码加密逻辑")
    print("支持：CryptoJS (MD5/SHA256/AES)、JSEncrypt (RSA)、Base64等")
    print("="*80)
    
    analyzer = FrontendCryptoAnalyzer()
    simulator = FrontendCryptoSimulator()
    
    # 示例密码模拟
    sample_password = "demo_password"
    print(f"\n[1] 前端加密算法模拟")
    simulator.run_all_simulations(sample_password)
    
    # 分析本地JS文件
    print(f"\n[2] 分析本地JS文件")
    js_files = [
        "exports/local_web_demo/main.js",
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            analyzer.analyze_js_file(js_file)
        else:
            print(f"\n跳过不存在的文件: {js_file}")
    
    # 输出分析总结
    print(f"\n{'='*80}")
    print("分析总结")
    print("="*80)
    print("\n常用前端加密算法特征:")
    print("-"*60)
    print("| 算法 | 关键词 | 输出特征 |")
    print("|------|--------|----------|")
    print("| CryptoJS.MD5 | md5, CryptoJS.MD5 | 32位小写十六进制 |")
    print("| CryptoJS.SHA256 | sha256, CryptoJS.SHA256 | 64位小写十六进制 |")
    print("| CryptoJS.AES | aes, CryptoJS.AES | Base64编码密文 |")
    print("| JSEncrypt(RSA) | JSEncrypt, setPublicKey | 长Base64字符串 |")
    print("| btoa(Base64) | btoa | 包含+/=字符 |")
    print("-"*60)
    
    print("\n建议操作步骤:")
    print("1. 启动本地演示：`python scripts/serve_local_web_demo.py`")
    print("2. 镜像静态资源：`python scripts/download_spa_static_mirror.py --base-url http://127.0.0.1:8765/`")
    print("3. 对 main.js 运行：`python scripts/analyze_frontend_crypto_in_file.py exports/local_web_demo/main.js`")
    print("4. 在 IDE 中根据关键字继续人工确认加密调用链")


if __name__ == "__main__":
    main()
