import { useState } from 'react';
import { chatAPI } from '../api/client';
import useChatStore from '../stores/useChatStore';
import './ImageReflectionChat.css';

export default function ImageReflectionChat({ conversationId, imageBase64 }) {
    const { addMessage } = useChatStore();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        const text = input.trim();
        if (!text || loading) return;
        setInput('');
        setLoading(true);

        addMessage({
            role: 'user',
            content: `[圖像聯想] ${text}`,
            created_at: new Date().toISOString(),
        });

        try {
            const resp = await chatAPI.imageReflection({
                conversation_id: conversationId,
                message: text,
                image_base64: imageBase64,
            });
            addMessage({
                role: 'assistant',
                content: resp.reply,
                created_at: new Date().toISOString(),
            });
        } catch {
            addMessage({
                role: 'assistant',
                content: '抱歉，無法處理圖像回應，請稍後再試。',
                isError: true,
                created_at: new Date().toISOString(),
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="img-reflection glass animate-fade-in">
            <div className="reflection-header">
                <span className="badge badge-sky">圖像聯想</span>
                <p>這張圖像讓你想到了什麼？</p>
            </div>
            <div className="reflection-preview">
                <img
                    src={`data:image/jpeg;base64,${imageBase64}`}
                    alt="選擇的圖像"
                />
            </div>
            <div className="reflection-input-row">
                <input
                    type="text"
                    className="input-field"
                    placeholder="分享你的聯想…"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSend()}
                    disabled={loading}
                />
                <button
                    className="btn btn-primary btn-icon"
                    onClick={handleSend}
                    disabled={!input.trim() || loading}
                    title="送出"
                >
                    {loading ? (
                        <div className="loading-dots" style={{ fontSize: '0.6rem' }}><span /><span /><span /></div>
                    ) : '→'}
                </button>
            </div>
        </div>
    );
}
