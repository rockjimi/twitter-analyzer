# 推特财经言论分析器

每天自动抓取影响美股/A股的关键推特博主言论，通过 AI 分析其市场影响，生成结构化报告。

## 快速开始

### 1. 环境准备

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

**方式A：环境变量（推荐）**
```powershell
[Environment]::SetEnvironmentVariable("MOONSHOT_API_KEY", "sk-你的Key", "User")
```

**方式B：临时设置**
```powershell
$env:MOONSHOT_API_KEY="sk-你的Key"
python main.py
```

### 3. 运行分析

```bash
# 基础运行（抓取最近24小时）
python main.py

# 使用代理（在中国大陆）
python main.py --proxy http://127.0.0.1:7890

# 模拟模式（测试用）
python main.py --mock

# 自定义参数
python main.py --hours 12 --max 50
```

## 无代理方案：GitHub Actions 自动运行

在中国大陆无法直接访问推特，推荐部署到 **GitHub Actions**（国外服务器，无需代理）。

### 部署步骤

1. **在 GitHub 创建仓库**
   - 登录 [github.com](https://github.com)
   - 新建仓库（如 `twitter-market-analyzer`）

2. **将代码 push 到仓库**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用户名/twitter-market-analyzer.git
   git push -u origin main
   ```

3. **设置 Secrets（API Key）**
   - 进入仓库 → `Settings` → `Secrets and variables` → `Actions`
   - 点击 `New repository secret`
   - Name: `MOONSHOT_API_KEY`
   - Value: 你的 API Key
   - 点击 `Add secret`

4. **手动触发测试**
   - 进入仓库 → `Actions` 标签
   - 点击 `每日推特财经言论分析`
   - 点击 `Run workflow` → `Run workflow`
   - 等待执行完成，报告会自动提交到 `reports/` 目录

5. **查看报告**
   - 每天北京时间 8:00 自动执行
   - 报告保存在 `reports/report_YYYY-MM-DD.md`
   - 数据保存在 `data/tweets_YYYYMMDD.json`

## 覆盖账号

| 优先级 | 博主 | 影响范围 |
|--------|------|----------|
| P1 | @elonmusk | TSLA、科技/AI、加密货币 |
| P1 | @realDonaldTrump | 大盘、关税、制造业 |
| P1 | @federalreserve | 全美股、利率 |
| P1 | @SECGov | 监管、中概股、加密货币 |
| P2 | @CathieWood | ARK ETF、成长股 |
| P2 | @BillAckman | 银行股、债市 |
| P2 | @Unusual_Whales | 期权异动 |
| P2 | @CNBC / @WSJ / @markets | 突发新闻 |
| P3 | @LynAldenContact / @PeterSchiff | 宏观分析 |

共 17 个账号，详见 `config/accounts.py`。

## 报告示例

报告按影响程度分级：
- 🚨 紧急关注
- ⚠️ 高市场影响
- 📌 中等市场影响
- 📝 其他动态

每条分析包含：情感倾向、美股板块影响、A股关联度、紧急程度、操作建议。

## 常见问题

**Q: snscrape 抓取失败怎么办？**
A: 推特在中国大陆被屏蔽。解决方案：
1. 使用 GitHub Actions 方案（推荐）
2. 使用代理：`--proxy http://host:port`
3. 切换 mock 模式：`--mock`

**Q: API Key 无效？**
A: 确认 Key 格式正确（`sk-` 开头），且未过期。可在 [Moonshot 平台](https://platform.moonshot.cn/) 查看余额和状态。

**Q: 如何添加/删除监控账号？**
A: 编辑 `config/accounts.py`，在对应列表中添加或删除 `TwitterAccount` 实例，设置 `enabled=False` 可临时停用。
