#!/usr/bin/env python3
"""Quick test to check if port 587 is accessible"""
import socket
import sys

server = "mail.niko-free.com"
port = 587

print(f"Testing port {port} connectivity to {server}...")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((server, port))
    sock.close()
    
    if result == 0:
        print(f"✅ Port {port} is open and reachable!")
        print("   You can try using port 587 with TLS")
        sys.exit(0)
    else:
        print(f"❌ Port {port} is closed or unreachable (Error code: {result})")
        print("   Port 587 is also blocked. You'll need to test on Azure.")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error testing port: {e}")
    sys.exit(1)

