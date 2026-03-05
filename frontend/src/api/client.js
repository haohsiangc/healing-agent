import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
    baseURL: API_BASE,
    timeout: 60000,
});

// Attach JWT
client.interceptors.request.use((config) => {
    const token = localStorage.getItem('healing_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

// Handle 401
client.interceptors.response.use(
    (res) => res,
    (err) => {
        if (err.response?.status === 401) {
            localStorage.removeItem('healing_token');
            localStorage.removeItem('healing_user');
            window.location.href = '/login';
        }
        return Promise.reject(err);
    }
);

export default client;

// --- Auth ---
export const authAPI = {
    register: (data) => client.post('/api/auth/register', data).then(r => r.data),
    login: (data) => client.post('/api/auth/login', data).then(r => r.data),
};

// --- Chat ---
export const chatAPI = {
    sendMessage: (data) => client.post('/api/chat/message', data).then(r => r.data),
    imageReflection: (data) => client.post('/api/chat/image-reflection', data).then(r => r.data),
    listConversations: () => client.get('/api/chat/conversations').then(r => r.data),
    getHistory: (id) => client.get(`/api/chat/history/${id}`).then(r => r.data),
};

// --- Image ---
export const imageAPI = {
    generate: (data) => client.post('/api/image/generate', data).then(r => r.data),
};

// --- Meditation ---
export const meditationAPI = {
    audioUrl: () => `${API_BASE}/api/meditation/audio`,
};
