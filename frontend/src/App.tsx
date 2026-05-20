import React, { useState, useRef, useEffect, useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  MiniMap,
  Background,
  ReactFlowProvider,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

type AgentRole = 'supervisor' | 'researcher' | 'analyst' | 'coder' | 'summarizer';

interface AgentNodeData {
  agent: AgentRole;
  label: string;
  icon: string;
  description: string;
  status: 'online' | 'processing' | 'idle' | 'thinking';
  progress?: string;
}

interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  agent?: string;
  timestamp?: string;
}

const agentColors: Record<AgentRole, string> = {
  supervisor: '#8b5cf6',
  researcher: '#3b82f6',
  analyst: '#06b6d4',
  coder: '#10b981',
  summarizer: '#f59e0b',
};

const agentIcons: Record<AgentRole, string> = {
  supervisor: '🧠',
  researcher: '🔍',
  analyst: '📊',
  coder: '💻',
  summarizer: '📝',
};

const AgentNode: React.FC<{ data: AgentNodeData }> = ({ data }) => {
  const color = agentColors[data.agent];
  const isActive = data.status === 'processing' || data.status === 'thinking';
  return (
    <div
      className="agent-node"
      style={{
        borderColor: isActive ? color : `${color}33`,
        boxShadow: isActive ? `0 0 24px ${color}40` : undefined,
      }}
    >
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: 12,
          background: `linear-gradient(135deg, ${color}33, ${color}11)`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 24,
          marginBottom: 12,
          animation: isActive ? 'pulse 1.5s ease-in-out infinite' : undefined,
        }}
      >
        {data.icon}
      </div>
      <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 4 }}>{data.label}</div>
      <div style={{ color: '#a0a0c0', fontSize: 13, marginBottom: 10 }}>{data.description}</div>
      {data.progress && (
        <div style={{ color: color, fontSize: 12, marginBottom: 8, fontStyle: 'italic' }}>
          {data.progress}
        </div>
      )}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: '#888' }}>
        <span
          style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: isActive ? color : data.status === 'online' ? '#10b981' : '#666',
            boxShadow: isActive ? `0 0 12px ${color}` : undefined,
            animation: isActive ? 'pulse 1s ease-in-out infinite' : undefined,
          }}
        />
        {isActive ? '处理中...' : data.status === 'online' ? '在线' : '空闲'}
      </div>
    </div>
  );
};

const nodeTypes = { agentNode: AgentNode };

const defaultNodes: Node<AgentNodeData>[] = [
  { id: 'supervisor', type: 'agentNode', position: { x: 400, y: 50 }, data: { agent: 'supervisor', label: 'Supervisor', icon: '🧠', description: '任务路由与调度', status: 'online' } },
  { id: 'researcher', type: 'agentNode', position: { x: 80, y: 260 }, data: { agent: 'researcher', label: 'Researcher', icon: '🔍', description: '信息检索与收集', status: 'idle' } },
  { id: 'analyst', type: 'agentNode', position: { x: 340, y: 260 }, data: { agent: 'analyst', label: 'Analyst', icon: '📊', description: '数据推理与分析', status: 'idle' } },
  { id: 'coder', type: 'agentNode', position: { x: 600, y: 260 }, data: { agent: 'coder', label: 'Coder', icon: '💻', description: '代码生成与执行', status: 'idle' } },
  { id: 'summarizer', type: 'agentNode', position: { x: 400, y: 480 }, data: { agent: 'summarizer', label: 'Summarizer', icon: '📝', description: '结果总结与输出', status: 'idle' } },
];

const defaultEdges: Edge[] = [
  { id: 'e-sup-res', source: 'supervisor', target: 'researcher', animated: false, style: { stroke: '#3b82f6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' } },
  { id: 'e-sup-ana', source: 'supervisor', target: 'analyst', animated: false, style: { stroke: '#06b6d4', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#06b6d4' } },
  { id: 'e-sup-cod', source: 'supervisor', target: 'coder', animated: false, style: { stroke: '#10b981', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' } },
  { id: 'e-res-sum', source: 'researcher', target: 'summarizer', animated: false, style: { stroke: '#f59e0b', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#f59e0b' } },
  { id: 'e-ana-sum', source: 'analyst', target: 'summarizer', animated: false, style: { stroke: '#f59e0b', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#f59e0b' } },
  { id: 'e-cod-sum', source: 'coder', target: 'summarizer', animated: false, style: { stroke: '#f59e0b', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#f59e0b' } },
];

function FlowCanvas({ agentStatuses }: { agentStatuses: Record<string, { status: AgentNodeData['status']; progress?: string }> }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(defaultNodes);
  const [edges, , onEdgesChange] = useEdgesState(defaultEdges);

  useEffect(() => {
    setNodes((nds) =>
      nds.map((n) => {
        const s = agentStatuses[n.id];
        if (s) {
          return { ...n, data: { ...n.data, status: s.status, progress: s.progress } };
        }
        return n;
      })
    );
  }, [agentStatuses, setNodes]);

  useEffect(() => {
    setEdges((eds) =>
      eds.map((e) => {
        const srcActive = agentStatuses[e.source]?.status === 'processing';
        const tgtActive = agentStatuses[e.target]?.status === 'processing';
        return {
          ...e,
          animated: srcActive || tgtActive,
        };
      })
    );
  }, [agentStatuses, setEdges]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      nodeTypes={nodeTypes}
      fitView
      proOptions={{ hideAttribution: true }}
      style={{ background: 'transparent' }}
    >
      <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="rgba(255,255,255,0.03)" />
      <Controls />
      <MiniMap
        nodeColor={(n) => agentColors[n.data?.agent as AgentRole] || '#666'}
        style={{ background: '#12122a', border: '1px solid rgba(255,255,255,0.08)' }}
        maskColor="rgba(0,0,0,0.5)"
      />
    </ReactFlow>
  );
}

function ChatPanel({ messages, onSend, isLoading }: { messages: ChatMessage[]; onSend: (msg: string) => void; isLoading: boolean }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = () => {
    if (!input.trim() || isLoading) return;
    onSend(input.trim());
    setInput('');
  };

  return (
    <div
      style={{
        width: 380,
        borderLeft: '1px solid rgba(255,255,255,0.06)',
        background: 'rgba(10,10,26,0.8)',
        backdropFilter: 'blur(20px)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <div style={{ padding: '14px 16px', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600, fontSize: 14 }}>
        对话
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#555', marginTop: 60, fontSize: 13, lineHeight: 1.8 }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>💬</div>
            输入任务，多 Agent 协作处理
          </div>
        )}
        {messages.map((m) => (
          <div key={m.id} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div
              style={{
                maxWidth: '85%',
                padding: '10px 14px',
                borderRadius: 12,
                fontSize: 13,
                lineHeight: 1.7,
                background: m.role === 'user' ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.05)',
                color: m.role === 'user' ? '#fff' : '#d0d0e0',
                border: m.role === 'user' ? 'none' : '1px solid rgba(255,255,255,0.08)',
                whiteSpace: 'pre-wrap',
              }}
            >
              {m.agent && (
                <div style={{ fontSize: 11, color: agentColors[m.agent as AgentRole] || '#888', marginBottom: 4, fontWeight: 500 }}>
                  {agentIcons[m.agent as AgentRole]} {m.agent}
                </div>
              )}
              {m.content}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div style={{ padding: 12, borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSubmit()}
            placeholder="输入任务描述..."
            disabled={isLoading}
            style={{
              flex: 1,
              padding: '10px 14px',
              borderRadius: 10,
              border: '1px solid rgba(255,255,255,0.1)',
              background: 'rgba(255,255,255,0.03)',
              color: '#fff',
              fontSize: 13,
              outline: 'none',
            }}
          />
          <button
            onClick={handleSubmit}
            disabled={isLoading || !input.trim()}
            style={{
              padding: '10px 18px',
              borderRadius: 10,
              background: isLoading ? '#555' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              color: '#fff',
              border: 'none',
              fontSize: 13,
              fontWeight: 500,
              cursor: isLoading ? 'not-allowed' : 'pointer',
              whiteSpace: 'nowrap',
            }}
          >
            {isLoading ? '处理中...' : '发送'}
          </button>
        </div>
      </div>
    </div>
  );
}

const agentsList = [
  { id: 'supervisor', name: 'Supervisor', icon: '🧠', desc: '任务路由与调度', color: '#8b5cf6' },
  { id: 'researcher', name: 'Researcher', icon: '🔍', desc: '信息检索与收集', color: '#3b82f6' },
  { id: 'analyst', name: 'Analyst', icon: '📊', desc: '数据推理与分析', color: '#06b6d4' },
  { id: 'coder', name: 'Coder', icon: '💻', desc: '代码生成与执行', color: '#10b981' },
  { id: 'summarizer', name: 'Summarizer', icon: '📝', desc: '结果总结与输出', color: '#f59e0b' },
];

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [agentStatuses, setAgentStatuses] = useState<Record<string, { status: AgentNodeData['status']; progress?: string }>>({});
  const [activeView, setActiveView] = useState<'workflow' | 'chat'>('workflow');
  const msgIdRef = useRef(0);

  const updateAgent = useCallback((id: string, status: AgentNodeData['status'], progress?: string) => {
    setAgentStatuses((prev) => ({ ...prev, [id]: { status, progress } }));
  }, []);

  const resetAgents = useCallback(() => {
    const idle: Record<string, { status: AgentNodeData['status'] }> = {};
    agentsList.forEach((a) => { idle[a.id] = { status: 'idle' }; });
    idle.supervisor = { status: 'online' };
    setAgentStatuses(idle);
  }, []);

  useEffect(() => { resetAgents(); }, [resetAgents]);

  const handleSend = async (text: string) => {
    const userMsg: ChatMessage = { id: ++msgIdRef.current, role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    resetAgents();
    updateAgent('supervisor', 'thinking', '分析任务中...');

    let assistantContent = '';
    let currentAgent = 'supervisor';

    try {
      const res = await fetch('/api/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, stream: true }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const reader = res.body?.getReader();
      if (!reader) throw new Error('No reader');
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const jsonStr = line.slice(6);
          try {
            const event = JSON.parse(jsonStr);
            switch (event.type) {
              case 'plan':
                updateAgent('supervisor', 'processing', '已制定路由计划');
                break;
              case 'step_start': {
                const aid = event.data.agent_id;
                updateAgent(aid, 'processing', event.data.task.slice(0, 40));
                if (aid !== currentAgent) {
                  currentAgent = aid;
                }
                break;
              }
              case 'step_chunk': {
                const aid = event.data.agent_id;
                assistantContent += event.data.chunk;
                setMessages((prev) => {
                  const last = prev[prev.length - 1];
                  if (last && last.role === 'assistant' && last.agent === aid) {
                    return [...prev.slice(0, -1), { ...last, content: assistantContent }];
                  }
                  return [...prev, { id: ++msgIdRef.current, role: 'assistant', agent: aid, content: assistantContent }];
                });
                break;
              }
              case 'step_complete':
                updateAgent(event.data.agent_id, 'online', '完成');
                break;
              case 'step_error':
                updateAgent(event.data.agent_id, 'idle', '出错');
                break;
              case 'results':
                break;
              case 'done':
                break;
            }
          } catch {}
        }
      }
    } catch (err: any) {
      assistantContent = `请求失败: ${err.message}`;
    }

    if (!assistantContent) {
      setMessages((prev) => [...prev, { id: ++msgIdRef.current, role: 'assistant', content: '（无响应）' }]);
    }
    setIsLoading(false);
    setTimeout(resetAgents, 2000);
  };

  const agentStatusForSidebar = (id: string) => {
    const s = agentStatuses[id];
    if (!s) return 'idle';
    return s.status === 'processing' || s.status === 'thinking' ? 'processing' : 'idle';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <header
        style={{
          height: 56,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
          background: 'rgba(10,10,26,0.8)',
          backdropFilter: 'blur(20px)',
          zIndex: 100,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, fontWeight: 700, color: '#fff' }}>A</div>
          <span style={{ fontWeight: 600, fontSize: 16, letterSpacing: '-0.02em', color: '#fff' }}>AI Multi-Agent Engine</span>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          {(['workflow', 'chat'] as const).map((v) => (
            <button
              key={v}
              onClick={() => setActiveView(v)}
              style={{
                padding: '6px 16px',
                borderRadius: 8,
                background: activeView === v ? 'rgba(99,102,241,0.2)' : 'transparent',
                border: activeView === v ? '1px solid rgba(99,102,241,0.3)' : '1px solid transparent',
                color: activeView === v ? '#a5b4fc' : '#888',
                fontSize: 13,
                cursor: 'pointer',
              }}
            >
              {v === 'workflow' ? '工作流' : '对话'}
            </button>
          ))}
        </div>
        <div style={{ width: 120 }} />
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <aside
          style={{
            width: 240,
            borderRight: '1px solid rgba(255,255,255,0.06)',
            background: 'rgba(10,10,26,0.6)',
            backdropFilter: 'blur(20px)',
            padding: 16,
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
            overflowY: 'auto',
          }}
        >
          <div style={{ fontSize: 11, fontWeight: 600, color: '#555', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4 }}>Agent 列表</div>
          {agentsList.map((a) => {
            const st = agentStatusForSidebar(a.id);
            return (
              <div key={a.id} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', borderRadius: 10, background: st === 'processing' ? `${a.color}11` : 'transparent', border: `1px solid ${st === 'processing' ? a.color + '33' : 'transparent'}` }}>
                <div style={{ width: 34, height: 34, borderRadius: 8, background: `linear-gradient(135deg, ${a.color}22, ${a.color}08)`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, flexShrink: 0 }}>{a.icon}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 500, fontSize: 13 }}>{a.name}</div>
                  <div style={{ color: '#777', fontSize: 11 }}>{a.desc}</div>
                </div>
                <div style={{ width: 7, height: 7, borderRadius: '50%', background: st === 'processing' ? a.color : '#555', boxShadow: st === 'processing' ? `0 0 8px ${a.color}` : 'none', animation: st === 'processing' ? 'pulse 1s ease-in-out infinite' : undefined, flexShrink: 0 }} />
              </div>
            );
          })}
          <div style={{ marginTop: 'auto', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: 12, fontSize: 11, color: '#555' }}>
            Powered by Anthropic Claude
          </div>
        </aside>

        {activeView === 'workflow' ? (
          <main style={{ flex: 1, position: 'relative' }}>
            <ReactFlowProvider>
              <FlowCanvas agentStatuses={agentStatuses} />
            </ReactFlowProvider>
            <div style={{ position: 'absolute', bottom: 16, left: 16, padding: 12, borderRadius: 10, background: 'rgba(18,18,42,0.9)', backdropFilter: 'blur(20px)', border: '1px solid rgba(255,255,255,0.08)', maxWidth: 300, fontSize: 12, color: '#888', lineHeight: 1.6 }}>
              <div style={{ fontWeight: 600, color: '#ccc', marginBottom: 6, fontSize: 13 }}>工作流说明</div>
              Supervisor 分析任务并路由给 Researcher / Analyst / Coder，最终由 Summarizer 汇总输出。
            </div>
          </main>
        ) : (
          <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <ChatPanel messages={messages} onSend={handleSend} isLoading={isLoading} />
          </main>
        )}
      </div>
    </div>
  );
}
