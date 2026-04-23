# -*- coding: utf-8 -*-
"""报告生成模块 - 将分析结果输出为可读报告"""

import json
import os
from datetime import datetime
from typing import List, Dict

from src.analyzer import TweetAnalysis


class ReportGenerator:
    """报告生成器"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_markdown(self, analyses: List[TweetAnalysis], date_str: str = None) -> str:
        """生成 Markdown 报告"""
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        high = [a for a in analyses if a.market_impact == "高"]
        medium = [a for a in analyses if a.market_impact == "中"]
        urgent = [a for a in analyses if a.urgency == "紧急"]
        a_share_direct = [a for a in analyses if a.a_share_relevance == "直接"]

        lines = [
            f"# 📊 推特财经言论分析报告 - {date_str}",
            "",
            f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## 📈 数据概览",
            "",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 分析推文总数 | {len(analyses)} |",
            f"| 高影响 | {len(high)} |",
            f"| 中等影响 | {len(medium)} |",
            f"| 紧急关注 | {len(urgent)} |",
            f"| 直接影响A股 | {len(a_share_direct)} |",
            "",
            "---",
            "",
        ]

        # 紧急事项
        if urgent:
            lines.extend([
                "## 🚨 紧急关注",
                "",
            ])
            for a in urgent:
                lines.extend(self._tweet_section(a))
            lines.append("---\n")

        # 高影响
        if high:
            lines.extend([
                "## ⚠️ 高市场影响",
                "",
            ])
            for a in high:
                if a not in urgent:
                    lines.extend(self._tweet_section(a))
            lines.append("---\n")

        # 中等影响
        if medium:
            lines.extend([
                "## 📌 中等市场影响",
                "",
            ])
            for a in medium:
                lines.extend(self._tweet_section(a))
            lines.append("---\n")

        # 其他
        others = [a for a in analyses if a.market_impact not in ("高", "中")]
        if others:
            lines.extend([
                "## 📝 其他动态",
                "",
            ])
            for a in others:
                lines.extend(self._tweet_section(a))
            lines.append("---\n")

        # A股关联汇总
        if a_share_direct:
            lines.extend([
                "## 🇨🇳 A股直接关联汇总",
                "",
                "| 博主 | 影响板块 | 紧急度 | 操作建议 |",
                "|------|----------|--------|----------|",
            ])
            for a in a_share_direct:
                sectors = ", ".join(a.a_share_sectors) if a.a_share_sectors else "-"
                lines.append(f"| @{a.username} | {sectors} | {a.urgency} | {a.action_suggestion} |")
            lines.append("")

        return "\n".join(lines)

    def _tweet_section(self, a: TweetAnalysis) -> List[str]:
        """生成单条推文的报告段落"""
        emoji_map = {"高": "🔴", "中": "🟡", "低": "🟢", "无": "⚪"}
        urgency_map = {"紧急": "🚨", "关注": "👀", "日常": "📋"}
        sentiment_emoji = "📈" if a.sentiment_score > 0 else "📉" if a.sentiment_score < 0 else "➖"

        lines = [
            f"### {emoji_map.get(a.market_impact, '⚪')} @{a.username} - {a.summary[:50]}{'...' if len(a.summary) > 50 else ''}",
            "",
            f"- **情感**: {sentiment_emoji} {a.sentiment} (评分: {a.sentiment_score})",
            f"- **市场影响**: {a.market_impact}",
            f"- **紧急度**: {urgency_map.get(a.urgency, '')} {a.urgency}",
        ]

        if a.affected_sectors:
            lines.append(f"- **美股板块**: {', '.join(a.affected_sectors)}")
        if a.affected_stocks:
            lines.append(f"- **相关股票**: {', '.join(a.affected_stocks)}")
        if a.a_share_relevance != "无":
            lines.append(f"- **A股关联**: {a.a_share_relevance}")
        if a.a_share_sectors:
            lines.append(f"- **A股板块**: {', '.join(a.a_share_sectors)}")

        if a.key_points:
            lines.extend(["", "**核心要点:**"])
            for p in a.key_points:
                lines.append(f"- {p}")

        if a.action_suggestion:
            lines.extend(["", f"**💡 操作建议**: {a.action_suggestion}", ""])

        lines.append("")
        return lines

    def save_report(self, analyses: List[TweetAnalysis], date_str: str = None) -> str:
        """保存报告到文件"""
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        md_content = self.generate_markdown(analyses, date_str)
        filepath = os.path.join(self.output_dir, f"report_{date_str}.md")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        # 同时保存 JSON
        json_path = os.path.join(self.output_dir, f"report_{date_str}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([a.to_dict() for a in analyses], f, ensure_ascii=False, indent=2)

        return filepath
