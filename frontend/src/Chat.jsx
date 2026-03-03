import React, { useState, useEffect, useRef } from 'react';
import './index.css';

function Chat() {
    // Determine the API URL from environment variables, falling back to localhost for local dev
    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

    const [documents, setDocuments] = useState([]);
    const [activeDoc, setActiveDoc] = useState("general");

    // Store chat histories mapped by document id
    const [chatHistories, setChatHistories] = useState({
        "general": [{ role: 'bot', text: 'Welcome! This is a demo chatbot operating on a mock ERP manual. If you have your own ERP module or specific manual, feel free to upload it using the button in the sidebar to get accurate, module-specific answers.' }]
    });

    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    // Current active messages
    const currentMessages = chatHistories[activeDoc] || [];

    useEffect(() => {
        fetchDocuments();
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [currentMessages, isLoading]);

    const fetchDocuments = async () => {
        try {
            const response = await fetch(`${API_URL}/documents`);
            if (response.ok) {
                const docs = await response.json();
                setDocuments(docs);

                // Initialize histories for any new docs that don't have one
                setChatHistories(prev => {
                    const newHistories = { ...prev };
                    docs.forEach(doc => {
                        if (!newHistories[doc.id]) {
                            newHistories[doc.id] = [{ role: 'bot', text: `You are now querying the module: ${doc.name}. Ask me anything about it!` }];
                        }
                    });
                    return newHistories;
                });
            }
        } catch (error) {
            console.error("Failed to fetch documents", error);
        }
    };

    const addMessage = (docId, message) => {
        setChatHistories(prev => ({
            ...prev,
            [docId]: [...(prev[docId] || []), message]
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput('');

        addMessage(activeDoc, { role: 'user', text: userMessage });
        setIsLoading(true);

        try {
            const response = await fetch(`${API_URL}/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: userMessage,
                    document_id: activeDoc
                }),
            });

            if (!response.ok) {
                let errorMsg = 'Failed to fetch response';
                try {
                    const errorData = await response.clone().json();
                    errorMsg = errorData.detail || errorMsg;
                } catch (e) { }
                throw new Error(errorMsg);
            }

            const data = await response.json();
            addMessage(activeDoc, {
                role: 'bot',
                text: data.answer,
                source: data.source
            });
        } catch (error) {
            addMessage(activeDoc, {
                role: 'bot',
                text: `Error: ${error.message || 'Server communication failed.'}`
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setIsLoading(true);
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_URL}/upload`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error("Upload failed.");

            const data = await response.json();

            // Re-fetch documents to update sidebar and initialize the new chat history
            await fetchDocuments();

            // Force the active document to switch to the new module 
            // and add a welcoming message specifically for the new manual
            const newDocId = data.document.id;
            setActiveDoc(newDocId);

            // Optionally, add a specific welcome message for the new upload to confirm the switch
            setChatHistories(prev => ({
                ...prev,
                [newDocId]: [{ role: 'bot', text: `Success! I've loaded ${data.document.name}. What would you like to know about it?` }]
            }));

        } catch (error) {
            console.error(error);
            alert(`Error uploading manual: ${error.message}`);
        } finally {
            setIsLoading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleClearData = async () => {
        if (!window.confirm("Are you sure you want to end the chat and permanently delete all your uploaded manuals?")) {
            return;
        }

        setIsLoading(true);
        try {
            const response = await fetch(`${API_URL}/clear`, { method: 'DELETE' });
            if (!response.ok) throw new Error("Failed to clear data on the server.");

            // Reset frontend state
            setActiveDoc("general");
            setChatHistories({
                "general": [{ role: 'bot', text: 'Welcome! This is a demo chatbot operating on a mock ERP manual. If you have your own ERP module or specific manual, feel free to upload it using the button in the sidebar to get accurate, module-specific answers.' }]
            });
            await fetchDocuments(); // Fetch docs again to update sidebar
            alert("Chat ended. All uploaded data has been securely deleted.");
        } catch (error) {
            console.error("Error clearing data:", error);
            alert("Error clearing data. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };


    return (
        <div className="app-layout">
            {/* Sidebar */}
            <div className="sidebar">
                <div className="sidebar-header">
                    <h2>ERP Assistant</h2>
                </div>

                <div className="module-section">
                    <h3>Knowledge Modules</h3>
                    <div className="module-list">
                        {documents.map(doc => (
                            <div
                                key={doc.id}
                                className={`module-item ${activeDoc === doc.id ? 'active' : ''}`}
                                onClick={() => setActiveDoc(doc.id)}
                            >
                                <span className="module-icon">{doc.id === 'general' ? '🗄️' : '📄'}</span>
                                <span className="module-name">{doc.name}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="sidebar-footer">
                    <input
                        type="file"
                        accept=".txt,.pdf"
                        ref={fileInputRef}
                        style={{ display: 'none' }}
                        onChange={handleFileUpload}
                    />
                    <button
                        className="upload-btn"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isLoading}
                    >
                        {isLoading ? 'Processing...' : '+ Upload New Module'}
                    </button>

                    <button
                        className="end-chat-btn"
                        onClick={handleClearData}
                        disabled={isLoading}
                    >
                        End Chat & Clear Data
                    </button>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="main-chat">
                <div className="chat-header">
                    <h2>{documents.find(d => d.id === activeDoc)?.name || "Loading..."}</h2>
                    <span className="badge">Active Module</span>
                </div>

                <div className="message-list">
                    {currentMessages.map((msg, idx) => (
                        <div key={idx} className={`message-wrapper ${msg.role}`}>
                            <div className={`message ${msg.role}`}>
                                <div className="message-content">{msg.text}</div>
                                {msg.source && (
                                    <div className="message-source">
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" /></svg>
                                        Source: {msg.source}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div className="message-wrapper bot">
                            <div className="message bot loading-msg">
                                <div className="loading">
                                    <div className="dot"></div>
                                    <div className="dot"></div>
                                    <div className="dot"></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <form className="input-box" onSubmit={handleSubmit}>
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={`Ask a question about ${documents.find(d => d.id === activeDoc)?.name || 'this module'}...`}
                        disabled={isLoading}
                    />
                    <button type="submit" disabled={isLoading || !input.trim()}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                    </button>
                </form>
            </div>
        </div>
    );
}

export default Chat;
