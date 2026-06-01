#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
import http.server
import socketserver
import os
import socket

# Windows 콘솔 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.chdir(r"C:\Users\wnsdu\OneDrive\Desktop\claude code")

# 현재 IP 주소 자동 감지
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

PORT = 3456
Handler = http.server.SimpleHTTPRequestHandler

try:
    local_ip = get_local_ip()
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"\n{'='*60}")
        print(f"✓ 정역학 심층훈련 서버 시작")
        print(f"{'='*60}")
        print(f"\n📱 폰에서 접속:")
        print(f"   http://{local_ip}:{PORT}/statics_trainer.html")
        print(f"\n💻 PC에서 접속:")
        print(f"   http://localhost:{PORT}/statics_trainer.html")
        print(f"\n포트: {PORT} | 디렉토리: {os.getcwd()}")
        print(f"{'='*60}\n")
        httpd.serve_forever()
except Exception as e:
    print(f"✗ 오류: {e}")
