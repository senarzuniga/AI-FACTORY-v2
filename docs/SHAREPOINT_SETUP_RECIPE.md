# SharePoint Setup Recipe

## Goal
Create a repeatable SharePoint site structure for Ingercart collaboration.

## Site
- Site URL: https://ingecart.sharepoint.com/sites/Adaptive-Sales-Core
- Site owner: isenar.cta@gmail.com

## Core Structure
- 00_ADMIN
- 01_TEMPLATES
- 02_INTERNAL_OPERATIONS
- 03_AI_ENGINE
- 04_SHARED_RESOURCES

## Client Structure
Create one client root per customer:
- client_ingercart

Inside client_ingercart:
- 00_GOVERNANCE
- 01_INPUT_DATA
- 02_ANALYSIS
- 03_PROJECTS
- 04_DELIVERABLES
- 05_COMMUNICATION
- 99_ARCHIVE

## Permissions
- Admin: full control
- Manager: contribute + approve
- Admin chief: contribute + governance
- External guest: read-only in 04_DELIVERABLES only

## Operational Rules
- Publish final artifacts to 04_DELIVERABLES only.
- Keep drafts in 03_PROJECTS or 02_ANALYSIS.
- Never share internal operation folders externally.
