import './MessageBubble.css';

export default function MessageBubble({ message }) {
    const isUser = message.role === 'user';
    const isError = message.isError;
    const isImageMsg = message.content === '[已生成療癒圖像]';

    if (isImageMsg) return null; // Image messages are shown in gallery

    const time = message.created_at
        ? new Date(message.created_at).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
        : '';

    return (
        <div className={`bubble-row ${isUser ? 'user-row' : 'bot-row'} animate-fade-in`}>
            {!isUser && (
                <div className="bot-avatar">
                    <svg viewBox="0 0 32 32" width="20" height="20">
                        <path d="M16 4 C12 9, 6 11, 8 17 C10 23, 16 25, 16 25 C16 25, 22 23, 24 17 C26 11, 20 9, 16 4Z"
                            fill="url(#bubbleGrad)" />
                        <defs>
                            <linearGradient id="bubbleGrad" x1="6" y1="4" x2="26" y2="25">
                                <stop offset="0%" stopColor="#fbbf24" />
                                <stop offset="100%" stopColor="#38bdf8" />
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
            )}
            <div className="bubble-content">
                <div className={`bubble ${isUser ? 'bubble-user' : 'bubble-bot'} ${isError ? 'bubble-error' : ''}`}>
                    {message.content.split('\n').map((line, i) => (
                        <span key={i}>{line}{i < message.content.split('\n').length - 1 && <br />}</span>
                    ))}
                </div>
                <div className={`bubble-meta ${isUser ? 'meta-right' : 'meta-left'}`}>
                    {time && <span className="bubble-time">{time}</span>}
                    {message.valence !== undefined && message.valence !== null && (
                        <span className={`badge ${message.arousal > 5.5 ? 'badge-amber' : 'badge-sky'}`}>
                            V{message.valence?.toFixed(1)} A{message.arousal?.toFixed(1)}
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
