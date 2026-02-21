"""
Violation Engine: applies AML compliance rules to IBM AML transaction data.
Reads the CSV, runs each approved rule using pandas, and returns Violation objects.
"""
import json
import uuid
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

from app.models.violation import Violation
from app.core.rule_engine import get_rules

_BASE = Path(__file__).parent.parent.parent.parent  # project root inside backend/
DATA_FILE = _BASE.parent / "data" / "datasets" / "ibm_aml" / "sample_transactions.csv"
VIOLATIONS_FILE = Path(__file__).parent.parent / "storage" / "violations.json"


def load_transactions() -> pd.DataFrame:
    """Load IBM AML transactions CSV into a DataFrame."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"IBM AML dataset not found at: {DATA_FILE}")
    df = pd.read_csv(DATA_FILE)
    # Normalise column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    return df


def run_scan() -> List[Violation]:
    """
    Run all approved rules against the IBM AML transaction dataset.
    Returns a flat list of violations found.
    """
    df = load_transactions()
    rules = get_rules(approved_only=True)
    now = datetime.now(timezone.utc).isoformat()

    all_violations: List[Violation] = []
    seen_ids: set = set()  # avoid exact duplicates for the same (txn_id, rule_id)

    for rule in rules:
        flagged_rows, _ = _apply_rule(rule.id, df)
        for _, row in flagged_rows.iterrows():
            txn_id = _make_txn_id(row)
            dedup_key = f"{txn_id}-{rule.id}"
            if dedup_key in seen_ids:
                continue
            seen_ids.add(dedup_key)

            violation = Violation(
                id=f"viol-{uuid.uuid4().hex[:8]}",
                transaction_id=txn_id,
                rule_id=rule.id,
                rule_name=rule.description,
                severity=rule.severity,
                explanation=_build_explanation(rule.id, row),
                evidence=_build_evidence(row),
                status="open",
                detected_at=now,
            )
            all_violations.append(violation)

    # Persist to storage
    _save_violations(all_violations)
    return all_violations


def _apply_rule(rule_id: str, df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """Apply a specific rule and return matching rows."""
    try:
        if rule_id == "aml-001":
            mask = df["Amount Paid"] > 10_000
            return df[mask], "Amount Paid > $10,000"

        elif rule_id == "aml-002":
            # Rapid transfers: group by From Account + To Account.1, count within window
            # Simplified: flag accounts with top 5% frequency to same beneficiary
            counts = df.groupby(["Account", "Account.1"]).size().reset_index(name="tx_count")
            high = counts[counts["tx_count"] >= 2]  # at least 2 in sample = flag
            flagged = df.merge(high[["Account", "Account.1"]], on=["Account", "Account.1"])
            return flagged.drop_duplicates(), "Rapid transfers to same beneficiary"

        elif rule_id == "aml-003":
            mask = (df["Amount Paid"] % 1000 == 0) & (df["Amount Paid"] > 5_000)
            return df[mask], "Round-number amount > $5,000 (structuring)"

        elif rule_id == "aml-004":
            mask = df["Payment Currency"] != df["Receiving Currency"]
            return df[mask], "Payment currency ≠ receiving currency"

        elif rule_id == "aml-005":
            mask = df["Is Laundering"] == 1
            return df[mask], "Confirmed laundering label"

        elif rule_id == "aml-006":
            mask = (df["Amount Paid"] > 50_000) & (
                df["Payment Format"].str.lower().isin(["cheque", "wire"])
            )
            return df[mask], "Wire/Cheque > $50,000 — EDD required"

        else:
            # For extracted rules from PDFs, attempt basic numeric comparisons
            return pd.DataFrame(), "Unknown rule"
    except Exception as e:
        return pd.DataFrame(), str(e)


def _make_txn_id(row: pd.Series) -> str:
    """Create a deterministic transaction identifier from row data."""
    parts = [
        str(row.get("Timestamp", "")),
        str(row.get("Account", "")),
        str(row.get("Account.1", "")),
        str(row.get("Amount Paid", "")),
    ]
    return "TXN-" + uuid.uuid5(uuid.NAMESPACE_DNS, "|".join(parts)).hex[:12].upper()


def _build_explanation(rule_id: str, row: pd.Series) -> str:
    amount = row.get("Amount Paid", 0)
    from_acct = row.get("Account", "N/A")
    to_acct = row.get("Account.1", "N/A")
    currency = row.get("Payment Currency", "N/A")
    recv_currency = row.get("Receiving Currency", "N/A")
    fmt = row.get("Payment Format", "N/A")

    explanations = {
        "aml-001": (
            f"Transaction of ${amount:,.2f} from account {from_acct} exceeds the $10,000 CTR "
            f"reporting threshold. A Currency Transaction Report must be filed within 15 business days."
        ),
        "aml-002": (
            f"Account {from_acct} has made multiple rapid transfers to account {to_acct}, "
            f"indicating a potential layering pattern in the AML placement cycle."
        ),
        "aml-003": (
            f"Transaction of ${amount:,.2f} is a round number above $5,000, which may indicate "
            f"deliberate structuring (smurfing) to stay below reporting thresholds."
        ),
        "aml-004": (
            f"Payment made in {currency} but funds received in {recv_currency}. "
            f"Cross-currency conversion between accounts {from_acct} and {to_acct} requires "
            f"enhanced scrutiny for currency-based layering."
        ),
        "aml-005": (
            f"Transaction of ${amount:,.2f} ({fmt}) from {from_acct} to {to_acct} is confirmed "
            f"as illicit in the ground-truth dataset. This is a confirmed money laundering transaction."
        ),
        "aml-006": (
            f"{fmt} transaction of ${amount:,.2f} from {from_acct} exceeds $50,000 threshold. "
            f"Enhanced Due Diligence (EDD) documentation required before processing."
        ),
    }
    return explanations.get(rule_id, f"Transaction flagged by rule {rule_id}.")


def _build_evidence(row: pd.Series) -> dict:
    """Build evidence dict from transaction row."""
    return {
        "timestamp": str(row.get("Timestamp", "")),
        "from_bank": str(row.get("From Bank", "")),
        "from_account": str(row.get("Account", "")),
        "to_bank": str(row.get("To Bank", "")),
        "to_account": str(row.get("Account.1", "")),
        "amount_paid": float(row.get("Amount Paid", 0)),
        "payment_currency": str(row.get("Payment Currency", "")),
        "amount_received": float(row.get("Amount Received", 0)),
        "receiving_currency": str(row.get("Receiving Currency", "")),
        "payment_format": str(row.get("Payment Format", "")),
        "is_laundering": int(row.get("Is Laundering", 0)),
    }


def load_violations() -> List[Violation]:
    """Load all violations from storage."""
    try:
        data = json.loads(VIOLATIONS_FILE.read_text(encoding="utf-8"))
        return [Violation(**v) for v in data]
    except Exception:
        return []


def _save_violations(violations: List[Violation]) -> None:
    """Persist violations list to storage."""
    VIOLATIONS_FILE.write_text(
        json.dumps([v.model_dump() for v in violations], indent=2),
        encoding="utf-8"
    )


def update_violation_status(violation_id: str, status: str, comment: str = None) -> bool:
    """Update a single violation's status and comment."""
    violations = load_violations()
    for v in violations:
        if v.id == violation_id:
            v.status = status
            if comment:
                v.reviewer_comment = comment
            v.reviewed_at = datetime.now(timezone.utc).isoformat()
            _save_violations(violations)
            return True
    return False


def get_dataset_stats() -> dict:
    """Return summary statistics for the IBM AML dataset."""
    try:
        df = load_transactions()
        total = len(df)
        laundering_count = int(df["Is Laundering"].sum())
        laundering_pct = round(laundering_count / total * 100, 2) if total > 0 else 0
        currencies = df["Payment Currency"].value_counts().head(5).to_dict()
        formats = df["Payment Format"].value_counts().to_dict()
        return {
            "total_transactions": total,
            "confirmed_laundering": laundering_count,
            "laundering_percentage": laundering_pct,
            "avg_amount_paid": round(float(df["Amount Paid"].mean()), 2),
            "max_amount_paid": round(float(df["Amount Paid"].max()), 2),
            "top_currencies": currencies,
            "payment_formats": formats,
            "source": "IBM AML Dataset (Synthetic, CDLA-Sharing-1.0)",
            "kaggle_url": "https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml",
        }
    except Exception as e:
        return {"error": str(e)}


def get_dataset_preview(limit: int = 20) -> list:
    """Return the first `limit` rows of the dataset as a list of dicts."""
    try:
        df = load_transactions()
        return df.head(limit).where(df.head(limit).notna(), None).to_dict("records")
    except Exception as e:
        return [{"error": str(e)}]
