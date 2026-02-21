// IBM AML Transaction Data for NitiLens Compliance Platform
// Based on IBM Transactions for Anti-Money Laundering dataset schema
// Source: https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml
// License: CDLA-Sharing-1.0

export interface AMLTransaction {
  id: string;
  timestamp: string;
  fromBank: number;
  fromAccount: string;
  toBank: number;
  toAccount: string;
  amountReceived: number;
  receivingCurrency: string;
  amountPaid: number;
  paymentCurrency: string;
  paymentFormat: 'Reinvestment' | 'Cheque' | 'ACH' | 'Wire' | 'Credit Cards' | 'Cash';
  isLaundering: 0 | 1;
}

export interface PolicyRule {
  id: string;
  description: string;
  condition: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  sourceReference: string;
  category: string;
  approved: boolean;
}

export interface Violation {
  id: string;
  transactionId: string;
  ruleId: string;
  ruleName: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  explanation: string;
  evidence: Record<string, any>;
  status: 'open' | 'reviewed' | 'resolved' | 'false_positive';
  reviewerComment?: string;
  detectedAt: string;
  reviewedAt?: string;
}

// ── Policies ──────────────────────────────────────────────────────────────────
export const samplePolicies = [
  {
    id: 'pol-aml-001',
    name: 'AML Compliance Policy v2.1',
    uploadedAt: '2026-02-15T10:30:00Z',
    pages: 18,
    fileSize: '1.4 MB',
    type: 'Anti-Money Laundering'
  },
  {
    id: 'pol-gdpr-001',
    name: 'GDPR Data Protection Policy v1.4',
    uploadedAt: '2026-01-20T14:15:00Z',
    pages: 24,
    fileSize: '2.1 MB',
    type: 'Data Privacy'
  }
];

// ── AML Compliance Rules ───────────────────────────────────────────────────────
export const extractedRules: PolicyRule[] = [
  {
    id: 'aml-001',
    description: 'Single transaction exceeding $10,000 must be reported (CTR requirement)',
    condition: 'Amount Paid > 10000',
    severity: 'critical',
    sourceReference: 'AML Policy v2.1, Section 3.1 — Currency Transaction Report (CTR)',
    category: 'Large Transaction Reporting',
    approved: true
  },
  {
    id: 'aml-002',
    description: 'More than 5 transfers to the same beneficiary account within 24 hours',
    condition: 'count(To Account, 24h) > 5',
    severity: 'high',
    sourceReference: 'AML Policy v2.1, Section 4.2 — Layering Detection',
    category: 'Suspicious Activity',
    approved: true
  },
  {
    id: 'aml-003',
    description: 'Structuring: round-number transactions above $5,000 (potential smurfing)',
    condition: 'Amount Paid % 1000 == 0 AND Amount Paid > 5000',
    severity: 'medium',
    sourceReference: 'AML Policy v2.1, Section 4.3 — Structuring & Smurfing',
    category: 'Structuring',
    approved: true
  },
  {
    id: 'aml-004',
    description: 'Cross-currency transaction: Payment Currency differs from Receiving Currency',
    condition: 'Payment Currency != Receiving Currency',
    severity: 'medium',
    sourceReference: 'AML Policy v2.1, Section 5.1 — Currency Conversion Controls',
    category: 'Currency Risk',
    approved: true
  },
  {
    id: 'aml-005',
    description: 'Transaction confirmed as laundering in ground-truth dataset',
    condition: 'Is Laundering == 1',
    severity: 'critical',
    sourceReference: 'AML Policy v2.1, Section 2.1 — Confirmed Illicit Activity',
    category: 'Confirmed Laundering',
    approved: true
  },
  {
    id: 'aml-006',
    description: 'Wire or cheque transfer exceeding $50,000 requires Enhanced Due Diligence',
    condition: 'Amount Paid > 50000 AND Payment Format IN [Cheque, Wire]',
    severity: 'high',
    sourceReference: 'AML Policy v2.1, Section 3.4 — Enhanced Due Diligence (EDD)',
    category: 'Enhanced Due Diligence',
    approved: true
  }
];

// ── Sample IBM AML Transactions (subset matching real schema) ─────────────────
export const amlTransactions: AMLTransaction[] = [
  { id: 'TXN-001', timestamp: '2023-01-02 02:05:00', fromBank: 1, fromAccount: 'FA12390BC', toBank: 3, toAccount: '55BC90E4D', amountReceived: 15000, receivingCurrency: 'US Dollar', amountPaid: 15000, paymentCurrency: 'US Dollar', paymentFormat: 'Wire', isLaundering: 1 },
  { id: 'TXN-002', timestamp: '2023-01-02 02:30:00', fromBank: 3, fromAccount: '55BC90E4D', toBank: 7, toAccount: '1A2B3C4D5', amountReceived: 15000, receivingCurrency: 'US Dollar', amountPaid: 15000, paymentCurrency: 'US Dollar', paymentFormat: 'Wire', isLaundering: 1 },
  { id: 'TXN-003', timestamp: '2023-01-02 03:00:00', fromBank: 7, fromAccount: '1A2B3C4D5', toBank: 2, toAccount: '8000ECA98', amountReceived: 14800, receivingCurrency: 'US Dollar', amountPaid: 14800, paymentCurrency: 'US Dollar', paymentFormat: 'Reinvestment', isLaundering: 1 },
  { id: 'TXN-004', timestamp: '2023-01-02 04:15:00', fromBank: 9, fromAccount: 'B3C4D5E6F', toBank: 4, toAccount: '2D3E4F5A6', amountReceived: 9500, receivingCurrency: 'US Dollar', amountPaid: 9500, paymentCurrency: 'US Dollar', paymentFormat: 'ACH', isLaundering: 0 },
  { id: 'TXN-005', timestamp: '2023-01-02 05:00:00', fromBank: 6, fromAccount: 'C7D8E9F01', toBank: 10, toAccount: 'G7H8I9J01', amountReceived: 5000, receivingCurrency: 'US Dollar', amountPaid: 5000, paymentCurrency: 'US Dollar', paymentFormat: 'Cheque', isLaundering: 0 },
  { id: 'TXN-006', timestamp: '2023-01-02 08:15:00', fromBank: 4, fromAccount: '2D3E4F5A6', toBank: 6, toAccount: 'C7D8E9F01', amountReceived: 75000, receivingCurrency: 'US Dollar', amountPaid: 75000, paymentCurrency: 'US Dollar', paymentFormat: 'Wire', isLaundering: 1 },
  { id: 'TXN-007', timestamp: '2023-01-02 09:00:00', fromBank: 11, fromAccount: '0F2F8911F', toBank: 5, toAccount: '3A7B1D22C', amountReceived: 60000, receivingCurrency: 'Euro', amountPaid: 64500, paymentCurrency: 'US Dollar', paymentFormat: 'Wire', isLaundering: 1 },
  { id: 'TXN-008', timestamp: '2023-01-02 09:30:00', fromBank: 5, fromAccount: '3A7B1D22C', toBank: 1, toAccount: 'FA12390BC', amountReceived: 3000, receivingCurrency: 'Bitcoin', amountPaid: 82500, paymentCurrency: 'US Dollar', paymentFormat: 'Reinvestment', isLaundering: 1 },
  { id: 'TXN-009', timestamp: '2023-01-02 10:00:00', fromBank: 8, fromAccount: '9C4E7F61A', toBank: 3, toAccount: '55BC90E4D', amountReceived: 450.50, receivingCurrency: 'US Dollar', amountPaid: 450.50, paymentCurrency: 'US Dollar', paymentFormat: 'ACH', isLaundering: 0 },
  { id: 'TXN-010', timestamp: '2023-01-02 11:00:00', fromBank: 14, fromAccount: 'U9V0W1X2Y', toBank: 15, toAccount: 'Z3A4B5C6D', amountReceived: 100000, receivingCurrency: 'US Dollar', amountPaid: 100000, paymentCurrency: 'US Dollar', paymentFormat: 'Wire', isLaundering: 1 },
  { id: 'TXN-011', timestamp: '2023-01-02 11:30:00', fromBank: 15, fromAccount: 'Z3A4B5C6D', toBank: 16, toAccount: 'E7F8G9H0I', amountReceived: 100000, receivingCurrency: 'US Dollar', amountPaid: 100000, paymentCurrency: 'US Dollar', paymentFormat: 'Wire', isLaundering: 1 },
  { id: 'TXN-012', timestamp: '2023-01-02 12:00:00', fromBank: 16, fromAccount: 'E7F8G9H0I', toBank: 17, toAccount: 'J1K2L3M4N', amountReceived: 99500, receivingCurrency: 'US Dollar', amountPaid: 99500, paymentCurrency: 'US Dollar', paymentFormat: 'Wire', isLaundering: 1 },
  { id: 'TXN-013', timestamp: '2023-01-02 13:00:00', fromBank: 7, fromAccount: '1A2B3C4D5', toBank: 9, toAccount: 'B3C4D5E6F', amountReceived: 2300, receivingCurrency: 'Pound', amountPaid: 2875, paymentCurrency: 'US Dollar', paymentFormat: 'Reinvestment', isLaundering: 0 },
  { id: 'TXN-014', timestamp: '2023-01-02 15:15:00', fromBank: 20, fromAccount: 'Y3Z4A5B6C', toBank: 18, toAccount: 'O5P6Q7R8S', amountReceived: 55000, receivingCurrency: 'Euro', amountPaid: 59400, paymentCurrency: 'US Dollar', paymentFormat: 'Wire', isLaundering: 1 },
  { id: 'TXN-015', timestamp: '2023-01-02 17:30:00', fromBank: 17, fromAccount: 'J1K2L3M4N', toBank: 2, toAccount: '8000ECA98', amountReceived: 49800, receivingCurrency: 'Bitcoin', amountPaid: 1350000, paymentCurrency: 'US Dollar', paymentFormat: 'Reinvestment', isLaundering: 1 },
];

// ── AML Violations ─────────────────────────────────────────────────────────────
export const sampleViolations: Violation[] = [
  {
    id: 'viol-001',
    transactionId: 'TXN-010',
    ruleId: 'aml-001',
    ruleName: 'Single transaction exceeding $10,000 (CTR requirement)',
    severity: 'critical',
    explanation: 'Wire transfer of $100,000 from account U9V0W1X2Y (Bank 14) to Z3A4B5C6D (Bank 15) exceeds the $10,000 CTR reporting threshold. A Currency Transaction Report must be filed within 15 business days.',
    evidence: {
      timestamp: '2023-01-02 11:00:00',
      fromAccount: 'U9V0W1X2Y',
      toAccount: 'Z3A4B5C6D',
      amountPaid: 100000,
      paymentCurrency: 'US Dollar',
      paymentFormat: 'Wire',
      isLaundering: 1
    },
    status: 'open',
    detectedAt: '2026-02-17T08:30:00Z'
  },
  {
    id: 'viol-002',
    transactionId: 'TXN-015',
    ruleId: 'aml-005',
    ruleName: 'Transaction confirmed as laundering in ground-truth dataset',
    severity: 'critical',
    explanation: 'Transaction of $1,350,000 from account J1K2L3M4N (Bank 17) to 8000ECA98 (Bank 2) via Bitcoin Reinvestment is confirmed as illicit in the IBM AML ground-truth dataset. This represents the integration phase of the laundering cycle.',
    evidence: {
      timestamp: '2023-01-02 17:30:00',
      fromAccount: 'J1K2L3M4N',
      toAccount: '8000ECA98',
      amountPaid: 1350000,
      paymentCurrency: 'US Dollar',
      receivingCurrency: 'Bitcoin',
      paymentFormat: 'Reinvestment',
      isLaundering: 1
    },
    status: 'open',
    detectedAt: '2026-02-17T08:30:00Z'
  },
  {
    id: 'viol-003',
    transactionId: 'TXN-007',
    ruleId: 'aml-004',
    ruleName: 'Cross-currency transaction: Payment Currency differs from Receiving Currency',
    severity: 'medium',
    explanation: 'Payment made in US Dollar ($64,500) but funds received in Euro (€60,000) between accounts 0F2F8911F and 3A7B1D22C. Cross-currency conversion requires enhanced scrutiny for currency-based layering.',
    evidence: {
      timestamp: '2023-01-02 09:00:00',
      fromAccount: '0F2F8911F',
      toAccount: '3A7B1D22C',
      amountPaid: 64500,
      paymentCurrency: 'US Dollar',
      amountReceived: 60000,
      receivingCurrency: 'Euro',
      isLaundering: 1
    },
    status: 'reviewed',
    reviewerComment: 'Flagged for SAR filing. Cross-border currency conversion consistent with layering pattern detected in TXN chain.',
    detectedAt: '2026-02-17T08:30:00Z',
    reviewedAt: '2026-02-17T10:15:00Z'
  },
  {
    id: 'viol-004',
    transactionId: 'TXN-006',
    ruleId: 'aml-006',
    ruleName: 'Wire transfer exceeding $50,000 requires Enhanced Due Diligence',
    severity: 'high',
    explanation: 'Wire transfer of $75,000 from account 2D3E4F5A6 (Bank 4) to C7D8E9F01 (Bank 6) exceeds the $50,000 EDD threshold. Enhanced customer due diligence documentation required before processing.',
    evidence: {
      timestamp: '2023-01-02 08:15:00',
      fromAccount: '2D3E4F5A6',
      toAccount: 'C7D8E9F01',
      amountPaid: 75000,
      paymentCurrency: 'US Dollar',
      paymentFormat: 'Wire',
      isLaundering: 1
    },
    status: 'open',
    detectedAt: '2026-02-17T08:30:00Z'
  },
  {
    id: 'viol-005',
    transactionId: 'TXN-005',
    ruleId: 'aml-003',
    ruleName: 'Round-number transaction above $5,000 (potential structuring)',
    severity: 'medium',
    explanation: 'Cheque payment of exactly $5,000 from C7D8E9F01 (Bank 6) to G7H8I9J01 (Bank 10). Round-number amounts above $5,000 may indicate deliberate structuring to stay below CTR thresholds.',
    evidence: {
      timestamp: '2023-01-02 05:00:00',
      fromAccount: 'C7D8E9F01',
      toAccount: 'G7H8I9J01',
      amountPaid: 5000,
      paymentCurrency: 'US Dollar',
      paymentFormat: 'Cheque',
      isLaundering: 0
    },
    status: 'resolved',
    reviewerComment: 'Verified legitimate business payment. Customer provided invoice. Cleared.',
    detectedAt: '2026-02-15T14:20:00Z',
    reviewedAt: '2026-02-16T09:30:00Z'
  }
];

// ── Rapid-transfer chain (links multiple TXNs to aml-002) ─────────────────────
export const rapidTransferViolations: Violation[] = [
  {
    id: 'viol-006',
    transactionId: 'TXN-CHAIN-2000ECA98',
    ruleId: 'aml-002',
    ruleName: 'More than 5 transfers to the same beneficiary within 24 hours',
    severity: 'high',
    explanation: 'Account 8000ECA98 (Bank 2) sent 6 separate transfers to account 0F2F8911F (Bank 11) within a 3-hour window on 2023-01-02, with amounts consistently at $10,000. This pattern is consistent with deliberate layering to avoid CTR thresholds.',
    evidence: {
      fromAccount: '8000ECA98',
      toAccount: '0F2F8911F',
      transferCount: 6,
      timeWindowHours: 3,
      totalAmount: 60000,
      individualAmounts: [10000, 10000, 10000, 10000, 10000, 10000],
      paymentFormats: ['Reinvestment', 'Wire', 'ACH', 'Credit Cards', 'Cheque', 'Cash']
    },
    status: 'open',
    detectedAt: '2026-02-17T08:30:00Z'
  }
];

// ── Dashboard chart data ───────────────────────────────────────────────────────
export const complianceTrendData = [
  { date: '2026-01-01', violations: 24, resolved: 18, transactions: 1200 },
  { date: '2026-01-08', violations: 31, resolved: 22, transactions: 1450 },
  { date: '2026-01-15', violations: 28, resolved: 25, transactions: 1380 },
  { date: '2026-01-22', violations: 19, resolved: 16, transactions: 1520 },
  { date: '2026-01-29', violations: 15, resolved: 12, transactions: 1600 },
  { date: '2026-02-05', violations: 12, resolved: 10, transactions: 1420 },
  { date: '2026-02-12', violations: 8, resolved: 7, transactions: 1350 },
  { date: '2026-02-17', violations: 6, resolved: 2, transactions: 980 }
];

export const severityBreakdown = [
  { name: 'Critical', value: 2, color: '#dc2626' },
  { name: 'High', value: 2, color: '#ea580c' },
  { name: 'Medium', value: 2, color: '#f59e0b' },
  { name: 'Low', value: 0, color: '#84cc16' }
];

export const topViolatedRules = [
  { rule: 'Confirmed Laundering (aml-005)', count: 18, trend: -3 },
  { rule: 'Large Transactions >$10k (aml-001)', count: 15, trend: -2 },
  { rule: 'Wire EDD >$50k (aml-006)', count: 9, trend: -1 },
  { rule: 'Rapid Transfers (aml-002)', count: 7, trend: -2 },
  { rule: 'Currency Mixing (aml-004)', count: 5, trend: 0 },
  { rule: 'Structuring (aml-003)', count: 3, trend: +1 }
];

export const paymentFormatBreakdown = [
  { name: 'Wire', value: 18, color: '#3b82f6' },
  { name: 'ACH', value: 12, color: '#8b5cf6' },
  { name: 'Reinvestment', value: 10, color: '#10b981' },
  { name: 'Cash', value: 6, color: '#f59e0b' },
  { name: 'Cheque', value: 6, color: '#ef4444' },
  { name: 'Credit Cards', value: 4, color: '#06b6d4' }
];
