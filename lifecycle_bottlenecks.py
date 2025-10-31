# lifecycle_bottlenecks.py
from __future__ import annotations

from collections import defaultdict
from statistics import mean, median
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import json

try:
    import model  # optional
except Exception:
    model = None


# ---------- Helper functions ----------
def _parse_iso(ts: str | None) -> datetime | None:
    """Parses ISO timestamps like '2024-01-01T12:34:56Z'."""
    if not ts:
        return None
    ts = ts.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _days_between(start: datetime | None, end: datetime | None) -> float | None:
    if not start or not end:
        return None
    delta = end - start
    return delta.days + delta.seconds / 86400.0


def _load_config_path(config_fname: str = "config.json") -> Path:
    """Returns the path to the issues JSON based on config.json keys."""
    cfg_path = Path(config_fname)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Cannot find {config_fname} in repo root.")
    data = json.loads(cfg_path.read_text(encoding="utf-8"))

    for key in ("issues_file", "issues_path", "data_file", "data_path"):
        if key in data and data[key]:
            return Path(data[key])

    for guess in ("issues.json", "data/issues.json", "data/poetry_issues.json"):
        if Path(guess).exists():
            return Path(guess)

    raise KeyError(
        "Could not determine issues JSON path from config.json. "
        "Add a key like 'issues_file': 'path/to/issues.json'."
    )


def _derive_closed_date_from_events(events: list[dict] | None) -> datetime | None:
    """Finds the last 'closed' event not followed by a later 'reopened'."""
    if not events:
        return None
    evs = []
    for e in events:
        et = (e.get("event_type") if isinstance(e, dict) else getattr(e, "event_type", None))
        dt = (e.get("event_date") if isinstance(e, dict) else getattr(e, "event_date", None))
        dt = _parse_iso(dt) if isinstance(dt, str) else dt
        if et and isinstance(dt, datetime):
            evs.append((dt, et.lower()))
    if not evs:
        return None
    evs.sort(key=lambda x: x[0])
    last_closed = max((dt for dt, et in evs if et == "closed"), default=None)
    last_reopen = max((dt for dt, et in evs if et in ("reopened", "reopen")), default=None)
    if not last_closed:
        return None
    if last_reopen and last_reopen > last_closed:
        return None
    return last_closed


def _extract_labels_any(iss) -> list[str]:
    labs = getattr(iss, "labels", None) or []
    out = []
    for l in labs:
        if isinstance(l, str):
            out.append(l)
        elif isinstance(l, dict):
            n = l.get("name")
            if n:
                out.append(n)
        else:
            n = getattr(l, "name", None)
            if n:
                out.append(n)
    return out


def _wrap_min_issue(j: dict) -> SimpleNamespace:
    """Builds a lightweight Issue-like object from a JSON dict."""
    created = j.get("created_date") or j.get("created_at")
    closed = j.get("closed_date") or j.get("closed_at")

    created_dt = _parse_iso(created) if isinstance(created, str) else None
    closed_dt = _parse_iso(closed) if isinstance(closed, str) else None

    labels = []
    for lbl in j.get("labels", []):
        if isinstance(lbl, str):
            labels.append(lbl)
        elif isinstance(lbl, dict):
            n = lbl.get("name")
            if n:
                labels.append(n)

    events = j.get("events") or j.get("event_list") or []

    return SimpleNamespace(created_date=created_dt, closed_date=closed_dt, labels=labels, events=events)


def _load_issues_generic(issues_json_path: Path):
    """Loads the issues file into Issue-like objects."""
    raw = json.loads(issues_json_path.read_text(encoding="utf-8"))
    if model and hasattr(model, "Issue") and hasattr(model.Issue, "from_json"):
        issues = []
        for jobj in raw:
            try:
                issues.append(model.Issue.from_json(jobj))
            except Exception:
                issues.append(_wrap_min_issue(jobj))
        return issues
    return [_wrap_min_issue(j) for j in raw]


# ---------- Main analysis ----------
def run():
    import matplotlib.pyplot as plt

    issues_path = _load_config_path("config.json")
    issues = _load_issues_generic(issues_path)

    durations = []                 # closed issues
    per_label = defaultdict(list)
    open_ages = []                 # open issues
    open_per_label = defaultdict(list)

    now = datetime.now().astimezone()

    for iss in issues:
        created = getattr(iss, "created_date", None)
        if isinstance(created, str):
            created = _parse_iso(created)

        closed = getattr(iss, "closed_date", None)
        if isinstance(closed, str):
            closed = _parse_iso(closed)

        if closed is None:
            events = getattr(iss, "events", None)
            closed = _derive_closed_date_from_events(events)

        labels = _extract_labels_any(iss)

        if created and closed:
            dur = _days_between(created, closed)
            if dur is not None:
                durations.append(dur)
                for name in labels:
                    per_label[name].append(dur)
        elif created:
            age = _days_between(created, now)
            if age is not None:
                open_ages.append(age)
                for name in labels:
                    open_per_label[name].append(age)

    # ---------- Closed issues ----------
    if durations:
        print(f"[Lifecycle] Closed issues: {len(durations)}")
        print(f"[Lifecycle] Mean days-to-close:   {mean(durations):.2f}")
        print(f"[Lifecycle] Median days-to-close: {median(durations):.2f}")

        agg = []
        for name, vals in per_label.items():
            if vals:
                agg.append((name, mean(vals), median(vals), len(vals)))
        agg.sort(key=lambda x: x[1], reverse=True)

        print("\n[Lifecycle] Slowest labels by avg days-to-close (top 10):")
        for name, avgd, med, n in agg[:10]:
            print(f"  • {name:25s}  avg={avgd:6.2f}  med={med:6.2f}  n={n}")

        plt.figure()
        plt.hist(durations, bins=30)
        plt.title("Issue Resolution Time Distribution (days)")
        plt.xlabel("Days to close")
        plt.ylabel("Number of issues")

        if agg:
            top = agg[:15]
            labels = [t[0] for t in top]
            avgs = [t[1] for t in top]
            plt.figure()
            plt.barh(labels, avgs)
            plt.gca().invert_yaxis()
            plt.title("Slowest Labels by Avg Days-to-Close")
            plt.xlabel("Average days")
            plt.ylabel("Label")
    else:
        print("[Lifecycle] No closed issues detected (maybe only open ones).")

    # ---------- Open issues ----------
    if open_ages:
        print(f"\n[Lifecycle/Open] Open issues: {len(open_ages)}")
        print(f"[Lifecycle/Open] Mean age (days):   {mean(open_ages):.2f}")
        print(f"[Lifecycle/Open] Median age (days): {median(open_ages):.2f}")

        open_agg = []
        for name, vals in open_per_label.items():
            if vals:
                open_agg.append((name, mean(vals), median(vals), len(vals)))
        open_agg.sort(key=lambda x: x[1], reverse=True)

        print("\n[Lifecycle/Open] Stalest labels by avg age (top 10):")
        for name, avgd, med, n in open_agg[:10]:
            print(f"  • {name:25s}  avg={avgd:6.2f}  med={med:6.2f}  n={n}")

        plt.figure()
        plt.hist(open_ages, bins=30)
        plt.title("Open Issues Age Distribution (days)")
        plt.xlabel("Days since created")
        plt.ylabel("Number of issues")

        if open_agg:
            top = open_agg[:15]
            labels = [t[0] for t in top]
            avgs = [t[1] for t in top]
            plt.figure()
            plt.barh(labels, avgs)
            plt.gca().invert_yaxis()
            plt.title("Stalest Open Labels by Avg Age")
            plt.xlabel("Average days open")
            plt.ylabel("Label")

    plt.show()
