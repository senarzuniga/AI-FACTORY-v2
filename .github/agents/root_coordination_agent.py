"""Compatibility entrypoint for the canonical root coordination agent."""

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from root_coordination_agent import MissionAction, RootCoordinationAgent, main


__all__ = ["MissionAction", "RootCoordinationAgent", "main"]


if __name__ == "__main__":
    main()
