'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import {
  Cloud,
  Sparkles,
  Shirt,
  MessageCircle,
  ArrowRight,
  Sun,
  MapPin,
  RefreshCw,
  Loader2,
  AlertCircle,
  Navigation,
  Leaf,
  Flower2,
} from 'lucide-react';
import { WeatherCard, ForecastCard, OutfitCard } from '@/components';
import { useWeather, useRecommendation, useAuth, useLocation } from '@/hooks';
import { weatherApi, aiApi } from '@/services/api';
import { useWeatherStore } from '@/store';
import type { OutfitRecommendation, Weather } from '@/types';

export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const { weather, forecast, loading: weatherLoading, error, currentCity, refresh } = useWeather();
  const [recommendation, setRecommendation] = useState<OutfitRecommendation | null>(null);
  const [advice, setAdvice] = useState<any[]>([]);
  const [loadingRec, setLoadingRec] = useState(false);
  const [recommendationError, setRecommendationError] = useState<string | null>(null);
  
  // 城市搜索状态
  const [searchCity, setSearchCity] = useState('');
  const [inputCity, setInputCity] = useState('');
  
  // 定位状态
  const [locationReady, setLocationReady] = useState(false);
  const { location, city: locateCity, loading: locating, error: locateError, refresh: refreshLocation } = useLocation();
  const { setCurrentCity } = useWeatherStore();
  
  // 当前使用的城市
  const effectiveCity = searchCity || locateCity || currentCity || '';

  // 页面加载时自动启动 GPS 定位
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const cityParam = params.get('city');
    
    if (!cityParam && !locating && !locationReady) {
      refreshLocation();
    }
  }, []);

  // 监听定位结果
  useEffect(() => {
    if (locateCity && locateCity.trim() !== '') {
      setSearchCity(locateCity);
      setInputCity(locateCity);
      setCurrentCity(locateCity);
      const newUrl = `/?city=${encodeURIComponent(locateCity)}`;
      window.history.pushState({}, '', newUrl);
      setLocationReady(true);
    }
  }, [locateCity, location]);

  // 监听定位失败
  useEffect(() => {
    if (locateError && !locating) {
      setLocationReady(true);
    }
  }, [locateError, locating]);
  
  // 从 URL 获取城市参数
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const cityParam = params.get('city');
    if (cityParam) {
      const decodedCity = decodeURIComponent(cityParam);
      setInputCity(decodedCity);
      setSearchCity(decodedCity);
      setCurrentCity(decodedCity);
      setLocationReady(true);
    }
  }, []);

  // 获取今日推荐
  useEffect(() => {
    if (isAuthenticated && effectiveCity) {
      fetchRecommendation();
    }
  }, [isAuthenticated, effectiveCity]);

  // 获取穿衣建议
  useEffect(() => {
    if (weather && effectiveCity) {
      fetchAdvice();
    }
  }, [weather, effectiveCity]);

  const fetchRecommendation = async () => {
    if (!effectiveCity) return;
    setLoadingRec(true);
    setRecommendationError(null);
    try {
      const res = await aiApi.getTodayRecommendation(effectiveCity, 'daily');
      setRecommendation(res.data.data || res.data);
    } catch (error: any) {
      setRecommendationError(error?.response?.data?.detail || error?.message || '获取推荐失败');
    } finally {
      setLoadingRec(false);
    }
  };

  const fetchAdvice = async () => {
    if (!effectiveCity) return;
    try {
      const params: any = { city: effectiveCity };
      if (weather) {
        params.temperature = weather.temperature;
        params.humidity = weather.humidity;
        params.weather_type = weather.weather;
        params.wind_speed = weather.wind_speed;
        params.uv_index = weather.uv_index;
      }
      const res = await weatherApi.getDressingAdvice(params);
      setAdvice(res.data.advice || []);
    } catch (error) {
      console.error('获取建议失败:', error);
    }
  };

  const handleCitySearch = async () => {
    const city = inputCity.trim();
    if (!city) return;
    
    setSearchCity(city);
    setCurrentCity(city);
    
    const newUrl = `/?city=${encodeURIComponent(city)}`;
    window.history.pushState({}, '', newUrl);
  };

  const handleUseLocation = () => {
    refreshLocation();
  };

  return (
    <div className="min-h-screen pb-20 md:pb-8">
      {/* Hero Section - 自然渐变风格 */}
      <section className="relative overflow-hidden">
        {/* 自然渐变背景 */}
        <div className="absolute inset-0 bg-gradient-to-br from-linen-100 via-sage-50 to-sky-100" />
        
        {/* 装饰性植物图案 */}
        <div className="absolute top-10 left-10 w-32 h-32 opacity-10">
          <Leaf className="w-full h-full text-forest-600 rotate-45" />
        </div>
        <div className="absolute top-20 right-20 w-24 h-24 opacity-10">
          <Flower2 className="w-full h-full text-moss-500" />
        </div>
        <div className="absolute bottom-10 left-1/4 w-20 h-20 opacity-10">
          <Leaf className="w-full h-full text-sage-500 -rotate-12" />
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            {/* Logo */}
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="inline-flex items-center gap-3 mb-6"
            >
              <div className="w-14 h-14 rounded-organic bg-gradient-to-br from-moss-500 to-forest-600 
                              flex items-center justify-center shadow-warm">
                <Sun className="w-8 h-8 text-white" />
              </div>
            </motion.div>
            
            <h1 className="text-4xl md:text-5xl font-bold mb-4 text-gradient">
              FashionWeather AI
            </h1>
            <p className="text-base md:text-lg text-sage-600 mb-8 max-w-lg mx-auto">
              清晨阳光照进充满绿植的房间，在自然与天气变化中获得轻松穿搭建议
            </p>
            
            {/* 城市搜索框 - 自然卡片风格 */}
            <div className="max-w-md mx-auto">
              <div className="nature-card flex items-center gap-3 p-3">
                <MapPin className="w-5 h-5 text-sage-400" />
                <input
                  type="text"
                  placeholder="输入城市名称..."
                  className="flex-1 bg-transparent outline-none text-gray-800 placeholder:text-mist-400"
                  value={inputCity}
                  onChange={(e) => setInputCity(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleCitySearch();
                    }
                  }}
                />
                <button 
                  className="p-2 bg-moss-500 rounded-organic text-white hover:bg-moss-600 
                             transition-colors duration-200"
                  onClick={handleCitySearch}
                  disabled={!inputCity.trim()}
                >
                  <RefreshCw className="w-5 h-5" />
                </button>
                <button 
                  className="p-2 bg-sky-400 rounded-organic text-white hover:bg-sky-500 
                             transition-colors duration-200"
                  onClick={handleUseLocation}
                  disabled={locating}
                  title="使用定位"
                >
                  {locating ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Navigation className="w-5 h-5" />
                  )}
                </button>
              </div>
              
              {/* 定位状态提示 */}
              {locating && (
                <p className="mt-3 text-sm text-sage-600 flex items-center justify-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  正在获取您的位置...
                </p>
              )}
              {locateError && (
                <p className="mt-3 text-sm text-earth-500 flex items-center justify-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  {locateError}
                </p>
              )}
              {effectiveCity && !locating && (
                <p className="mt-3 text-sm text-sage-500">
                  当前城市：{effectiveCity}
                </p>
              )}
            </div>
          </motion.div>
        </div>
      </section>

      {/* 错误提示 */}
      {error && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-10">
          <div className="nature-card p-4 bg-sunrise-50/50 border border-sunrise-200">
            <div className="flex items-center gap-3 text-earth-600">
              <AlertCircle className="w-5 h-5" />
              <p>{error}</p>
              <button 
                className="ml-auto text-sm btn-ghost"
                onClick={() => refresh()}
              >
                重试
              </button>
            </div>
          </div>
        </section>
      )}

      {/* 天气概览 */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-10">
        {/* 定位中状态 */}
        {locating ? (
          <div className="nature-card p-8 flex items-center justify-center gap-3">
            <Loader2 className="w-8 h-8 animate-spin text-moss-500" />
            <span className="text-sage-600">正在获取您的位置...</span>
          </div>
        ) : weatherLoading ? (
          <div className="nature-card p-8 flex items-center justify-center gap-3">
            <Loader2 className="w-8 h-8 animate-spin text-moss-500" />
            <span className="text-sage-600">加载天气数据...</span>
          </div>
        ) : weather ? (
          <WeatherCard weather={weather} />
        ) : locateError && !effectiveCity ? (
          <div className="nature-card p-8 flex flex-col items-center justify-center">
            <MapPin className="w-8 h-8 text-sage-400 mb-3" />
            <span className="text-sage-600 mb-2">定位失败</span>
            <span className="text-sm text-sage-400">请在上方搜索框输入城市名称</span>
          </div>
        ) : !effectiveCity ? (
          <div className="nature-card p-8 flex flex-col items-center justify-center">
            <Leaf className="w-8 h-8 text-sage-400 mb-3" />
            <span className="text-sage-600 mb-2">请选择城市</span>
            <span className="text-sm text-sage-400">在上方搜索框输入城市名称，开始穿搭之旅</span>
          </div>
        ) : null}
      </section>

      {/* 穿衣建议 */}
      {advice.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
          <h2 className="section-title">
            <Shirt className="w-6 h-6 text-moss-500" />
            今日穿衣建议
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {advice.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="nature-card p-4"
              >
                <div className="flex items-start gap-3">
                  <span className="text-3xl">{getTipEmoji(item.type)}</span>
                  <div>
                    <p className="font-medium text-forest-800 mb-1">{item.level}</p>
                    <p className="text-sm text-sage-600">{item.suggestion}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </section>
      )}

      {/* 天气预报 */}
      {forecast.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
          <h2 className="section-title">
            <Cloud className="w-6 h-6 text-sky-500" />
            7日天气预报
          </h2>
          <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
            {forecast.slice(0, 7).map((day, index) => (
              <div key={index} className="flex-shrink-0">
                <ForecastCard forecast={day} isToday={index === 0} />
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 今日推荐 */}
      {isAuthenticated ? (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-title mb-0">
              <Sparkles className="w-6 h-6 text-sunrise-500" />
              今日穿搭推荐
            </h2>
            <Link
              href="/recommend"
              className="flex items-center gap-1 text-moss-600 hover:text-forest-700 text-sm font-medium btn-ghost"
            >
              查看更多
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          
          {loadingRec ? (
            <div className="nature-card p-8 flex items-center justify-center gap-3">
              <Loader2 className="w-8 h-8 animate-spin text-sunrise-500" />
              <span className="text-sage-600">加载推荐...</span>
            </div>
          ) : recommendationError ? (
            <div className="nature-card p-8 text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-earth-50 flex items-center justify-center">
                <AlertCircle className="w-8 h-8 text-earth-400" />
              </div>
              <p className="text-sage-700 mb-2">{recommendationError}</p>
              <button
                onClick={fetchRecommendation}
                className="btn-primary inline-flex items-center gap-2 mt-2"
              >
                <RefreshCw className="w-4 h-4" />
                重新生成
              </button>
            </div>
          ) : recommendation ? (
            <OutfitCard 
              recommendation={recommendation}
              date={new Date().toLocaleDateString('zh-CN', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            />
          ) : !effectiveCity ? (
            <div className="nature-card p-8 text-center">
              <MapPin className="w-8 h-8 text-sage-400 mx-auto mb-3" />
              <p className="text-sage-600 mb-2">请先选择城市获取天气</p>
              <p className="text-sm text-sage-400">穿搭推荐需要根据当地天气生成</p>
            </div>
          ) : (
            <div className="nature-card p-8 text-center">
              <Sparkles className="w-8 h-8 text-sunrise-400 mx-auto mb-3" />
              <p className="text-sage-600 mb-2">正在生成穿搭推荐...</p>
              <p className="text-sm text-sage-400">根据您的衣橱和今日天气为您推荐</p>
            </div>
          )}
        </section>
      ) : (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
          <div className="nature-card p-8 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-organic bg-gradient-to-br from-moss-500 to-forest-600 
                            flex items-center justify-center shadow-warm">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-forest-800 mb-2">
              开启智能穿搭之旅
            </h3>
            <p className="text-sage-600 mb-6 max-w-md mx-auto">
              登录后，我们将根据您的衣橱和今日天气，为您推荐最佳穿搭方案
            </p>
            <div className="flex gap-4 justify-center">
              <Link href="/login" className="btn-primary">
                登录
              </Link>
              <Link href="/wardrobe" className="btn-secondary">
                管理衣橱
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* 快捷入口 */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 grid md:grid-cols-3 gap-4">
        <Link href="/weather" className="nature-card p-6 hover:shadow-lifted transition-all duration-300 group">
          <div className="w-12 h-12 rounded-organic bg-gradient-to-br from-sky-100 to-sky-200 
                          flex items-center justify-center mb-4 
                          group-hover:scale-110 transition-transform duration-300">
            <Cloud className="w-6 h-6 text-sky-600" />
          </div>
          <h3 className="font-semibold text-forest-800 mb-2">天气详情</h3>
          <p className="text-sm text-sage-600">查看详细天气数据和可视化图表</p>
        </Link>
        
        <Link href="/wardrobe" className="nature-card p-6 hover:shadow-lifted transition-all duration-300 group">
          <div className="w-12 h-12 rounded-organic bg-gradient-to-br from-moss-100 to-forest-100 
                          flex items-center justify-center mb-4 
                          group-hover:scale-110 transition-transform duration-300">
            <Shirt className="w-6 h-6 text-forest-600" />
          </div>
          <h3 className="font-semibold text-forest-800 mb-2">我的衣橱</h3>
          <p className="text-sm text-sage-600">管理您的衣服收藏，AI自动识别分类</p>
        </Link>
        
        <Link href="/chat" className="nature-card p-6 hover:shadow-lifted transition-all duration-300 group">
          <div className="w-12 h-12 rounded-organic bg-gradient-to-br from-sunrise-100 to-linen-200 
                          flex items-center justify-center mb-4 
                          group-hover:scale-110 transition-transform duration-300">
            <MessageCircle className="w-6 h-6 text-sunrise-600" />
          </div>
          <h3 className="font-semibold text-forest-800 mb-2">AI 聊天</h3>
          <p className="text-sm text-sage-600">与AI对话，获取专属穿搭建议</p>
        </Link>
      </section>
    </div>
  );
}

function getTipEmoji(type: string): string {
  const emojiMap: Record<string, string> = {
    'cold': '🧥',
    'cool': '🍂',
    'comfortable': '🌿',
    'hot': '🌻',
    'rain': '🌧️',
    'snow': '❄️',
    'windy': '🍃',
    'uv': '☀️',
    'humid': '💧',
    'dry': '🏜️',
  };
  return emojiMap[type] || '🌱';
}
