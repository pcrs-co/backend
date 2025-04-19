import { ACCESS_TOKEN } from "./constants";
import axios from "axios";

const DEFAULT_API_URL = "http://localhost:8000"; // Your local dev server
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || DEFAULT_API_URL,
    headers: {
        "Content-Type": "application/json",
    },
    withCredentials: false, // only set to true if backend supports sessions/cookies
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default api;
