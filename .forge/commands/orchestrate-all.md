---
description: Complete ecosystem optimization command for AI-FACTORY-v2
---

Run the complete agent optimization workflow:

1. **/factory-init --force --create-agents --setup-actor-framework**
2. **/scan-agents --depth=recursive --discover-interactions --map-dependencies**
3. **@product-owner /optimize-vision --repository="AI-FACTORY-v2"**
4. **@architect /restructure-agents --target=performance**
5. **@planner /create-optimization-milestones --agents=all**
6. **@technical-writer /refine-agent-specs**
7. **@engineer /implement-agent-optimizations --changeset=complete**
8. **@quality-assurance /validate-agent-performance**
9. **/sync-agent-configs --source="AI-FACTORY-v2" --targets=auto-discovered**
10. **/optimize-agent-performance --mode=aggressive**
11. **/agent-learning-loop --source=interaction-logs --auto-correct**
12. **/validate-ecosystem --tests=all**
13. **/deploy-agents --environment=production**

After completion, run:
- **/monitor-agents --duration=24h --auto-remediate**
- **/auto-improvement-pr --schedule=hourly**

Invoke with:

```bash
/orchestrate-all --force --yes --verbose
```
