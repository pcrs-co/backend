import axios from 'axios';
import { ACCESS_TOKEN, REFRESH_TOKEN } from './constants';

const DEFAULT_API_URL = "http://localhost:8000/api";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || DEFAULT_API_URL,
    headers: { "Content-Type": "application/json" },
});

const refreshUrl = `${import.meta.env.VITE_API_URL || DEFAULT_API_URL}/token/refresh/`;

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => Promise.reject(error));

// Handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem(REFRESH_TOKEN);
                if (!refreshToken) throw new Error('No refresh token');

                const { data } = await axios.post(refreshUrl, { refresh: refreshToken });

                localStorage.setItem(ACCESS_TOKEN, data.access);
                originalRequest.headers.Authorization = `Bearer ${data.access}`;
                return api(originalRequest);
            } catch (refreshError) {
                localStorage.removeItem(ACCESS_TOKEN);
                localStorage.removeItem(REFRESH_TOKEN);
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;