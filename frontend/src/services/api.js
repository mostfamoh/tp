import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Services d'authentification
export const authService = {
  register: async (userData) => {
    const response = await api.post('/regester/', userData);
    return response.data;
  },
  
  login: async (credentials) => {
    const response = await api.post('/login/', credentials);
    return response.data;
  },
  
  getUser: async (username) => {
    const response = await api.get(`/user/${username}/`);
    return response.data;
  },
};

// Services de protection de compte
export const protectionService = {
  toggleProtection: async (username, enabled) => {
    const response = await api.post(`/users/${username}/toggle-protection/`, { enabled });
    return response.data;
  },
  
  getProtectionStatus: async (username) => {
    const response = await api.get(`/users/${username}/protection-status/`);
    return response.data;
  },
  
  unlockAccount: async (username) => {
    const response = await api.post(`/users/${username}/unlock/`);
    return response.data;
  },
};

// Services d'attaques
export const attackService = {
  bruteforce: async (username, maxSeconds = 30, limit = 1000) => {
    const response = await api.post('/attack/full_bruteforce/', { 
      target_username: username,
      max_seconds: maxSeconds,
      limit: limit
    });
    return response.data;
  },
  
  dictionary: async (username, maxSeconds = 120, limit = 0, dictionaryType = 'digits6') => {
    const response = await api.post('/attack/full_dictionary/', { 
      target_username: username,
      max_seconds: maxSeconds,
      limit: limit,
      dictionary_type: dictionaryType
    });
    return response.data;
  },
  
  combined: async (username, maxSeconds = 30, limit = 1000) => {
    // Utiliser bruteforce comme combiné pour l'instant
    const response = await api.post('/attack/full_bruteforce/', { 
      target_username: username,
      max_seconds: maxSeconds,
      limit: limit,
      mode: 'both'
    });
    return response.data;
  },
  
  getStatistics: async () => {
    const response = await api.get('/attack/statistics/');
    return response.data;
  },
};

export default api;

