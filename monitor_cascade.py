#!/usr/bin/env python3
"""Real-time monitor for Cascade Orchestrator logs."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path


LOG_FILE = Path("logs/cascade.log")


class CascadeMonitor:
    def __init__(self, log_file: Path = LOG_FILE) -> None:
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self._last_pos = 0

    async def start(self) -> None:
        print("=" * 80)
        print("CASCADE ORCHESTRATOR MONITOR")
        print("=" * 80)
        print(f"Watching: {self.log_file}")

        while True:
            self._read_new_lines()
            await asyncio.sleep(0.5)

    def _read_new_lines(self) -> None:
        if not self.log_file.exists():
            return

        with self.log_file.open("r", encoding="utf-8") as f:
            f.seek(self._last_pos)
            lines = f.readlines()
            self._last_pos = f.tell()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            self._display(line)

    def _display(self, raw: str) -> None:
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            return

        event_type = event.get("type", "unknown")
        timestamp = event.get("timestamp", datetime.now().isoformat())
        short_ts = timestamp[11:19] if len(timestamp) >= 19 else timestamp
        data = event.get("data", {})

        if event_type == "cascade_started":
            print(f"[{short_ts}] START {data.get('cascade_id','')[:8]} | {data.get('trigger','')}")
        elif event_type == "agent_started":
            print(f"[{short_ts}] AGENT START {data.get('agent')} phase={data.get('phase')}")
        elif event_type == "agent.completed":
            print(f"[{short_ts}] AGENT DONE  {data.get('agent')} duration={float(data.get('duration',0.0)):.2f}s")
        elif event_type == "agent.failed":
            print(f"[{short_ts}] AGENT FAIL  {data.get('agent')} error={data.get('error')}")
        elif event_type == "cascade.phase_complete":
            print(f"[{short_ts}] PHASE DONE  {data.get('phase')}")
        elif event_type == "cascade_complete":
            print(
                f"[{short_ts}] COMPLETE    {data.get('cascade_id','')[:8]} "
                f"duration={float(data.get('duration',0.0)):.2f}s agents={len(data.get('agents_used',[]))}"
            )
        elif event_type == "cascade_failed":
            print(f"[{short_ts}] FAILED      {data.get('cascade_id','')[:8]} error={data.get('error',{}).get('message')}")
        elif event_type == "deployment_complete":
            print(f"[{short_ts}] DEPLOY      status={data.get('status')} id={data.get('deployment_id')}")


if __name__ == "__main__":
    asyncio.run(CascadeMonitor().start())
