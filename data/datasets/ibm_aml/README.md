# IBM AML Transactions Dataset

## Overview
This directory contains the IBM Transactions for Anti-Money Laundering (AML) dataset,
used as the primary compliance scanning target for NitiLens.

## Schema (11 Columns)

| Column | Type | Description |
|---|---|---|
| `Timestamp` | datetime | Transaction date and time |
| `From Bank` | integer | Originating bank ID |
| `Account` | string | Originating account number |
| `To Bank` | integer | Receiving bank ID |
| `Account.1` | string | Receiving account number |
| `Amount Received` | float | Amount received (in receiving currency) |
| `Receiving Currency` | string | Currency of received funds |
| `Amount Paid` | float | Amount paid (in payment currency) |
| `Payment Currency` | string | Currency of payment |
| `Payment Format` | string | `Reinvestment`, `Cheque`, `ACH`, `Wire`, `Credit Cards`, `Cash` |
| `Is Laundering` | integer | **Ground truth**: `1` = laundering, `0` = legitimate |

## Current File
`sample_transactions.csv` — 50 synthetic rows demonstrating all AML violation patterns:
- Large transactions (>$10,000 CTR threshold)
- Wire transfer layering chains
- Cross-currency conversion (USD → Bitcoin, USD → EUR)
- Round-number structuring
- Confirmed laundering labels (Is Laundering = 1)

## Full Dataset
The full IBM AML dataset contains **over 5 million transactions** across multiple size tiers.

🔗 **Download**: https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml

📜 **License**: CDLA-Sharing-1.0 (Community Data License Agreement — permissive for sharing and use)

### To use the full dataset:
1. Download `HI-Small_Trans.csv` or `HI-Large_Trans.csv` from Kaggle
2. Replace `sample_transactions.csv` with your downloaded file
3. Rename the file to `sample_transactions.csv` OR update `DATA_FILE` path in `violation_engine.py`

## Citation
> Altman, E. (2019). IBM Transactions for Anti-Money Laundering (AML). Kaggle.
> Based on: E. Altman, M. Blanco, et al. "Realistic Synthetic Financial Transactions for Anti-Money Laundering Models." NeurIPS 2023.
