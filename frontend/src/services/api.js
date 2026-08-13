import axios from 'axios';

// ─────────────────────────────────────────────────────────────────────────────
// When running in Docker: VITE_API_BASE_URL should be EMPTY ("").
//   → All requests become relative (/api/..., /ready, /health)
//   → Nginx proxies them to the backend container.
//
// When running locally (npm run dev): VITE_API_BASE_URL = http://localhost:8000
//   → Vite dev-server proxy OR direct call to local backend.
// ─────────────────────────────────────────────────────────────────────────────
const BASE_ORIGIN = import.meta.env.VITE_API_BASE_URL || '';

const api = axios.create({
  baseURL: BASE_ORIGIN + '/api',
  headers: { 'Content-Type': 'application/json' },
});

const systemApi = axios.create({
  baseURL: BASE_ORIGIN,
  headers: { 'Content-Type': 'application/json' },
});

// Products
export const getProducts       = ()         => api.get('/products/');
export const getProduct        = (id)       => api.get(`/products/${id}`);
export const createProduct     = (data)     => api.post('/products/', data);
export const updateProduct     = (id, data) => api.put(`/products/${id}`, data);
export const deleteProduct     = (id)       => api.delete(`/products/${id}`);
export const getCategories     = ()         => api.get('/products/categories/all');
export const getProductSales   = (id)       => api.get(`/products/${id}/sales`);

// Orders
export const getOrders         = ()         => api.get('/orders/');
export const createOrder       = (data)     => api.post('/orders/', data);

// Events
export const getProductEvents  = (id)       => api.get(`/products/${id}/events`);

// Health – proxied via Nginx (no /api prefix)
export const getHealth         = ()         => systemApi.get('/health');
export const getReadiness      = ()         => systemApi.get('/ready');

export default api;
