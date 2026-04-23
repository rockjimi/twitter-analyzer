# -*- coding: utf-8 -*-
"""AI 分析模块 - 使用大模型分析推文对市场的影响"""

import json
import os
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class TweetAnalysis:
    tweet_id: str
    username: str
    sentiment: str
    sentiment_score: int
    market_impact: str
    affected_sectors: List[str]
    affected_stocks: List[str]
    key_points: List[str]
    summary: str
    a_share_relevance: str
    a_share_sectors: List[str]
    urgency: str
    action_suggestion: str

    def to_dict(self):
        return asdict(self)


class TweetAnalyzer:
    API_BASE = "https://api.moonshot.cn/v1"
    MODEL = "moonshot-v1-128k"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("MOONSHOT_API_KEY")
        if not self.api_key:
            logger.warning("未设置 MOONSHOT_API_KEY，将使用模拟分析")

    def _call_api(self, messages: List[Dict], temperature: float = 0.3) -> Optional[str]:
        if not self.api_key:
            return None
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.MODEL,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }
        try:
            resp = requests.post(
                f"{self.API_BASE}/chat/completions",
                headers=headers, json=payload, timeout=120
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"API 调用失败: {e}")
            return None

    def analyze(self, content: str, username: str, name: str,
                scope: List[str], category: str, tweet_id: str) -> Optional[TweetAnalysis]:
        system_prompt = (
            "你是一位资深的跨市场金融分析师，精通美股和A股联动分析。"
            "请根据推文内容分析其对金融市场的影响。严格按JSON格式输出，"
            "包含字段: sentiment(积极/消极/中性), sentiment_score(-10到+10整数), "
            "market_impact(高/中/低/无), affected_sectors(美股板块列表), "
            "affected_stocks(股票代码列表), key_points(核心要点3-5条), "
            "summary(一句话总结), a_share_relevance(直接/间接/无), "
            "a_share_sectors(A股板块列表), urgency(紧急/关注/日常), "
            "action_suggestion(操作建议)。"
        )
        user_prompt = (
            f"博主: @{username} ({name}), 分类: {category}, "
            f"影响范围: {', '.join(scope)}\n\n推文:\n{content}\n\n请输出JSON分析结果。"
        )
        resp = self._call_api([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        if not resp:
            return self._mock_analysis(tweet_id, username)
        try:
            d = json.loads(resp)
            return TweetAnalysis(
                tweet_id=tweet_id, username=username,
                sentiment=d.get("sentiment", "中性"),
                sentiment_score=d.get("sentiment_score", 0),
                market_impact=d.get("market_impact", "无"),
                affected_sectors=d.get("affected_sectors", []),
                affected_stocks=d.get("affected_stocks", []),
                key_points=d.get("key_points", []),
                summary=d.get("summary", ""),
                a_share_relevance=d.get("a_share_relevance", "无"),
                a_share_sectors=d.get("a_share_sectors", []),
                urgency=d.get("urgency", "日常"),
                action_suggestion=d.get("action_suggestion", "")
            )
        except Exception as e:
            logger.error(f"解析失败: {e}")
            return self._mock_analysis(tweet_id, username)

    def _mock_analysis(self, tweet_id: str, username: str) -> TweetAnalysis:
        return TweetAnalysis(
            tweet_id=tweet_id, username=username,
            sentiment="中性", sentiment_score=0, market_impact="低",
            affected_sectors=[], affected_stocks=[], key_points=["API不可用，使用默认分析"],
            summary="需要手动查看原文", a_share_relevance="无",
            a_share_sectors=[], urgency="日常", action_suggestion="关注后续动态"
        )

    def analyze_batch(self, tweets: List[Dict], accounts: Dict[str, Dict]) -> List[TweetAnalysis]:
        results = []
        for t in tweets:
            u = t.get("username", "")
            info = accounts.get(u, {})
            logger.info(f"分析 @{u} ...")
            r = self.analyze(
                content=t.get("content", ""), username=u,
                name=t.get("display_name", u), scope=info.get("scope", []),
                category=info.get("category", "未知"), tweet_id=t.get("id", "")
            )
            if r:
                results.append(r)
        return results
