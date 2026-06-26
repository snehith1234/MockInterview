import React, { useState, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import { Upload, Play, Send, Square, FileText, Key, Mic, MicOff } from 'lucide-react';
import './style.css';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8020';

function App() {
  const [apiKey, setApiKey] = useState('');
  const [llmModel, setLlmModel] = useState('gpt-4.1-mini');
  const [resumeText, setResumeText] = useState('');
  const [jdText, setJdText] = useState('');
  const [role, setRole] = useState('DevOps Engineer');
  const [company, setCompany] = useState('');
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
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);
  const shouldRestartRef = useRef(false);
  const inactivityTimerRef = useRef(null);

  const INACTIVITY_TIMEOUT = 5 * 60 * 1000; // 5 minutes

  function resetInactivityTimer() {
    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current);
    }
    if (sessionId && !report) {
      inactivityTimerRef.current = setTimeout(() => {
        handleInactivityEnd();
      }, INACTIVITY_TIMEOUT);
    }
  }

  async function handleInactivityEnd() {
    if (!sessionId || report) return;
    if (isListening) stopListening();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/interview/end/${sessionId}`, {
        method: 'POST',
        headers: getHeaders(),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Could not end interview');
      setMessages(prev => [...prev, {
        from: 'interviewer',
        text: "It seems like you may have stepped away. I'll go ahead and wrap up the interview here. Thank you for your time — we'll review everything and follow up with next steps. If you have any questions, feel free to reach out via email."
      }]);
      setReport(data.report);
      setEvaluations(data.evaluations || []);
      setSessionId(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function startListening() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError('Speech recognition is not supported in your browser. Try Chrome or Edge.');
      return;
    }

    // Stop any existing instance
    if (recognitionRef.current) {
      shouldRestartRef.current = false;
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = 0; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      if (transcript) {
        setAnswer(transcript);
      }
    };

    recognition.onaudiostart = () => {
      console.log('Audio capturing started');
    };

    recognition.onspeechstart = () => {
      console.log('Speech detected');
    };

    recognition.onerror = (event) => {
      if (event.error === 'not-allowed') {
        setError('Microphone access denied. Please allow microphone permission in your browser.');
        shouldRestartRef.current = false;
        setIsListening(false);
      } else if (event.error === 'no-speech') {
        // Silence — don't show error, will auto-restart
      } else if (event.error !== 'aborted') {
        setError(`Speech error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      // Auto-restart if user hasn't clicked Stop
      if (shouldRestartRef.current) {
        setTimeout(() => {
          if (shouldRestartRef.current && recognitionRef.current) {
            try {
              recognitionRef.current.start();
            } catch (e) {
              shouldRestartRef.current = false;
              setIsListening(false);
            }
          }
        }, 100);
      } else {
        setIsListening(false);
      }
    };

    recognitionRef.current = recognition;
    shouldRestartRef.current = true;

    try {
      recognition.start();
      setIsListening(true);
      setError('');
    } catch (e) {
      setError('Could not start speech recognition. Check microphone permissions.');
      shouldRestartRef.current = false;
    }
  }

  function stopListening() {
    shouldRestartRef.current = false;
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
  }

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
          company: company || undefined,
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
      resetInactivityTimer();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function submitAnswer() {
    if (!answer.trim()) return;
    // Stop listening if active
    if (isListening) stopListening();
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
      resetInactivityTimer();

      // If interview was auto-ended by the agent
      if (data.interview_ended) {
        setReport(data.report || '');
        setEvaluations(data.evaluations || []);
        setSessionId(null);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function endInterview() {
    if (isListening) stopListening();
    if (inactivityTimerRef.current) clearTimeout(inactivityTimerRef.current);
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

  function downloadReport() {
    const content = `MOCK INTERVIEW ASSESSMENT REPORT\n${'='.repeat(40)}\nRole: ${role}\nDate: ${new Date().toLocaleDateString()}\n\n${report}\n\n${'='.repeat(40)}\nGenerated by Mock Interview Agent`;
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview-report-${role.replace(/\s+/g, '-').toLowerCase()}-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function downloadTranscript() {
    let transcript = `MOCK INTERVIEW TRANSCRIPT\n${'='.repeat(40)}\nRole: ${role}\nDate: ${new Date().toLocaleDateString()}\nDuration: ${duration} minutes\nDifficulty: ${difficulty}\n\n`;

    messages.forEach((m, i) => {
      const speaker = m.from === 'interviewer' ? 'INTERVIEWER' : 'CANDIDATE';
      transcript += `${speaker}:\n${m.text}\n\n`;
    });

    if (evaluations.length > 0) {
      transcript += `\n${'='.repeat(40)}\nQUESTION-BY-QUESTION SCORES\n${'='.repeat(40)}\n\n`;
      evaluations.forEach((ev, i) => {
        const score = ev.evaluation?.score || 'N/A';
        transcript += `Q${i + 1}: ${ev.question}\nScore: ${score}/10\nStrengths: ${(ev.evaluation?.strengths || []).join(', ')}\nWeaknesses: ${(ev.evaluation?.weaknesses || []).join(', ')}\n\n`;
      });
    }

    transcript += `\n${'='.repeat(40)}\nGenerated by Mock Interview Agent`;

    const blob = new Blob([transcript], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview-transcript-${role.replace(/\s+/g, '-').toLowerCase()}-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
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
              <option value="gpt-5.5">GPT-5.5</option>
              <option value="gpt-5.4-mini">GPT-5.4 Mini</option>
              <option value="gpt-5.4">GPT-5.4</option>
              <option value="gpt-5.4-nano">GPT-5.4 Nano</option>
              <option value="gpt-5-mini">GPT-5 Mini</option>
              <option value="gpt-5">GPT-5</option>
              <option value="gpt-4.1">GPT-4.1</option>
              <option value="gpt-4.1-mini">GPT-4.1 Mini</option>
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4o-mini">GPT-4o Mini</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            </select>
            {!apiKey && <small className="warning">⚠️ No API key — mock responses will be used.</small>}
          </div>

          <hr />

          <label>Role</label>
          <input value={role} onChange={e => setRole(e.target.value)} />

          <label>Company / Domain <small>(optional)</small></label>
          <input value={company} onChange={e => setCompany(e.target.value)} placeholder="e.g. Amazon, Banking, Healthcare..." />

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

          <label>Upload Resume (PDF or Word)</label>
          <input type="file" accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={e => e.target.files?.[0] && uploadResume(e.target.files[0])} />
          <small>{resumeText ? `Resume loaded: ${resumeText.length} characters` : 'Supports PDF and Word (.doc, .docx) files.'}</small>

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
              <textarea value={answer} onChange={e => setAnswer(e.target.value)} placeholder="Type your answer or click the mic to speak..." />
              <div className="buttonRow">
                <button
                  className={isListening ? 'mic-active' : 'mic'}
                  onClick={isListening ? stopListening : startListening}
                  title={isListening ? 'Stop recording' : 'Start voice input'}
                  type="button"
                >
                  {isListening ? <MicOff size={16}/> : <Mic size={16}/>}
                  {isListening ? ' Stop' : ' Speak'}
                </button>
                <button onClick={submitAnswer} disabled={loading || !answer.trim()}><Send size={16}/> Submit Answer</button>
                <button className="secondary" onClick={endInterview} disabled={loading}><Square size={16}/> End Interview</button>
              </div>
              {isListening && <small className="listening-indicator">🔴 Listening... Speak your answer</small>}
            </div>
          )}
        </section>

        <section className="card details">
          <h2>Plan & Report</h2>
          {profile && <details open><summary>Candidate Profile</summary><pre>{JSON.stringify(profile, null, 2)}</pre></details>}
          {plan && <details open><summary>Interview Plan</summary><pre>{JSON.stringify(plan, null, 2)}</pre></details>}
          {report && (
            <div className="report">
              <h3>Final Assessment Report</h3>
              <pre>{report}</pre>
              <div className="download-buttons">
                <button className="download-btn" onClick={downloadReport}>
                  📄 Download Report
                </button>
                <button className="download-btn" onClick={downloadTranscript}>
                  💬 Download Conversation
                </button>
              </div>
            </div>
          )}
          {evaluations.length > 0 && <details><summary>Question Evaluations</summary><pre>{JSON.stringify(evaluations, null, 2)}</pre></details>}
        </section>
      </main>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
