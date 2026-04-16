import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "ai-factory-v2"
sys.path.insert(0, str(APP_DIR))

from agents.evaluator import EvaluatorAgent
from agents.executor import ExecutorAgent
from models.hypothesis import (
    CycleResult,
    Hypothesis,
    HypothesisScore,
    HypothesisStatus,
    Problem,
)


class FakeGitHubClient:
    def __init__(self):
        self.branch_created = False
        self.upserts = []

    def create_branch(self, branch_name):
        self.branch_created = True
        return "sha"

    def upsert_file(self, path, content, message, branch):
        self.upserts.append((path, content, message, branch))
        return {}

    def create_pull_request(self, title, body, head, base=None, labels=None):
        return {"html_url": "https://example/pr/1", "number": 1}

    def get_file_content(self, path):
        return "print('hello')\n"


class SafetyExecutor(ExecutorAgent):
    def __init__(self, github_client):
        super().__init__(github_client=github_client, openai_client=object())

    def _generate_changes(self, hypothesis):
        return [
            {"path": f"src/file_{i}.py", "content": f"print({i})\n"}
            for i in range(10)
        ]


class OrchestrationTaxonomyTests(unittest.TestCase):
    def test_problem_fields_are_normalized_to_taxonomy(self):
        problem = Problem(
            id="p1",
            title="Improve performance",
            description="desc",
            category="Performance / Optimization",
            priority="Critical",
        )
        self.assertEqual(problem.category, "performance")
        self.assertEqual(problem.priority, "critical")

    def test_evaluator_rejects_low_quality_selected_option(self):
        evaluator = EvaluatorAgent(openai_client=object())
        hypothesis = Hypothesis(
            id="h1",
            problem_id="p1",
            title="Unsafe option",
            description="desc",
            approach="large refactor",
            implementation_plan="1. Rewrite many things",
        )
        hypothesis.score = HypothesisScore(
            business_impact=8,
            technical_risk=3,
            complexity=8,
            maintainability=2,
            scalability=2,
        )
        hypothesis.status = HypothesisStatus.EVALUATED

        evaluator._select_best([hypothesis])
        self.assertNotEqual(hypothesis.status, HypothesisStatus.SELECTED)

    def test_executor_blocks_mass_changes_for_safety(self):
        github = FakeGitHubClient()
        executor = SafetyExecutor(github)
        cycle = CycleResult(cycle_id="c1", repository="owner/repo")
        hypothesis = Hypothesis(
            id="h1",
            problem_id="p1",
            title="Too many changes",
            description="desc",
            approach="broad rewrite",
            implementation_plan="1. Touch everything",
            files_to_modify=["src/file_1.py"],
            status=HypothesisStatus.APPROVED,
        )
        problem = Problem(
            id="p1",
            title="Problem",
            description="desc",
            category="maintainability",
        )

        result = executor.execute(cycle, hypothesis, problem, [hypothesis])

        self.assertTrue(result.rejected)
        self.assertFalse(github.branch_created)
        self.assertIsNone(result.pr_url)


if __name__ == "__main__":
    unittest.main()
