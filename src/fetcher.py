# -*- coding: utf-8 -*-
"""
推特数据抓取模块 - 使用 snscrape 抓取公开推文
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Tweet:
    """推文数据结构"""
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


class TwitterFetcher:
    """推特数据抓取器"""

    def __init__(self, proxy: Optional[str] = None):
        """
        初始化抓取器
        :param proxy: 代理地址，如 http://127.0.0.1:7890
        """
        self.proxy = proxy
        self._setup_proxy()

    def _setup_proxy(self):
        """设置代理环境变量"""
        if self.proxy:
            os.environ['HTTP_PROXY'] = self.proxy
            os.environ['HTTPS_PROXY'] = self.proxy
            logger.info(f"已设置代理: {self.proxy}")

    def fetch_user_tweets(
        self,
        username: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        max_tweets: int = 50
    ) -> List[Tweet]:
        """
        抓取指定用户的推文

        :param username: 推特用户名（不含@）
        :param since: 起始时间
        :param until: 结束时间
        :param max_tweets: 最大抓取数量
        :return: 推文列表
        """
        tweets = []

        try:
            import snscrape.modules.twitter as sntwitter
        except ImportError:
            logger.error("snscrape 未安装，请先运行: pip install snscrape")
            return tweets

        # 构建查询
        query_parts = [f"from:{username}"]

        if since:
            since_str = since.strftime("%Y-%m-%d")
            query_parts.append(f"since:{since_str}")

        if until:
            until_str = until.strftime("%Y-%m-%d")
            query_parts.append(f"until:{until_str}")

        query = " ".join(query_parts)
        logger.info(f"开始抓取 @{username} 的推文，查询: {query}")

        scraper = sntwitter.TwitterSearchScraper(query)

        for i, tweet in enumerate(scraper.get_items()):
            if i >= max_tweets:
                break

            try:
                # 提取媒体URL
                media_urls = []
                if tweet.media:
                    for media in tweet.media:
                        if hasattr(media, 'fullUrl') and media.fullUrl:
                            media_urls.append(media.fullUrl)
                        elif hasattr(media, 'url') and media.url:
                            media_urls.append(media.url)

                tweet_obj = Tweet(
                    id=str(tweet.id),
                    username=username,
                    display_name=tweet.user.displayname if hasattr(tweet.user, 'displayname') else username,
                    content=tweet.rawContent if hasattr(tweet, 'rawContent') else str(tweet),
                    created_at=tweet.date.isoformat() if hasattr(tweet, 'date') else datetime.now().isoformat(),
                    url=tweet.url if hasattr(tweet, 'url') else f"https://twitter.com/{username}/status/{tweet.id}",
                    reply_count=tweet.replyCount if hasattr(tweet, 'replyCount') else 0,
                    retweet_count=tweet.retweetCount if hasattr(tweet, 'retweetCount') else 0,
                    like_count=tweet.likeCount if hasattr(tweet, 'likeCount') else 0,
                    quote_count=tweet.quoteCount if hasattr(tweet, 'quoteCount') else 0,
                    is_retweet=tweet.retweetedTweet is not None if hasattr(tweet, 'retweetedTweet') else False,
                    is_reply=tweet.inReplyToTweetId is not None if hasattr(tweet, 'inReplyToTweetId') else False,
                    media_urls=media_urls
                )
                tweets.append(tweet_obj)
            except Exception as e:
                logger.warning(f"解析推文时出错: {e}")
                continue

        logger.info(f"成功抓取 @{username} 的 {len(tweets)} 条推文")
        return tweets

    def fetch_accounts(
        self,
        accounts: List[str],
        hours_back: int = 24,
        max_per_account: int = 30
    ) -> Dict[str, List[Tweet]]:
        """
        批量抓取多个账号的推文

        :param accounts: 用户名列表
        :param hours_back: 回溯多少小时
        :param max_per_account: 每个账号最大数量
        :return: {username: [Tweet, ...]}
        """
        since = datetime.now() - timedelta(hours=hours_back)
        until = datetime.now()

        results = {}
        for username in accounts:
            try:
                tweets = self.fetch_user_tweets(
                    username=username,
                    since=since,
                    until=until,
                    max_tweets=max_per_account
                )
                results[username] = tweets
            except Exception as e:
                logger.error(f"抓取 @{username} 失败: {e}")
                results[username] = []

        return results

    def save_tweets(self, tweets_dict: Dict[str, List[Tweet]], filepath: str):
        """保存推文到 JSON 文件"""
        data = {}
        for username, tweets in tweets_dict.items():
            data[username] = [asdict(t) for t in tweets]

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"推文已保存到: {filepath}")

    def load_tweets(self, filepath: str) -> Dict[str, List[Tweet]]:
        """从 JSON 文件加载推文"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        result = {}
        for username, tweets_data in data.items():
            result[username] = [Tweet(**t) for t in tweets_data]

        return result


class MockFetcher(TwitterFetcher):
    """模拟抓取器 - 用于测试或 snscrape 不可用时"""

    def fetch_user_tweets(
        self,
        username: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        max_tweets: int = 50
    ) -> List[Tweet]:
        """返回模拟数据"""
        logger.warning(f"使用模拟数据: @{username}")
        return [
            Tweet(
                id=f"mock_{username}_1",
                username=username,
                display_name=username,
                content=f"这是 @{username} 的模拟推文内容，用于测试分析系统。",
                created_at=datetime.now().isoformat(),
                url=f"https://twitter.com/{username}/status/mock1",
                reply_count=10,
                retweet_count=50,
                like_count=200,
                quote_count=5,
                is_retweet=False,
                is_reply=False,
                media_urls=[]
            )
        ]


def create_fetcher(use_mock: bool = False, proxy: Optional[str] = None) -> TwitterFetcher:
    """工厂函数：创建抓取器"""
    if use_mock:
        return MockFetcher(proxy=proxy)
    return TwitterFetcher(proxy=proxy)
