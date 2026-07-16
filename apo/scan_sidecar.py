#!/usr/bin/env python3
"""
Scan WorkCode sidecar port on VM 192.168.233.129
Sidecar uses random high port with Basic Auth
Common ports: 30000-50000
"""
import asyncio
import socket
import sys
import time

target = '192.168.233.129'

async def check_port(port, sem):
    async with sem:
        try:
            future = asyncio.open_connection(target, port)
            reader, writer = await asyncio.wait_for(future, timeout=1.0)
            # Try HTTP request
            writer.write(f'GET /api/health HTTP/1.1\\r\\nHost: {target}\\r\\n\\r\\n'.encode())
            await writer.drain()
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                if data:
                    print(f"[+] Port {port}: {data[:100]}")
                    return port
            except:
                print(f"[+] Port {port}: OPEN (no HTTP response)")
                return port
            writer.close()
            await writer.wait_closed()
        except:
            return None

async def main():
    print(f"[*] Scanning WorkCode sidecar on {target}")
    print(f"[*] Checking ports 30000-50000...")
    
    sem = asyncio.Semaphore(300)
    tasks = [check_port(p, sem) for p in range(30000, 50001)]
    results = await asyncio.gather(*tasks)
    
    open_ports = [p for p in results if p is not None]
    print(f"\\n[+] Open ports: {open_ports}")
    
    # Also check common dev ports
    print(f"\\n[*] Checking common dev ports...")
    dev_ports = [8080, 8443, 9000, 9090, 3000, 5000, 4000, 7000, 8000, 8888, 9999, 10000]
    for p in dev_ports:
        try:
            s = socket.socket()
            s.settimeout(2)
            s.connect((target, p))
            s.send(f'GET / HTTP/1.1\\r\\nHost: {target}\\r\\n\\r\\n'.encode())
            try:
                data = s.recv(1024)
                print(f"[+] Port {p}: {data[:100]}")
            except:
                print(f"[+] Port {p}: OPEN")
            s.close()
        except:
            pass
    
    return open_ports

if __name__ == '__main__':
    open_ports = asyncio.run(main())
