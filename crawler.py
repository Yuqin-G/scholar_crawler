import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import csv
import re

ua = UserAgent()

def fetch_original_title(url, headers, proxies):
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "lxml")
        print("原始标题页面内容预览:", response.text[:500])  # 打印前500字符
        title_tag = soup.select_one(".gs_r h2.gs_rt a")
        return title_tag.text.strip() if title_tag else "Unknown Title"
    except requests.RequestException as e:
        return f"Error: {e}"

def fetch_cited_papers(url, headers, proxies):
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "lxml")
        print("引用页面内容预览:", response.text[:500])  # 打印前500字符
        papers = soup.select(".gs_r.gs_or.gs_scl")
        # 后续代码不变
        
        cited_papers = []
        for paper in papers:
            title_tag = paper.select_one(".gs_rt a")
            title = title_tag.text if title_tag else "No title"
            info = paper.select_one(".gs_a")
            info = info.get_text(strip=True) if info else "No info"
            link = title_tag["href"] if title_tag and title_tag.get("href") else "No link"
            cited_papers.append({"title": title, "info": info, "link": link})

        next_page = soup.select_one(".gs_ico_nav_next")
        next_url = "https://scholar.google.com" + next_page.parent["href"] if next_page and next_page.parent.get("href") else None
        return cited_papers, next_url
    except requests.RequestException:
        return [], None

def crawl_scholar(url, proxy):
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://scholar.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Accept-Encoding": "gzip, deflate, br"
    }
    proxies = {"http": proxy, "https": proxy} if proxy else None
    proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
    all_papers = []
    original_title = fetch_original_title(url, headers, proxies)
    current_url = url

    while current_url:
        papers, next_url = fetch_cited_papers(current_url, headers, proxies)
        all_papers.extend(papers)
        current_url = next_url
        if next_url:
            time.sleep(random.uniform(2, 5))

    sanitized_title = re.sub(r'[<>:"/\\|?*]', '', original_title)[:50]
    filename = f"cite_{sanitized_title}.csv"
    
    with open(f"static/{filename}", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "info", "link"])
        writer.writeheader()
        writer.writerows(all_papers)
    
    return original_title, len(all_papers), filename, all_papers[:5]  # 返回前5篇作为预览