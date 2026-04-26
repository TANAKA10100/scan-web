import logging
import argparse
import urllib.parse
import hashlib
import secrets
import base64
import os
import warnings
import uuid
import http.client
import requests.packages.urllib3
import queue
import signal
import re
import threading
import subprocess
import sys
import json
import requests
import socket
import time
import random
from urllib.parse import urlparse, quote, urljoin
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

agents = [
    "Mozilla/5.0",
    "Chrome/120.0",
    "Safari/537.36"
]

headers = {
    "User-Agent": random.choice(agents)
}

def normalize_url(url):
    if not url.startswith("http"):
       url="http://" + url
    return url


def rainbow_text(text):
    colors = [
        "\033[1;31m",
        "\033[1;33m",
        "\033[1;32m",
        "\033[1;34m",
        "\033[1;35m",
    ]
    for i,char in enumerate(text):
        print(colors[i % len(colors)] + char, end='',flush=True)
        time.sleep(0.01)
    print("\033[0m")

def red_text(text):
    print("\033[1;31m" + text + "\033[0m")
def green_text(text):
    print("\033[1;32m" + text + "\033[0m")

def banner():
    art ="""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
                                                       ■
$$$$$$$$$$$$$$$$ (___________________________________) ■
$    $$$$$$    $ |                                   | ■
$( ● )$$$$( ● )$ |PEMBUAT |ANONYMOUS WIBU ELIT       | ■
$_____$$$$_____$ |VERSION |1.1.0                     | ■
$$$$$$$$$$$$$$$$ |TOOLS   |SCAN WEB                  | ■
$ VVVVVVVVVVVV $ |____________________________________ ■
$              $ (aku bodoh dalem pelajaran atau cinta)■
$ MMMMMMMMMMMM $ (tapi aku pinter dalem dunia maya    )■
$$$$$$$$$$$$$$$$ (____________________________________)■
                                                       ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""
    print("\033[1;32m" + art + "\033[0m")
    rainbow_text("\nANONYMOUS WIBU ELIT\n")

def scan_target_web(url):
    try:
        response=requests.get(url,timeout=6,headers=headers)
        print(f"[+] URL: {url}")
        print(f"[+] Status: {response.status_code}")
        print(f"[+] Headers:")
        for key,value in response.headers.items():
             print(f"   {key}: {value}")
        print("\n[+] Technology Detection:")
        server = response.headers.get("Server","Unknown")
        powered = response.headers.get("X-Powered-By") or response.headers.get("x-powered-by") or "Unknown"
        print(f" Server: {server}")
        print(f" x-powered-By: {powered}")

        print("\n[+] Security Headers Check:")
        security_headers = [
            "X-Frame-Options",
            "Content-Security-Policy",
            "Strict-Transport-Security",
            "X-XSS-Protection",
            "X-Content-Type-Options"
        ]
        for header in security_headers:
            if header in response.headers:
               green_text(f"[OK] {header} found")
            else:
                red_text(f"[MISSING] {header}")
    except Exception as e:
        print(f"[-] ERROR: {e}")

def scan_subdomains(url):
    print("\n[+] Subdomain Scanning:")
    subdomains = ["admin", "dev","test","api","staging"]
    parsed = urlparse(url)
    domain = parsed.netloc if parsed.netloc else parsed.path
    for sub in subdomains:
        sub_url = f"http://{sub}.{domain}"
        try:
           res = requests.get(sub_url,timeout=3,headers=headers)
           if res.status_code == 200:
               green_text(f"[FOUND SUBDOMAIN] {sub_url}")
               save_log(f"[FOUND SUBDOMAIN] {sub_url}")

        except:
            pass
def scan_ports(url):
    parsed = urlparse(url)
    host = parsed.netloc if parsed.netloc else parsed.path

    ports = [21,22,25,53,80,110,139,143,443,445,8080]

    print("\n[+] Scanning ports:")
    for port in ports:
        s = socket.socket()
        s.settimeout(1)
        try:
            s.connect((host, port))
            print(f"[OPEN] Port {port}")
        except:
             pass
        finally:
             s.close()

def check_http_methods(url):
    print("\n[+] Checking HTTP Methods:")
    methods = ["GET","POST","PUT","DELETE","OPTIONS","PATCH"]
    for method in methods:
        try:
            res = requests.request(method,url,timeout=4,headers=headers)
            if res.status_code < 400:
               green_text(f"[ALLOWED] {method} method")
               save_log(f"[ALLOWED] {method} method")
        except:
            pass

def check_path(url,path):
    full_url = url.rstrip("/")  + "/" + path
    try:
       res = requests.get(full_url,timeout=6,headers=headers)
       if res.status_code == 200:
                green_text(f"[FOUND] {full_url}")
                save_log(f"[FOUND] {full_url}")
       elif res.status_code == 403:
                red_text(f"[FORBIDDEN] {full_url}")
                save_log(f"[FORBIDDEN] {full_url}")
       elif res.status_code in [301,302]:
                print(f"[REDIRECT] {full_url}")
                save_log(f"[REDIRECT] {full_url}")
    except:
        pass

def scan_directories(url):
    print("\n[+] Directory Scanning:")

    paths = [
        "admin",
        "login",
        "dashboard",
        "api",
        "backup",
        "config",
        "uploads",
        "images",
        ".env",
        ".git",
        "robots.txt",
        "sitemap.xml",
        ".htaccess"
    ]
    with ThreadPoolExecutor(max_workers=10) as executor:
         executor.map(lambda path: check_path(url,path),paths)

def save_log(text):
    with open("result.txt","a") as f:
       f.write(text + "\n")


def scan_sensitive_files(url):
    print(f"\n[+] Sensitive File Scan:")

    files = [
        ".env",
        ".git",
        ".htaccess",
        "config.php",
        "backup.zip"
    ]
    for file in files:
        full_url = url.rstrip("/") + "/" + file
        try:
           res = requests.get(full_url,timeout=5,headers=headers)
           if res.status_code == 200:
              red_text(f"[SENSITIVE FOUND] {full_url}")
              save_log(f"[SENSITIVE FOUND] {full_url}")
        except:
            pass

def crawl_links(url):
    print("\n[+] Crawling Links:")
    found_links = set()
    try:
       res = requests.get(url, timeout=5, headers=headers)
       html = res.text
       import re
       links = re.findall('href=["\'](.*?)["\']',html)
       for link in links:
           if link.startswith("http"):
              found_links.add(link)
           elif link.startswith("/"):
                full_link = url.rstrip("/") + link
                found_links.add(full_link)
       for i in found_links:
           print(f"[LINK] {i}")
           save_log(f"[LINK] {i}")
    except:
        pass

    return found_links

def find_parameters(links):
    print("\n[+] Parameter Detection:")
    for link in links:
        if "?" in link and "=" in link:
            red_text(f"[PARAM FOUND] {link}")
            save_log(f"[PARAM FOUND] {link}")

def test_sqli_advanced(links):
    print("\n[+] SQL Injection Test (Advanced):")
    payloads = ["'", "\"", "'--", "\"--"]
    for link in links:
        if "?" in link and "=" in link:
            try:
               normal = requests.get(link,timeout=5, headers=headers)
               normal_len = len(normal.text)
               for payload in payloads:
                   test_url = link + payload
                   res = requests.get(test_url, timeout=5, headers=headers)
                   test_len = len(res.text)
                   if abs(normal_len - test_len) > 50:
                       red_text(f"[POSSIBLE SQLI] {link}")
                       save_log(f"[SQLI] {link}")
                       break
            except:
                pass

def test_xss(links):
    print("\n[+] XSS Test (Basic):")
    payload = "<script>alert(1)</script>"
    for link in links:
        if "?" in link and "=" in link:
            test_url = link + payload
            try:
               res= requests.get(test_url,timeout=5,headers=headers)
               if res and payload in res.text:
                   red_text(f"[POSSIBLE XSS] {link}")
                   save_log(f"[POSSIBLE XSS] {link}")
            except:
                pass

def report_issue(level, text):
    print(f"[{level}] {text}")
    save_log(f"[{level}] {text}")


def detect_waf(response):
    waf_signatures = [
        "cloudflare",
        "sucuri",
        "mod_security",
        "akamai",
        "imperva",
        "incapsula",
        "f5 big-ip",
        "barracuda",
        "citrix",
        "aws waf",
        "azure",
        "gcp",
        "stackpath",
        "fastly",
        "edgecast",
        "varnish",
        "perimeterx",
        "radware",
        "wallarm"
    ]
    headers = str(response.headers).lower()
    for waf in waf_signatures:
        if waf in headers:
           red_text(f"[WAF TERDITEKSI PADA WEB INIH] {waf}")
def fingerprint(response):
    print("\n[+] Fingerprinting Response")
    body = response.text
    headers = response.headers
    raw_hash = hashlib.md5(body.encode()).hexdigest()
    print(f"[+] RAW HASH {raw_hash}")
    stable_part = body[:5000]
    stable_hash = hashlib.md5(stable_part.encode()).hexdigest()
    print(f"[+] STABLE HASH:{stable_hash}")
    server = headers.get("server","unknown")
    powered = headers.get("X-Powered-By","unknown")
    print(f"[+] SERVER : {server}")
    print(f"[+] POWERED BY :{powered}")
    title = re.findall(r"<title>(.*?)</title>",body,re.IGNORECASE)
    if title:
        print(f"[+] TITLE :{title[0]}")
    structure = re.sub(r"\d+","",body)
    structure = re.sub(r"\s+","",structure)
    structure_hash = hashlib.md5(structure[:5000].encode()).hexdigest()
    print(f"[+] STRUCTURE HASH  :{structure_hash}")
    inputs = re.findall(r"name=[\"'](.*?)[\"']",body)
    if inputs:
       unique_inputs = list(set(inputs))
       param_hash = hashlib.md5("".join(sorted(unique_inputs)).encode()).hexdigest()
       print(f"[+] PARAM HASH : {param_hash}")
       print(f"[+] PARAM COUNT : {len(unique_inputs)}")
def crawl_links(url, depth=2):
    print("\n[+] Crawling Links:")
    visited = set()
    to_visit = [url]
    base_domain = urlparse(url).netloc
    for _ in range(depth):
        new_links = []
        for current_url in to_visit:
            try:
               r = requests.get(current_url,timeout=5)
               links = re.findall(r'href=["\'](.*?)["\']', r.text)
               for link in links:
                   full = urljoin(current_url,link)
                   if urlparse(full).netloc == base_domain:
                      if full not in visited:
                          visited.add(full)
                          new_links.append(full)
                          print(f"[LINK] {full}")
            except:
                pass
        to_visit = new_links 
    return list(visited)
banner()
target = input("MASUKIN URL TARGET WEB LUH:  ")
target = normalize_url(target)
scan_target_web(target)
scan_ports(target)
scan_directories(target)
links = crawl_links(target)
find_parameters(links)
test_sqli_advanced(links)
test_xss(links)
