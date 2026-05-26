import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useRouter } from 'next/router';
import { useUserStore, useWeatherStore, useWardrobeStore, useChatStore, useRecommendationStore } from '@/store';
import api, { authApi, weatherApi, clothesApi } from '@/services/api';
import type { User, Weather } from '@/types';

// 使用认证
export function useAuth() {
  const router = useRouter();
  const { user, token, isAuthenticated, setUser, setToken, logout } = useUserStore();
  const [loading, setLoading] = useState(true);

  // 统一存储 token 到 localStorage（供 API 拦截器使用）
  const saveToken = useCallback((newToken: string | null) => {
    if (typeof window !== 'undefined') {
      if (newToken) {
        localStorage.setItem('auth-token', newToken);
      } else {
        localStorage.removeItem('auth-token');
      }
    }
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    console.log('[useAuth] 开始登录:', username);
    try {
      const response = await authApi.login({ username, password });
      console.log('[useAuth] 登录响应:', response.data);
      
      const { access_token, user: userData } = response.data;
      
      // 更新 Zustand store（自动持久化）
      setToken(access_token);
      setUser(userData);
      
      // 同步到 localStorage（供 API 拦截器使用）
      saveToken(access_token);
      
      console.log('[useAuth] 登录成功，token:', access_token);
      return { success: true };
    } catch (error: any) {
      console.error('[useAuth] 登录失败:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || '登录失败' 
      };
    }
  }, [setToken, setUser, saveToken]);

  const register = useCallback(async (data: { username: string; password: string; email?: string }) => {
    try {
      const response = await authApi.register(data);
      return { success: true, user: response.data };
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || '注册失败' 
      };
    }
  }, []);

  const checkAuth = useCallback(async () => {
    console.log('[useAuth] 检查认证状态...');
    
    // 优先从 Zustand store 读取
    const storeToken = useUserStore.getState().token;
    const storedToken = localStorage.getItem('auth-token') || storeToken;
    
    if (!storedToken) {
      console.log('[useAuth] 没有找到 token');
      setLoading(false);
      return;
    }

    console.log('[useAuth] 找到 token，验证中...');
    
    try {
      const response = await authApi.getCurrentUser();
      console.log('[useAuth] 验证成功，用户:', response.data);
      
      // 更新 store
      setUser(response.data);
      if (!storeToken) {
        setToken(storedToken);
      }
      saveToken(storedToken);
    } catch (error: any) {
      console.error('[useAuth] 验证失败:', error);
      // 清除无效的 token
      localStorage.removeItem('auth-token');
      setUser(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  }, [setUser, setToken, saveToken]);

  const handleLogout = useCallback(() => {
    console.log('[useAuth] 登出');
    logout();
    saveToken(null);
    router.push('/login');
  }, [logout, router, saveToken]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return {
    user,
    token,
    isAuthenticated,
    loading,
    login,
    register,
    logout: handleLogout,
    checkAuth,
  };
}

// ============ 天气缓存配置 ============
const WEATHER_CACHE_TTL = 10 * 60 * 1000; // 10 分钟缓存

interface CachedWeatherData {
  weather: any;
  forecast: any[];
  hourly: any[];
  timestamp: number;
}

// 全局天气缓存（模块级别单例）
const weatherCache = new Map<string, CachedWeatherData>();

// 缓存 key 生成
function getCacheKey(city: string): string {
  return `weather_${city.trim().toLowerCase()}`;
}

// 检查缓存是否有效
function isCacheValid(cache: CachedWeatherData | undefined): boolean {
  if (!cache) return false;
  return Date.now() - cache.timestamp < WEATHER_CACHE_TTL;
}

// 深度比较两个对象是否相等
function isEqual(obj1: any, obj2: any): boolean {
  return JSON.stringify(obj1) === JSON.stringify(obj2);
}

// 使用天气 - 支持城市切换（最终稳定版）
export function useWeather(city?: string) {
  const { 
    currentWeather, 
    forecast, 
    hourlyWeather, 
    loading, 
    error,
    currentCity,
    setCurrentCity,
    setLocationId,
    setCurrentWeather, 
    setForecast, 
    setHourlyWeather, 
    setLoading,
    setError,
    resetWeather
  } = useWeatherStore();

  // 优先使用传入的 city，其次使用 store 中的 currentCity
  const effectiveCity = city || currentCity || '';

  // 用于 AbortController 的 ref
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // 加载锁，防止并发请求
  const loadingRef = useRef(false);
  
  // 初始化锁 - 确保只在首次挂载时初始化
  const initializedRef = useRef(false);
  
  // 上一次请求的城市 - 用于检测城市变化
  const lastCityRef = useRef<string>('');

  // 核心：fetchWeather 函数 - 使用稳定的引用
  const fetchWeather = useCallback(async (forceRefresh = false) => {
    const targetCity = city || currentCity || '';
    
    // 只有当城市明确有值时才请求天气
    if (!targetCity || targetCity.trim() === '') {
      console.log('[useWeather] 没有城市参数，跳过请求');
      return;
    }
    
    // 检查缓存（除非强制刷新）
    if (!forceRefresh) {
      const cacheKey = getCacheKey(targetCity);
      const cached = weatherCache.get(cacheKey);
      if (isCacheValid(cached)) {
        console.log(`[useWeather] 缓存有效，跳过请求，城市: ${targetCity}`);
        // 直接返回，不更新任何状态
        return;
      }
    }
    
    // 防止并发请求
    if (loadingRef.current) {
      console.log('[useWeather] 正在请求中，跳过重复请求');
      return;
    }
    
    // 取消之前的请求
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    
    console.log(`[useWeather] 获取天气: ${targetCity}`);
    loadingRef.current = true;
    setLoading(true);
    setError(null);
    
    try {
      const [weatherRes, forecastRes, hourlyRes] = await Promise.all([
        weatherApi.getWeather(targetCity),
        weatherApi.getForecast(targetCity, 7),
        weatherApi.getHourly(targetCity, 24),
      ]);
      
      console.log(`[useWeather] 天气数据:`, weatherRes.data);
      
      const weatherData = weatherRes.data;
      const forecastData = forecastRes.data.forecast || forecastRes.data;
      const hourlyData = hourlyRes.data.hourly || hourlyRes.data;
      
      // 只在数据真正变化时才更新 store
      if (!isEqual(currentWeather, weatherData)) {
        setCurrentWeather(weatherData);
      }
      if (!isEqual(forecast, forecastData)) {
        setForecast(forecastData);
      }
      if (!isEqual(hourlyWeather, hourlyData)) {
        setHourlyWeather(hourlyData);
      }
      
      // 更新全局缓存
      const cacheKey = getCacheKey(targetCity);
      weatherCache.set(cacheKey, {
        weather: weatherData,
        forecast: forecastData,
        hourly: hourlyData,
        timestamp: Date.now(),
      });
    } catch (err: any) {
      // 忽略被取消的请求错误
      if (err.name === 'AbortError' || err.cancelled) {
        console.log('[useWeather] 请求被取消');
        return;
      }
      console.error('[useWeather] 获取天气失败:', err);
      const errorMessage = err.response?.data?.detail || err.message || '获取天气失败';
      setError(errorMessage);
    } finally {
      loadingRef.current = false;
      setLoading(false);
    }
  }, [city, currentCity, currentWeather, forecast, hourlyWeather, setCurrentWeather, setForecast, setHourlyWeather, setLoading, setError]);

  // 初始化和城市变化处理 - 核心逻辑
  useEffect(() => {
    // 防止重复初始化
    if (initializedRef.current && lastCityRef.current === effectiveCity) {
      return;
    }
    
    if (!effectiveCity || effectiveCity.trim() === '') {
      return;
    }
    
    // 首次初始化
    if (!initializedRef.current) {
      initializedRef.current = true;
      
      // 检查缓存
      const cacheKey = getCacheKey(effectiveCity);
      const cached = weatherCache.get(cacheKey);
      
      if (isCacheValid(cached)) {
        console.log(`[useWeather] 初始化使用缓存，城市: ${effectiveCity}`);
        // 有缓存，直接用缓存更新 store（只更新一次）
        if (!isEqual(currentWeather, cached!.weather)) {
          setCurrentWeather(cached!.weather);
        }
        if (!isEqual(forecast, cached!.forecast)) {
          setForecast(cached!.forecast);
        }
        if (!isEqual(hourlyWeather, cached!.hourly)) {
          setHourlyWeather(cached!.hourly);
        }
      } else {
        // 无缓存，发起请求
        lastCityRef.current = effectiveCity;
        fetchWeather();
      }
      return;
    }
    
    // 城市变化后的处理
    if (lastCityRef.current !== effectiveCity) {
      console.log(`[useWeather] 城市变化: ${lastCityRef.current} -> ${effectiveCity}`);
      lastCityRef.current = effectiveCity;
      
      // 先检查缓存
      const cacheKey = getCacheKey(effectiveCity);
      const cached = weatherCache.get(cacheKey);
      
      if (isCacheValid(cached)) {
        console.log(`[useWeather] 城市变化使用缓存，城市: ${effectiveCity}`);
        if (!isEqual(currentWeather, cached!.weather)) {
          setCurrentWeather(cached!.weather);
        }
        if (!isEqual(forecast, cached!.forecast)) {
          setForecast(cached!.forecast);
        }
        if (!isEqual(hourlyWeather, cached!.hourly)) {
          setHourlyWeather(cached!.hourly);
        }
      } else {
        // 缓存无效，发起请求
        fetchWeather();
      }
    }
  }, [effectiveCity, currentWeather, forecast, hourlyWeather, setCurrentWeather, setForecast, setHourlyWeather, fetchWeather]);

  // 清理函数：组件卸载时取消请求
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // 强制刷新函数
  const refresh = useCallback(() => {
    // 清除当前城市的缓存
    const cacheKey = getCacheKey(effectiveCity);
    weatherCache.delete(cacheKey);
    // 重新获取
    fetchWeather(true);
  }, [effectiveCity, fetchWeather]);

  return {
    weather: currentWeather,
    forecast,
    hourlyWeather,
    loading,
    error,
    currentCity: effectiveCity,
    refresh,
    reset: resetWeather,
    clearCache: () => {
      weatherCache.clear();
    },
  };
}

// 使用衣橱
export function useWardrobe() {
  const { clothes, total, page, pageSize, filters, setClothes, addClothes, removeClothes, updateClothes, setTotal, setPage, setFilters, resetFilters } = useWardrobeStore();

  const fetchClothes = useCallback(async () => {
    console.log('[useWardrobe] 开始获取衣橱数据', { page, pageSize, filters });
    try {
      const response = await clothesApi.getList({
        page,
        page_size: pageSize,
        ...filters,
      });
      console.log('[useWardrobe] 衣橱数据返回:', {
        itemsCount: response.data.items?.length,
        total: response.data.total,
        items: response.data.items
      });
      setClothes(response.data.items);
      setTotal(response.data.total);
    } catch (error) {
      console.error('[useWardrobe] 获取衣服列表失败:', error);
    }
  }, [page, pageSize, filters, setClothes, setTotal]);

  const uploadClothes = useCallback(async (file: File) => {
    try {
      const response = await clothesApi.upload(file);
      const { image_url, analysis } = response.data;

      // 添加到数据库
      const addResponse = await clothesApi.add({
        image_url,
        name: `${analysis.color}${analysis.type}`,
        type: analysis.type,
        color: analysis.color,
        material: analysis.material,
        thickness: analysis.thickness,
        style: analysis.style,
      });

      addClothes(addResponse.data);
      return { success: true, clothes: addResponse.data };
    } catch (error) {
      console.error('上传衣服失败:', error);
      return { success: false, error: '上传失败' };
    }
  }, [addClothes]);

  // 使用已有的分析结果上传（推荐使用，确保弹窗显示与保存数据一致）
  const uploadClothesWithAnalysis = useCallback(async (file: File, analysisResult: {
    type: string;
    color: string;
    material: string;
    thickness: string;
    style: string;
    season?: string;
    formality?: number;
    gender?: string;
    temperature_min?: number;
    temperature_max?: number;
  }) => {
    try {
      // 1. 先上传图片获取 image_url
      const uploadResponse = await clothesApi.upload(file);
      const { image_url } = uploadResponse.data;

      // 2. 使用已有的分析结果保存（不重新分析，确保数据一致）
      const addResponse = await clothesApi.add({
        image_url,
        name: `${analysisResult.color}${analysisResult.type}`,
        type: analysisResult.type,
        color: analysisResult.color,
        material: analysisResult.material,
        thickness: analysisResult.thickness,
        style: analysisResult.style,
        season: analysisResult.season,
        formality: analysisResult.formality,
        gender: analysisResult.gender,
        temperature_min: analysisResult.temperature_min,
        temperature_max: analysisResult.temperature_max,
      });

      addClothes(addResponse.data);
      return { success: true, clothes: addResponse.data };
    } catch (error) {
      console.error('上传衣服失败:', error);
      return { success: false, error: '上传失败' };
    }
  }, [addClothes]);

  const deleteClothes = useCallback(async (id: number) => {
    try {
      await clothesApi.delete(id);
      removeClothes(id);
      return { success: true };
    } catch (error) {
      console.error('删除衣服失败:', error);
      return { success: false, error: '删除失败' };
    }
  }, [removeClothes]);

  const analyzeClothes = useCallback(async (file: File) => {
    try {
      const response = await clothesApi.analyze(file);
      return { success: true, analysis: response.data };
    } catch (error) {
      console.error('分析衣服失败:', error);
      return { success: false, error: '分析失败' };
    }
  }, []);

  useEffect(() => {
    fetchClothes();
  }, [fetchClothes]);

  return {
    clothes,
    total,
    page,
    pageSize,
    filters,
    setPage,
    setFilters,
    resetFilters,
    refresh: fetchClothes,
    uploadClothes,
    uploadClothesWithAnalysis,
    deleteClothes,
    analyzeClothes,
  };
}

// 使用地理位置 - 支持定位
export function useLocation() {
  const [location, setLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [city, setCity] = useState<string>(''); // 初始为空，不再默认北京
  const [loading, setLoading] = useState(false); // 初始为 false，不自动定位
  const [error, setError] = useState<string | null>(null);

  // 检查定位权限状态
  const checkPermission = useCallback(async () => {
    if (!navigator.permissions) return 'prompt'; // 旧浏览器默认 prompt
    
    try {
      const result = await navigator.permissions.query({ name: 'geolocation' });
      return result.state;
    } catch {
      return 'prompt';
    }
  }, []);

  const getLocation = useCallback(async () => {
    console.log('[useLocation] 开始获取定位...');
    
    if (!navigator.geolocation) {
      const errorMsg = '浏览器不支持地理定位功能';
      console.error('[useLocation]', errorMsg);
      setError(errorMsg);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    setCity(''); // 清空之前的结果

    // 检查权限状态
    const permission = await checkPermission();
    console.log('[useLocation] 定位权限状态:', permission);
    
    if (permission === 'denied') {
      setError('定位权限被拒绝，请在浏览器设置中开启定位权限');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        console.log('[useLocation] GPS定位成功:', { latitude, longitude });
        setLocation({ latitude, longitude });
        
        try {
          // 调用后端API通过坐标获取城市
          console.log('[useLocation] 开始解析城市，坐标:', longitude, latitude);
          const response = await api.get('/api/weather/location/by-coords', {
            params: { longitude, latitude }
          });
          
          console.log('[useLocation] 坐标转城市API返回:', response.data);
          
          if (response.data && response.data.name) {
            setCity(response.data.name);
            console.log('[useLocation] GPS定位成功，解析到城市:', response.data.name);
          } else {
            setError('无法解析定位位置为城市');
            console.warn('[useLocation] 无法解析城市');
          }
        } catch (err: any) {
          console.error('[useLocation] 坐标转城市失败:', err);
          setError('定位解析失败，请手动搜索城市');
        }
        
        setLoading(false);
      },
      (err) => {
        console.error('[useLocation] GPS定位失败:', {
          code: err.code,
          message: err.message
        });
        
        let errorMessage = '定位失败';
        switch (err.code) {
          case err.PERMISSION_DENIED:
            errorMessage = '定位权限被拒绝，请允许浏览器获取位置';
            break;
          case err.POSITION_UNAVAILABLE:
            errorMessage = '无法获取位置信息，请检查网络';
            break;
          case err.TIMEOUT:
            errorMessage = '定位请求超时，请重试';
            break;
        }
        
        setError(errorMessage);
        setCity(''); // 定位失败时不设置默认城市
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0, // 每次都获取最新定位
      }
    );
  }, [checkPermission]);

  // 不再自动调用定位，由用户主动触发
  // return { location, city, loading, error, refresh: getLocation };
  return { location, city, loading, error, refresh: getLocation };
}

// 使用动画
export function useAnimation() {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  return { ref, isVisible };
}

// 使用本地存储
export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(initialValue);

  useEffect(() => {
    try {
      const item = window.localStorage.getItem(key);
      if (item) {
        setStoredValue(JSON.parse(item));
      }
    } catch (error) {
      console.error(`Error loading ${key} from localStorage:`, error);
    }
  }, [key]);

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting ${key} to localStorage:`, error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue] as const;
}

// 使用屏幕宽度
export function useWindowSize() {
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
  });

  useEffect(() => {
    function handleResize() {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
}

// 重新导出 Chat Store
export { useChatStore } from '@/store';

// 重新导出 Recommendation Store
export { useRecommendationStore } from '@/store';

// 使用推荐
export function useRecommendation() {
  return useRecommendationStore();
}
