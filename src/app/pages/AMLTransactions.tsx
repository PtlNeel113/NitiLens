import { useState, useMemo, useEffect } from 'react';
import { Search, ArrowUpDown, AlertTriangle, CheckCircle, Filter, ExternalLink, Loader2 } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { type AMLTransaction } from '../data/mockData';
import { api, type AMLStats } from '../services/api';

type SortKey = keyof AMLTransaction;
type SortDir = 'asc' | 'desc';

const CURRENCIES = ['All', 'US Dollar', 'Euro', 'Bitcoin', 'Pound'];
const FORMATS = ['All', 'Wire', 'ACH', 'Reinvestment', 'Cheque', 'Credit Cards', 'Cash'];

export function AMLTransactions() {
    const [originalTransactions, setOriginalTransactions] = useState<AMLTransaction[]>([]);
    const [stats, setStats] = useState<AMLStats | null>(null);
    const [loading, setLoading] = useState(true);

    const [search, setSearch] = useState('');
    const [currencyFilter, setCurrencyFilter] = useState('All');
    const [formatFilter, setFormatFilter] = useState('All');
    const [launderingFilter, setLaunderingFilter] = useState<'all' | '0' | '1'>('all');
    const [minAmount, setMinAmount] = useState('');
    const [maxAmount, setMaxAmount] = useState('');
    const [sortKey, setSortKey] = useState<SortKey>('timestamp');
    const [sortDir, setSortDir] = useState<SortDir>('asc');

    useEffect(() => {
        const loadData = async () => {
            try {
                const [txnBatch, amlStats] = await Promise.all([
                    api.getAMLPreview(500),
                    api.getAMLStats()
                ]);

                // Map API keys to camelCase if needed, but our api.ts preview 
                // uses the dict from pandas which might have spaces or dots.
                // Looking at violation_engine.py _make_txn_id, parts are 
                // Timestamp, Account, Account.1, Amount Paid.

                const mapped: AMLTransaction[] = txnBatch.rows.map((r: any) => ({
                    id: r.id ?? 'TXN-' + Math.random().toString(36).substr(2, 9).toUpperCase(),
                    timestamp: r.Timestamp,
                    fromBank: r['From Bank'],
                    fromAccount: r.Account,
                    toBank: r['To Bank'],
                    toAccount: r['Account.1'],
                    amountReceived: r['Amount Received'],
                    receivingCurrency: r['Receiving Currency'],
                    amountPaid: r['Amount Paid'],
                    paymentCurrency: r['Payment Currency'],
                    paymentFormat: r['Payment Format'],
                    isLaundering: r['Is Laundering']
                }));

                setOriginalTransactions(mapped);
                setStats(amlStats);
            } catch (error) {
                console.error('Failed to load transactions:', error);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    const toggleSort = (key: SortKey) => {
        if (sortKey === key) {
            setSortDir(d => d === 'asc' ? 'desc' : 'asc');
        } else {
            setSortKey(key);
            setSortDir('asc');
        }
    };

    const filtered = useMemo(() => {
        return originalTransactions
            .filter(t => {
                if (search) {
                    const q = search.toLowerCase();
                    if (
                        !t.id.toLowerCase().includes(q) &&
                        !t.fromAccount.toLowerCase().includes(q) &&
                        !t.toAccount.toLowerCase().includes(q)
                    ) return false;
                }
                if (currencyFilter !== 'All' && t.paymentCurrency !== currencyFilter) return false;
                if (formatFilter !== 'All' && t.paymentFormat !== formatFilter) return false;
                if (launderingFilter !== 'all' && String(t.isLaundering) !== launderingFilter) return false;
                if (minAmount && t.amountPaid < Number(minAmount)) return false;
                if (maxAmount && t.amountPaid > Number(maxAmount)) return false;
                return true;
            })
            .sort((a, b) => {
                const aVal = a[sortKey];
                const bVal = b[sortKey];
                let cmp = 0;
                if (typeof aVal === 'number' && typeof bVal === 'number') {
                    cmp = aVal - bVal;
                } else {
                    cmp = String(aVal).localeCompare(String(bVal));
                }
                return sortDir === 'asc' ? cmp : -cmp;
            });
    }, [originalTransactions, search, currencyFilter, formatFilter, launderingFilter, minAmount, maxAmount, sortKey, sortDir]);

    const SortBtn = ({ k, label }: { k: SortKey; label: string }) => (
        <button
            onClick={() => toggleSort(k)}
            className="flex items-center gap-1 hover:text-blue-700 font-medium whitespace-nowrap"
        >
            {label}
            <ArrowUpDown className={`w-3 h-3 ${sortKey === k ? 'text-blue-600' : 'text-gray-400'}`} />
        </button>
    );

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-6 flex items-start justify-between">
                    <div>
                        <h1 className="text-3xl font-bold mb-1">AML Transactions</h1>
                        <p className="text-gray-600">
                            IBM Anti-Money Laundering dataset ·{' '}
                            <a
                                href="https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:underline inline-flex items-center gap-1"
                            >
                                Kaggle <ExternalLink className="w-3 h-3" />
                            </a>{' '}
                            · CDLA-Sharing-1.0
                        </p>
                    </div>
                </div>

                {/* KPI Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <Card className="p-4 text-center">
                        <p className="text-2xl font-bold text-gray-900">{stats?.total_transactions ?? 0}</p>
                        <p className="text-sm text-gray-600">Total Transactions</p>
                    </Card>
                    <Card className="p-4 text-center bg-red-50 border-red-200">
                        <p className="text-2xl font-bold text-red-600">{stats?.confirmed_laundering ?? 0}</p>
                        <p className="text-sm text-red-700">Confirmed Laundering</p>
                    </Card>
                    <Card className="p-4 text-center bg-yellow-50 border-yellow-200">
                        <p className="text-2xl font-bold text-yellow-700">
                            {originalTransactions.filter(t => t.amountPaid > 10000).length}
                        </p>
                        <p className="text-sm text-yellow-700">Above $10k (CTR)</p>
                    </Card>
                    <Card className="p-4 text-center bg-blue-50 border-blue-200">
                        <p className="text-2xl font-bold text-blue-700">
                            ${((stats?.avg_amount_paid ?? 0) * (stats?.total_transactions ?? 0) / 1_000_000).toFixed(2)}M
                        </p>
                        <p className="text-sm text-blue-700">Est. Total Volume</p>
                    </Card>
                </div>

                {/* Filters */}
                <Card className="p-4 mb-6">
                    <div className="flex flex-wrap gap-3 items-end">
                        {/* Search */}
                        <div className="flex-1 min-w-[200px]">
                            <label className="block text-xs font-medium text-gray-600 mb-1">Search</label>
                            <div className="relative">
                                <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="TXN ID, account..."
                                    value={search}
                                    onChange={e => setSearch(e.target.value)}
                                    className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>

                        {/* Currency */}
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Currency</label>
                            <select
                                value={currencyFilter}
                                onChange={e => setCurrencyFilter(e.target.value)}
                                className="border border-gray-300 rounded-md text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                {CURRENCIES.map(c => <option key={c}>{c}</option>)}
                            </select>
                        </div>

                        {/* Format */}
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Format</label>
                            <select
                                value={formatFilter}
                                onChange={e => setFormatFilter(e.target.value)}
                                className="border border-gray-300 rounded-md text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                {FORMATS.map(f => <option key={f}>{f}</option>)}
                            </select>
                        </div>

                        {/* Laundering */}
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Laundering</label>
                            <select
                                value={launderingFilter}
                                onChange={e => setLaunderingFilter(e.target.value as 'all' | '0' | '1')}
                                className="border border-gray-300 rounded-md text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="all">All</option>
                                <option value="1">Confirmed</option>
                                <option value="0">Clean</option>
                            </select>
                        </div>

                        {/* Min Amount */}
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Min Amount ($)</label>
                            <input
                                type="number"
                                placeholder="0"
                                value={minAmount}
                                onChange={e => setMinAmount(e.target.value)}
                                className="w-28 border border-gray-300 rounded-md text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        {/* Max Amount */}
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Max Amount ($)</label>
                            <input
                                type="number"
                                placeholder="∞"
                                value={maxAmount}
                                onChange={e => setMaxAmount(e.target.value)}
                                className="w-28 border border-gray-300 rounded-md text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                                setSearch('');
                                setCurrencyFilter('All');
                                setFormatFilter('All');
                                setLaunderingFilter('all');
                                setMinAmount('');
                                setMaxAmount('');
                            }}
                        >
                            <Filter className="w-4 h-4 mr-1" />
                            Clear
                        </Button>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                        Showing {filtered.length} of {originalTransactions.length} transactions
                    </p>
                </Card>

                {/* Laundering legend */}
                <div className="flex items-center gap-4 mb-3 text-sm">
                    <div className="flex items-center gap-1.5">
                        <div className="w-3 h-3 rounded bg-red-200 border border-red-400" />
                        <span className="text-gray-600">Confirmed laundering</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <div className="w-3 h-3 rounded bg-white border border-gray-300" />
                        <span className="text-gray-600">Clean transaction</span>
                    </div>
                </div>

                {/* Table */}
                <Card className="overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead className="bg-gray-100 text-xs text-gray-700 uppercase tracking-wider">
                                <tr>
                                    <th className="px-4 py-3 text-left"><SortBtn k="id" label="TXN ID" /></th>
                                    <th className="px-4 py-3 text-left"><SortBtn k="timestamp" label="Timestamp" /></th>
                                    <th className="px-4 py-3 text-left">From → To</th>
                                    <th className="px-4 py-3 text-right"><SortBtn k="amountPaid" label="Amount Paid" /></th>
                                    <th className="px-4 py-3 text-right"><SortBtn k="amountReceived" label="Received" /></th>
                                    <th className="px-4 py-3 text-left"><SortBtn k="paymentCurrency" label="Pay Currency" /></th>
                                    <th className="px-4 py-3 text-left"><SortBtn k="receivingCurrency" label="Recv Currency" /></th>
                                    <th className="px-4 py-3 text-left"><SortBtn k="paymentFormat" label="Format" /></th>
                                    <th className="px-4 py-3 text-center"><SortBtn k="isLaundering" label="Laundering" /></th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {filtered.length === 0 ? (
                                    <tr>
                                        <td colSpan={9} className="text-center py-12 text-gray-500">
                                            No transactions match your filters.
                                        </td>
                                    </tr>
                                ) : (
                                    filtered.map(txn => (
                                        <tr
                                            key={txn.id}
                                            className={`hover:bg-gray-50 transition-colors ${txn.isLaundering === 1 ? 'bg-red-50/60' : ''
                                                }`}
                                        >
                                            <td className="px-4 py-3 font-mono text-xs text-gray-700">{txn.id}</td>
                                            <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{txn.timestamp}</td>
                                            <td className="px-4 py-3">
                                                <span className="font-mono text-xs">
                                                    Bank {txn.fromBank}/{txn.fromAccount.slice(0, 6)}…
                                                    <span className="text-gray-400"> → </span>
                                                    Bank {txn.toBank}/{txn.toAccount.slice(0, 6)}…
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-right font-mono">
                                                <span className={txn.amountPaid > 10000 ? 'text-orange-700 font-semibold' : ''}>
                                                    ${txn.amountPaid.toLocaleString()}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-right font-mono text-gray-600">
                                                {txn.receivingCurrency !== txn.paymentCurrency
                                                    ? <span className="text-purple-700">{txn.amountReceived.toLocaleString()}</span>
                                                    : txn.amountReceived.toLocaleString()
                                                }
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className={`text-xs px-2 py-0.5 rounded ${txn.paymentCurrency === 'Bitcoin' ? 'bg-yellow-100 text-yellow-800' :
                                                    txn.paymentCurrency === 'Euro' ? 'bg-blue-100 text-blue-800' :
                                                        txn.paymentCurrency === 'Pound' ? 'bg-purple-100 text-purple-800' :
                                                            'bg-gray-100 text-gray-700'
                                                    }`}>
                                                    {txn.paymentCurrency}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3">
                                                {txn.receivingCurrency !== txn.paymentCurrency ? (
                                                    <span className="text-xs px-2 py-0.5 rounded bg-yellow-50 text-yellow-800 border border-yellow-200">
                                                        ⚠ {txn.receivingCurrency}
                                                    </span>
                                                ) : (
                                                    <span className="text-xs text-gray-500">{txn.receivingCurrency}</span>
                                                )}
                                            </td>
                                            <td className="px-4 py-3">
                                                <Badge className={
                                                    txn.paymentFormat === 'Wire' ? 'bg-blue-100 text-blue-700 border-blue-200' :
                                                        txn.paymentFormat === 'Cash' ? 'bg-gray-100 text-gray-700' :
                                                            txn.paymentFormat === 'Reinvestment' ? 'bg-yellow-100 text-yellow-700' :
                                                                'bg-slate-100 text-slate-700'
                                                }>
                                                    {txn.paymentFormat}
                                                </Badge>
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                {txn.isLaundering === 1 ? (
                                                    <span className="inline-flex items-center gap-1 bg-red-100 text-red-700 px-2 py-0.5 rounded text-xs font-semibold">
                                                        <AlertTriangle className="w-3 h-3" /> YES
                                                    </span>
                                                ) : (
                                                    <span className="inline-flex items-center gap-1 bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs">
                                                        <CheckCircle className="w-3 h-3" /> No
                                                    </span>
                                                )}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </Card>

                <p className="text-xs text-gray-400 text-center mt-4">
                    Sample data — 51 synthetic rows. Replace with full IBM AML dataset (6M+ rows) for production use.
                    See <code>data/datasets/ibm_aml/README.md</code> for download instructions.
                </p>
            </div>
        </div>
    );
}
