import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/useAuthStore';
import useChatStore from '../stores/useChatStore';
import { chatAPI, imageAPI } from '../api/client';
import MessageBubble from '../components/MessageBubble';
import EmotionMeter from '../components/EmotionMeter';
import ImageGallery from '../components/ImageGallery';
import MeditationModal from '../components/MeditationModal';
import ImageReflectionChat from '../components/ImageReflectionChat';
import './ChatPage.css';

export default function ChatPage() {
    const navigate = useNavigate();
    const { user, logout } = useAuthStore();
    const {
        conversations, messages, isTyping, emotionState,
        showMeditationModal, generatedImages, selectedImageIndex, showImagePanel,
        setConversations, setCurrentConversation, currentConversationId,
        addMessage, setMessages, setTyping, applyEmotionResponse,
        setGeneratedImages, setSelectedImage, dismissMeditationModal, markMeditationDone,
    } = useChatStore();

    const [input, setInput] = useState('');
    const [loadingImages, setLoadingImages] = useState(false);
    const [loadingHistory, setLoadingHistory] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    // Load conversation list on mount
    useEffect(() => {
        chatAPI.listConversations().then(setConversations).catch(() => { });
    }, []);

    const handleSend = useCallback(async () => {
        const text = input.trim();
        if (!text || isTyping) return;
        setInput('');
        setTyping(true);

        // Optimistically add user message
        addMessage({ role: 'user', content: text, created_at: new Date().toISOString() });

        try {
            const resp = await chatAPI.sendMessage({
                conversation_id: currentConversationId,
                message: text,
                conversation_turns: emotionState.conversationTurns,
                valence_history: emotionState.valenceHistory,
                arousal_history: emotionState.arousalHistory,
                meditation_done: emotionState.meditationDone,
            });

            // Add assistant reply
            addMessage({ role: 'assistant', content: resp.reply, created_at: new Date().toISOString() });
            applyEmotionResponse(resp);

            // Refresh sidebar
            chatAPI.listConversations().then(setConversations).catch(() => { });
        } catch (err) {
            addMessage({
                role: 'assistant',
                content: '抱歉，我現在無法回應，請稍後再試。',
                created_at: new Date().toISOString(),
                isError: true,
            });
        } finally {
            setTyping(false);
            inputRef.current?.focus();
        }
    }, [input, isTyping, currentConversationId, emotionState, addMessage, applyEmotionResponse, setTyping, setConversations]);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
    };

    const loadConversationHistory = useCallback(async (id) => {
        setLoadingHistory(true);
        setCurrentConversation(id);
        try {
            const history = await chatAPI.getHistory(id);
            setMessages(history);
            // Restore generated images from history
            const imgMsg = [...history].reverse().find(m => m.images?.length);
            if (imgMsg) setGeneratedImages(imgMsg.images);
        } catch (e) {
            console.error(e);
        } finally {
            setLoadingHistory(false);
        }
    }, [setCurrentConversation, setMessages, setGeneratedImages]);

    const handleNewConversation = () => {
        setCurrentConversation(null);
        setMessages([]);
        inputRef.current?.focus();
    };

    const handleGenerateImages = async () => {
        if (!currentConversationId || loadingImages) return;
        setLoadingImages(true);
        try {
            const resp = await imageAPI.generate({ conversation_id: currentConversationId });
            setGeneratedImages(resp.images);
        } catch (e) {
            console.error(e);
        } finally {
            setLoadingImages(false);
        }
    };

    const handleMeditationYes = () => {
        markMeditationDone();
        navigate('/meditation', { state: { conversationId: currentConversationId } });
    };

    return (
        <div className="chat-root">
            {/* Sidebar */}
            <aside className="sidebar glass">
                <div className="sidebar-header">
                    <div className="sidebar-logo">
                        <svg viewBox="0 0 32 32" width="28" height="28">
                            <path d="M16 4 C12 9, 6 11, 8 17 C10 23, 16 25, 16 25 C16 25, 22 23, 24 17 C26 11, 20 9, 16 4Z"
                                fill="url(#sidebarGrad)" />
                            <defs>
                                <linearGradient id="sidebarGrad" x1="6" y1="4" x2="26" y2="25">
                                    <stop offset="0%" stopColor="#fbbf24" />
                                    <stop offset="100%" stopColor="#38bdf8" />
                                </linearGradient>
                            </defs>
                        </svg>
                        <span>療癒機器人</span>
                    </div>
                    <button className="btn btn-primary btn-sm" onClick={handleNewConversation} title="新對話">
                        ＋ 新對話
                    </button>
                </div>

                <div className="sidebar-conversations">
                    {conversations.length === 0 && (
                        <div className="sidebar-empty">還沒有對話記錄</div>
                    )}
                    {conversations.map(conv => (
                        <div
                            key={conv.id}
                            className={`conv-item ${conv.id === currentConversationId ? 'active' : ''}`}
                            onClick={() => loadConversationHistory(conv.id)}
                            role="button"
                            tabIndex={0}
                        >
                            <span className="conv-title">{conv.title || '新對話'}</span>
                            <span className="conv-count">{conv.message_count} 則</span>
                        </div>
                    ))}
                </div>

                <div className="sidebar-footer">
                    <div className="user-chip">
                        <div className="user-avatar">{user?.username?.[0]?.toUpperCase()}</div>
                        <span>{user?.username}</span>
                    </div>
                    <button className="btn btn-ghost btn-sm" onClick={() => { logout(); navigate('/login'); }}>
                        登出
                    </button>
                </div>
            </aside>

            {/* Main area */}
            <main className="chat-main">
                {/* Emotion meter top bar */}
                <div className="chat-topbar glass">
                    <EmotionMeter
                        valence={emotionState.avgValence}
                        arousal={emotionState.avgArousal}
                        turns={emotionState.conversationTurns}
                    />
                    {currentConversationId && (
                        <button
                            className="btn btn-secondary btn-sm"
                            onClick={handleGenerateImages}
                            disabled={loadingImages}
                        >
                            {loadingImages ? (
                                <span className="loading-dots"><span /><span /><span /></span>
                            ) : '✦ 生成療癒圖像'}
                        </button>
                    )}
                    <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => navigate('/meditation', { state: { conversationId: currentConversationId } })}
                    >
                        🎵 放鬆練習
                    </button>
                </div>

                <div className="chat-body">
                    {/* Messages panel */}
                    <div className={`chat-messages-panel ${showImagePanel ? 'with-gallery' : ''}`}>
                        {loadingHistory ? (
                            <div className="messages-loading">
                                <div className="loading-dots"><span /><span /><span /></div>
                            </div>
                        ) : messages.length === 0 ? (
                            <div className="messages-empty animate-fade-in">
                                <div className="empty-icon">🌸</div>
                                <h3>今天想跟我分享什麼呢？</h3>
                                <p>我在這裡陪伴你，無論是喜悅、煩惱或任何感受，都可以自由分享。</p>
                            </div>
                        ) : (
                            <div className="messages-list">
                                {messages.map((msg, i) => (
                                    <MessageBubble key={msg.id || i} message={msg} />
                                ))}
                                {isTyping && (
                                    <div className="typing-indicator animate-fade-in">
                                        <div className="typing-bubble glass">
                                            <div className="loading-dots"><span /><span /><span /></div>
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>
                        )}
                    </div>

                    {/* Image gallery side panel */}
                    {showImagePanel && generatedImages.length > 0 && (
                        <div className="gallery-panel animate-slide-right">
                            <ImageGallery
                                images={generatedImages}
                                selectedIndex={selectedImageIndex}
                                onSelect={setSelectedImage}
                            />
                            {selectedImageIndex !== null && (
                                <ImageReflectionChat
                                    conversationId={currentConversationId}
                                    imageBase64={generatedImages[selectedImageIndex]}
                                />
                            )}
                        </div>
                    )}
                </div>

                {/* Input area */}
                <div className="chat-input-area glass">
                    <textarea
                        ref={inputRef}
                        className="chat-textarea"
                        placeholder="今天想要跟我分享什麼呢？（按 Enter 送出）"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        rows={1}
                        disabled={isTyping}
                    />
                    <button
                        className="btn btn-primary send-btn"
                        onClick={handleSend}
                        disabled={!input.trim() || isTyping}
                        title="送出 (Enter)"
                    >
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="22" y1="2" x2="11" y2="13" />
                            <polygon points="22 2 15 22 11 13 2 9 22 2" />
                        </svg>
                    </button>
                </div>
            </main>

            {/* Meditation suggestion modal */}
            {showMeditationModal && (
                <MeditationModal
                    onAccept={handleMeditationYes}
                    onDecline={dismissMeditationModal}
                />
            )}
        </div>
    );
}
