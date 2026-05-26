import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, Weather, Clothes, OutfitRecommendation } from '@/types';

// 用户 Store
interface UserState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  wardrobeCount: number;  // 衣橱数量
  favoritesCount: number;  // 收藏数量
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setWardrobeCount: (count: number) => void;
  setFavoritesCount: (count: number) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      wardrobeCount: 0,
      favoritesCount: 0,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setToken: (token) => set({ token }),
      setWardrobeCount: (count) => set({ wardrobeCount: count }),
      setFavoritesCount: (count) => set({ favoritesCount: count }),
      logout: () => set({ user: null, token: null, isAuthenticated: false, wardrobeCount: 0, favoritesCount: 0 }),
    }),
    {
      name: 'user-storage',
      storage: {
        getItem: (name) => {
          if (typeof window === 'undefined') return null;
          const value = localStorage.getItem(name);
          return value ? JSON.parse(value) : null;
        },
        setItem: (name, value) => {
          if (typeof window !== 'undefined') {
            localStorage.setItem(name, JSON.stringify(value));
          }
        },
        removeItem: (name) => {
          if (typeof window !== 'undefined') {
            localStorage.removeItem(name);
          }
        },
      },
    }
  )
);

// 天气 Store
interface WeatherState {
  currentCity: string;  // 当前城市
  locationId: string | null;  // LocationID
  currentWeather: Weather | null;
  forecast: any[];
  hourlyWeather: any[];
  loading: boolean;
  error: string | null;
  lastUpdated: number | null;  // 最后更新时间戳
  setCurrentCity: (city: string) => void;
  setLocationId: (locationId: string) => void;
  setCurrentWeather: (weather: Weather | null) => void;
  setForecast: (forecast: any[]) => void;
  setHourlyWeather: (hourly: any[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  resetWeather: () => void;
}

export const useWeatherStore = create<WeatherState>((set) => ({
  currentCity: '',  // 不再默认北京，等定位或用户选择
  locationId: null,
  currentWeather: null,
  forecast: [],
  hourlyWeather: [],
  loading: false,
  error: null,
  lastUpdated: null,
  setCurrentCity: (city) => set({ currentCity: city, error: null }),
  setLocationId: (locationId) => set({ locationId }),
  setCurrentWeather: (weather) => set({ currentWeather: weather, lastUpdated: Date.now() }),
  setForecast: (forecast) => set({ forecast }),
  setHourlyWeather: (hourly) => set({ hourlyWeather: hourly }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  resetWeather: () => set({ 
    currentWeather: null, 
    forecast: [], 
    hourlyWeather: [],
    error: null,
    locationId: null,
    currentCity: ''
  }),
}));

// 衣橱 Store
interface WardrobeState {
  clothes: Clothes[];
  total: number;
  page: number;
  pageSize: number;
  filters: {
    type?: string;
    color?: string;
    season?: string;
    style?: string;
  };
  setClothes: (clothes: Clothes[]) => void;
  addClothes: (clothes: Clothes) => void;
  removeClothes: (id: number) => void;
  updateClothes: (id: number, data: Partial<Clothes>) => void;
  setTotal: (total: number) => void;
  setPage: (page: number) => void;
  setFilters: (filters: Partial<WardrobeState['filters']>) => void;
  resetFilters: () => void;
}

export const useWardrobeStore = create<WardrobeState>((set) => ({
  clothes: [],
  total: 0,
  page: 1,
  pageSize: 20,
  filters: {},
  setClothes: (clothes) => set({ clothes }),
  addClothes: (clothes) =>
    set((state) => ({ clothes: [clothes, ...state.clothes], total: state.total + 1 })),
  removeClothes: (id) =>
    set((state) => ({
      clothes: state.clothes.filter((c) => c.id !== id),
      total: state.total - 1,
    })),
  updateClothes: (id, data) =>
    set((state) => ({
      clothes: state.clothes.map((c) => (c.id === id ? { ...c, ...data } : c)),
    })),
  setTotal: (total) => set({ total }),
  setPage: (page) => set({ page }),
  setFilters: (filters) =>
    set((state) => ({ filters: { ...state.filters, ...filters }, page: 1 })),
  resetFilters: () => set({ filters: {}, page: 1 }),
}));

// 推荐 Store
interface RecommendationState {
  todayRecommendation: OutfitRecommendation | null;
  recommendations: OutfitRecommendation[];
  scenes: any[];
  styles: any[];
  selectedScene: string;
  selectedStyle: string;
  setTodayRecommendation: (rec: OutfitRecommendation | null) => void;
  setScenes: (scenes: any[]) => void;
  setStyles: (styles: any[]) => void;
  setSelectedScene: (scene: string) => void;
  setSelectedStyle: (style: string) => void;
}

export const useRecommendationStore = create<RecommendationState>((set) => ({
  todayRecommendation: null,
  recommendations: [],
  scenes: [],
  styles: [],
  selectedScene: 'daily',
  selectedStyle: 'casual',
  setTodayRecommendation: (rec) => set({ todayRecommendation: rec }),
  setScenes: (scenes) => set({ scenes }),
  setStyles: (styles) => set({ styles }),
  setSelectedScene: (scene) => set({ selectedScene: scene }),
  setSelectedStyle: (style) => set({ selectedStyle: style }),
}));

// 聊天 Store
interface ChatState {
  messages: Array<{
    id: number;
    message: string;
    response?: string;
    isUser: boolean;
  }>;
  isLoading: boolean;
  suggestions: string[];
  addMessage: (message: string, response?: string) => void;
  setMessages: (messages: any[]) => void;
  setLoading: (loading: boolean) => void;
  setSuggestions: (suggestions: string[]) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  suggestions: [],
  addMessage: (message, response) =>
    set((state) => ({
      messages: [
        ...state.messages,
        { id: Date.now(), message, response, isUser: !response },
      ],
    })),
  setMessages: (messages) =>
    set({
      messages: messages.map((m: any) => ({
        id: m.id,
        message: m.message,
        response: m.response,
        isUser: false,
      })),
    }),
  setLoading: (loading) => set({ isLoading: loading }),
  setSuggestions: (suggestions) => set({ suggestions }),
  clearMessages: () => set({ messages: [] }),
}));
