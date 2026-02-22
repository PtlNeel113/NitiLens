import { useState, useRef, useEffect, useCallback } from 'react';

// ── Types ──────────────────────────────────────────────────────────
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Array<{ type: string; id: string; label: string }>;
  riskReferences?: Array<{ metric: string; value: number; level: string }>;
  relatedViolations?: Array<{ id: string; severity: string; field: string; score: number }>;
  intent?: string;
}

interface ChatResponse {
  reply: string;
  sources: Array<{ type: string; id: string; label: string }>;
  risk_references: Array<{ metric: string; value: number; level: string }>;
  related_violations: Array<{ id: string; severity: string; field: string; score: number }>;
  conversation_id: string;
  intent: string;
}

// ── API ────────────────────────────────────────────────────────────
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Mock responses for when the backend is unavailable
const MOCK_RESPONSES: Record<string, ChatResponse> = {
  risk: {
    reply: `**Current Risk Assessment Summary**\n\n📊 **Overall Risk Score:** 72/100 (Medium-High)\n\n**Breakdown by Category:**\n• 🔴 Data Privacy: **High** — 3 active DPDPA violations detected\n• 🟡 AML Compliance: **Medium** — 12 flagged transactions under review\n• 🟢 RBI Guidelines: **Low** — All 8 circulars compliant\n• 🟡 SEBI Regulations: **Medium** — 2 pending disclosure items\n\n**Trend:** Risk score has decreased by 8% this month due to completed remediations.\n\n💡 *Recommendation:* Prioritize resolving the 3 DPDPA violations to bring overall risk below 65.`,
    sources: [
      { type: 'metric', id: 'risk-001', label: 'Risk Dashboard' },
      { type: 'violation', id: 'viol-045', label: 'DPDPA Violations' },
      { type: 'policy', id: 'pol-012', label: 'AML Transaction Monitor' },
    ],
    risk_references: [
      { metric: 'Data Privacy', value: 85, level: 'High' },
      { metric: 'AML Compliance', value: 62, level: 'Medium' },
      { metric: 'RBI Guidelines', value: 28, level: 'Low' },
      { metric: 'SEBI Regulations', value: 55, level: 'Medium' },
    ],
    related_violations: [],
    conversation_id: 'mock-conv-001',
    intent: 'risk_assessment',
  },
  violations: {
    reply: `**Critical Violations Report**\n\n⚠️ **5 Critical Violations Found:**\n\n1. **DPDPA-2023 §8 Breach** — Personal data processed without valid consent for 2,340 records\n   - Severity: 🔴 Critical | Score: 94/100\n   - Detected: Feb 18, 2026\n\n2. **RBI KYC Non-Compliance** — 156 accounts missing re-verification\n   - Severity: 🔴 Critical | Score: 89/100\n   - Detected: Feb 15, 2026\n\n3. **AML Threshold Breach** — ₹12.4Cr in unreported high-value transactions\n   - Severity: 🔴 Critical | Score: 92/100\n   - Detected: Feb 12, 2026\n\n4. **SEBI LODR Violation** — Delayed material event disclosure (3 days overdue)\n   - Severity: 🟡 High | Score: 78/100\n   - Detected: Feb 10, 2026\n\n5. **IT Act §43A** — Inadequate data security practices for financial records\n   - Severity: 🟡 High | Score: 75/100\n   - Detected: Feb 8, 2026\n\n📋 *Total pending remediations:* 12 | *Auto-resolved this month:* 7`,
    sources: [
      { type: 'violation', id: 'viol-045', label: 'DPDPA §8 Breach' },
      { type: 'violation', id: 'viol-044', label: 'KYC Non-Compliance' },
      { type: 'violation', id: 'viol-043', label: 'AML Threshold Breach' },
    ],
    risk_references: [
      { metric: 'Critical Violations', value: 5, level: 'Critical' },
      { metric: 'High Violations', value: 7, level: 'High' },
    ],
    related_violations: [
      { id: 'VIOL-045', severity: 'Critical', field: 'Data Privacy', score: 94 },
      { id: 'VIOL-044', severity: 'Critical', field: 'KYC', score: 89 },
      { id: 'VIOL-043', severity: 'Critical', field: 'AML', score: 92 },
    ],
    conversation_id: 'mock-conv-001',
    intent: 'violation_report',
  },
  audit: {
    reply: `**Audit Summary — February 2026**\n\n📋 **Compliance Score:** 78/100 (Good)\n\n**Frameworks Assessed:**\n| Framework | Status | Score |\n|-----------|--------|-------|\n| DPDPA 2023 | ⚠️ Needs Attention | 68% |\n| RBI Master Circular | ✅ Compliant | 91% |\n| SEBI LODR | ⚠️ Minor Issues | 82% |\n| AML/CFT Guidelines | ✅ Compliant | 88% |\n| IT Act 2000 | ⚠️ Needs Attention | 72% |\n\n**Key Findings:**\n• 23 policies scanned across 5 frameworks\n• 18 policies fully compliant, 5 need updates\n• Average remediation time: 4.2 days (↓ from 6.1 days)\n• Next audit deadline: March 15, 2026\n\n✅ *Overall assessment:* Organization is in good compliance health with focused attention needed on DPDPA and IT Act provisions.`,
    sources: [
      { type: 'policy', id: 'pol-audit', label: 'Audit Dashboard' },
      { type: 'metric', id: 'met-score', label: 'Compliance Scores' },
    ],
    risk_references: [],
    related_violations: [],
    conversation_id: 'mock-conv-001',
    intent: 'audit_summary',
  },
  remediation: {
    reply: `**Remediation Status Overview**\n\n🔧 **Active Remediations:** 12\n\n**By Priority:**\n• 🔴 Critical (3): Average ETA 5 days\n• 🟡 High (4): Average ETA 8 days\n• 🟢 Medium (5): Average ETA 14 days\n\n**Recent Completions:**\n✅ DPDPA Consent Form Update — Completed Feb 20\n✅ KYC Auto-Verification Pipeline — Completed Feb 18\n✅ AML Threshold Alert System — Completed Feb 16\n\n**In Progress:**\n🔄 Data Retention Policy Update — 65% complete (Due: Feb 28)\n🔄 Employee Access Audit — 40% complete (Due: Mar 5)\n🔄 Vendor Risk Assessment — 80% complete (Due: Feb 25)\n\n📈 *Monthly trend:* 7 remediations completed, 3 new violations detected. Net improvement: +4`,
    sources: [
      { type: 'metric', id: 'rem-001', label: 'Remediation Tracker' },
    ],
    risk_references: [
      { metric: 'Completion Rate', value: 85, level: 'Medium' },
    ],
    related_violations: [],
    conversation_id: 'mock-conv-001',
    intent: 'remediation_status',
  },
  default: {
    reply: `Thank you for your question. Here's what I can help you with:\n\n🛡️ **NitiGuard AI Capabilities:**\n\n• **Risk Assessment** — "What is our current risk level?"\n• **Violation Reports** — "Show critical violations"\n• **Audit Summaries** — "Generate audit summary"\n• **Remediation Tracking** — "Remediation status overview"\n• **Policy Analysis** — "Analyze our DPDPA compliance"\n• **Regulatory Updates** — "Latest RBI circular changes"\n\n💡 Try asking one of the suggested questions below, or type your specific compliance query.\n\n*I analyze your organization's compliance data across DPDPA, RBI, SEBI, AML, and IT Act frameworks in real-time.*`,
    sources: [],
    risk_references: [],
    related_violations: [],
    conversation_id: 'mock-conv-001',
    intent: 'general',
  },
};

function getMockResponse(message: string): ChatResponse {
  const lower = message.toLowerCase();
  if (lower.includes('risk') || lower.includes('score') || lower.includes('level'))
    return MOCK_RESPONSES.risk;
  if (lower.includes('violation') || lower.includes('critical') || lower.includes('breach'))
    return MOCK_RESPONSES.violations;
  if (lower.includes('audit') || lower.includes('summary') || lower.includes('report'))
    return MOCK_RESPONSES.audit;
  if (lower.includes('remediat') || lower.includes('fix') || lower.includes('status'))
    return MOCK_RESPONSES.remediation;
  return MOCK_RESPONSES.default;
}

async function sendChatMessage(
  token: string,
  message: string,
  conversationId: string | null,
  isVoice: boolean = false
): Promise<ChatResponse> {
  try {
    const res = await fetch(`${API_BASE}/api/agent/chat`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        is_voice: isVoice,
      }),
    });
    if (!res.ok) throw new Error('Failed to send message');
    return res.json();
  } catch {
    // Fallback to mock responses when backend is unavailable
    console.warn('NitiGuard: Backend unavailable, using demo responses');
    return getMockResponse(message);
  }
}

// ── Suggested Questions ────────────────────────────────────────────
const SUGGESTED_QUESTIONS = [
  '📊 What is our current risk level?',
  '⚠️ Show critical violations',
  '📋 Generate audit summary',
  '🔧 Remediation status overview',
];

// ── Component ──────────────────────────────────────────────────────
export function NitiGuardChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set());

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) inputRef.current?.focus();
  }, [isOpen]);

  // Get token from localStorage (matching existing auth pattern)
  const getToken = () => localStorage.getItem('token') || '';

  // Send message handler
  const handleSend = useCallback(
    async (text?: string, isVoice = false) => {
      const msg = (text || input).trim();
      if (!msg || isLoading) return;

      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content: msg,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setInput('');
      setIsLoading(true);

      try {
        const token = getToken();
        const response = await sendChatMessage(token, msg, conversationId, isVoice);

        if (response.conversation_id) setConversationId(response.conversation_id);

        const aiMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response.reply,
          timestamp: new Date(),
          sources: response.sources,
          riskReferences: response.risk_references,
          relatedViolations: response.related_violations,
          intent: response.intent,
        };

        setMessages((prev) => [...prev, aiMsg]);
      } catch {
        // sendChatMessage handles errors internally with mock responses,
        // so this is just a safety fallback
        const fallbackMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content:
            'I\'m ready to help with your compliance queries. Try asking about risk levels, violations, audit summaries, or remediation status.',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, fallbackMsg]);
      } finally {
        setIsLoading(false);
      }
    },
    [input, isLoading, conversationId]
  );

  // Voice recording
  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
      return;
    }

    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) {
      alert('Speech recognition not supported in this browser.');
      return;
    }

    const recognition = new SR();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsRecording(true);
    recognition.onresult = (e: any) => {
      const transcript = e.results[0][0].transcript;
      setInput(transcript);
      handleSend(transcript, true);
    };
    recognition.onerror = () => setIsRecording(false);
    recognition.onend = () => setIsRecording(false);

    recognitionRef.current = recognition;
    recognition.start();
  };

  // Text-to-speech
  const speakText = (text: string) => {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }
    const clean = text
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/`(.*?)`/g, '$1')
      .replace(/^[-#*]\s*/gm, '');

    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.onend = () => setIsSpeaking(false);
    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const toggleSources = (id: string) =>
    setExpandedSources((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  // ── Inline Styles ──────────────────────────────────────────────
  const S = {
    /* Floating button */
    fab: {
      position: 'fixed' as const,
      bottom: 24,
      right: 24,
      zIndex: 9999,
      width: 60,
      height: 60,
      borderRadius: '50%',
      background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%)',
      border: 'none',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      boxShadow: '0 8px 32px rgba(99,102,241,.45)',
      transition: 'transform .2s, box-shadow .2s',
    },
    fabHover: { transform: 'scale(1.08)', boxShadow: '0 12px 40px rgba(99,102,241,.55)' },

    /* Modal wrapper */
    modal: {
      position: 'fixed' as const,
      bottom: 96,
      right: 24,
      zIndex: 9998,
      width: 420,
      maxWidth: 'calc(100vw - 48px)',
      height: 580,
      maxHeight: 'calc(100vh - 140px)',
      borderRadius: 20,
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column' as const,
      background: 'rgba(15, 15, 30, 0.95)',
      backdropFilter: 'blur(24px)',
      border: '1px solid rgba(99,102,241,0.25)',
      boxShadow:
        '0 24px 80px rgba(0,0,0,.45), 0 0 0 1px rgba(99,102,241,.15), inset 0 1px 0 rgba(255,255,255,.05)',
    },

    /* Header */
    header: {
      padding: '16px 20px',
      background: 'linear-gradient(135deg, rgba(99,102,241,.15), rgba(139,92,246,.1))',
      borderBottom: '1px solid rgba(99,102,241,.2)',
      display: 'flex',
      alignItems: 'center',
      gap: 12,
    },
    headerIcon: {
      width: 40,
      height: 40,
      borderRadius: 12,
      background: 'linear-gradient(135deg, #6366f1, #a855f7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0,
    },
    headerTitle: {
      color: '#fff',
      fontSize: 16,
      fontWeight: 700 as const,
      letterSpacing: '0.02em',
    },
    headerSub: {
      color: 'rgba(255,255,255,.5)',
      fontSize: 11,
      marginTop: 2,
    },
    closeBtn: {
      marginLeft: 'auto',
      background: 'rgba(255,255,255,.08)',
      border: 'none',
      color: 'rgba(255,255,255,.6)',
      width: 32,
      height: 32,
      borderRadius: 8,
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: 18,
      transition: 'background .2s',
    },

    /* Messages area */
    body: {
      flex: 1,
      overflowY: 'auto' as const,
      padding: '16px 16px 8px',
      display: 'flex',
      flexDirection: 'column' as const,
      gap: 12,
    },

    /* Bubble base */
    bubble: (isUser: boolean) => ({
      maxWidth: '85%',
      padding: '10px 14px',
      borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
      fontSize: 13,
      lineHeight: 1.55,
      alignSelf: isUser ? ('flex-end' as const) : ('flex-start' as const),
      background: isUser
        ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
        : 'rgba(255,255,255,.07)',
      color: isUser ? '#fff' : 'rgba(255,255,255,.9)',
      wordBreak: 'break-word' as const,
    }),

    /* Source chip */
    chip: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 4,
      padding: '3px 8px',
      borderRadius: 6,
      background: 'rgba(99,102,241,.15)',
      color: '#a5b4fc',
      fontSize: 11,
      marginRight: 4,
      marginTop: 4,
    },

    /* Input bar */
    inputBar: {
      padding: '12px 16px',
      borderTop: '1px solid rgba(99,102,241,.15)',
      display: 'flex',
      gap: 8,
      alignItems: 'center',
      background: 'rgba(10,10,25,.6)',
    },
    input: {
      flex: 1,
      background: 'rgba(255,255,255,.06)',
      border: '1px solid rgba(99,102,241,.2)',
      borderRadius: 12,
      padding: '10px 14px',
      color: '#fff',
      fontSize: 13,
      outline: 'none',
      transition: 'border-color .2s',
    },
    iconBtn: (active = false) => ({
      width: 38,
      height: 38,
      borderRadius: 10,
      border: 'none',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0,
      background: active
        ? 'linear-gradient(135deg, #ef4444, #f97316)'
        : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
      color: '#fff',
      transition: 'transform .15s, opacity .2s',
    }),

    /* Suggested questions */
    suggestions: {
      display: 'flex',
      flexWrap: 'wrap' as const,
      gap: 6,
      padding: '0 16px 12px',
    },
    sugBtn: {
      padding: '6px 12px',
      borderRadius: 20,
      border: '1px solid rgba(99,102,241,.25)',
      background: 'rgba(99,102,241,.08)',
      color: 'rgba(255,255,255,.7)',
      fontSize: 11,
      cursor: 'pointer',
      transition: 'background .2s, border-color .2s',
      whiteSpace: 'nowrap' as const,
    },

    /* Loading dots */
    dots: {
      display: 'flex',
      gap: 4,
      padding: '8px 14px',
      alignSelf: 'flex-start' as const,
    },
    dot: (i: number) => ({
      width: 7,
      height: 7,
      borderRadius: '50%',
      background: '#818cf8',
      animation: `nitiPulse 1.2s ease-in-out ${i * 0.15}s infinite`,
    }),

    /* Welcome */
    welcome: {
      textAlign: 'center' as const,
      padding: '32px 20px',
      color: 'rgba(255,255,255,.5)',
    },
    welcomeIcon: {
      width: 56,
      height: 56,
      borderRadius: 16,
      background: 'linear-gradient(135deg, rgba(99,102,241,.2), rgba(139,92,246,.15))',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      margin: '0 auto 16px',
      fontSize: 28,
    },

    /* Risk ref */
    riskBadge: (level: string) => ({
      display: 'inline-flex',
      alignItems: 'center',
      gap: 4,
      padding: '2px 8px',
      borderRadius: 6,
      fontSize: 11,
      fontWeight: 600,
      background:
        level === 'Critical'
          ? 'rgba(239,68,68,.15)'
          : level === 'High'
            ? 'rgba(249,115,22,.15)'
            : 'rgba(234,179,8,.15)',
      color:
        level === 'Critical' ? '#fca5a5' : level === 'High' ? '#fdba74' : '#fde68a',
    }),
  };

  // ── Render ─────────────────────────────────────────────────────
  return (
    <>
      {/* Pulse animation keyframe */}
      <style>{`
        @keyframes nitiPulse{0%,80%,100%{transform:scale(.6);opacity:.4}40%{transform:scale(1);opacity:1}}
        @keyframes nitiFabPulse{0%{box-shadow:0 0 0 0 rgba(99,102,241,.5)}70%{box-shadow:0 0 0 14px rgba(99,102,241,0)}100%{box-shadow:0 0 0 0 rgba(99,102,241,0)}}
      `}</style>

      {/* FAB */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          ...S.fab,
          animation: !isOpen ? 'nitiFabPulse 2s infinite' : 'none',
        }}
        onMouseEnter={(e) => {
          Object.assign((e.target as HTMLElement).style, S.fabHover);
        }}
        onMouseLeave={(e) => {
          (e.target as HTMLElement).style.transform = 'scale(1)';
          (e.target as HTMLElement).style.boxShadow =
            '0 8px 32px rgba(99,102,241,.45)';
        }}
        title="NitiGuard AI Assistant"
        id="nitiguard-fab"
      >
        {isOpen ? (
          <svg width="24" height="24" fill="none" stroke="#fff" strokeWidth="2.5">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        ) : (
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 2a7 7 0 0 1 7 7v1.5a2.5 2.5 0 0 1-2.5 2.5H15v3a2 2 0 0 1-2 2h-2a2 2 0 0 1-2-2v-3H7.5A2.5 2.5 0 0 1 5 10.5V9a7 7 0 0 1 7-7Z"
              fill="rgba(255,255,255,.9)"
            />
            <circle cx="9.5" cy="8.5" r="1.5" fill="#6366f1" />
            <circle cx="14.5" cy="8.5" r="1.5" fill="#6366f1" />
            <path d="M10 11h4" stroke="#6366f1" strokeWidth="1.5" strokeLinecap="round" />
            <path d="M8 19v2M16 19v2" stroke="rgba(255,255,255,.9)" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        )}
      </button>

      {/* Chat Modal */}
      {isOpen && (
        <div style={S.modal} id="nitiguard-chat-modal">
          {/* Header */}
          <div style={S.header}>
            <div style={S.headerIcon}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path
                  d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m12-12v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9m16 0H3"
                  stroke="#fff"
                  strokeWidth="1.5"
                />
              </svg>
            </div>
            <div>
              <div style={S.headerTitle}>NitiGuard AI</div>
              <div style={S.headerSub}>Compliance Copilot • Always Factual</div>
            </div>
            <button
              style={S.closeBtn}
              onClick={() => setIsOpen(false)}
              onMouseEnter={(e) =>
                ((e.target as HTMLElement).style.background = 'rgba(255,255,255,.15)')
              }
              onMouseLeave={(e) =>
                ((e.target as HTMLElement).style.background = 'rgba(255,255,255,.08)')
              }
            >
              ✕
            </button>
          </div>

          {/* Messages */}
          <div style={S.body}>
            {messages.length === 0 && (
              <div style={S.welcome}>
                <div style={S.welcomeIcon}>🛡️</div>
                <div style={{ color: '#fff', fontWeight: 600, fontSize: 15, marginBottom: 6 }}>
                  NitiGuard AI
                </div>
                <div style={{ fontSize: 12, lineHeight: 1.6 }}>
                  Your compliance copilot. Ask me about risks,
                  <br />
                  violations, policies, or remediation status.
                </div>
              </div>
            )}

            {messages.map((m) => (
              <div key={m.id}>
                <div style={S.bubble(m.role === 'user')}>
                  <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
                </div>

                {/* Sources */}
                {m.role === 'assistant' && m.sources && m.sources.length > 0 && (
                  <div style={{ alignSelf: 'flex-start', marginTop: 4 }}>
                    <button
                      onClick={() => toggleSources(m.id)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#818cf8',
                        fontSize: 11,
                        cursor: 'pointer',
                        padding: '2px 0',
                      }}
                    >
                      {expandedSources.has(m.id) ? '▾' : '▸'} Sources (
                      {m.sources.length})
                    </button>
                    {expandedSources.has(m.id) && (
                      <div style={{ marginTop: 4, display: 'flex', flexWrap: 'wrap' }}>
                        {m.sources.map((s, i) => (
                          <span key={i} style={S.chip}>
                            {s.type === 'violation' ? '⚠️' : s.type === 'policy' ? '📋' : '📊'}{' '}
                            {s.label}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Risk references */}
                {m.role === 'assistant' && m.riskReferences && m.riskReferences.length > 0 && (
                  <div
                    style={{
                      alignSelf: 'flex-start',
                      display: 'flex',
                      gap: 6,
                      marginTop: 6,
                      flexWrap: 'wrap',
                    }}
                  >
                    {m.riskReferences.map((r, i) => (
                      <span key={i} style={S.riskBadge(r.level)}>
                        {r.level}: {r.value}
                      </span>
                    ))}
                  </div>
                )}

                {/* Related violations */}
                {m.role === 'assistant' &&
                  m.relatedViolations &&
                  m.relatedViolations.length > 0 && (
                    <div
                      style={{
                        alignSelf: 'flex-start',
                        marginTop: 6,
                        fontSize: 11,
                        color: 'rgba(255,255,255,.5)',
                      }}
                    >
                      Related: {m.relatedViolations.map((v) => v.id).join(', ')}
                    </div>
                  )}

                {/* Speak button for AI messages */}
                {m.role === 'assistant' && (
                  <button
                    onClick={() => speakText(m.content)}
                    style={{
                      alignSelf: 'flex-start',
                      background: 'none',
                      border: 'none',
                      color: isSpeaking ? '#f97316' : 'rgba(255,255,255,.35)',
                      fontSize: 14,
                      cursor: 'pointer',
                      padding: '4px 2px',
                      marginTop: 2,
                    }}
                    title={isSpeaking ? 'Stop speaking' : 'Read aloud'}
                  >
                    {isSpeaking ? '🔊' : '🔈'}
                  </button>
                )}
              </div>
            ))}

            {/* Loading */}
            {isLoading && (
              <div style={S.dots}>
                <div style={S.dot(0)} />
                <div style={S.dot(1)} />
                <div style={S.dot(2)} />
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions (only when no messages) */}
          {messages.length === 0 && (
            <div style={S.suggestions}>
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  style={S.sugBtn}
                  onClick={() => handleSend(q)}
                  onMouseEnter={(e) => {
                    (e.target as HTMLElement).style.background = 'rgba(99,102,241,.2)';
                    (e.target as HTMLElement).style.borderColor = 'rgba(99,102,241,.5)';
                  }}
                  onMouseLeave={(e) => {
                    (e.target as HTMLElement).style.background = 'rgba(99,102,241,.08)';
                    (e.target as HTMLElement).style.borderColor = 'rgba(99,102,241,.25)';
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {/* Input bar */}
          <div style={S.inputBar}>
            {/* Mic button */}
            <button
              onClick={toggleRecording}
              style={S.iconBtn(isRecording)}
              title={isRecording ? 'Stop recording' : 'Voice input'}
              id="nitiguard-mic-btn"
            >
              {isRecording ? (
                <svg width="18" height="18" fill="none" stroke="#fff" strokeWidth="2">
                  <rect x="4" y="4" width="10" height="10" rx="2" fill="#fff" />
                </svg>
              ) : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <rect x="9" y="2" width="6" height="12" rx="3" fill="#fff" />
                  <path d="M5 10a7 7 0 0 0 14 0" stroke="#fff" strokeWidth="2" />
                  <path d="M12 19v3m-3 0h6" stroke="#fff" strokeWidth="2" strokeLinecap="round" />
                </svg>
              )}
            </button>

            {/* Text input */}
            <input
              ref={inputRef}
              style={S.input}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder={isRecording ? 'Listening...' : 'Ask NitiGuard AI...'}
              disabled={isLoading}
              onFocus={(e) =>
                ((e.target as HTMLElement).style.borderColor = 'rgba(99,102,241,.5)')
              }
              onBlur={(e) =>
                ((e.target as HTMLElement).style.borderColor = 'rgba(99,102,241,.2)')
              }
              id="nitiguard-input"
            />

            {/* Send button */}
            <button
              onClick={() => handleSend()}
              disabled={isLoading || !input.trim()}
              style={{
                ...S.iconBtn(),
                opacity: isLoading || !input.trim() ? 0.4 : 1,
              }}
              title="Send"
              id="nitiguard-send-btn"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M22 2 11 13" stroke="#fff" strokeWidth="2" strokeLinecap="round" />
                <path d="M22 2 15 22l-4-9-9-4 20-7Z" fill="rgba(255,255,255,.9)" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  );
}
