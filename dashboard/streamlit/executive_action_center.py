"""AI Executive Action Center for Ingecart / Outlook context."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Any, Iterable, Optional

import streamlit as st

from agents.action_engine import (
    Action,
    ActionCategory,
    ActionPool,
    ActionPriority,
    ActionRole,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INGECART_ROOT = Path(r"C:\Users\Inaki Senar\Documents\INGECART")
APP_TITLE = "AI Executive Action Center"

EMAIL_ACTION_PATTERNS = [
    r"\breply\b",
    r"\bfollow[- ]?up\b",
    r"\bfeedback\b",
    r"\bconfirm\b",
    r"\breview\b",
    r"\bwaiting\b",
    r"\bpending\b",
    r"\baction required\b",
    r"\bplease\b",
    r"\bcall\b",
    r"\bmeeting\b",
    r"\bquote\b",
    r"\bproposal\b",
    r"\bdeadline\b",
    r"\burgent\b",
    r"\bstatus update\b",
]

PROJECT_HINTS = {
    "cascades": "Cascades",
    "pacificsouth": "PacificSouth",
    "psc": "PSC",
    "fuma": "FUMA",
    "amr": "AMR",
    "waterloo": "Waterloo AMR",
    "ip amr": "IP AMR Project",
    "bhs": "BHS Corrugator",
    "page": "Page",
    "ingecart": "Ingecart",
    "sterner": "Sterner Global",
    "sigmaq": "Sigmaq Guatemala",
}

CATEGORY_HINTS = {
    ActionCategory.OFFER_CREATION: ("proposal", "quote", "cost", "price", "budget", "offer"),
    ActionCategory.QUOTE_SENDING: ("quotation", "quote", "proposal"),
    ActionCategory.PROJECT_MANAGEMENT: ("layout", "engineering", "validation", "freeze", "decision", "action register"),
    ActionCategory.INSTALLATION_PLANNING: ("installation", "commissioning", "site", "sat", "fat"),
    ActionCategory.AFTERSALES_SUPPORT: ("support", "warranty", "service", "aftersales"),
    ActionCategory.DELIVERY_COORDINATION: ("delivery", "shipment", "shipping", "logistics"),
    ActionCategory.NEGOTIATION: ("negotiation", "terms", "meeting", "call", "follow up"),
}


@dataclass
class MailItem:
    path: Path
    kind: str
    subject: str
    sender: str
    recipients: list[str]
    date: Optional[datetime]
    body: str
    project: str
    tags: list[str]
    action_required: bool
    waiting_for_response: bool
    priority: ActionPriority
    category: ActionCategory
    role: ActionRole
    score: float
    due_date: Optional[datetime]
    reason: str


def _safe_read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-16", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding, errors="ignore")
        except OSError:
            continue
    return ""


def _strip_html(text: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _project_from_text(value: str) -> str:
    haystack = value.lower()
    for needle, label in PROJECT_HINTS.items():
        if needle in haystack:
            return label
    return "General"


def _guess_project(path: Path, text: str) -> str:
    return _project_from_text(f"{path.as_posix()} {text[:2000]}")


def _extract_dates(text: str) -> list[datetime]:
    candidates: list[datetime] = []
    patterns = [
        r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b",
        r"\b(\d{1,2})-(\d{1,2})-(\d{2,4})\b",
        r"\b(\d{4}-\d{2}-\d{2})\b",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            try:
                if len(match.groups()) == 1:
                    candidates.append(datetime.fromisoformat(match.group(1)))
                    continue
                parts = [int(group) for group in match.groups()]
                if parts[2] < 100:
                    parts[2] += 2000
                candidates.append(datetime(parts[2], parts[1], parts[0]))
            except ValueError:
                continue
    return candidates


def _parse_eml(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_content()
                break
        if not body:
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    body = _strip_html(part.get_content())
                    break
    else:
        body = msg.get_content()
        if msg.get_content_type() == "text/html":
            body = _strip_html(body)

    try:
        parsed_date = parsedate_to_datetime(msg.get("Date")) if msg.get("Date") else None
    except (TypeError, ValueError):
        parsed_date = None

    subject = str(msg.get("Subject", "")).strip()
    sender = str(msg.get("From", "")).strip()
    recipients = [str(msg.get("To", "")).strip()]
    cc = str(msg.get("Cc", "")).strip()
    if cc:
        recipients.append(cc)

    return {
        "path": path,
        "kind": "email",
        "subject": subject,
        "sender": sender,
        "recipients": recipients,
        "date": parsed_date,
        "body": body or "",
    }


def _parse_text_like(path: Path) -> dict[str, Any]:
    text = _safe_read_text(path)
    lines = text.splitlines()
    fields = {"From": "", "To": "", "Cc": "", "Subject": "", "Date": ""}
    for line in lines[:25]:
        match = re.match(r"^(From|To|Cc|Subject|Date|Sent)\s*:\s*(.+)$", line.strip(), re.IGNORECASE)
        if match:
            fields[match.group(1).title()] = match.group(2).strip()

    subject = fields.get("Subject", "") or path.stem
    sender = fields.get("From", "")
    recipients = [fields.get("To", ""), fields.get("Cc", "")]
    body = text
    parsed_date = None
    for key in ("Date", "Sent"):
        value = fields.get(key, "")
        if value:
            try:
                parsed_date = parsedate_to_datetime(value)
                break
            except (TypeError, ValueError):
                continue

    if not sender and len(lines) > 0 and "@" in lines[0]:
        sender = lines[0]

    return {
        "path": path,
        "kind": "text",
        "subject": subject,
        "sender": sender,
        "recipients": [r for r in recipients if r],
        "date": parsed_date,
        "body": body,
    }


def _detect_signals(text: str) -> dict[str, Any]:
    lowered = text.lower()
    hits = [pattern for pattern in EMAIL_ACTION_PATTERNS if re.search(pattern, lowered)]
    waiting = any(
        token in lowered
        for token in (
            "waiting for",
            "pending response",
            "follow up",
            "no response",
            "response required",
            "reply required",
            "esperando",
            "sin respuesta",
            "pendiente",
        )
    )
    return {"hits": hits, "waiting": waiting}


def _category_for_text(text: str) -> ActionCategory:
    lowered = text.lower()
    for category, needles in CATEGORY_HINTS.items():
        if any(needle in lowered for needle in needles):
            return category
    return ActionCategory.PROJECT_MANAGEMENT


def _role_for_text(text: str) -> ActionRole:
    lowered = text.lower()
    if any(word in lowered for word in ("proposal", "quote", "price", "budget", "commercial", "sales")):
        return ActionRole.SALES
    if any(word in lowered for word in ("support", "warranty", "aftersales", "service")):
        return ActionRole.AFTERSALES
    if any(word in lowered for word in ("engineering", "layout", "validation", "amr", "technical")):
        return ActionRole.ENGINEERING
    if any(word in lowered for word in ("invoice", "cost", "administration")):
        return ActionRole.ADMIN
    return ActionRole.PROJECT_MANAGER


def _priority_for_text(text: str, waiting: bool) -> ActionPriority:
    lowered = text.lower()
    if any(word in lowered for word in ("urgent", "critical", "asap", "today", "immediately", "deadline")):
        return ActionPriority.CRITICAL
    if waiting or any(word in lowered for word in ("reply", "feedback", "follow up", "pending", "review", "confirm")):
        return ActionPriority.HIGH
    if any(word in lowered for word in ("meeting", "call", "proposal", "quote", "layout", "action")):
        return ActionPriority.MEDIUM
    return ActionPriority.LOW


def _due_date_for(text: str, base_date: datetime, priority: ActionPriority, waiting: bool) -> Optional[datetime]:
    dates = _extract_dates(text)
    if dates:
        normalized_base = _to_naive(base_date)
        return min(dates, key=lambda d: abs((_to_naive(d) - normalized_base).total_seconds()))
    if priority == ActionPriority.CRITICAL:
        return base_date + timedelta(days=1)
    if waiting:
        return base_date + timedelta(days=3)
    if priority == ActionPriority.HIGH:
        return base_date + timedelta(days=5)
    if priority == ActionPriority.MEDIUM:
        return base_date + timedelta(days=7)
    return None


def _score(priority: ActionPriority, waiting: bool, recency_days: int, text: str) -> float:
    score = priority.value * 18
    if waiting:
        score += 12
    score += max(0, 10 - min(recency_days, 10))
    if "attachment" in text.lower() or "adjunto" in text.lower():
        score += 4
    if any(word in text.lower() for word in ("proposal", "layout", "validation", "reply", "follow up")):
        score += 6
    return min(100.0, float(score))


def _to_naive(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.astimezone().replace(tzinfo=None)
    return dt


def _build_mail_item(path: Path) -> Optional[dict[str, Any]]:
    try:
        if path.suffix.lower() == ".eml":
            item = _parse_eml(path)
        else:
            item = _parse_text_like(path)
    except OSError:
        return None

    text = f"{item['subject']}\n{item['body']}"
    project = _guess_project(path, text)
    signals = _detect_signals(text)
    date = item["date"] or datetime.fromtimestamp(path.stat().st_mtime)
    priority = _priority_for_text(text, signals["waiting"])
    category = _category_for_text(text)
    role = _role_for_text(text)
    due_date = _due_date_for(text, date, priority, signals["waiting"])
    recency_days = max(0, (datetime.now() - _to_naive(date)).days)
    score = _score(priority, signals["waiting"], recency_days, text)
    tags = [project.lower().replace(" ", "_")]
    if signals["waiting"]:
        tags.append("waiting_follow_up")
    if signals["hits"]:
        tags.extend(sorted({hit.replace(r"\b", "").replace("\\", "") for hit in signals["hits"]}))

    action_required = priority.value >= ActionPriority.MEDIUM.value or signals["waiting"]
    reason = " / ".join(
        part
        for part in (
            f"Project: {project}",
            "Waiting for response" if signals["waiting"] else "",
            f"Signals: {', '.join(signals['hits'])}" if signals["hits"] else "",
        )
        if part
    )

    return {
        "path": path,
        "kind": item["kind"],
        "subject": item["subject"],
        "sender": item["sender"],
        "recipients": item["recipients"],
        "date": date,
        "body": item["body"],
        "project": project,
        "tags": tags,
        "action_required": action_required,
        "waiting_for_response": signals["waiting"],
        "priority": priority,
        "category": category,
        "role": role,
        "score": score,
        "due_date": due_date,
        "reason": reason or "General context item",
    }


def _iter_context_files(root: Path) -> Iterable[Path]:
    for suffix in (".eml", ".txt", ".md"):
        yield from root.rglob(f"*{suffix}")


@st.cache_data(show_spinner=False)
def build_report(root_value: str, refresh_token: int = 0) -> dict[str, Any]:
    root = Path(root_value)
    items: list[dict[str, Any]] = []
    errors: list[str] = []

    if not root.exists():
        return {
            "root": str(root),
            "items": [],
            "actions": [],
            "notes": [],
            "errors": [f"Source root not found: {root}"],
            "statistics": {},
            "projects": [],
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        }

    for path in _iter_context_files(root):
        if path.stat().st_size > 1_000_000:
            continue
        try:
            built = _build_mail_item(path)
            if built:
                items.append(built)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: {exc}")

    actions: list[Action] = []
    notes: list[dict[str, Any]] = []
    pool = ActionPool()

    for item in items:
        if item["action_required"]:
            title = item["subject"] or item["path"].stem
            description = f"{item['project']} | {item['reason']}"
            action = Action(
                id=f"MAIL_{len(actions)+1:04d}",
                title=title[:120],
                description=description[:280],
                category=item["category"],
                priority=item["priority"],
                role=item["role"],
                score=item["score"],
                created_at=item["date"],
                due_date=item["due_date"],
                source=str(item["path"]),
                context_data={
                    "path": str(item["path"]),
                    "project": item["project"],
                    "sender": item["sender"],
                    "recipients": item["recipients"],
                    "tags": item["tags"],
                    "kind": item["kind"],
                },
                tags=item["tags"],
            )
            actions.append(action)
            pool.add_action(action)
        else:
            notes.append(
                {
                    "title": item["subject"] or item["path"].stem,
                    "project": item["project"],
                    "path": str(item["path"]),
                    "date": item["date"].isoformat(timespec="seconds") if item["date"] else "",
                    "snippet": (item["body"] or "")[:220].replace("\n", " ").strip(),
                }
            )

    actions.sort(key=lambda a: (a.priority.value, a.score), reverse=True)
    notes.sort(key=lambda n: n["date"], reverse=True)

    today = datetime.now()
    stats = {
        "files_scanned": len(items),
        "emails": len([i for i in items if i["kind"] == "email"]),
        "documents": len([i for i in items if i["kind"] == "text"]),
        "actions": len(actions),
        "unprocessed": len([i for i in items if i["kind"] == "email" and i["action_required"]]),
        "critical": len([a for a in actions if a.priority == ActionPriority.CRITICAL]),
        "high": len([a for a in actions if a.priority == ActionPriority.HIGH]),
        "waiting": len([a for a in actions if "waiting_follow_up" in a.tags]),
        "overdue": len(
            [
                a
                for a in actions
                if a.due_date and _to_naive(a.due_date) < today and a.status == "pending"
            ]
        ),
        "this_week": len(
            [
                a
                for a in actions
                if a.due_date and 0 <= (_to_naive(a.due_date) - today).days <= 7
            ]
        ),
        "recommendations": min(6, len(actions)),
    }
    project_counter = Counter(item["project"] for item in items)

    return {
        "root": str(root),
        "items": items,
        "actions": [action_to_dict(a) for a in actions],
        "notes": notes[:50],
        "errors": errors,
        "statistics": stats,
        "projects": project_counter.most_common(10),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "action_pool_stats": pool.get_statistics(),
    }


def action_to_dict(action: Action) -> dict[str, Any]:
    return {
        "id": action.id,
        "title": action.title,
        "description": action.description,
        "priority": action.priority.name,
        "role": action.role.value,
        "category": action.category.value,
        "score": action.score,
        "due_date": action.due_date.isoformat(timespec="seconds") if action.due_date else "",
        "source": action.source,
        "tags": action.tags,
        "context_data": action.context_data,
    }


def _metric_value(label: str, value: Any) -> None:
    st.metric(label, value)


def _action_card(action: dict[str, Any], index: int) -> None:
    due = action["due_date"] or "No due date"
    st.markdown(
        f"""
        <div style="padding:12px 14px;border:1px solid rgba(255,255,255,0.08);border-radius:14px;margin-bottom:10px;background:rgba(255,255,255,0.03);">
            <div style="display:flex;justify-content:space-between;gap:12px;">
                <div style="font-weight:700;">{index}. {action['title']}</div>
                <div style="font-size:12px;opacity:0.8;">{action['priority']} | score {action['score']:.1f}</div>
            </div>
            <div style="margin-top:6px;font-size:13px;opacity:0.92;">{action['description']}</div>
            <div style="margin-top:8px;font-size:12px;opacity:0.75;">{action['role']} · {action['category']} · Due: {due}</div>
            <div style="margin-top:4px;font-size:11px;opacity:0.62;">{action['source']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _note_card(note: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div style="padding:10px 12px;border:1px solid rgba(255,255,255,0.06);border-radius:12px;margin-bottom:10px;">
            <div style="font-weight:600;">{note['title']}</div>
            <div style="font-size:12px;opacity:0.75;">{note['project']} · {note['date']}</div>
            <div style="margin-top:6px;font-size:13px;opacity:0.9;">{note['snippet']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _build_briefing(actions: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    top = actions[:4]
    for action in top:
        label = action["title"] or action["description"]
        due = action["due_date"][:10] if action["due_date"] else "soon"
        lines.append(f"- {label} ({action['priority']}, due {due})")
    if not lines:
        lines.append("- No high-signal items found in the selected source folder.")
    return lines


def _download_payload(report: dict[str, Any]) -> str:
    payload = {
        "generated_at": report["generated_at"],
        "statistics": report["statistics"],
        "projects": report["projects"],
        "actions": report["actions"][:25],
        "notes": report["notes"][:25],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="AI", layout="wide")

    st.markdown(
        """
        <style>
            .block-container { padding-top: 1rem; }
            div[data-testid="metric-container"] { background: rgba(255,255,255,0.03); padding: 10px 12px; border-radius: 12px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title(APP_TITLE)
    st.caption("Executive Action & Follow-up Center for Ingecart mailbox context")

    with st.sidebar:
        st.header("Source settings")
        root_input = st.text_input("Context root", value=str(DEFAULT_INGECART_ROOT))
        refresh = st.button("Refresh analysis", use_container_width=True)
        st.caption("This panel analyzes .eml, .txt and .md files from the selected root.")
        st.divider()
        st.markdown("**Local focus**")
        st.write("- Outlook mail context")
        st.write("- Ingecart project documents")
        st.write("- Follow-up and action detection")

    report = build_report(root_input, 1 if refresh else 0)

    if report["errors"]:
        with st.expander("Parsing warnings", expanded=False):
            for error in report["errors"][:20]:
                st.write(f"- {error}")

    stats = report["statistics"]
    metrics = st.columns(6)
    with metrics[0]:
        _metric_value("🔴 Critical actions", stats.get("critical", 0))
    with metrics[1]:
        _metric_value("🟠 Pending this week", stats.get("this_week", 0))
    with metrics[2]:
        _metric_value("⏳ Waiting", stats.get("waiting", 0))
    with metrics[3]:
        _metric_value("📧 Emails sin procesar", stats.get("unprocessed", 0))
    with metrics[4]:
        _metric_value("📅 Tasks vencidas", stats.get("overdue", 0))
    with metrics[5]:
        _metric_value("🤖 Recomendaciones IA", stats.get("recommendations", 0))

    briefing = _build_briefing(report["actions"])
    left, right = st.columns([1.3, 1])
    with left:
        st.subheader("AI briefing")
        st.markdown("**Today | Priority | Waiting | Follow-up | Tasks | Notes | Intelligence**")
        st.markdown(
            "\n".join(
                [
                    "Good morning, Inaki.",
                    "",
                    f"You have {stats.get('critical', 0)} critical actions today and {stats.get('this_week', 0)} items to review this week.",
                    "",
                    "Recommended focus:",
                    *briefing,
                ]
            )
        )
    with right:
        st.subheader("Download")
        st.download_button(
            "Export summary JSON",
            data=_download_payload(report),
            file_name="ai_executive_action_center_summary.json",
            mime="application/json",
            use_container_width=True,
        )
        st.caption(f"Generated at {report['generated_at']}")

    tabs = st.tabs(["Today", "Priority", "Waiting", "Follow-up", "Tasks", "Notes", "Intelligence"])
    actions = report["actions"]
    notes = report["notes"]

    with tabs[0]:
        todays = [
            action
            for action in actions
            if action["priority"] in {"CRITICAL", "HIGH"}
            or (action["due_date"] and action["due_date"][:10] == datetime.now().strftime("%Y-%m-%d"))
        ]
        for idx, action in enumerate(todays[:8], start=1):
            _action_card(action, idx)

    with tabs[1]:
        for idx, action in enumerate(actions[:12], start=1):
            _action_card(action, idx)

    with tabs[2]:
        waiting = [action for action in actions if "waiting_follow_up" in action["tags"]]
        for idx, action in enumerate(waiting[:12], start=1):
            _action_card(action, idx)

    with tabs[3]:
        follow_up = [action for action in actions if action["priority"] in {"CRITICAL", "HIGH"}]
        for idx, action in enumerate(follow_up[:12], start=1):
            _action_card(action, idx)

    with tabs[4]:
        overdue = [
            action
            for action in actions
            if action["due_date"] and action["due_date"][:10] < datetime.now().strftime("%Y-%m-%d")
        ]
        upcoming = [
            action
            for action in actions
            if action["due_date"]
            and datetime.now().strftime("%Y-%m-%d")
            <= action["due_date"][:10]
            <= (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        ]
        c1, c2 = st.columns(2)
        with c1:
            st.write("Overdue")
            for idx, action in enumerate(overdue[:8], start=1):
                _action_card(action, idx)
        with c2:
            st.write("Upcoming")
            for idx, action in enumerate(upcoming[:8], start=1):
                _action_card(action, idx)

    with tabs[5]:
        for note in notes[:20]:
            _note_card(note)

    with tabs[6]:
        p1, p2, p3 = st.columns(3)
        with p1:
            st.subheader("Source mix")
            st.write(f"- Files scanned: {stats.get('files_scanned', 0)}")
            st.write(f"- Emails: {stats.get('emails', 0)}")
            st.write(f"- Documents: {stats.get('documents', 0)}")
        with p2:
            st.subheader("Top projects")
            for project, count in report["projects"]:
                st.write(f"- {project}: {count}")
        with p3:
            st.subheader("Action engine")
            for key, value in report.get("action_pool_stats", {}).items():
                if key != "by_role" and key != "by_priority":
                    st.write(f"- {key}: {value}")

        st.divider()
        st.subheader("Selected action evidence")
        for action in actions[:5]:
            with st.expander(action["title"], expanded=False):
                st.write(action["description"])
                st.write(f"Source: {action['source']}")
                st.write(f"Tags: {', '.join(action['tags'])}")
                st.write(f"Context: {json.dumps(action['context_data'], ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()
