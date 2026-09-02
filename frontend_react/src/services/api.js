// Import base URL from env
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// ==========================================
// SECURE TOKEN MANAGEMENT
// ==========================================
const TOKEN_KEY = 'omni_access_token';
const REFRESH_TOKEN_KEY = 'omni_refresh_token';

export const getAccessToken = () => sessionStorage.getItem(TOKEN_KEY);
export const getRefreshToken = () => sessionStorage.getItem(REFRESH_TOKEN_KEY);

export const setTokens = (accessToken, refreshToken) => {
  sessionStorage.setItem(TOKEN_KEY, accessToken);
  sessionStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
};

export const clearTokens = () => {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(REFRESH_TOKEN_KEY);
};

// ==========================================
// CORE FETCH WRAPPER (Enterprise Ready)
// ==========================================
const apiFetch = async (endpoint, options = {}) => {
  const token = getAccessToken();
  const isFormData = options.body instanceof FormData; // For file uploads
  const isUrlEncoded = options.body instanceof URLSearchParams; // For login form

  const headers = {
    'Accept': 'application/json',
    ...options.headers,
  };

  // JWT Token add karein (agar exists karta hai)
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // FormData ya URLEncoded ke liye Content-Type set NAHI karte
  if (!isFormData && !isUrlEncoded && options.body) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    // Body ko handle karein (FormData, URLEncoded, ya JSON)
    body: isFormData ? options.body : (isUrlEncoded ? options.body : (options.body ? JSON.stringify(options.body) : undefined)),
  });

  // Handle 401 (Token Expired) -> Try Refresh
  if (response.status === 401 && token && !endpoint.includes('/auth/refresh')) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      return apiFetch(endpoint, options);
    } else {
      clearTokens();
      window.location.href = '/login'; // Redirect to login
      throw new Error('Session expired. Please login again.');
    }
  }

  // Handle other errors
  if (!response.ok) {
    let errorDetail = 'Something went wrong';
    try {
      const data = await response.json();
      errorDetail = data.detail || data.message || errorDetail;
      
      // 🔥 FIX: Agar errorDetail array hai (FastAPI validation errors), toh usko readable string banao
      if (Array.isArray(errorDetail)) {
        errorDetail = errorDetail.map(err => err.msg).join(', ');
      }
    } catch (e) {
      // ignore parse error
    }
    throw new Error(errorDetail);
  }

  return response.json();
};

// Refresh Token Logic (Auto-Rotation)
const refreshAccessToken = async () => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) return false;

    const data = await response.json();
    setTokens(data.access_token, data.refresh_token);
    return true;
  } catch (error) {
    return false;
  }
};

// ==========================================
// AUTHENTICATION API
// ==========================================
export const AuthAPI = {
  login: (email, password) => apiFetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    // OAuth2PasswordRequestForm expects URL encoded data
    body: new URLSearchParams({ username: email, password: password })
  }),
  register: (email, password, full_name) => apiFetch('/api/v1/auth/register', {
    method: 'POST',
    body: { email, password, full_name }
  }),
};

export const SettingsAPI = {
  getIntegrations: () => apiFetch('/api/v1/settings/integrations'),
  
  connectVectorDB: (provider, credentials) => apiFetch('/api/v1/settings/vector-db', {
    method: 'POST',
    body: { provider, credentials }
  }),

  connectDataSource: (type, credentials) => apiFetch('/api/v1/settings/data-source', {
    method: 'POST',
    body: { type, credentials }
  }),

  selectVectorDB: (provider, collection_name) => apiFetch('/api/v1/settings/vector-db/select', {
    method: 'POST',
    body: { provider, collection_name }
  }),

  // 🔥 NAYA FUNCTION: Delete Integration
  deleteIntegration: (provider) => apiFetch(`/api/v1/settings/integration/${provider}`, {
    method: 'DELETE'
  }),
};

// ==========================================
// VISUAL SEARCH API (Public Widget) - Uses API Key
// ==========================================
export const VisualAPI = {
  // Admin/Private - uses JWT
  triggerSync: () => apiFetch('/api/v1/visual/sync', { method: 'POST' }),
  getJobStatus: (jobId) => apiFetch(`/api/v1/visual/jobs/${jobId}`),
  
  // Public/Widget - uses x-api-key header
  searchByImage: (apiKey, file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiFetch('/api/v1/visual/search', {
      method: 'POST',
      headers: { 'x-api-key': apiKey }, // API Key header
      body: formData,
    });
  },
};

// ==========================================
// INGESTION API (Jobs History)
// ==========================================
export const IngestionAPI = {
  getJobs: () => apiFetch('/api/v1/ingestion/jobs'),
  getJobStatus: (jobId) => apiFetch(`/api/v1/ingestion/jobs/${jobId}`),
};

// ==========================================
// FILE UPLOAD API (CSV / JSON)
// ==========================================
export const FileAPI = {
  // Step 1: File upload karke headers/keys return karta hai
  previewFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiFetch('/api/v1/visual/file/preview', {
      method: 'POST',
      body: formData,
    });
  },

  // Step 2: Field mapping ke saath background job start karta hai
  processFile: (file, fieldMapping) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('field_mapping', JSON.stringify(fieldMapping));
    return apiFetch('/api/v1/visual/file/process', {
      method: 'POST',
      body: formData,
    });
  },
};