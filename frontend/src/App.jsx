import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Upload, Play, Send, Square, FileText, Key } from 'lucide-react';
import './style.css';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8020';

function App() {
  const [apiKey, setApiKey] = useState('');
  const [llmModel, setLlmModel] = useState('gpt-4.1-mini');
  const [resumeText, setResumeText] = useState('');
  const [jdText, setJdText] = useState('');
  const [role, setRole] = useState('DevOps Engineer');
  const [duration, setDuration] = useState(30);
  const [difficulty, setDifficulty] = useState('mid');
  const [sessionId, setSessionId] = useState(null);
  const [profile, setProfile] = useState(null);
  const [plan, setPlan] = useState(null);
  const [messages, setMessages] = useState([]);
  const [answer, setAnswer] = useState('');
  const [report, setReport] = useState('');
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  function getHeaders(contentType = null) {
    const headers = {};
    if (apiKey) headers['x-openai-api-key'] = apiKey;
    if (llmModel) headers['x-llm-model'] = llmModel;
    if (contentType) headers['Content-Type'] = contentType;
    return headers;
  }

  async function uploadResume(file) {
    setError('');
    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/resume/upload`, {
        method: 'POST',
        headers: getHeaders(),
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Resume upload failed');
      setResumeText(data.resume_text);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function startInterview() {
    setError('');
    setLoading(true);
    setReport('');
    setEvaluations([]);
    try {
      const res = await fetch(`${API_BASE}/interview/start`, {
        method: 'POST',
        headers: getHeaders('application/json'),
        body: JSON.stringify({
          resume_text: resumeText,
          job_description: jdText,
          role,
          duration_minutes: Number(duration),
          difficulty,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Could not start interview');
      setSessionId(data.session_id);
      setProfile(data.profile);
      setPlan(data.interview_plan);
      setMessages([{ from: 'interviewer', text: data.first_question }]);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function submitAnswer() {
    if (!answer.trim()) return;
    const currentAnswer = answer;
    setAnswer('');
    setMessages(prev => [...prev, { from: 'candidate', text: currentAnswer }]);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/interview/answer`, {
        method: 'POST',
        headers: getHeaders('application/json'),
        body: JSON.stringify({ session_id: sessionId, answer: currentAnswer }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Could not submit answer');
      setMessages(prev => [...prev, { from: 'interviewer', text: data.next_question }]);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function endInterview() {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/interview/end/${sessionId}`, {
        method: 'POST',
        headers: getHeaders(),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Could not end interview');
      setReport(data.report);
      setEvaluations(data.evaluations || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Mock Interview Agent</h1>
        <p>Resume-aware, JD-aware mock interviews for computer science roles.</p>
      </header>

      {error && <div className="error">{error}</div>}
      {loading && <div className="loading">Working...</div>}

      <main className="grid">
        <section className="card setup">
          <h2><FileText size={20}/> Setup</h2>

          <div className="api-settings">
            <label><Key size={14}/> OpenAI API Key</label>
            <input
              type="password"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
              placeholder="sk-..."
            />
            <label>LLM Model</label>
            <select value={llmModel} onChange={e => setLlmModel(e.target.value)}>
              <option value="gpt-4.1-mini">GPT-4.1 Mini</option>
              <option value="gpt-4.1">GPT-4.1</option>
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4o-mini">GPT-4o Mini</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            </select>
            {!apiKey && <small className="warning">⚠️ No API key — mock responses will be used.</small>}
          </div>

          <hr />

          <label>Role</label>
          <input value={role} onChange={e => setRole(e.target.value)} />

          <div className="row">
            <div>
              <label>Duration</label>
              <select value={duration} onChange={e => setDuration(e.target.value)}>
                <option value={30}>30 minutes</option>
                <option value={60}>60 minutes</option>
              </select>
            </div>
            <div>
              <label>Difficulty</label>
              <select value={difficulty} onChange={e => setDifficulty(e.target.value)}>
                <option value="junior">Junior</option>
                <option value="mid">Mid</option>
                <option value="senior">Senior</option>
              </select>
            </div>
          </div>

          <label>Upload Resume PDF</label>
          <input type="file" accept="application/pdf" onChange={e => e.target.files?.[0] && uploadResume(e.target.files[0])} />
          <small>{resumeText ? `Resume loaded: ${resumeText.length} characters` : 'PDF only for this MVP.'}</small>

          <label>Or paste resume text</label>
          <textarea value={resumeText} onChange={e => setResumeText(e.target.value)} placeholder="Paste resume text here..." />

          <label>Job Description / Company Requirement</label>
          <textarea value={jdText} onChange={e => setJdText(e.target.value)} placeholder="Paste job description here..." />

          <button onClick={startInterview} disabled={loading || resumeText.length < 20 || jdText.length < 20}>
            <Play size={16}/> Start Interview
          </button>
        </section>

        <section className="card interview">
          <h2>Interview</h2>
          <div className="chat">
            {messages.length === 0 && <p className="muted">Start an interview to see questions here.</p>}
            {messages.map((m, idx) => (
              <div key={idx} className={`message ${m.from}`}>
                <strong>{m.from === 'interviewer' ? 'Interviewer' : 'You'}</strong>
                <p>{m.text}</p>
              </div>
            ))}
          </div>
          {sessionId && !report && (
            <div className="answerBox">
              <textarea value={answer} onChange={e => setAnswer(e.target.value)} placeholder="Type your answer..." />
              <div className="buttonRow">
                <button onClick={submitAnswer} disabled={loading || !answer.trim()}><Send size={16}/> Submit Answer</button>
                <button className="secondary" onClick={endInterview} disabled={loading}><Square size={16}/> End Interview</button>
              </div>
            </div>
          )}
        </section>

        <section className="card details">
          <h2>Plan & Report</h2>
          {profile && <details open><summary>Candidate Profile</summary><pre>{JSON.stringify(profile, null, 2)}</pre></details>}
          {plan && <details open><summary>Interview Plan</summary><pre>{JSON.stringify(plan, null, 2)}</pre></details>}
          {report && <div className="report"><h3>Final Report</h3><pre>{report}</pre></div>}
          {evaluations.length > 0 && <details><summary>Question Evaluations</summary><pre>{JSON.stringify(evaluations, null, 2)}</pre></details>}
        </section>
      </main>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
