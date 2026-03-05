import './MeditationModal.css';

export default function MeditationModal({ onAccept, onDecline }) {
    return (
        <div className="modal-overlay animate-fade-in" role="dialog" aria-modal="true">
            <div className="modal-card glass animate-fade-in">
                {/* Ripple decoration */}
                <div className="modal-ripple" aria-hidden>
                    <div className="ripple-ring" />
                    <div className="ripple-ring delay-1" />
                    <div className="ripple-ring delay-2" />
                    <span className="ripple-icon">🧘</span>
                </div>

                <h3>需要一些放鬆嗎？</h3>
                <p>
                    我注意到你目前的狀態，想邀請你進行一個短暫的呼吸放鬆練習。
                    這只需要幾分鐘，可以幫助你恢復平靜。
                </p>

                <div className="modal-actions">
                    <button className="btn btn-primary" onClick={onAccept}>
                        好，我想試試看
                    </button>
                    <button className="btn btn-ghost" onClick={onDecline}>
                        我想再多分享一點
                    </button>
                </div>
            </div>
        </div>
    );
}
