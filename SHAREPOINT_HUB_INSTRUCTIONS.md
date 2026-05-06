# SharePoint Hub Usage Guide

This guide explains how to use the SharePoint Hub for client deliverables in AI-FACTORY-v2 workflows.

## 1. Purpose

The SharePoint Hub is the central location to:
- store client artifacts
- review and approve generated outputs
- publish final deliverables for teams and stakeholders

## 2. Recommended Folder Structure

Use one top-level folder per client:
- `client_<ClientName>/`

Inside each client folder, use:
- `01_BRIEF/` for requirements and context
- `02_ANALYSIS/Reports/` for analysis outputs
- `03_WORKING/` for drafts and internal revisions
- `04_DELIVERABLES/Proposals/` for final proposals
- `04_DELIVERABLES/Presentations/` for final decks

## 3. Upload and Naming Rules

Use clear filenames with date and version:
- `YYYY-MM-DD_<client>_<artifact>_vN.ext`

Examples:
- `2026-05-03_ingercart_proposal_v1.docx`
- `2026-05-03_ingercart_q2-report_v2.xlsx`

Best practices:
- keep names lowercase and consistent
- avoid spaces in automated artifacts
- increment version only after meaningful edits

## 4. Permissions Model

Apply least-privilege access:
- Readers: view-only access
- Contributors: upload and edit drafts
- Approvers: validate and approve release
- Admins: full access and external sharing control

Before external sharing:
- confirm the file is approved
- verify no sensitive internal data is included
- use expiration dates on external links when possible

## 5. Human Approval Workflow

For high-impact assets (proposals, external delivery):
1. Upload draft to `03_WORKING/`.
2. Request review from approver.
3. Resolve comments and update version.
4. Move approved file to `04_DELIVERABLES/`.
5. Publish link to the client communication channel.

## 6. Versioning and Recovery

Use SharePoint version history to:
- compare revisions
- restore a previous file version
- audit who changed what and when

Do not delete old versions unless retention policy requires it.

## 7. Teams Integration

When posting in Teams:
- share the SharePoint link, not local attachments
- include summary, owner, and due date
- pin the latest approved deliverable in the project channel

## 8. Integration With This Repository

The delivery flow can publish to SharePoint destinations based on content type:
- proposal -> `04_DELIVERABLES/Proposals`
- report -> `02_ANALYSIS/Reports`
- presentation -> `04_DELIVERABLES/Presentations`

If you update folder conventions, also update the delivery mapping in the delivery agent so automation stays aligned.

## 9. Troubleshooting

If upload fails:
- check file size limits
- verify your role has write permission
- confirm folder path exists

If link access fails:
- review link sharing scope (internal vs external)
- confirm recipient domain permissions
- regenerate sharing link with correct access level

## 10. Quick Checklist

Before publishing:
- content validated
- naming follows standard
- correct destination folder
- permissions reviewed
- approval recorded
- Teams link posted
