import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "ai-factory-v2"
sys.path.insert(0, str(APP_DIR))

import config
from agents.evaluator import EvaluatorAgent
from agents.executor import ExecutorAgent
from agents.generator import GeneratorAgent
from models.hypothesis import (
    CycleResult,
    Hypothesis,
    HypothesisScore,
    HypothesisStatus,
    Problem,
    RepositoryAnalysis,
)
from orchestrator import Orchestrator
from utils.github_client import GitHubClient


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


class DummyGenerator:
    def __init__(self, hypotheses):
        self.hypotheses = hypotheses

    def generate(self, problem, repo_context=""):
        return self.hypotheses


class DummyEvaluator:
    def __init__(self, hypotheses):
        self.hypotheses = hypotheses

    def evaluate(self, problem, hypotheses):
        return self.hypotheses


class FallbackCritic:
    def __init__(self):
        self.calls = []

    def validate(self, problem, hypothesis):
        self.calls.append(hypothesis.title)
        if hypothesis.title == "Primary option":
            hypothesis.status = HypothesisStatus.REJECTED
            hypothesis.critic_feedback = "blocked first option"
        else:
            hypothesis.status = HypothesisStatus.APPROVED
            hypothesis.critic_feedback = "approved fallback"
        return hypothesis


class SuccessExecutor:
    def __init__(self):
        self.executed = []

    def execute(self, cycle_result, hypothesis, problem, all_hypotheses):
        self.executed.append(hypothesis.title)
        cycle_result.pr_url = "https://example/pr/2"
        cycle_result.pr_number = 2
        hypothesis.status = HypothesisStatus.EXECUTED
        return cycle_result


class OrchestrationTaxonomyTests(unittest.TestCase):
    def test_generator_hardens_plan_with_validation_and_files(self):
        generator = GeneratorAgent(openai_client=object())
        problem = Problem(
            id="p1",
            title="Improve reliability",
            description="desc",
            category="maintainability",
            affected_files=["src/app.tsx"],
        )
        hypothesis = Hypothesis(
            id="h1",
            problem_id="p1",
            title="Minimal fix",
            description="desc",
            approach="logic simplification",
            implementation_plan="1. Make a small fix",
            files_to_modify=[],
        )

        hardened = generator._harden_hypothesis(problem, hypothesis)

        self.assertIn("validation", hardened.implementation_plan.lower())
        self.assertIn("rollback", hardened.implementation_plan.lower())
        self.assertEqual(hardened.files_to_modify, ["src/app.tsx"])

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

    def test_multi_repo_filter_honors_owner_scope_and_deduplicates(self):
        payloads = [
            {"full_name": "senarzuniga/repo-a", "owner": {"login": "senarzuniga"}, "archived": False, "fork": False},
            {"full_name": "senarzuniga/repo-a", "owner": {"login": "senarzuniga"}, "archived": False, "fork": False},
            {"full_name": "my-org/repo-b", "owner": {"login": "my-org"}, "archived": False, "fork": False},
            {"full_name": "someone-else/repo-c", "owner": {"login": "someone-else"}, "archived": False, "fork": False},
            {"full_name": "senarzuniga/repo-d", "owner": {"login": "senarzuniga"}, "archived": True, "fork": False},
            {"full_name": "my-org/repo-e", "owner": {"login": "my-org"}, "archived": False, "fork": True},
        ]

        filtered = GitHubClient._filter_repo_payloads(
            payloads,
            skip_archived=True,
            skip_forks=True,
            allowed_owners={"senarzuniga", "my-org"},
        )

        self.assertEqual(filtered, ["senarzuniga/repo-a", "my-org/repo-b"])

    def test_orchestrator_uses_fallback_hypothesis_after_critic_block(self):
        primary = Hypothesis(
            id="h1",
            problem_id="p1",
            title="Primary option",
            description="desc",
            approach="architecture refactor",
            implementation_plan="1. first",
            status=HypothesisStatus.SELECTED,
        )
        primary.score = HypothesisScore(8, 3, 4, 8, 8)

        fallback = Hypothesis(
            id="h2",
            problem_id="p1",
            title="Fallback option",
            description="desc",
            approach="logic simplification",
            implementation_plan="1. second",
            status=HypothesisStatus.EVALUATED,
        )
        fallback.score = HypothesisScore(7, 2, 3, 8, 7)

        orchestrator = Orchestrator.__new__(Orchestrator)
        orchestrator.generator = DummyGenerator([primary, fallback])
        orchestrator.evaluator = DummyEvaluator([primary, fallback])
        orchestrator.critic = FallbackCritic()
        orchestrator.executor = SuccessExecutor()

        result = CycleResult(cycle_id="c1", repository="owner/repo", decision_log=[])
        problem = Problem(id="p1", title="Improve reliability", description="desc", category="maintainability")
        analysis = RepositoryAnalysis(repo_context="ctx", problems=[problem])

        old_dry_run = config.DRY_RUN
        try:
            config.DRY_RUN = False
            created = orchestrator._process_problem(result, problem, analysis)
        finally:
            config.DRY_RUN = old_dry_run

        self.assertTrue(created)
        self.assertEqual(result.pr_url, "https://example/pr/2")
        self.assertEqual(orchestrator.executor.executed, ["Fallback option"])


if __name__ == "__main__":
    unittest.main()
