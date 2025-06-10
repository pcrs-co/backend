import api from './api';
import { ACCESS_TOKEN, REFRESH_TOKEN } from './constants';

const RESOURCE_MAP = {
    customers: 'api/admin/customers/',
    vendors: 'api/admin/vendors/',
    products: 'api/admin/products/',
    order: 'api/admin/order/',
    questions: 'api/admin/questions/',
    activities: 'api/admin/activities/',
    applications: 'api/admin/applications/',
    cpu_benchmarks: 'api/admin/cpu-benchmarks/',
    gpu_benchmarks: 'api/admin/gpu-benchmarks/',
};

const getEndpoint = (resource) => RESOURCE_MAP[resource] || `${resource}/`;

const saveToLocalStorage = (key, value) => localStorage.setItem(key, value);
const getFromLocalStorage = (key) => localStorage.getItem(key);
const removeFromLocalStorage = (keys) => keys.forEach(k => localStorage.removeItem(k));

const formatError = (error) => {
    const detail = error.response?.data?.detail || error.response?.data?.message;
    return new Error(detail || error.message || 'Request failed');
};

const ensureArrayData = (data) => {
    if (Array.isArray(data?.results)) return data.results;
    if (Array.isArray(data)) return data;
    return data && typeof data === 'object' ? [data] : [];
};

const isFileData = (data) => {
    return Object.values(data).some(
        value => value instanceof File || (value && typeof value === 'object' && value.uri)
    );
};

const convertToFormData = (data) => {
    const formData = new FormData();
    for (let key in data) {
        if (data[key] !== undefined && data[key] !== null) {
            formData.append(key, data[key]);
        }
    }
    return formData;
};

const dataProvider = {
    login: async ({ username, password }) => {
        try {
            const { data } = await api.post('/api/token/', { username, password });

            saveToLocalStorage(ACCESS_TOKEN, data.access);
            saveToLocalStorage(REFRESH_TOKEN, data.refresh);
            saveToLocalStorage('userRole', data.role || 'user');
            saveToLocalStorage('username', data.username || username);

            return { data };
        } catch (error) {
            throw formatError(error);
        }
    },

    logout: () => {
        removeFromLocalStorage([ACCESS_TOKEN, REFRESH_TOKEN, 'userRole', 'username']);
        return Promise.resolve({ data: { success: true } });
    },

    checkAuth: () => getFromLocalStorage(ACCESS_TOKEN) ? Promise.resolve() : Promise.reject(),

    checkError: (error) => {
        if ([401, 403].includes(error?.status)) {
            return dataProvider.logout().then(() => Promise.reject());
        }
        return Promise.resolve();
    },

    getIdentity: () => {
        try {
            const username = getFromLocalStorage('username');
            const role = getFromLocalStorage('userRole');
            return Promise.resolve({
                data: { id: username, fullName: username, avatar: null, role },
            });
        } catch (error) {
            throw formatError(error);
        }
    },

    getList: async (resource, { pagination = {}, sort = {}, filter = {} }) => {
        const { page = 1, perPage = 10 } = pagination;
        const { field = 'id', order = 'DESC' } = sort;
        const endpoint = getEndpoint(resource);

        try {
            const { data } = await api.get(endpoint, {
                params: {
                    page,
                    page_size: perPage,
                    ordering: order === 'ASC' ? field : `-${field}`,
                    ...filter,
                },
            });

            const results = ensureArrayData(data);
            const total = data.count || results.length;
            return { data: results, total };
        } catch (error) {
            throw formatError(error);
        }
    },

    getOne: async (resource, { id }) => {
        try {
            const { data } = await api.get(`${getEndpoint(resource)}${id}/`);
            return { data };
        } catch (error) {
            throw formatError(error);
        }
    },

    create: async (resource, { data }) => {
        try {
            const payload = isFileData(data) ? convertToFormData(data) : data;
            const headers = isFileData(data) ? { 'Content-Type': 'multipart/form-data' } : {};
            const res = await api.post(getEndpoint(resource), payload, { headers });
            return { data: res.data };
        } catch (error) {
            throw formatError(error);
        }
    },

    createMany: async (resource, { data }) => {
        try {
            const res = await api.post(getEndpoint(resource), data);
            return { data: res.data.map((item, i) => ({ ...item, id: item.id || i })) };
        } catch (error) {
            throw formatError(error);
        }
    },

    update: async (resource, { id, data }) => {
        try {
            const payload = isFileData(data) ? convertToFormData(data) : data;
            const headers = isFileData(data) ? { 'Content-Type': 'multipart/form-data' } : {};
            const res = await api.patch(`${getEndpoint(resource)}${id}/`, payload, { headers });
            return { data: res.data };
        } catch (error) {
            throw formatError(error);
        }
    },

    updateMany: async (resource, { ids, data }) => {
        try {
            const results = await Promise.all(
                ids.map(id =>
                    api.patch(`${getEndpoint(resource)}${id}/`, data).then(res => res.data)
                )
            );
            return { data: results.map(item => item.id) };
        } catch (error) {
            throw formatError(error);
        }
    },

    delete: async (resource, { id }) => {
        try {
            await api.delete(`${getEndpoint(resource)}${id}/`);
            return { data: { id } };
        } catch (error) {
            throw formatError(error);
        }
    },

    deleteMany: async (resource, { ids }) => {
        try {
            await Promise.all(ids.map(id => api.delete(`${getEndpoint(resource)}${id}/`)));
            return { data: ids };
        } catch (error) {
            throw formatError(error);
        }
    },
};

export default dataProvider;
