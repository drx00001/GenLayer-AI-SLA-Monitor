# GenLayer-AI-SLA-Monitor
一个技术型 GenLayer 项目: AI SLA 监控与争议判定应用。项目包含 SlaMonitor 智能合约，接收 API 可用性、延迟、错误率、区域、端点和事件日志等 incident packet JSON，由 GenLayer validators 通过 AI 共识判断是否违反 SLA，输出 breached、severity、credit_bps 和 reason，并包含 app/index.html 前端用于生成部署参数和 submit_incident(packet_json) 调用参数。
# GenLayer AI SLA Monitor

Technical GenLayer project for AI-assisted service-level agreement monitoring.

The app models an operations workflow: a service provider publishes SLA terms, an operator submits incident telemetry, and GenLayer validators decide whether the evidence proves an SLA breach.

## Files

- `contracts/sla_monitor.py` - Intelligent Contract that evaluates incident telemetry with AI consensus.
- `app/index.html` - static frontend for building constructor args and incident payloads.

## Use Case

API uptime and latency disputes often depend on mixed evidence: logs, timestamps, error rates, regions, failed endpoints, and plain-English incident notes. A normal smart contract can check fixed numbers, but it cannot judge whether messy incident evidence actually proves a contractual breach. GenLayer validators can reason over the incident packet and reach consensus on the result.

## Contract Flow

1. Deploy `SlaMonitor` with a service name and SLA terms.
2. Submit an incident packet as JSON text.
3. Validators return:
   - `breached`: true or false
   - `severity`: `none`, `minor`, `major`, or `critical`
   - `credit_bps`: service credit in basis points
   - `reason`: short technical explanation
4. The contract stores the latest verdict for users, operators, or payout logic.

## Example Incident Packet

```json
{
  "window": "2026-07-05T08:00:00Z/2026-07-05T09:00:00Z",
  "region": "ap-southeast-1",
  "endpoint": "/v1/orders",
  "availability_percent": 98.72,
  "p95_latency_ms": 1840,
  "error_rate_percent": 1.28,
  "logs": "Elevated 5xx responses for 31 minutes after database failover.",
  "operator_note": "Users could submit reads but order creation intermittently failed."
}
```

## Deploy

Deploy through GenLayer Studio:

1. Open https://studio.genlayer.com/contracts
2. Import `contracts/sla_monitor.py`
3. Constructor args:
   - `service_name`: `Order API`
   - `sla_terms`: `Availability must be at least 99.9%, p95 latency below 800ms, and error rate below 0.1% per one-hour window.`
4. Call `submit_incident(packet_json)` with the incident packet.
