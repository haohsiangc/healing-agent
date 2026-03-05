import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../api/client';

const useAuthStore = create(
    persist(
        (set) => ({
            user: null,
            token: null,

            login: async (username, password) => {
                const data = await authAPI.login({ username, password });
                localStorage.setItem('healing_token', data.access_token);
                set({ user: { id: data.user_id, username: data.username }, token: data.access_token });
                return data;
            },

            register: async (username, email, password) => {
                const data = await authAPI.register({ username, email, password });
                localStorage.setItem('healing_token', data.access_token);
                set({ user: { id: data.user_id, username: data.username }, token: data.access_token });
                return data;
            },

            logout: () => {
                localStorage.removeItem('healing_token');
                localStorage.removeItem('healing_user');
                set({ user: null, token: null });
            },

            isAuthenticated: () => {
                const token = localStorage.getItem('healing_token');
                return !!token;
            },
        }),
        {
            name: 'healing_user',
            partialize: (state) => ({ user: state.user, token: state.token }),
        }
    )
);

export default useAuthStore;
