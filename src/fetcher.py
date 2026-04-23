# -*- coding: utf-8 -*-
"""
推特数据抓取模块 - 多源抓取（xcancel/nitter/rss + snscrape 备用）
"""

import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import logging

import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Tweet:
    id: str
    username: str
    display_name: str
    content: str
    created_at: str
    url: str
    reply_count: int
    retweet_count: int
    like_count: int
    quote_count: int
    is_retweet: bool
    is_reply: bool
    media_urls: List[str]


class HttpFetcher:
    """基于 HTTP 的抓取器（xcancel / nitter RSS）"""

    RSS_HOSTS = [
        "https://xcancel.com",
        "https://nitter.privacydev.net",
        "https://nitter.poast.org",
    ]

    def __init__(self, proxy: Optional[str] = None):
        self.proxy = {"http": proxy, "https": proxy} if proxy else None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def _fetch_rss(self, username: str) -> Optional[str]:
        """从多个 RSS 源尝试获取"""
        for host in self.RSS_HOSTS:
            url = f"{host}/{username}/rss"
            try:
                logger.info(f"尝试 RSS 源: {url}")
                resp = self.session.get(url, proxies=self.proxy, timeout=15)
                if resp.status_code == 200 and "<rss" in resp.text:
                    logger.info(f"RSS 源成功: {host}")
                    return resp.text
            except Exception as e:
                logger.warning(f"RSS 源失败 {host}: {e}")
        return None

    def _parse_rss(self, rss_text: str, username: str, since: Optional[datetime]) -> List[Tweet]:
        """解析 RSS XML"""
        tweets = []
        try:
            root = ET.fromstring(rss_text)
            channel = root.find("channel")
            if channel is None:
                return tweets

            for item in channel.findall("item"):
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "")
                pub_date = item.findtext("pubDate", "")

                if not title or not link:
                    continue

                # 解析时间
                try:
                    dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                except Exception:
                    dt = datetime.now()

                # 时间过滤
                if since and dt < since:
                    continue

                # 提取 tweet ID
                tweet_id = link.split("/")[-1].split("#")[0]
                if not tweet_id.isdigit():
                    tweet_id = f"rss_{username}_{int(dt.timestamp())}"

                tweets.append(Tweet(
                    id=tweet_id,
                    username=username,
                    display_name=username,
                    content=title,
                    created_at=dt.isoformat(),
                    url=link,
                    reply_count=0,
                    retweet_count=0,
                    like_count=0,
                    quote_count=0,
                    is_retweet=title.startswith("RT @"),
                    is_reply=title.startswith("@"),
                    media_urls=[]
                ))
        except Exception as e:
            logger.error(f"解析 RSS 失败: {e}")

        return tweets

    def fetch_user_tweets(
        self, username: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        max_tweets: int = 50
    ) -> List[Tweet]:
        rss_text = self._fetch_rss(username)
        if not rss_text:
            logger.error(f"所有 RSS 源均不可用: @{username}")
            return []

        tweets = self._parse_rss(rss_text, username, since)
        logger.info(f"@{username} RSS 解析到 {len(tweets)} 条推文")
        return tweets[:max_tweets]

    def fetch_accounts(
        self, accounts: List[str],
        hours_back: int = 24,
        max_per_account: int = 30
    ) -> Dict[str, List[Tweet]]:
        since = datetime.now() - timedelta(hours=hours_back)
        results = {}
        for username in accounts:
            try:
                tweets = self.fetch_user_tweets(username, since=since, max_tweets=max_per_account)
                results[username] = tweets
            except Exception as e:
                logger.error(f"抓取 @{username} 失败: {e}")
                results[username] = []
        return results


class SnscrapeFetcher:
    """snscrape 抓取器（备用）"""

    def fetch_accounts(self, accounts, hours_back=24, max_per_account=30):
        results = {}
        for username in accounts:
            try:
                import snscrape.modules.twitter as sntwitter
                since = datetime.now() - timedelta(hours=hours_back)
                query = f"from:{username} since:{since.strftime('%Y-%m-%d')}"
                scraper = sntwitter.TwitterSearchScraper(query)
                tweets = []
                for i, tweet in enumerate(scraper.get_items()):
                    if i >= max_per_account:
                        break
                    tweets.append(Tweet(
                        id=str(tweet.id), username=username,
                        display_name=getattr(tweet.user, 'displayname', username),
                        content=getattr(tweet, 'rawContent', str(tweet)),
                        created_at=tweet.date.isoformat() if hasattr(tweet, 'date') else datetime.now().isoformat(),
                        url=getattr(tweet, 'url', f"https://twitter.com/{username}/status/{tweet.id}"),
                        reply_count=0, retweet_count=0, like_count=0, quote_count=0,
                        is_retweet=False, is_reply=False, media_urls=[]
                    ))
                results[username] = tweets
                logger.info(f"snscrape @{username}: {len(tweets)} 条")
            except Exception as e:
                logger.warning(f"snscrape @{username} 失败: {e}")
                results[username] = []
        return results


class MockFetcher:
    """模拟抓取器"""

    def fetch_accounts(self, accounts, hours_back=24, max_per_account=30):
        results = {}
        for username in accounts:
            results[username] = [Tweet(
                id=f"mock_{username}_1", username=username, display_name=username,
                content=f"[{username}] 模拟推文内容，用于测试。当前市场波动较大，投资者需保持谨慎。",
                created_at=datetime.now().isoformat(),
                url=f"https://twitter.com/{username}/status/mock1",
                reply_count=10, retweet_count=50, like_count=200, quote_count=5,
                is_retweet=False, is_reply=False, media_urls=[]
            )]
        return results


def create_fetcher(use_mock: bool = False, proxy: Optional[str] = None):
    """工厂函数：优先 HTTP，失败回退 snscrape，再失败用 mock"""
    if use_mock:
        return MockFetcher()
    return HttpFetcher(proxy=proxy)
