#!/usr/bin/env python3
"""
Fast async port scanner for 192.168.233.129
Scans all 65535 ports using async TCP connect
"""
import asyncio
import socket
import time
import sys

target = '192.168.233.129'

async def scan_port(port, sem):
    async with sem:
        try:
            future = asyncio.open_connection(target, port)
            reader, writer = await asyncio.wait_for(future, timeout=1.5)
            print(f"[+] OPEN: {port}")
            # Try to get banner
            try:
                writer.write(b'\r\n')
                await writer.drain()
                data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                if data:
                    print(f"    Banner: {data[:80]}")
            except:
                pass
            writer.close()
            await writer.wait_closed()
            return port
        except:
            return None

async def main():
    print(f"[*] Full port scan on {target}")
    print(f"[*] Scanning ports 1-65535 with 500 concurrent connections...")
    start = time.time()
    
    sem = asyncio.Semaphore(500)
    tasks = [scan_port(p, sem) for p in range(1, 65536)]
    results = await asyncio.gather(*tasks)
    
    open_ports = [p for p in results if p is not None]
    elapsed = time.time() - start
    
    print(f"\n[*] Scan complete in {elapsed:.1f}s")
    print(f"[+] Open ports: {open_ports}")
    
    # Service identification
    port_services = {
        21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
        53: 'DNS', 80: 'HTTP', 88: 'Kerberos', 110: 'POP3',
        135: 'RPC', 139: 'NetBIOS', 143: 'IMAP', 389: 'LDAP',
        443: 'HTTPS', 445: 'SMB', 587: 'SMTP-TLS',
        873: 'rsync', 902: 'VMware', 990: 'FTPS',
        993: 'IMAPS', 995: 'POP3S', 1080: 'SOCKS',
        1099: 'RMI', 1433: 'MSSQL', 1521: 'Oracle',
        2049: 'NFS', 2181: 'Zookeeper', 2375: 'Docker',
        3000: 'Node.js', 3306: 'MySQL', 3389: 'RDP',
        4040: 'HTTP-alt', 4443: 'HTTPS-alt', 5000: 'UPnP',
        5432: 'PostgreSQL', 5601: 'Kibana', 5900: 'VNC',
        5984: 'CouchDB', 5985: 'WinRM-HTTP', 5986: 'WinRM-HTTPS',
        6000: 'X11', 6379: 'Redis', 6443: 'Kubernetes',
        7001: 'WebLogic', 7777: 'HTTP-alt', 8000: 'HTTP-alt',
        8080: 'HTTP-alt', 8081: 'HTTP-alt', 8443: 'HTTPS-alt',
        8888: 'HTTP-alt', 9000: 'HTTP-alt', 9090: 'HTTP-alt',
        9200: 'Elasticsearch', 9300: 'ES-Transport',
        10000: 'Webmin', 11211: 'Memcached', 27017: 'MongoDB',
        50000: 'SAP',
    }
    
    print("\n[*] Service identification:")
    for p in sorted(open_ports):
        svc = port_services.get(p, 'Unknown')
        print(f"    {p}/tcp -> {svc}")
    
    return open_ports

if __name__ == '__main__':
    open_ports = asyncio.run(main())