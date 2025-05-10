import api from "./api"; // Axios instance with token
const apiUrl = 'http://localhost:8000/api';

const resourceMap = {
    vendors: 'admin/vendor_list',
    customers: 'admin/user_list',
    orders: 'order/list',
    // Add more mappings as needed
};

const mapResource = (resource) => resourceMap[resource] || resource;

const dataProvider = {
    // GET many records: /api/resource/
    getList: async (resource, params) => {
        const url = `${apiUrl}/${mapResource(resource)}`;
        const response = await api.get(url);

        const data = response.data;

        return {
            data: Array.isArray(data.results) ? data.results : data,
            total: data.count || data.length || data.results?.length || 0,
        };
    },

    // GET one record by ID: /api/resource/:id/
    getOne: async (resource, params) => {
        const url = `${apiUrl}/${mapResource(resource)}/${params.id}/`;
        const response = await api.get(url);
        return { data: response.data };
    },

    // POST (create) one: /api/resource/
    create: async (resource, params) => {
        const url = `${apiUrl}/${mapResource(resource)}/`;
        const response = await api.post(url, params.data);
        return { data: response.data };
    },

    // PUT (update): /api/resource/:id/
    update: async (resource, params) => {
        const url = `${apiUrl}/${mapResource(resource)}/${params.id}/`;
        const response = await api.put(url, params.data);
        return { data: response.data };
    },

    // DELETE one: /api/resource/:id/
    delete: async (resource, params) => {
        const url = `${apiUrl}/${mapResource(resource)}/${params.id}/`;
        await api.delete(url);
        return { data: { id: params.id } };
    },

    // Optional: GET many by ID array
    getMany: async (resource, params) => {
        const responses = await Promise.all(
            params.ids.map((id) => api.get(`${apiUrl}/${mapResource(resource)}/${id}/`))
        );
        return {
            data: responses.map((res) => res.data),
        };
    },

    // 🔁 Optional: GET related records (reference field)
    getManyReference: async (resource, params) => {
        const url = `${apiUrl}/${mapResource(resource)}?${params.target}=${params.id}`;
        const response = await api.get(url);
        return {
            data: response.data.results || response.data,
            total: response.data.count || response.data.length || 0,
        };
    },
};

export default dataProvider;
