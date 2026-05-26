import axios, { AxiosResponse } from 'axios';
import { useUserStore } from '@/store';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  // 允许处理 204 No Content 状态码
  validateStatus: (status) => {
    return (status >= 200 && status < 300) || status === 204;
  },
});

// 获取 token 的统一函数
const getToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  
  // 优先从 Zustand store 读取
  try {
    const storeToken = useUserStore.getState().token;
    if (storeToken) {
      return storeToken;
    }
  } catch (e) {
    // Zustand store 可能还未初始化
  }
  
  // 降级到 localStorage
  return localStorage.getItem('auth-token');
};

// 请求拦截器 - 添加 Token
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 清除无效的 token
      localStorage.removeItem('auth-token');
      try {
        useUserStore.getState().logout();
      } catch (e) {
        // store 可能还未初始化
      }
      // 只有不在登录页时才跳转
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// 认证 API
export const authApi = {
  register: (data: { username: string; password: string; email?: string }) =>
    api.post('/api/auth/register', data),
  
  login: (data: { username: string; password: string }) =>
    api.post('/api/auth/login', data),
  
  getCurrentUser: () =>
    api.get('/api/auth/me'),
  
  updateProfile: (data: any) =>
    api.put('/api/auth/me', data),
};

// 天气 API
export const weatherApi = {
  getWeather: (city: string) =>
    api.get('/api/weather', { params: { city } }),
  
  getForecast: (city: string, days?: number) =>
    api.get('/api/weather/forecast', { params: { city, days } }),
  
  getHourly: (city: string, hours?: number) =>
    api.get('/api/weather/hourly', { params: { city, hours } }),
  
  getAQI: (aqi: number) =>
    api.get('/api/weather/aqi', { params: { aqi } }),
  
  // 优化：支持传入天气参数避免后端重复请求
  getDressingAdvice: (params: string | {
    city: string;
    temperature?: number;
    humidity?: number;
    weather_type?: string;
    wind_speed?: number;
    uv_index?: number;
  }) => {
    const requestParams = typeof params === 'string' 
      ? { city: params }
      : params;
    return api.get('/api/weather/advice', { params: requestParams });
  },
};

// 衣服 API
export const clothesApi = {
  getList: (params?: {
    page?: number;
    page_size?: number;
    type?: string;
    color?: string;
    season?: string;
    style?: string;
  }) => api.get('/api/clothes', { params }),
  
  add: (data: any) => api.post('/api/clothes', data),
  
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/clothes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  getDetail: (id: number) => api.get(`/api/clothes/${id}`),
  
  update: (id: number, data: any) => api.put(`/api/clothes/${id}`, data),
  
  delete: (id: number) => api.delete(`/api/clothes/${id}`),
  
  analyze: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/clothes/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// AI 推荐 API
export const aiApi = {
  getRecommendation: (data: {
    city?: string;
    temperature?: number;
    weather?: string;
    scene?: string;
    style_preference?: string;
  }) => api.post('/api/ai/recommend', data),
  
  getTodayRecommendation: (city?: string, scene?: string) =>
    api.get('/api/ai/recommend/today', { params: { city, scene } }),
  
  getScenes: () => api.get('/api/ai/recommend/scenes'),
  
  getStyles: () => api.get('/api/ai/recommend/styles'),
};

// 聊天 API
export const chatApi = {
  sendMessage: (data: { message: string; context?: any }) =>
    api.post('/api/chat', data),
  
  getHistory: (limit?: number) =>
    api.get('/api/chat/history', { params: { limit } }),
  
  clearHistory: () => api.delete('/api/chat/history'),
  
  getSuggestions: () => api.get('/api/chat/suggestions'),
};

// 个人中心 API
export const profileApi = {
  // 获取用户统计
  getStats: () => api.get('/api/profile/stats'),
  
  // 获取收藏列表
  getFavorites: (page = 1, pageSize = 20) =>
    api.get('/api/profile/favorites', { params: { page, page_size: pageSize } }),
  
  // 添加收藏
  addFavorite: (outfitId: number) =>
    api.post(`/api/profile/favorites/${outfitId}`),
  
  // 取消收藏
  removeFavorite: (outfitId: number) =>
    api.delete(`/api/profile/favorites/${outfitId}`),
  
  // 快速收藏（用于推荐）
  quickFavorite: (outfitData: any) =>
    api.post('/api/profile/quick-favorite', outfitData),
  
  // 获取衣服详情（用于穿搭卡片展示）
  getClothesDetail: (clothesId: number) =>
    api.get(`/api/profile/favorite-clothes/${clothesId}`),
};

// 独立收藏 API（修复 422 问题）
export const favoritesApi = {
  // 添加收藏
  add: (data: {
    outfit_id: string;
    outfit_data: any;
    weather?: string;
    scene?: string;
    temperature?: number;
  }) => api.post('/api/favorites', data),
  
  // 获取收藏列表
  getList: (page = 1, pageSize = 20) =>
    api.get('/api/favorites', { params: { page, page_size: pageSize } }),
  
  // 取消收藏
  remove: (outfitId: string) =>
    api.delete(`/api/favorites/${outfitId}`),
  
  // 检查是否已收藏
  check: (outfitId: string) =>
    api.get(`/api/favorites/check/${outfitId}`),
  
  // 获取收藏数量
  getCount: () =>
    api.get('/api/favorites/stats/count'),
};
