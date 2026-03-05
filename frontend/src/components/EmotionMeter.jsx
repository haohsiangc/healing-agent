import './EmotionMeter.css';

const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

export default function EmotionMeter({ valence = 5, arousal = 5, turns = 0 }) {
    // Normalize 1-9 scale to 0-100%
    const vPct = ((clamp(valence, 1, 9) - 1) / 8) * 100;
    const aPct = ((clamp(arousal, 1, 9) - 1) / 8) * 100;

    const getLabel = () => {
        if (turns < 3) return '開始對話';
        if (arousal > 6.5) return '情緒激動';
        if (arousal < 3.5) return '情緒平靜';
        if (valence < 3.5) return '情緒低落';
        if (valence > 6.5) return '情緒愉快';
        return '情緒平衡';
    };

    if (turns === 0) return null;

    return (
        <div className="emotion-meter" title={`效價 ${valence.toFixed(1)} / 激發 ${arousal.toFixed(1)}`}>
            <div className="emotion-label">{getLabel()}</div>
            <div className="emotion-bars">
                <div className="bar-track" title="效價（愉快程度）">
                    <div className="bar-fill bar-valence" style={{ width: `${vPct}%` }} />
                </div>
                <div className="bar-track" title="激發（情緒強度）">
                    <div className="bar-fill bar-arousal" style={{ width: `${aPct}%` }} />
                </div>
            </div>
            <span className="emotion-turns">{turns} 輪</span>
        </div>
    );
}
