# Gap Analysis

## Architecture gaps

- The repo contains a real AI_FACTORY and a real operational shell, but the boundary between them is not yet fully formalized in the generic menu.
- The user-facing shell is not yet aligned with a strict IS_BACKOFFICE model.
- The AI_FACTORY brain remains visible enough to blur the separation of concerns.

## Application gaps

- The transcript app is added but still under development.
- The repository does not yet expose a canonical application registry in a single authoritative file for all operational apps.
- Some app metadata is present in scripts and configuration, but it is not consolidated in a single registry structure.

## Integration gaps

- Direct links between AI_FACTORY and the menu shell are present, but not formalized in a strict app contract model.
- The linked external business app is operational but not represented as a fully integrated app contract.

## UI gaps

- The menu is not yet fully canonicalized into user-visible business panels.
- Internal engines and technical services are still too accessible in the general dashboard context.

## API gaps

- Metadata and health endpoints are present, but there is no global application contract registry for API health and routes.
- No single application registry maps route to health endpoint and owner.

## Registry gaps

- Capability and platform registry files are not yet part of the canonical runtime catalog.
- The app catalog is currently fragmented across JSON, scripts, and documentation.

## Testing gaps

- Smoke tests exist, but there is no end-to-end validation across the general menu to the app, API, and backend functions.
- There is no explicit test coverage for the transcript panel or general navigation shell.

## Documentation gaps

- Documentation exists, but it is spread across README.md, .forge, docs/, and ad-hoc logs.
- Architecture documents need to be centralized under /Architecture.

## Knowledge gaps

- The system has useful knowledge artifacts, but the repo is not yet presenting them as a single knowledge hub experience.

## Evidence gaps

- Logs, config, and data exist, but there is no unified evidence registry connecting each application to its health/status evidence.

## Security gaps

- There is no formal application-level security model for user roles and endpoints in the menu shell.

## Performance gaps

- The local UI shell is lightweight, but it does not yet provide a clear latency/performance contract or benchmark for each app.

## Technical debt

- Legacy AI_FACTORY v2 remains active in parallel with the newer orchestrator/ directory.
- Some menu and launch scripts still refer to older assumptions about external apps.

## Duplicate functionality

- The repo has a duplicate conceptual split between a legacy AI implementation and the active protocol orchestrator.
- The operational shell and the orchestration shell should remain separated to avoid duplication.

## Orphan components

- Several internal engine modules and metadata files are not directly user-visible.
- They should remain, but not be surfaced as independent applications.
