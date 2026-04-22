# AI-FACTORY-v2

Autonomous multi-agent engineering orchestrator for GitHub repositories.

## Included capabilities

- Full repository analysis with structured summary and opportunity detection
- Multi-hypothesis generation with structural-diversity enforcement
- Scoring gates based on business impact, risk, complexity, maintainability, and scalability
- Critic validation with explicit risk tracking
- Safe execution guardrails for minimal, validated changes only
- Automatic branch and pull-request creation
- Learning history and per-cycle audit reports

## Run locally on Windows

1. Copy the environment template and fill in your credentials.
2. Set the following environment variables as needed:
   - `GITHUB_TOKEN`: Your GitHub token.
   - `GITHUB_REPOSITORY`: Target repository or "ALL".
   - `SKIP_REPOS`: Repositories to skip in ALL mode.
   - `SKIP_FORKS`: Set to "true" to skip forked repositories.
   - `OPENAI_API_KEY`: Your OpenAI API key.
   - `AI_MODEL`: AI model to use (default is "gpt-4o").
   - `AI_MAX_TOKENS`: Maximum tokens for AI (default is 4096).
   - `AI_TEMPERATURE`: Temperature for AI (default is 0.3).
   - `MIN_BUSINESS_IMPACT`, `MAX_TECHNICAL_RISK`, `MIN_MAINTAINABILITY`, `MIN_SCALABILITY`, `MIN_COMPOSITE_SCORE`, `MAX_COMPLEXITY`: Scoring thresholds.
   - `SUPABASE_URL`, `SUPABASE_KEY`: Supabase configuration for remote persistence.
3. Run the launcher from the app folder.
4. Use dry-run mode when you want analysis without PR creation.
