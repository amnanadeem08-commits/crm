const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

let authToken = localStorage.getItem("token");

export function setAuthToken(token) {
  authToken = token;
}

async function request(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(Array.isArray(error.detail) ? error.detail[0].msg : error.detail);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export const api = {
  register: (body) => request("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (body) => request("/auth/login", { method: "POST", body: JSON.stringify(body) }),
  categories: () => request("/products/categories"),
  createCategory: (body) => request("/products/categories", { method: "POST", body: JSON.stringify(body) }),
  products: () => request("/products"),
  createProduct: (body) => request("/products", { method: "POST", body: JSON.stringify(body) }),
  updateProduct: (id, body) => request(`/products/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  deleteProduct: (id) => request(`/products/${id}`, { method: "DELETE" }),
  stock: () => request("/inventory/stock"),
  upsertStock: (body) => request("/inventory/stock", { method: "POST", body: JSON.stringify(body) }),
  lowStock: () => request("/inventory/alerts/low-stock"),
  movements: () => request("/inventory/movements"),
  createMovement: (body) => request("/inventory/movements", { method: "POST", body: JSON.stringify(body) }),
  inventoryInsight: () => request("/ai/inventory-insight"),
  businessHealth: () => request("/ai/business-health"),
  exceptions: () => request("/ai/exceptions"),
  dailyBrief: () => request("/ai/daily-brief"),
};
