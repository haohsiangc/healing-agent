import { useEffect, useRef, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { meditationAPI, imageAPI } from '../api/client';
import useChatStore from '../stores/useChatStore';
import './MeditationPage.css';

const BREATHING_CYCLE_MS = 8000; // 4s inhale + 4s exhale

export default function MeditationPage() {
    const navigate = useNavigate();
    const location = useLocation();
    const conversationId = location.state?.conversationId;

    const { setGeneratedImages, markMeditationDone } = useChatStore();
    const [phase, setPhase] = useState('loading'); // loading | playing | done
    const [breatheLabel, setBreatheLabel] = useState('準備放鬆…');
    const [progress, setProgress] = useState(0); // 0-100
    const [duration, setDuration] = useState(0);
    const [currentTime, setCurrentTime] = useState(0);
    const audioRef = useRef(null);
    const intervalRef = useRef(null);
    const genDoneRef = useRef(false);

    // Start breathing cycle animation
    const startBreathing = () => {
        let tick = 0;
        intervalRef.current = setInterval(() => {
            tick = (tick + 1) % (BREATHING_CYCLE_MS / 100);
            const half = BREATHING_CYCLE_MS / 200;
            setBreatheLabel(tick < half ? '吸氣…' : '呼氣…');
        }, 100);
    };

    useEffect(() => {
        // Generate images in background while meditating
        if (conversationId && !genDoneRef.current) {
            genDoneRef.current = true;
            imageAPI.generate({ conversation_id: conversationId })
                .then(resp => setGeneratedImages(resp.images))
                .catch(() => { });
        }

        return () => clearInterval(intervalRef.current);
    }, []);

    const handleAudioLoad = () => setPhase('playing');

    const handleTimeUpdate = (e) => {
        const audio = e.target;
        setCurrentTime(audio.currentTime);
        setDuration(audio.duration || 0);
        setProgress(audio.duration ? (audio.currentTime / audio.duration) * 100 : 0);
    };

    const handleAudioPlay = () => {
        setPhase('playing');
        startBreathing();
    };

    const handleAudioEnd = () => {
        clearInterval(intervalRef.current);
        setBreatheLabel('練習完成 🌸');
        setPhase('done');
        markMeditationDone();
    };

    const handleReturn = () => {
        clearInterval(intervalRef.current);
        navigate('/chat');
    };

    const formatTime = (sec) => {
        if (!sec || isNaN(sec)) return '0:00';
        const m = Math.floor(sec / 60);
        const s = Math.floor(sec % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    return (
        <div className="med-root">
            {/* Ambient orbs */}
            <div className="med-orb orb-1" />
            <div className="med-orb orb-2" />
            <div className="med-orb orb-3" />

            <div className="med-content animate-fade-in">
                <h2 className="med-title">放鬆呼吸練習</h2>
                <p className="med-subtitle">閉上眼睛，跟著指引慢慢呼吸</p>

                {/* Breathing circle */}
                <div className={`breathe-container ${phase === 'playing' ? 'active' : ''}`}>
                    <div className="breathe-ring ring-3" />
                    <div className="breathe-ring ring-2" />
                    <div className="breathe-ring ring-1" />
                    <div className="breathe-core">
                        <span className="breathe-label">{breatheLabel}</span>
                    </div>
                </div>

                {/* Audio element */}
                <audio
                    ref={audioRef}
                    src={meditationAPI.audioUrl()}
                    onLoadedData={handleAudioLoad}
                    onTimeUpdate={handleTimeUpdate}
                    onPlay={handleAudioPlay}
                    onEnded={handleAudioEnd}
                    preload="auto"
                />

                {/* Custom audio controls */}
                <div className="med-player glass">
                    <div className="player-times">
                        <span>{formatTime(currentTime)}</span>
                        <span>{formatTime(duration)}</span>
                    </div>
                    <div className="player-progress">
                        <div className="progress-fill" style={{ width: `${progress}%` }} />
                    </div>
                    <div className="player-controls">
                        <button
                            className="btn btn-primary"
                            onClick={() => {
                                const a = audioRef.current;
                                if (!a) return;
                                a.paused ? a.play() : a.pause();
                            }}
                        >
                            {phase === 'playing' ? '⏸ 暫停' : '▶ 播放'}
                        </button>
                    </div>
                </div>

                {phase === 'done' && (
                    <div className="med-done animate-fade-in">
                        <p>練習完成！圖像已在背景生成，返回查看你的療癒圖像。</p>
                    </div>
                )}

                <button className="btn btn-ghost med-back" onClick={handleReturn}>
                    ← 返回對話
                </button>
            </div>
        </div>
    );
}
