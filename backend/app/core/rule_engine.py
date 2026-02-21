"""
Rule engine: loads, stores, and manages compliance rules from storage.
"""
import json
from pathlib import Path
from typing import List, Optional
from app.models.rule import PolicyRule

RULES_FILE = Path(__file__).parent.parent / "storage" / "rules.json"


def get_rules(approved_only: bool = False) -> List[PolicyRule]:
    """Load all rules from storage."""
    try:
        data = json.loads(RULES_FILE.read_text(encoding="utf-8"))
        rules = [PolicyRule(**r) for r in data]
        if approved_only:
            rules = [r for r in rules if r.approved]
        return rules
    except Exception:
        return []


def get_rule_by_id(rule_id: str) -> Optional[PolicyRule]:
    """Get a single rule by ID."""
    return next((r for r in get_rules() if r.id == rule_id), None)


def save_rules(rules: List[PolicyRule]) -> None:
    """Persist rules to storage."""
    RULES_FILE.write_text(
        json.dumps([r.model_dump() for r in rules], indent=2),
        encoding="utf-8"
    )


def add_rules(new_rules: List[PolicyRule]) -> List[PolicyRule]:
    """Add new rules (from extraction), avoiding duplicates by id."""
    existing = get_rules()
    existing_ids = {r.id for r in existing}
    to_add = [r for r in new_rules if r.id not in existing_ids]
    all_rules = existing + to_add
    save_rules(all_rules)
    return to_add


def approve_rule(rule_id: str, approved: bool = True) -> Optional[PolicyRule]:
    """Approve or unapprove a rule."""
    rules = get_rules()
    for rule in rules:
        if rule.id == rule_id:
            rule.approved = approved
            save_rules(rules)
            return rule
    return None


def update_rule(rule_id: str, updates: dict) -> Optional[PolicyRule]:
    """Update fields on a rule."""
    rules = get_rules()
    for rule in rules:
        if rule.id == rule_id:
            for k, v in updates.items():
                if hasattr(rule, k):
                    setattr(rule, k, v)
            save_rules(rules)
            return rule
    return None


def delete_rule(rule_id: str) -> bool:
    """Delete a rule by ID."""
    rules = get_rules()
    original_len = len(rules)
    rules = [r for r in rules if r.id != rule_id]
    if len(rules) < original_len:
        save_rules(rules)
        return True
    return False
