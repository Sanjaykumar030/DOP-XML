import React, { useState, useEffect, useRef } from 'react';

// --- CONSTANTS ---
const DOPAMINE_FACTORS = [ 'No Dominant Factor', 'Repetitive Music/Audio', 'Catchy/Melodic Music', 'Element of Surprise', 'On-screen Positive Feedback', 'Game-like Progression', 'Familiar Characters', 'Distinctive Sound Effects', 'Engaging Narrative', 'Visual Effects', 'Unique Animation Style', 'Creative Elements' ];
const DOMINANT_COLORS = [ 'No Dominant Color', 'Multi Colors', 'Blue', 'Pink', 'White', 'Violet', 'Peach', 'Green', 'Red', 'Yellow', 'Orange', 'Brown', 'Black', 'Grey', 'Purple' ];
const VIDEO_CATEGORIES = [ 'Advertisement', 'Country Vlog', 'Documentary', 'Education', 'Entertainment', 'Food Vlog', 'Gaming', 'Informative', 'Inspirational', 'Motivational', 'Music', 'Nature', 'Nursery Rhymes', 'Short Story', 'Shots', 'Tourism', 'Travel Vlog', 'Vlog' ];

// --- STYLES ---
const GlobalStyles = () => (
  <style>{`
    :root { /* ... existing root variables ... */ --accent-color-start: #6a11cb; --accent-color-end: #2575fc; --gradient: linear-gradient(45deg, var(--accent-color-start) 0%, var(--accent-color-end) 100%); --gradient-high: linear-gradient(45deg, #00F260 0%, #0575E6 100%); --gradient-medium: linear-gradient(45deg, #F2994A 0%, #F2C94C 100%); --gradient-low: linear-gradient(45deg, #ED213A 0%, #93291E 100%); }
    .user-mode { --background-color: #000000; --text-color: #f5f5f7; --subtle-text-color: #a1a1a6; --border-color: #222222; --card-background: #1a1a1a; }
    .advanced-mode { --background-color: #f5f5f7; --text-color: #1d1d1f; --subtle-text-color: #515154; --border-color: #d2d2d7; --card-background: #ffffff; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; background-color: var(--background-color); color: var(--text-color); transition: background-color 0.5s ease, color 0.5s ease; overflow-x: hidden; }
    main { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }
    .fade-in-section { opacity: 0; transform: translateY(40px); transition: opacity 0.8s cubic-bezier(0.165, 0.84, 0.44, 1), transform 0.8s cubic-bezier(0.165, 0.84, 0.44, 1); will-change: opacity, transform; }
    .fade-in-section.is-visible { opacity: 1; transform: translateY(0); }
    .cta-button { background-image: var(--gradient); color: white; font-size: 1rem; font-weight: 600; border: none; padding: 14px 28px; border-radius: 980px; cursor: pointer; transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease; text-decoration: none; display: inline-block; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); }
    .cta-button:hover { transform: scale(1.08); box-shadow: 0 10px 25px rgba(0, 122, 255, 0.3); }
    .cta-button:disabled { opacity: 0.6; cursor: not-allowed; transform: scale(1); }
    h1, h2 { font-weight: 700; letter-spacing: -0.04em; }
    p { color: var(--subtle-text-color); line-height: 1.7; max-width: 650px; }
    
    .login-container { display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 100vh; padding: 2rem; }
    .login-card { max-width: 420px; width: 100%; margin: 0 auto; padding: 2.5rem; background: var(--card-background); border: 1px solid var(--border-color); border-radius: 24px; text-align: center; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15); }
    .login-card h2 { font-size: 2rem; margin-bottom: 1.5rem; } .login-card form { display: flex; flex-direction: column; gap: 1rem; } .login-card input { width: 100%; padding: 14px 20px; font-size: 1rem; background: var(--background-color); border: 1px solid var(--border-color); border-radius: 12px; color: var(--text-color); transition: border-color 0.3s, box-shadow 0.3s; } .login-card input:focus { outline: none; border-color: var(--accent-color-end); box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent-color-end) 20%, transparent); } .login-card .error { color: #ff4d4d; margin-top: 1rem; font-size: 0.9rem; text-align: left; }
    .header { position: sticky; top: 0; width: 100%; padding: 1rem 5%; background-color: color-mix(in srgb, var(--background-color) 70%, transparent); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); z-index: 1000; border-bottom: 1px solid var(--border-color); }
    .header-content { display: flex; justify-content: space-between; align-items: center; max-width: 1400px; margin: 0 auto; }
    .logo { font-size: 1.5rem; font-weight: 800; color: var(--text-color); text-decoration: none; }
    .header-controls { display: flex; align-items: center; gap: 1rem; }
    .mode-switcher { background-color: var(--card-background); border: 1px solid var(--border-color); padding: 5px; border-radius: 980px; display: grid; grid-template-columns: 1fr 1fr; position: relative; } .mode-switcher-btn { background: transparent; border: none; color: var(--subtle-text-color); padding: 8px 12px; border-radius: 980px; cursor: pointer; font-weight: 600; z-index: 2; transition: color 0.3s ease; white-space: nowrap; display: flex; align-items: center; justify-content: center; gap: 0.5rem; } .mode-switcher-btn.active { color: white; } .advanced-mode .mode-switcher-btn.active { color: black; } .mode-switcher-backdrop { position: absolute; top: 5px; left: 5px; bottom: 5px; width: calc(50% - 5px); background-image: var(--gradient); border-radius: 980px; z-index: 1; transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1); }
    .logout-button { background: var(--card-background); border: 1px solid var(--border-color); color: var(--subtle-text-color); padding: 8px 16px; border-radius: 980px; cursor: pointer; font-weight: 600; transition: all 0.2s ease; }
    .logout-button:hover { border-color: var(--accent-color-end); color: var(--text-color); }
    .hero-section { min-height: 80vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 8rem 20px 7rem 20px; } .hero-title { font-size: clamp(3.2rem, 10vw, 6.5rem); margin-bottom: 0.5rem; } .user-mode .hero-title { background: linear-gradient(90deg, #fff, #999, #fff); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shine 8s linear infinite; } @keyframes shine { to { background-position: 200% center; } } .hero-subtitle { font-size: clamp(1.2rem, 4vw, 1.8rem); margin-bottom: 2.5rem; font-weight: 500; max-width: 700px; }
    .analyzer-section { background: var(--card-background); border: 1px solid var(--border-color); border-radius: 32px; padding: 3rem 4rem 4rem 4rem; text-align: center; margin: -80px auto 100px auto; max-width: 800px; position: relative; z-index: 10; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); min-height: 350px; display: flex; flex-direction: column; justify-content: center; } .advanced-mode .analyzer-section { box-shadow: 0 25px 50px -12px rgba(0,0,0,0.1); } .analyzer-section h2 { font-size: clamp(2rem, 5vw, 2.5rem); margin-bottom: 1rem; } .analyzer-form { display: flex; gap: 1rem; max-width: 600px; margin: 2rem auto 0 auto; } .analyzer-input { width: 100%; padding: 14px 20px; font-size: 1rem; background: var(--background-color); border: 1px solid var(--border-color); border-radius: 12px; color: var(--text-color); transition: border-color 0.3s, box-shadow 0.3s; } .analyzer-input:focus { outline: none; border-color: var(--accent-color-end); box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent-color-end) 20%, transparent); } .analyzer-button { padding: 14px 28px; flex-shrink: 0; } .error-message { color: #ff4d4d; margin-top: 1rem; } .video-info-card { background: var(--background-color); padding: 1.5rem; border-radius: 16px; text-align: left; margin-bottom: 2rem; border: 1px solid var(--border-color); } .video-info-card h3 { font-size: 1.2rem; margin-bottom: 0.5rem; } .video-info-card p { margin: 0; font-size: 0.9rem; } .manual-input-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; text-align: left; margin-top: 2rem; } .manual-input-grid .full-width { grid-column: 1 / -1; } .form-group label { display: block; font-weight: 500; margin-bottom: 0.5rem; font-size: 0.9rem; } .form-group select, .form-group input { width: 100%; padding: 10px 14px; font-size: 1rem; background: var(--background-color); border: 1px solid var(--border-color); border-radius: 12px; color: var(--text-color); } .prediction-result-card { padding: 2rem; border-radius: 16px; } .prediction-result-card h3 { font-size: 1.5rem; margin-bottom: 1rem; } .score-display { font-size: 5rem; font-weight: 800; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; } .score-label { font-weight: 600; font-size: 1.2rem; margin-top: 0.5rem; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; } .probabilities { margin-top: 2rem; display: flex; justify-content: center; gap: 2rem; text-align: center; } .probability-item p { margin: 0; font-size: 1.2rem; font-weight: 600; color: var(--text-color); } .probability-item span { font-size: 0.9rem; color: var(--subtle-text-color); }
    .footer { text-align: center; padding: 4rem 2rem 2rem; border-top: 1px solid var(--border-color); margin-top: 100px; } .footer-logo { font-size: 1.8rem; font-weight: 800; margin-bottom: 1rem; } .footer-copyright { color: #555; font-size: 0.9rem; } .user-mode .footer-copyright { color: #444; }
    @media (max-width: 640px) { .analyzer-form { flex-direction: column; } .analyzer-section { padding: 2.5rem 1.5rem; } .manual-input-grid { grid-template-columns: 1fr; } .header-controls { gap: 0.5rem; } .logout-button { padding: 8px 10px; } }
    
    /* --- CHATBOT STYLES --- */
    .chatbot-fab { position: fixed; bottom: 2rem; right: 2rem; background-image: var(--gradient); color: white; width: 60px; height: 60px; border-radius: 50%; border: none; cursor: pointer; display: flex; justify-content: center; align-items: center; box-shadow: 0 8px 20px rgba(0,0,0,0.3); z-index: 1001; transition: transform 0.3s ease, box-shadow 0.3s ease; }
    .chatbot-fab:hover { transform: scale(1.1); box-shadow: 0 12px 30px rgba(0,0,0,0.25); }
    .chatbot-fab-icon { font-size: 28px; transition: transform 0.4s ease; }
    .chatbot-fab.is-open .chatbot-fab-icon { transform: rotate(180deg) scale(0); }
    .chatbot-fab.is-open .chatbot-close-icon { transform: rotate(0) scale(1); }
    .chatbot-close-icon { position: absolute; font-size: 28px; transform: scale(0); transition: transform 0.4s ease; }
    .chat-window { position: fixed; bottom: calc(2rem + 75px); right: 2rem; width: 90vw; max-width: 400px; height: 70vh; max-height: 600px; background: var(--card-background); border: 1px solid var(--border-color); border-radius: 24px; box-shadow: 0 15px 35px rgba(0,0,0,0.2); z-index: 1000; display: flex; flex-direction: column; overflow: hidden; transform-origin: bottom right; transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1), opacity 0.4s ease; }
    .chat-window.is-closed { transform: scale(0); opacity: 0; pointer-events: none; }
    .chat-header { padding: 1rem 1.5rem; border-bottom: 1px solid var(--border-color); background: var(--background-color); }
    .chat-header h3 { font-size: 1.2rem; margin: 0; }
    .chat-header p { font-size: 0.85rem; margin: 0; color: var(--subtle-text-color); }
    .chat-messages { flex-grow: 1; padding: 1.5rem; overflow-y: auto; display: flex; flex-direction: column; gap: 1rem; }
    .message-bubble { max-width: 80%; padding: 0.75rem 1rem; border-radius: 18px; line-height: 1.5; word-wrap: break-word; }
    .message-bubble.user { background-image: var(--gradient); color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
    .message-bubble.bot { background: var(--background-color); color: var(--text-color); border: 1px solid var(--border-color); align-self: flex-start; border-bottom-left-radius: 4px; }
    .message-bubble.bot.loading::after { content: '▋'; display: inline-block; animation: blink 1s infinite; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } 100% { opacity: 1; } }
    .chat-input-form { display: flex; padding: 1rem; border-top: 1px solid var(--border-color); gap: 0.5rem; }
    .chat-input { flex-grow: 1; background: var(--background-color); border: 1px solid var(--border-color); border-radius: 12px; padding: 0.75rem 1rem; font-size: 1rem; color: var(--text-color); transition: border-color 0.3s, box-shadow 0.3s; }
    .chat-input:focus { outline: none; border-color: var(--accent-color-end); box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent-color-end) 15%, transparent); }
    .chat-send-btn { background: transparent; border: none; color: var(--accent-color-end); cursor: pointer; padding: 0.5rem; font-size: 1.5rem; display: flex; align-items: center; justify-content: center; }
    .chat-send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
  `}</style>
);

// --- CHATBOT COMPONENT ---
const Chatbot = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([ { role: 'bot', content: 'Hi there! I can answer questions about this website or the concept of dopamine in content. How can I help?' } ]);
    const [userInput, setUserInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });

    useEffect(() => { scrollToBottom(); }, [messages]);
    useEffect(() => { if (isOpen) inputRef.current?.focus(); }, [isOpen]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        const trimmedInput = userInput.trim();
        if (!trimmedInput || isLoading) return;

        const newUserMessage = { role: 'user', content: trimmedInput };
        setMessages(prev => [...prev, newUserMessage, { role: 'bot', content: '' }]);
        setUserInput('');
        setIsLoading(true);

        try {
            const response = await fetch("http://127.0.0.1:5000/chat", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: trimmedInput }),
            });

            if (!response.body) throw new Error("Response has no body");
            const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
            
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const lines = value.split('\n\n').filter(line => line.trim());
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const jsonStr = line.substring(6);
                        const parsed = JSON.parse(jsonStr);
                        if (parsed.content) {
                            setMessages(prev => {
                                const lastMessage = prev[prev.length - 1];
                                const updatedLastMessage = { ...lastMessage, content: lastMessage.content + parsed.content };
                                return [...prev.slice(0, -1), updatedLastMessage];
                            });
                        }
                        if (parsed.error) throw new Error(parsed.error);
                    }
                }
            }
        } catch (err) {
            console.error("Chatbot error:", err);
            setMessages(prev => {
                const lastMessage = prev[prev.length - 1];
                const updatedLastMessage = { ...lastMessage, content: `Sorry, I ran into an error. Please try again.` };
                return [...prev.slice(0, -1), updatedLastMessage];
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            <div className={`chat-window ${isOpen ? 'is-open' : 'is-closed'}`}>
                <div className="chat-header">
                    <h3>Dopamine AI Assistant</h3>
                    <p>Powered by DeepSeek</p>
                </div>
                <div className="chat-messages">
                    {messages.map((msg, index) => (
                        <div key={index} className={`message-bubble ${msg.role} ${isLoading && index === messages.length - 1 ? 'loading' : ''}`}>
                            {msg.content}
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>
                <form className="chat-input-form" onSubmit={handleSendMessage}>
                    <input ref={inputRef} type="text" className="chat-input" placeholder="Ask a question..." value={userInput} onChange={(e) => setUserInput(e.target.value)} disabled={isLoading} />
                    <button type="submit" className="chat-send-btn" disabled={isLoading || !userInput.trim()}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
                    </button>
                </form>
            </div>
            <button className={`chatbot-fab ${isOpen ? 'is-open' : ''}`} onClick={() => setIsOpen(!isOpen)} aria-label="Toggle Chatbot">
                <span className="chatbot-fab-icon">💬</span>
                <span className="chatbot-close-icon">✖️</span>
            </button>
        </>
    );
};

// --- CHILD COMPONENTS ---
const Login = ({ onLogin }) => {
    const [email, setEmail] = useState(''); const [otp, setOtp] = useState(''); const [step, setStep] = useState(1); const [isLoading, setIsLoading] = useState(false); const [error, setError] = useState('');
    const BACKEND_URL = "http://127.0.0.1:5000";

    const handleEmailSubmit = async (e) => { e.preventDefault(); setIsLoading(true); setError(''); try { const response = await fetch(`${BACKEND_URL}/send-otp`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email }) }); const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Failed to send OTP.'); setStep(2); } catch (err) { setError(err.message); } finally { setIsLoading(false); } };
    const handleOtpSubmit = async (e) => { e.preventDefault(); setIsLoading(true); setError(''); try { const response = await fetch(`${BACKEND_URL}/verify-otp`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, otp }) }); const data = await response.json(); if (!response.ok) throw new Error(data.error || 'OTP verification failed.'); onLogin(); } catch (err) { setError(err.message); setOtp(''); setStep(1); } finally { setIsLoading(false); } };
    return ( <div className="login-container"> <div className="login-card"> <h2>Welcome</h2> {error && <p className="error">{error}</p>} {step === 1 ? ( <form onSubmit={handleEmailSubmit}> <p style={{marginBottom: '1.5rem'}}>Enter your email to receive a one-time password.</p> <input type="email" placeholder="e.g., your-email@gmail.com" value={email} onChange={(e) => setEmail(e.target.value)} required /> <button type="submit" className="cta-button" disabled={isLoading}>{isLoading ? 'Sending...' : 'Send OTP'}</button> </form> ) : ( <form onSubmit={handleOtpSubmit}> <p style={{marginBottom: '1.5rem'}}>We've sent an OTP to {email}.</p> <input type="text" placeholder="Enter OTP" value={otp} onChange={(e) => setOtp(e.target.value)} required /> <button type="submit" className="cta-button" disabled={isLoading}>{isLoading ? 'Verifying...' : 'Login'}</button> </form> )} </div> </div> );
};
const Header = ({ mode, setMode, onLogout }) => { const isUser = mode === 'user'; return ( <header className="header"> <div className="header-content"> <a href="#hero" className="logo">DopamineExp</a> <div className="header-controls"> <div className="mode-switcher"> <div className="mode-switcher-backdrop" style={{ transform: `translateX(${isUser ? '0%' : '100%'})` }}/> <button onClick={() => setMode('user')} className={`mode-switcher-btn ${isUser ? 'active' : ''}`}>👤 User</button> <button onClick={() => setMode('advanced')} className={`mode-switcher-btn ${!isUser ? 'active' : ''}`}>⚙️ Advanced</button> </div> <button onClick={onLogout} className="logout-button">Logout</button> </div> </div> </header> ); };
const UrlInputStep = ({ url, setUrl, handleUrlSubmit, isLoading }) => ( <> <h2>Get Your Dopamine Score</h2> <p>Paste any YouTube URL to analyze its potential for engagement.</p> <form className="analyzer-form" onSubmit={handleUrlSubmit}> <input type="url" className="analyzer-input" placeholder="https://www.youtube.com/watch?v=..." value={url} onChange={(e) => setUrl(e.target.value)} required /> <button type="submit" className="cta-button analyzer-button" disabled={isLoading}> {isLoading ? 'Analyzing...' : 'Analyze URL'} </button> </form> </> );
const DetailsStep = ({ apiData, manualInputs, handleManualInputChange, handlePredictionSubmit, isLoading }) => ( <> <h2>Step 2: Provide Additional Details</h2> <div className="video-info-card"> <h3>{apiData.video_title}</h3> <p>by {apiData.channel_name}</p> </div> <form onSubmit={handlePredictionSubmit}> <div className="manual-input-grid"> <div className="form-group"> <label htmlFor="freq_cut_per_video">Frequent Cuts (0 or 1)</label> <input type="number" id="freq_cut_per_video" name="freq_cut_per_video" min="0" max="1" value={manualInputs.freq_cut_per_video} onChange={handleManualInputChange} /> </div> <div className="form-group"> <label htmlFor="is_for_kids">Is For Kids (0 or 1)</label> <input type="number" id="is_for_kids" name="is_for_kids" min="0" max="1" value={manualInputs.is_for_kids} onChange={handleManualInputChange} /> </div> <div className="form-group full-width"> <label htmlFor="key_dopamine_factor">Key Dopamine Factor</label> <select id="key_dopamine_factor" name="key_dopamine_factor" value={manualInputs.key_dopamine_factor} onChange={handleManualInputChange}> {DOPAMINE_FACTORS.map(factor => <option key={factor}>{factor}</option>)} </select> </div> <div className="form-group"> <label htmlFor="dominant_color">Dominant Color</label> <select id="dominant_color" name="dominant_color" value={manualInputs.dominant_color} onChange={handleManualInputChange}> {DOMINANT_COLORS.map(color => <option key={color}>{color}</option>)} </select> </div> <div className="form-group"> <label htmlFor="video_category">Video Category</label> <select id="video_category" name="video_category" value={manualInputs.video_category} onChange={handleManualInputChange}> {VIDEO_CATEGORIES.map(category => <option key={category} value={category}>{category}</option>)} </select> </div> </div> <button type="submit" className="cta-button" style={{marginTop: '2rem'}} disabled={isLoading}> {isLoading ? 'Calculating...' : 'Get Score'} </button> </form> </> );
const ResultStep = ({ prediction, handleReset }) => ( <div className="prediction-result-card"> <h3>Prediction Result</h3> <div className="score-label" style={{ background: 'var(--gradient)', fontSize: '1.5rem', marginBottom: '1rem', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}> {prediction.final_label} </div> <div className="probabilities"> <div className="probability-item"> <p style={{background: 'var(--gradient-low)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>{(prediction.probability_low * 100).toFixed(2)}%</p> <span>Low Dopamine</span> </div> <div className="probability-item"> <p style={{background: 'var(--gradient-high)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>{(prediction.probability_high * 100).toFixed(2)}%</p> <span>High Dopamine</span> </div> </div> <button onClick={handleReset} className="cta-button" style={{marginTop: '2rem', background: 'var(--card-background)', border: '1px solid var(--border-color)', color: 'var(--text-color)'}}> Analyze Another </button> </div> );
const DopamineAnalyzer = () => { const BACKEND_URL = "http://127.0.0.1:5000"; const [step, setStep] = useState(1); const [url, setUrl] = useState(''); const [isLoading, setIsLoading] = useState(false); const [error, setError] = useState(''); const [apiData, setApiData] = useState(null); const [manualInputs, setManualInputs] = useState({ freq_cut_per_video: '0', dominant_color: 'No Dominant Color', video_category: 'Advertisement', is_for_kids: '0', key_dopamine_factor: 'No Dominant Factor', }); const [prediction, setPrediction] = useState(null); const handleUrlSubmit = async (e) => { e.preventDefault(); if (!url) return; setIsLoading(true); setError(''); setPrediction(null); try { const response = await fetch(`${BACKEND_URL}/analyze-url`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url }) }); const data = await response.json(); if (!response.ok) { throw new Error(data.error || 'Failed to analyze URL.'); } setApiData(data); setStep(2); } catch (err) { setError(err.message); } finally { setIsLoading(false); } }; const handlePredictionSubmit = async (e) => { e.preventDefault(); setIsLoading(true); setError(''); const payload = { ...apiData, ...manualInputs }; try { const response = await fetch(`${BACKEND_URL}/predict`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }); const data = await response.json(); if (!response.ok) { throw new Error(data.error || 'Prediction failed.'); } setPrediction(data); setStep(3); } catch (err) { setError(err.message); } finally { setIsLoading(false); } }; const handleManualInputChange = (e) => { const { name, value } = e.target; setManualInputs(prev => ({...prev, [name]: value})); }; const handleReset = () => { setStep(1); setUrl(''); setError(''); setApiData(null); setPrediction(null); }; const renderStep = () => { switch (step) { case 2: return <DetailsStep apiData={apiData} manualInputs={manualInputs} handleManualInputChange={handleManualInputChange} handlePredictionSubmit={handlePredictionSubmit} isLoading={isLoading} />; case 3: return <ResultStep prediction={prediction} handleReset={handleReset} />; default: return <UrlInputStep url={url} setUrl={setUrl} handleUrlSubmit={handleUrlSubmit} isLoading={isLoading} />; } }; return ( <section id="analyzer" className="analyzer-section fade-in-section"> {renderStep()} {error && <p className="error-message">{error}</p>} </section> ); };
const AppContent = () => ( <> <section id="hero" className="hero-section fade-in-section"> <h1 className="hero-title">Unlock Your Content's Potential.</h1> <p className="hero-subtitle">Instantly analyze any piece of content to understand its engagement score and optimize for maximum impact.</p> <a href="#analyzer" className="cta-button">Start Analyzing</a> </section> <DopamineAnalyzer /> </> );
const Footer = () => ( <footer className="footer"> <div className="footer-logo">DopamineExp</div> <p className="footer-copyright">Copyright © 2025 Dopamine Experience. All rights reserved.</p> </footer> );


// --- MAIN APP COMPONENT ---
function App() {
  const [mode, setMode] = useState('user');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => setIsLoggedIn(true);
  const handleLogout = () => setIsLoggedIn(false); // <-- LOGOUT HANDLER

  useEffect(() => { document.body.className = `${mode}-mode`; }, [mode]);
  useEffect(() => {
    if (!isLoggedIn) return;
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('is-visible'); });
    }, { threshold: 0.1 });
    const sections = document.querySelectorAll('.fade-in-section');
    sections.forEach(section => observer.observe(section));
    return () => sections.forEach(section => { if(section) observer.unobserve(section) });
  }, [isLoggedIn]);

  return (
    <>
      <GlobalStyles />
      <div className="App">
        {isLoggedIn ? (
            <>
                <Header mode={mode} setMode={setMode} onLogout={handleLogout} /> {/* <-- PASS LOGOUT HANDLER */}
                <main> <AppContent /> </main>
                <Footer />
                <Chatbot />
            </>
        ) : ( <Login onLogin={handleLogin} /> )}
      </div>
    </>
  );
}

export default App;

