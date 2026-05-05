import React, { useState, useEffect, useRef } from 'react';
import './MissionControl.css';
import FileExplorer from './FileExplorer';

const API = 'http://127.0.0.1:8000';

const MissionControl = () => {
    const [task, setTask] = useState('');
    const [logs, setLogs] = useState([]);
    const [status, setStatus] = useState('idle');
    const [model, setModel] = useState(localStorage.getItem('oa_model') || '');
    const [availableModels, setAvailableModels] = useState([]);
    const [ollamaUrl, setOllamaUrl] = useState(localStorage.getItem('oa_url') || '');
    const [workspacePath, setWorkspacePath] = useState('./workspace');
    const [selectedFile, setSelectedFile] = useState(null);
    const [fileContent, setFileContent] = useState('');
    const [pendingAction, setPendingAction] = useState(null);
    const [history, setHistory] = useState([]);
    const [savedTask, setSavedTask] = useState('');
    const [objective, setObjective] = useState('');
    const [backendOk, setBackendOk] = useState(false);

    
    const logEndRef = useRef(null);
    const textareaRef = useRef(null);
    const abortControllerRef = useRef(null);

    // Persist settings
    useEffect(() => { localStorage.setItem('oa_model', model); }, [model]);
    useEffect(() => { localStorage.setItem('oa_url', ollamaUrl); }, [ollamaUrl]);

    useEffect(() => {
        const init = async () => {
            try {
                const r = await fetch(`${API}/`);
                if (r.ok) {
                    setBackendOk(true);
                    fetchModels();
                }
            } catch (e) {
                setBackendOk(false);
            }
        };
        init();
    }, []);

    useEffect(() => { 
        logEndRef.current?.scrollIntoView({ behavior: "smooth" }); 
    }, [logs, pendingAction]);

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 150) + 'px';
        }
    }, [task]);

    const fetchModels = async () => {
        try {
            const params = ollamaUrl ? `?ollama_url=${encodeURIComponent(ollamaUrl)}` : '';
            const r = await fetch(`${API}/api/models${params}`);
            if (r.ok) {
                const d = await r.json();
                const models = d.models || [];
                setAvailableModels(models);
                
                if (models.length > 0) {
                    // Check if remembered model still exists
                    if (!models.includes(model)) {
                        console.warn(`Model ${model} not found, falling back to ${models[0]}`);
                        setModel(models[0]);
                    }
                } else {
                    setModel('');
                }
            }
        } catch (e) { console.error(e); }
    };

    const stopTask = () => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            setStatus('idle');
            setLogs(prev => [...prev, { type: 'error', text: 'Task stopped by user.' }]);
        }
    };

    const clearSession = () => {
        setHistory([]);
        setObjective('');
        setLogs([]);
        setTask('');
        setStatus('idle');
        setPendingAction(null);
    };


    const startTask = async (customTask = null, customHistory = null) => {
        const taskToRun = customTask || task;
        if (!taskToRun) return;

        const activeHistory = customHistory || history;

        const currentObjective = objective || taskToRun;
        
        // If this is a user follow-up (not the first message and not an auto-resume)
        // Add it to history so the AI knows the plan has changed
        let updatedHistory = [...activeHistory];
        if (objective && !customTask) {
            updatedHistory.push(`User Update: ${taskToRun}`);
        }

        setStatus('running');
        setSavedTask(taskToRun);
        if (!objective) setObjective(taskToRun);
        
        // Setup abort controller
        abortControllerRef.current = new AbortController();
        
        if (!customTask) {
            setLogs(prev => [...prev, { type: 'user', text: taskToRun }]);
            setTask('');
        }



        try {
            const response = await fetch(`${API}/run-task`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task: taskToRun,
                    model,
                    ollama_url: ollamaUrl || undefined,
                    history: updatedHistory,
                    objective: currentObjective
                }),


                signal: abortControllerRef.current.signal
            });

            if (!response.body) throw new Error("No response body");
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            let currentThought = "";
            let streamIdx = -1;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                for (const line of chunk.split('\n')) {
                    if (!line.startsWith('data: ')) continue;
                    try {
                        const data = JSON.parse(line.substring(6));
                        
                        if (data.status === 'thinking') {
                            currentThought = "";
                            setLogs(prev => {
                                streamIdx = prev.length;
                                return [...prev, { type: 'thinking', text: '', isStreaming: true }];
                            });
                        } else if (data.status === 'token') {
                            currentThought += data.chunk;
                            setLogs(prev => {
                                const n = [...prev];
                                if (n[streamIdx]) n[streamIdx] = { ...n[streamIdx], text: currentThought };
                                return n;
                            });
                        } else if (data.status === 'acting') {
                            setLogs(prev => {
                                const n = [...prev];
                                if (n[streamIdx]) n[streamIdx] = { ...n[streamIdx], isStreaming: false };
                                return [...n, { type: 'action', text: '⚡ ' + data.tool }];
                            });
                        } else if (data.status === 'step_result') {
                            const short = typeof data.result === 'string' ? data.result.substring(0, 80) : String(data.result).substring(0, 80);
                            setLogs(prev => [...prev, { type: 'result', text: short }]);
                        } else if (data.status === 'pending_approval') {
                            setLogs(prev => {
                                const n = [...prev];
                                if (n[streamIdx]) n[streamIdx] = { ...n[streamIdx], isStreaming: false };
                                return n;
                            });
                            setPendingAction(data);
                            setStatus('waiting');
                        } else if (data.status === 'completed') {
                            setLogs(prev => {
                                const n = [...prev];
                                if (n[streamIdx]) n[streamIdx] = { ...n[streamIdx], isStreaming: false };
                                return [...n, { type: 'done', text: data.thought }];
                            });
                            setStatus('idle');
                            setHistory([]);
                            setObjective('');

                        } else if (data.status === 'error') {
                            setLogs(prev => [...prev, { type: 'error', text: data.message }]);
                            setStatus('error');
                        }
                    } catch (parseErr) { /* skip */ }
                }
            }
        } catch (e) {
            if (e.name === 'AbortError') return;
            setLogs(prev => [...prev, { type: 'error', text: 'Connection: ' + e.message }]);
            setStatus('error');
        }
    };

    const approveAction = async () => {
        if (!pendingAction) return;
        setStatus('running');
        try {
            const r = await fetch(API + '/api/execute-tool', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tool: pendingAction.tool, args: pendingAction.args })
            });
            const d = await r.json();
            setLogs(prev => [...prev, { type: 'result', text: '✅ ' + (pendingAction.args.file_path || 'Done') }]);
            
            const newHistory = [
                ...history,
                'Action: ' + pendingAction.tool + ' -> ' + (pendingAction.args.file_path || ''),
                'Observation: ' + d.result
            ];
            setHistory(newHistory);
            setPendingAction(null);
            startTask(savedTask, newHistory);
        } catch (e) {
            setLogs(prev => [...prev, { type: 'error', text: 'Execution failed' }]);
            setStatus('error');
        }
    };

    const isRunning = status === 'running';
    const isWaiting = status === 'waiting';

    const icon = (type) => ({ user:'\u{1F464}', thinking:'\u{1F9E0}', action:'\u26A1', result:'\u{1F4CB}', done:'\u2705', error:'\u274C' }[type] || '\u{1F4AC}');

    return (
        <div className="ide-container">
            <aside className="sidebar">
                <div className="sidebar-header">Open-Aigent</div>
                
                {!backendOk && (
                    <div className="backend-warning">
                        ⚠️ Backend Offline
                        <button onClick={() => window.location.reload()}>Retry</button>
                    </div>
                )}

                {objective && (
                    <div className="objective-display">
                        <strong>Current Goal:</strong>
                        <p>{objective}</p>
                    </div>
                )}

                <div className="config-content">

                    <label>Ollama URL</label>
                    <input 
                        value={ollamaUrl} 
                        onChange={(e) => setOllamaUrl(e.target.value)} 
                        disabled={isRunning || isWaiting} 
                        placeholder="Default: local"
                    />
                    <button onClick={fetchModels} className="btn-small" disabled={isRunning || isWaiting}>
                        🔄 Scan Models
                    </button>

                    <label>Model</label>
                    <select value={model} onChange={(e) => setModel(e.target.value)} disabled={isRunning || isWaiting || availableModels.length === 0}>
                        {availableModels.length === 0 && <option value="">Select a model</option>}
                        {availableModels.map(m => <option key={m} value={m}>{m}</option>)}
                    </select>

                    <label>Workspace</label>
                    <input value={workspacePath} onChange={(e) => setWorkspacePath(e.target.value)} disabled={isRunning || isWaiting} />
                    <button onClick={async () => {
                        await fetch(`${API}/api/workspace`, {
                            method: 'POST', headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ path: workspacePath })
                        });
                        setLogs(prev => [...prev, { type: 'result', text: '📂 Workspace updated.' }]);
                    }} className="btn-small" disabled={isRunning || isWaiting}>Set</button>

                    <button onClick={clearSession} className="btn-clear" disabled={isRunning || isWaiting}>
                        🗑️ New Task / Clear
                    </button>
                </div>

                <FileExplorer onFileSelect={async (p) => {
                    setSelectedFile(p);
                    try {
                        const r = await fetch(`${API}/api/file-content?path=${encodeURIComponent(p)}`);
                        const d = await r.json(); setFileContent(d.content);
                    } catch (e) { setFileContent("Error reading file"); }
                }} />
            </aside>

            <section className="editor-area">
                <div className="editor-header"><span>{selectedFile || 'No file selected'}</span></div>
                <div className="code-container"><pre><code>{fileContent || '// Select a file to view code'}</code></pre></div>
            </section>

            <section className="chat-area">
                <div className="logs-container">
                    {logs.map((log, i) => (
                        <div key={i} className={`chat-bubble type-${log.type}`}>
                            <span className="bubble-icon">{icon(log.type)}</span>
                            <div className="bubble-text">
                                {log.text}
                                {log.isStreaming && <span className="cursor-blink" />}
                            </div>
                        </div>
                    ))}
                    <div ref={logEndRef} />
                </div>

                {pendingAction && (
                    <div className="approval-card-fixed">
                        <div className="approval-top">
                            <span>📝</span>
                            <span className="approval-title">Action Required</span>
                        </div>
                        <div className="approval-info">
                            <p className="approval-thought">{pendingAction.thought}</p>
                            <div className="approval-tags">
                                <span className="tag tag-tool">{pendingAction.tool}</span>
                                <span className="tag tag-file">{pendingAction.args.file_path}</span>
                            </div>
                            {pendingAction.args.content && (
                                <div className="code-preview">
                                    <pre>{pendingAction.args.content.substring(0, 300)}{pendingAction.args.content.length > 300 ? '\n...' : ''}</pre>
                                </div>
                            )}
                        </div>
                        <div className="approval-buttons">
                            <button className="btn-reject" onClick={() => { setPendingAction(null); setStatus('idle'); setLogs(prev => [...prev, { type: 'error', text: 'Cancelled.' }]); }}>✕ Cancel</button>
                            <button className="btn-approve" onClick={approveAction}>✓ Approve</button>
                        </div>
                    </div>
                )}

                <div className="chat-input-area">
                    <textarea ref={textareaRef} rows="1" placeholder="Describe your task..." value={task} onChange={(e) => setTask(e.target.value)} disabled={isRunning || isWaiting}
                        onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); startTask(); } }} />
                    
                    {isRunning ? (
                        <button className="stop-btn" onClick={stopTask}>⏹️</button>
                    ) : (
                        <button className="send-btn" onClick={() => startTask()} disabled={isWaiting}>→</button>
                    )}
                </div>
            </section>
        </div>
    );
};

export default MissionControl;
