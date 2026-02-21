"""
API routes for IBM AML dataset operations.
"""
from fastapi import APIRouter, HTTPException, Query
from app.core.violation_engine import get_dataset_preview, get_dataset_stats, load_transactions

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])


@router.get("", summary="List available datasets")
def list_datasets():
    return [
        {
            "id": "ibm-aml",
            "name": "IBM AML Transactions",
            "description": "Synthetic financial transaction dataset with laundering labels (IBM Research)",
            "license": "CDLA-Sharing-1.0",
            "source": "https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml",
            "columns": [
                "Timestamp", "From Bank", "Account", "To Bank", "Account.1",
                "Amount Received", "Receiving Currency", "Amount Paid",
                "Payment Currency", "Payment Format", "Is Laundering"
            ],
            "connected": True,
        },
        {
            "id": "paysim",
            "name": "PaySim Mobile Money",
            "description": "6.3M synthetic mobile transactions with fraud labels (CC BY-SA 4.0)",
            "license": "CC BY-SA 4.0",
            "source": "https://www.kaggle.com/datasets/ealaxi/paysim1",
            "columns": [
                "step", "type", "amount", "nameOrig", "oldbalanceOrg", "newbalanceOrig",
                "nameDest", "oldbalanceDest", "newbalanceDest", "isFraud", "isFlaggedFraud"
            ],
            "connected": False,
        },
    ]


@router.get("/aml/stats", summary="Statistics for the IBM AML dataset")
def aml_stats():
    stats = get_dataset_stats()
    if "error" in stats:
        raise HTTPException(status_code=500, detail=stats["error"])
    return stats


@router.get("/aml/preview", summary="Preview first N rows of IBM AML dataset")
def aml_preview(limit: int = Query(default=20, ge=1, le=200)):
    rows = get_dataset_preview(limit)
    if rows and "error" in rows[0]:
        raise HTTPException(status_code=500, detail=rows[0]["error"])
    return {"rows": rows, "count": len(rows)}


@router.get("/aml/schema", summary="Column schema for IBM AML dataset")
def aml_schema():
    return {
        "columns": [
            {"name": "Timestamp", "type": "datetime", "description": "Transaction timestamp"},
            {"name": "From Bank", "type": "integer", "description": "Originating bank ID"},
            {"name": "Account", "type": "string", "description": "Originating account number"},
            {"name": "To Bank", "type": "integer", "description": "Receiving bank ID"},
            {"name": "Account.1", "type": "string", "description": "Receiving account number"},
            {"name": "Amount Received", "type": "float", "description": "Amount received (in receiving currency)"},
            {"name": "Receiving Currency", "type": "string", "description": "Currency received (e.g. USD, EUR)"},
            {"name": "Amount Paid", "type": "float", "description": "Amount paid (in payment currency)"},
            {"name": "Payment Currency", "type": "string", "description": "Currency paid (e.g. USD, Bitcoin)"},
            {"name": "Payment Format", "type": "string", "description": "Method: Reinvestment, Cheque, ACH, Wire, Credit Cards, Cash"},
            {"name": "Is Laundering", "type": "integer", "description": "Ground truth label: 1 = laundering, 0 = legitimate"},
        ]
    }
