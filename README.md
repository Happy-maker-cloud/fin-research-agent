# Fin Research Agent

面向金融投研场景的可验证 Agent。

## 目标功能

- 金融行情和财务数据查询
- 财报与公告 RAG
- 金融指标计算
- 因子分析与回测
- MCP 工具服务
- Agent 轨迹评测
- 引用校验与合规审查

## 开发环境

- Python 3.11
- Conda 环境：fin_agent

## 本地安装

```bash
conda activate fin_agent
python -m pip install -e .
python -m pip install -r requirements-dev.txt
pytest