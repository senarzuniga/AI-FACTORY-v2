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
from hashlib import sha1
from html import escape, unescape
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

PRIORITIES_PATH = REPO_ROOT / "data" / "commercial_priorities.json"
CHAT_LOG_PATH = REPO_ROOT / "data" / "agent_chat_log.json"
ACTION_STATE_PATH = REPO_ROOT / "data" / "action_center_state.json"


def load_priorities() -> dict[str, Any]:
    """Load the canonical commercial priority registry.

    The registry is the single source of truth for account ranking, closed
    topics and key people. Editing the JSON (or using the Chat tab) changes the
    dashboard behaviour without touching this module.
    """
    try:
        with PRIORITIES_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {"accounts": [], "key_people": [], "supersedes": []}


PRIORITIES = load_priorities()

PROJECT_HINTS = {
    needle.lower(): account["name"]
    for account in PRIORITIES.get("accounts", [])
    for needle in account.get("match", [])
}

ACCOUNT_WEIGHTS = {
    account["name"]: account.get("weight", 50)
    for account in PRIORITIES.get("accounts", [])
}

DEMOTED_ACCOUNTS = {
    account["name"]
    for account in PRIORITIES.get("accounts", [])
    if account.get("demote")
}

CLOSED_TOPICS = [
    topic.lower()
    for topic in PRIORITIES.get("supersedes", [])
] + [
    topic.lower()
    for account in PRIORITIES.get("accounts", [])
    for topic in account.get("closed_topics", [])
]

KEY_PEOPLE = {
    person["name"].lower(): person
    for person in PRIORITIES.get("key_people", [])
}


def _is_closed_topic(subject: str) -> bool:
    """Return True when a subject matches a topic the user marked as closed."""
    haystack = (subject or "").lower()
    if not haystack:
        return False
    for topic in CLOSED_TOPICS:
        stem = topic.lstrip("fwd:").lstrip("re:").strip()
        if stem and stem[:40] in haystack:
            return True
    return False


def load_action_state() -> dict[str, Any]:
    """Load user-managed action edits, closures and operational notes."""
    try:
        with ACTION_STATE_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        data = {}
    return {
        "version": data.get("version", 1),
        "updated_at": data.get("updated_at", ""),
        "actions": data.get("actions", {}),
        "manual_actions": data.get("manual_actions", []),
        "notes": data.get("notes", []),
    }


def save_action_state(state: dict[str, Any]) -> None:
    """Persist action-center state to disk."""
    ACTION_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state["version"] = 1
    state["updated_at"] = datetime.now().isoformat(timespec="seconds")
    with ACTION_STATE_PATH.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, ensure_ascii=False)


def _stable_action_id(source: str, title: str) -> str:
    digest = sha1(f"{source}|{title}".encode("utf-8", errors="ignore")).hexdigest()[:12]
    return f"MAIL_{digest}"


def _parse_action_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


def _deadline_urgency_boost(due_date: Optional[datetime]) -> tuple[float, str]:
    """Return urgency score added by proximity to the action deadline."""
    if not due_date:
        return 0.0, "no_deadline"
    today = datetime.now().date()
    days = (_to_naive(due_date).date() - today).days
    if days < 0:
        return 35.0, "overdue"
    if days == 0:
        return 30.0, "due_today"
    if days == 1:
        return 24.0, "due_tomorrow"
    if days <= 3:
        return 18.0, "due_in_3_days"
    if days <= 7:
        return 10.0, "due_this_week"
    if days <= 14:
        return 5.0, "due_next_two_weeks"
    return 0.0, "scheduled"


def _priority_from_name(value: str, fallback: str) -> str:
    candidate = (value or "").upper()
    names = {priority.name for priority in ActionPriority}
    return candidate if candidate in names else fallback


def _priority_rank(value: str) -> int:
    try:
        return ActionPriority[value].value
    except KeyError:
        return 0


def _default_recommendations(action: dict[str, Any]) -> str:
    priority = action.get("priority", "LOW")
    project = action.get("context_data", {}).get("project", "General")
    due = action.get("due_date")[:10] if action.get("due_date") else "without confirmed deadline"
    return (
        f"Review this {priority.lower()} action for {project}. Confirm the real business next step, "
        f"owner and deadline ({due}). If it no longer requires action, close it to keep the pipeline clean."
    )


def _context_boost_for_action(action: dict[str, Any], chat_messages: list[dict[str, Any]]) -> float:
    project = action.get("context_data", {}).get("project") or ""
    if not project:
        return 0.0
    recent_project_context = [
        message
        for message in chat_messages
        if message.get("role") == "user"
        and message.get("project") == project
        and message.get("intent") in {"context", "priority", "question"}
    ]
    return min(10.0, float(len(recent_project_context) * 2))


def apply_action_state(report: dict[str, Any]) -> dict[str, Any]:
    """Apply persisted edits and deadline urgency to generated actions."""
    state = load_action_state()
    chat_messages = load_chat_log()
    active_actions: list[dict[str, Any]] = []
    closed_actions: list[dict[str, Any]] = []

    for action in report["actions"]:
        overrides = state["actions"].get(action["id"], {})
        due_date = _parse_action_datetime(overrides.get("due_date") or action.get("due_date"))
        deadline_boost, deadline_status = _deadline_urgency_boost(due_date)
        base_score = float(overrides.get("score", action["score"]))
        context_boost = _context_boost_for_action(action, chat_messages)
        action.update(
            {
                "title": overrides.get("title", action["title"]),
                "description": overrides.get("description", action["description"]),
                "priority": _priority_from_name(overrides.get("priority", ""), action["priority"]),
                "score": min(100.0, base_score + deadline_boost + context_boost),
                "base_score": base_score,
                "deadline_boost": deadline_boost,
                "context_boost": context_boost,
                "deadline_status": deadline_status,
                "due_date": due_date.isoformat(timespec="seconds") if due_date else "",
                "status": overrides.get("status", action.get("status", "pending")),
                "owner": overrides.get("owner", action.get("owner", "")),
                "next_step": overrides.get("next_step", action.get("next_step", "")),
                "content": overrides.get("content", action.get("content", action["description"])),
                "editable_context": overrides.get(
                    "editable_context",
                    action.get("editable_context", json.dumps(action["context_data"], ensure_ascii=False, indent=2)),
                ),
                "recommendations": overrides.get(
                    "recommendations",
                    action.get("recommendations", _default_recommendations(action)),
                ),
                "management_notes": overrides.get("management_notes", action.get("management_notes", "")),
            }
        )
        if action["status"] in {"closed", "completed", "dismissed"}:
            closed_actions.append(action)
        else:
            active_actions.append(action)

    for manual_action in state["manual_actions"]:
        due_date = _parse_action_datetime(manual_action.get("due_date"))
        deadline_boost, deadline_status = _deadline_urgency_boost(due_date)
        base_score = float(manual_action.get("score", 50))
        action = {
            "id": manual_action["id"],
            "title": manual_action.get("title", "Manual action"),
            "description": manual_action.get("description", ""),
            "priority": _priority_from_name(manual_action.get("priority", ""), "MEDIUM"),
            "role": manual_action.get("role", ActionRole.SALES.value),
            "category": manual_action.get("category", ActionCategory.PROJECT_MANAGEMENT.value),
            "score": min(100.0, base_score + deadline_boost),
            "base_score": base_score,
            "deadline_boost": deadline_boost,
            "context_boost": 0.0,
            "deadline_status": deadline_status,
            "due_date": due_date.isoformat(timespec="seconds") if due_date else "",
            "source": manual_action.get("source", "manual_note"),
            "tags": manual_action.get("tags", ["manual"]),
            "context_data": manual_action.get("context_data", {}),
            "status": manual_action.get("status", "pending"),
            "owner": manual_action.get("owner", ""),
            "next_step": manual_action.get("next_step", ""),
            "content": manual_action.get("content", manual_action.get("description", "")),
            "editable_context": manual_action.get("editable_context", ""),
            "recommendations": manual_action.get("recommendations", ""),
            "management_notes": manual_action.get("management_notes", ""),
        }
        if action["status"] in {"closed", "completed", "dismissed"}:
            closed_actions.append(action)
        else:
            active_actions.append(action)

    active_actions.sort(key=lambda item: (_priority_rank(item["priority"]), item["score"]), reverse=True)
    report["actions"] = active_actions
    report["closed_actions"] = closed_actions
    report["managed_notes"] = state["notes"]
    today = datetime.now().date()
    report["statistics"].update(
        {
            "actions": len(active_actions),
            "closed_actions": len(closed_actions),
            "overdue": len(
                [
                    action
                    for action in active_actions
                    if action["due_date"]
                    and _parse_action_datetime(action["due_date"])
                    and _parse_action_datetime(action["due_date"]).date() < today
                ]
            ),
            "this_week": len(
                [
                    action
                    for action in active_actions
                    if action["due_date"]
                    and _parse_action_datetime(action["due_date"])
                    and 0 <= (_parse_action_datetime(action["due_date"]).date() - today).days <= 7
                ]
            ),
            "critical": len([action for action in active_actions if action["priority"] == "CRITICAL"]),
            "high": len([action for action in active_actions if action["priority"] == "HIGH"]),
            "deadline_risk": len(
                [
                    action
                    for action in active_actions
                    if action.get("deadline_status") in {"overdue", "due_today", "due_tomorrow", "due_in_3_days"}
                ]
            ),
        }
    )
    return report

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
    for needle in sorted(PROJECT_HINTS, key=len, reverse=True):
        if needle in haystack:
            return PROJECT_HINTS[needle]
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
            if _is_closed_topic(title):
                continue
            description = f"{item['project']} | {item['reason']}"
            weight = ACCOUNT_WEIGHTS.get(item["project"], 40)
            priority = item["priority"]
            if item["project"] in DEMOTED_ACCOUNTS and priority in {
                ActionPriority.CRITICAL,
                ActionPriority.HIGH,
            }:
                priority = ActionPriority.MEDIUM
            action_id = _stable_action_id(str(item["path"]), title)
            action = Action(
                id=action_id,
                title=title[:120],
                description=description[:280],
                category=item["category"],
                priority=priority,
                role=item["role"],
                score=item["score"] * (weight / 100.0),
                created_at=item["date"],
                due_date=item["due_date"],
                source=str(item["path"]),
                context_data={
                    "path": str(item["path"]),
                    "project": item["project"],
                    "account_weight": weight,
                    "sender": item["sender"],
                    "recipients": item["recipients"],
                    "tags": item["tags"],
                    "kind": item["kind"],
                    "content_preview": (item["body"] or "")[:1200].replace("\n", " ").strip(),
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
        "base_score": action.score,
        "deadline_boost": 0.0,
        "context_boost": 0.0,
        "deadline_status": "no_deadline",
        "due_date": action.due_date.isoformat(timespec="seconds") if action.due_date else "",
        "source": action.source,
        "tags": action.tags,
        "context_data": action.context_data,
        "status": action.status,
        "owner": action.assigned_to or "",
        "next_step": "",
        "content": action.context_data.get("content_preview", action.description),
        "editable_context": json.dumps(action.context_data, ensure_ascii=False, indent=2),
        "recommendations": _default_recommendations(
            {
                "priority": action.priority.name,
                "due_date": action.due_date.isoformat(timespec="seconds") if action.due_date else "",
                "context_data": action.context_data,
            }
        ),
        "management_notes": "",
    }


def _metric_value(label: str, value: Any) -> None:
    st.metric(label, value)


def _action_card(action: dict[str, Any], index: int) -> None:
    due = action["due_date"] or "No due date"
    deadline_label = action.get("deadline_status", "no_deadline").replace("_", " ")
    with st.container(border=True):
        c1, c2, c3 = st.columns([4, 1, 1])
        with c1:
            st.markdown(f"**{index}. {escape(action['title'])}**")
            st.write(action["description"])
        with c2:
            st.metric("Score", f"{action['score']:.1f}", delta=f"+{action.get('deadline_boost', 0):.0f} deadline")
        with c3:
            st.write(f"**{action['priority']}**")
            st.caption(f"Due: {due[:10] if due != 'No due date' else due}")
            st.caption(deadline_label)
        st.caption(f"{action['role']} · {action['category']} · {action['source']}")

        with st.expander("Open action workspace", expanded=False):
            _render_action_editor(action)


def _render_action_editor(action: dict[str, Any]) -> None:
    state = load_action_state()
    action_id = action["id"]
    existing = state["actions"].get(action_id, {})
    parsed_due = _parse_action_datetime(action.get("due_date"))
    default_due = parsed_due.date() if parsed_due else None
    priority_names = [priority.name for priority in ActionPriority]
    status_options = ["pending", "in_progress", "waiting", "completed", "closed", "dismissed"]

    with st.form(f"action_editor_{action_id}", border=False):
        title = st.text_input("Action", value=existing.get("title", action["title"]))
        description = st.text_area(
            "Executive summary / description",
            value=existing.get("description", action["description"]),
            height=90,
        )
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            status_value = existing.get("status", action.get("status", "pending"))
            if status_value not in status_options:
                status_value = "pending"
            status = st.selectbox(
                "Status",
                status_options,
                index=status_options.index(status_value),
            )
        with c2:
            priority_value = _priority_from_name(existing.get("priority", ""), action["priority"])
            priority = st.selectbox(
                "Priority",
                priority_names,
                index=priority_names.index(priority_value),
            )
        with c3:
            score = st.number_input(
                "Base score",
                min_value=0.0,
                max_value=100.0,
                value=float(existing.get("score", action.get("base_score", action["score"]))),
                step=1.0,
            )
        with c4:
            due_enabled = st.checkbox("Has deadline", value=default_due is not None)
            due_date = st.date_input(
                "Deadline",
                value=default_due or datetime.now().date(),
                disabled=not due_enabled,
            )

        owner = st.text_input("Owner", value=existing.get("owner", action.get("owner", "")))
        next_step = st.text_input("Next concrete step", value=existing.get("next_step", action.get("next_step", "")))
        content = st.text_area("Content", value=existing.get("content", action.get("content", "")), height=160)
        editable_context = st.text_area(
            "Context",
            value=existing.get("editable_context", action.get("editable_context", "")),
            height=140,
        )
        recommendations = st.text_area(
            "Recommendations",
            value=existing.get("recommendations", action.get("recommendations", "")),
            height=110,
        )
        management_notes = st.text_area(
            "Management notes",
            value=existing.get("management_notes", action.get("management_notes", "")),
            height=90,
        )
        save, close = st.columns(2)
        with save:
            saved = st.form_submit_button("Save action")
        with close:
            closed = st.form_submit_button("Close action")

    if saved or closed:
        selected_due = datetime(due_date.year, due_date.month, due_date.day) if due_enabled else None
        state["actions"][action_id] = {
            "title": title,
            "description": description,
            "status": "closed" if closed else status,
            "priority": priority,
            "score": float(score),
            "due_date": selected_due.isoformat(timespec="seconds") if selected_due else "",
            "owner": owner,
            "next_step": next_step,
            "content": content,
            "editable_context": editable_context,
            "recommendations": recommendations,
            "management_notes": management_notes,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        save_action_state(state)
        st.success("Action saved.")
        st.rerun()


def _note_card(note: dict[str, Any]) -> None:
    with st.container(border=True):
        st.markdown(f"**{escape(note['title'])}**")
        st.caption(f"{note['project']} · {note['date']}")
        st.write(note["snippet"])


def _render_notes_workspace(notes: list[dict[str, Any]], managed_notes: list[dict[str, Any]]) -> None:
    st.subheader("Notes and action candidates")
    st.caption("Create structured notes with enough metadata to convert them into managed actions.")

    state = load_action_state()
    projects = ["General"] + sorted(ACCOUNT_WEIGHTS)
    priority_names = [priority.name for priority in ActionPriority]

    with st.form("managed_note_form"):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            title = st.text_input("Note title")
        with c2:
            project = st.selectbox("Linked account / project", projects)
        with c3:
            priority = st.selectbox("Candidate priority", priority_names, index=2)
        related_person = st.text_input("Related person / company")
        action_candidate = st.text_input("Potential action")
        note_context = st.text_area("Context", height=110)
        recommendation = st.text_area("Recommendation / agent interpretation", height=90)
        c4, c5, c6 = st.columns(3)
        with c4:
            owner = st.text_input("Owner", value="Inaki Senar")
        with c5:
            has_deadline = st.checkbox("Convert with deadline")
        with c6:
            due_date = st.date_input("Deadline", value=datetime.now().date(), disabled=not has_deadline)
        convert_to_action = st.checkbox("Convert this note into an action", value=False)
        submitted = st.form_submit_button("Save note")

    if submitted:
        note_id = f"NOTE_{len(state['notes']) + 1:04d}"
        selected_due = datetime(due_date.year, due_date.month, due_date.day) if has_deadline else None
        note = {
            "id": note_id,
            "title": title or action_candidate or "Operational note",
            "project": project,
            "priority": priority,
            "related_person": related_person,
            "action_candidate": action_candidate,
            "context": note_context,
            "recommendation": recommendation,
            "owner": owner,
            "due_date": selected_due.isoformat(timespec="seconds") if selected_due else "",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "converted_to_action": convert_to_action,
        }
        state["notes"].append(note)
        if convert_to_action:
            manual_id = f"MANUAL_{sha1(note_id.encode('utf-8')).hexdigest()[:12]}"
            state["manual_actions"].append(
                {
                    "id": manual_id,
                    "title": action_candidate or note["title"],
                    "description": note["title"],
                    "priority": priority,
                    "score": 55.0,
                    "due_date": note["due_date"],
                    "source": note_id,
                    "tags": ["manual", project.lower().replace(" ", "_")],
                    "context_data": {
                        "project": project,
                        "related_person": related_person,
                        "note_id": note_id,
                    },
                    "owner": owner,
                    "next_step": action_candidate,
                    "content": note_context,
                    "editable_context": note_context,
                    "recommendations": recommendation,
                    "management_notes": "",
                    "status": "pending",
                }
            )
        save_action_state(state)
        st.success("Note saved.")
        st.rerun()

    if managed_notes:
        st.divider()
        st.markdown("**Managed notes**")
        for note in reversed(managed_notes[-20:]):
            with st.container(border=True):
                st.markdown(f"**{escape(note.get('title', 'Operational note'))}**")
                st.caption(
                    f"{note.get('project', 'General')} · {note.get('priority', '')} · "
                    f"{note.get('related_person', '')} · {note.get('created_at', '')}"
                )
                st.write(note.get("context", ""))
                if note.get("action_candidate"):
                    st.info(f"Action candidate: {note['action_candidate']}")
                if note.get("recommendation"):
                    st.success(note["recommendation"])

    if notes:
        st.divider()
        st.markdown("**Source notes from scanned files**")
        for note in notes[:20]:
            _note_card(note)


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
        "closed_actions": report.get("closed_actions", [])[:25],
        "notes": report["notes"][:25],
        "managed_notes": report.get("managed_notes", [])[:25],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


CHAT_INTENTS = {
    "context": "Aporta contexto o matiza informacion existente.",
    "priority": "Cambia la prioridad de un asunto o cuenta.",
    "note": "Registra una nota vinculada a persona, empresa o proyecto.",
    "close": "Marca un asunto como cerrado para que deje de aparecer.",
    "question": "Pide analisis, redaccion o interpretacion a los agentes.",
}


def load_chat_log() -> list[dict[str, Any]]:
    """Read the persisted agent conversation."""
    try:
        with CHAT_LOG_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data.get("messages", [])
    except (OSError, json.JSONDecodeError):
        return []


def append_chat_message(
    role: str,
    text: str,
    intent: str = "context",
    project: str = "",
) -> dict[str, Any]:
    """Persist one chat turn so agents can read it between sessions."""
    messages = load_chat_log()
    entry = {
        "id": f"MSG_{len(messages) + 1:04d}",
        "role": role,
        "intent": intent,
        "project": project,
        "text": text,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "processed": False,
    }
    messages.append(entry)
    CHAT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "messages": messages,
    }
    with CHAT_LOG_PATH.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    return entry


def _agent_acknowledge(entry: dict[str, Any]) -> str:
    """Produce the in-app agent reply for a captured user turn.

    The reply is deterministic and states exactly what was persisted and what
    the agent will do with it, so the user always knows the input landed.
    """
    project = entry.get("project") or "sin proyecto asignado"
    intent = entry.get("intent", "context")
    base = f"Registrado `{entry['id']}` — intencion **{intent}**, proyecto **{project}**."
    guidance = {
        "context": "Este contexto se incorpora al dossier del proyecto y pesara en los proximos analisis.",
        "priority": "Actualiza el peso en `data/commercial_priorities.json` para que sea permanente.",
        "note": "Nota guardada. Quedara vinculada al proyecto indicado en el proximo refresco.",
        "close": "El asunto se anadira a `closed_topics` y dejara de generar acciones.",
        "question": "Pregunta encolada para los agentes. La respuesta se escribira en este mismo hilo.",
    }
    return f"{base}\n\n{guidance.get(intent, '')}"


def _render_chat_tab(report: dict[str, Any]) -> None:
    st.subheader("Agent chat")
    st.caption(
        "Espacio de interaccion con los agentes que gestionan la herramienta. "
        "Aporta contexto, matiza informacion, cambia prioridades o pide redaccion y analisis. "
        f"Todo se persiste en `{CHAT_LOG_PATH.relative_to(REPO_ROOT).as_posix()}`."
    )

    projects = ["(sin proyecto)"] + sorted(ACCOUNT_WEIGHTS)
    c1, c2 = st.columns([1, 1])
    with c1:
        intent = st.selectbox(
            "Intencion",
            options=list(CHAT_INTENTS),
            format_func=lambda key: f"{key} — {CHAT_INTENTS[key]}",
        )
    with c2:
        project = st.selectbox("Proyecto / cuenta", options=projects)

    history = load_chat_log()
    for message in history[-40:]:
        with st.chat_message("user" if message["role"] == "user" else "assistant"):
            meta = f"`{message['id']}` · {message.get('intent', '')}"
            if message.get("project"):
                meta += f" · {message['project']}"
            st.caption(meta)
            st.markdown(message["text"])

    prompt = st.chat_input("Escribe contexto, una nota, un cambio de prioridad o una peticion...")
    if prompt:
        entry = append_chat_message(
            role="user",
            text=prompt,
            intent=intent,
            project="" if project == "(sin proyecto)" else project,
        )
        append_chat_message(
            role="agent",
            text=_agent_acknowledge(entry),
            intent=intent,
            project=entry["project"],
        )
        st.rerun()

    st.divider()
    st.markdown("**Prioridades activas**")
    for account in sorted(
        PRIORITIES.get("accounts", []),
        key=lambda a: a.get("weight", 0),
        reverse=True,
    ):
        flag = " (baja prioridad comercial)" if account.get("demote") else ""
        st.write(f"- **{account['name']}** · {account.get('weight', 0)} — {account.get('focus', '')}{flag}")


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
        refresh = st.button("Refresh analysis", width="stretch")
        st.caption("This panel analyzes .eml, .txt and .md files from the selected root.")
        st.divider()
        st.markdown("**Local focus**")
        st.write("- Outlook mail context")
        st.write("- Ingecart project documents")
        st.write("- Follow-up and action detection")

    report = apply_action_state(build_report(root_input, 1 if refresh else 0))

    if report["errors"]:
        with st.expander("Parsing warnings", expanded=False):
            for error in report["errors"][:20]:
                st.write(f"- {error}")

    stats = report["statistics"]
    metrics = st.columns(7)
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
        _metric_value("⏱️ Deadline risk", stats.get("deadline_risk", 0))
    with metrics[6]:
        _metric_value("🤖 Recomendaciones IA", stats.get("recommendations", 0))

    briefing = _build_briefing(report["actions"])
    left, right = st.columns([1.3, 1])
    with left:
        st.subheader("AI briefing")
        st.markdown("**Chat | Today | Priority | Waiting | Follow-up | Tasks | Notes | Intelligence**")
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
            width="stretch",
        )
        st.caption(f"Generated at {report['generated_at']}")

    tabs = st.tabs(
        ["Chat", "Today", "Priority", "Waiting", "Follow-up", "Tasks", "Notes", "Intelligence"]
    )
    actions = report["actions"]
    notes = report["notes"]
    managed_notes = report.get("managed_notes", [])

    with tabs[0]:
        _render_chat_tab(report)

    with tabs[1]:
        todays = [
            action
            for action in actions
            if action["priority"] in {"CRITICAL", "HIGH"}
            or (action["due_date"] and action["due_date"][:10] == datetime.now().strftime("%Y-%m-%d"))
        ]
        for idx, action in enumerate(todays[:8], start=1):
            _action_card(action, idx)

    with tabs[2]:
        for idx, action in enumerate(actions[:12], start=1):
            _action_card(action, idx)

    with tabs[3]:
        waiting = [action for action in actions if "waiting_follow_up" in action["tags"]]
        for idx, action in enumerate(waiting[:12], start=1):
            _action_card(action, idx)

    with tabs[4]:
        follow_up = [action for action in actions if action["priority"] in {"CRITICAL", "HIGH"}]
        for idx, action in enumerate(follow_up[:12], start=1):
            _action_card(action, idx)

    with tabs[5]:
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

    with tabs[6]:
        _render_notes_workspace(notes, managed_notes)

    with tabs[7]:
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
            st.write(f"- editable open actions: {len(actions)}")
            st.write(f"- closed / completed actions: {len(report.get('closed_actions', []))}")
            st.write(f"- deadline risk actions: {stats.get('deadline_risk', 0)}")

        st.divider()
        st.subheader("Selected action evidence")
        for action in actions[:5]:
            with st.expander(action["title"], expanded=False):
                st.write(action["description"])
                st.write(f"Source: {action['source']}")
                st.write(f"Tags: {', '.join(action['tags'])}")
                st.write(f"Context: {json.dumps(action['context_data'], ensure_ascii=False, indent=2)}")

        closed_actions = report.get("closed_actions", [])
        if closed_actions:
            st.divider()
            st.subheader("Recently closed actions")
            for action in closed_actions[-10:]:
                st.write(f"- {action['title']} · {action.get('status', 'closed')} · score {action['score']:.1f}")


if __name__ == "__main__":
    main()
