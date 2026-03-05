import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/useAuthStore';
import './LoginPage.css';

export default function LoginPage() {
    const navigate = useNavigate();
    const { login, register } = useAuthStore();
    const [tab, setTab] = useState('login'); // 'login' | 'register'
    const [form, setForm] = useState({ username: '', email: '', password: '' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            if (tab === 'login') {
                await login(form.username, form.password);
            } else {
                if (!form.email) { setError('請填寫電子郵件'); setLoading(false); return; }
                await register(form.username, form.email, form.password);
            }
            navigate('/chat');
        } catch (err) {
            setError(err.response?.data?.detail || '操作失敗，請再試一次');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-root">
            {/* Ambient particles */}
            <div className="particles" aria-hidden>
                {Array.from({ length: 18 }).map((_, i) => (
                    <div key={i} className="particle" style={{ '--i': i }} />
                ))}
            </div>

            <div className="login-card glass animate-fade-in">
                {/* Logo / Hero */}
                <div className="login-hero">
                    <div className="login-logo">
                        <svg viewBox="0 0 48 48" fill="none">
                            <circle cx="24" cy="24" r="22" stroke="#f59e0b" strokeWidth="2" strokeDasharray="4 2" />
                            <path d="M24 12 C18 18, 10 20, 12 28 C14 36, 24 38, 24 38 C24 38, 34 36, 36 28 C38 20, 30 18, 24 12Z"
                                fill="url(#heartGrad)" />
                            <defs>
                                <linearGradient id="heartGrad" x1="12" y1="12" x2="36" y2="38">
                                    <stop offset="0%" stopColor="#fbbf24" />
                                    <stop offset="100%" stopColor="#0ea5e9" />
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                    <h1>療癒對話機器人</h1>
                    <p>在這裡，你可以安心分享，找到屬於自己的平靜</p>
                </div>

                {/* Tabs */}
                <div className="login-tabs">
                    <button className={`tab ${tab === 'login' ? 'active' : ''}`} onClick={() => { setTab('login'); setError(''); }}>
                        登入
                    </button>
                    <button className={`tab ${tab === 'register' ? 'active' : ''}`} onClick={() => { setTab('register'); setError(''); }}>
                        註冊
                    </button>
                    <div className="tab-indicator" style={{ transform: `translateX(${tab === 'register' ? '100%' : '0%'})` }} />
                </div>

                {/* Form */}
                <form className="login-form" onSubmit={handleSubmit}>
                    <div className="field-group">
                        <label>用戶名稱</label>
                        <input
                            type="text"
                            name="username"
                            className="input-field"
                            placeholder="請輸入用戶名稱"
                            value={form.username}
                            onChange={handleChange}
                            required
                            autoComplete="username"
                        />
                    </div>

                    {tab === 'register' && (
                        <div className="field-group animate-fade-in">
                            <label>電子郵件</label>
                            <input
                                type="email"
                                name="email"
                                className="input-field"
                                placeholder="example@email.com"
                                value={form.email}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    )}

                    <div className="field-group">
                        <label>密碼</label>
                        <input
                            type="password"
                            name="password"
                            className="input-field"
                            placeholder={tab === 'register' ? '至少 8 個字元' : '請輸入密碼'}
                            value={form.password}
                            onChange={handleChange}
                            required
                            minLength={tab === 'register' ? 6 : undefined}
                            autoComplete={tab === 'login' ? 'current-password' : 'new-password'}
                        />
                    </div>

                    {error && <div className="login-error animate-fade-in">⚠ {error}</div>}

                    <button type="submit" className="btn btn-primary btn-lg" disabled={loading} style={{ width: '100%' }}>
                        {loading ? (
                            <span className="loading-dots"><span /><span /><span /></span>
                        ) : (
                            tab === 'login' ? '登入' : '建立帳號'
                        )}
                    </button>
                </form>

                <p className="login-footer">你的對話記錄將被安全保存</p>
            </div>
        </div>
    );
}
