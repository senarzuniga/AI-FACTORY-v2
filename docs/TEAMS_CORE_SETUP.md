# Teams Core Setup

## Team
- Name: Ingercart Core
- Suggested URL slug: ingecart_core

## Channels
- general
- sales-ops
- docs-and-deliverables
- ai-engine
- incidents

## Integrations
- Pin SharePoint site in docs-and-deliverables channel.
- Add API health endpoint as a tab: http://localhost:8000/hub/status
- Add Human Portal tab: http://localhost:8502

## Governance
- Admin: isenar.cta@gmail.com
- Manager: sales@ingecart.es
- Admin chief: administracion@ingecart.es

## Notification Pattern
- New proposal approved -> notify docs-and-deliverables
- Validation issue -> notify incidents
- Deployment event -> notify general
