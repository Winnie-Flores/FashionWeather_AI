'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Cloud, Sun, CloudRain, CloudSnow, Wind, Droplets, Thermometer, Eye, Leaf } from 'lucide-react';
import { cn } from '@/utils';
import type { Weather as WeatherType } from '@/types';

interface WeatherCardProps {
  weather: WeatherType;
  className?: string;
  showDetails?: boolean;
}

export function WeatherCard({ weather, className, showDetails = true }: WeatherCardProps) {
  const WeatherIcon = getWeatherIcon(weather.weather_code);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className={cn('nature-card p-6', className)}
    >
      {/* 主要信息 */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sage-500">
              <Cloud className="w-4 h-4" />
            </span>
            <p className="text-sage-600 text-sm">{weather.city}</p>
          </div>
          <h2 className="text-6xl font-bold text-forest-800 mb-2 tracking-tight">
            {Math.round(weather.temperature)}°
          </h2>
          <p className="text-sage-600 text-lg">{weather.description}</p>
        </div>
        <motion.div
          animate={{ y: [0, -8, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
          className="text-7xl"
        >
          <WeatherIcon />
        </motion.div>
      </div>

      {/* 详细信息 */}
      {showDetails && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <WeatherDetail
            icon={Thermometer}
            label="体感温度"
            value={`${Math.round(weather.feels_like)}°`}
            color="sunrise"
          />
          <WeatherDetail
            icon={Droplets}
            label="湿度"
            value={`${weather.humidity}%`}
            color="sky"
          />
          <WeatherDetail
            icon={Wind}
            label="风速"
            value={`${weather.wind_speed} m/s`}
            color="sage"
          />
          <WeatherDetail
            icon={Leaf}
            label="空气指数"
            value={`${weather.aqi} AQI`}
            color="moss"
          />
        </div>
      )}
    </motion.div>
  );
}

interface WeatherDetailProps {
  icon: React.ElementType;
  label: string;
  value: string;
  color?: 'sunrise' | 'sky' | 'sage' | 'moss' | 'earth';
}

function WeatherDetail({ icon: Icon, label, value, color = 'sage' }: WeatherDetailProps) {
  const colorClasses = {
    sunrise: 'bg-sunrise-50 text-sunrise-600 border-sunrise-200',
    sky: 'bg-sky-50 text-sky-600 border-sky-200',
    sage: 'bg-sage-50 text-sage-600 border-sage-200',
    moss: 'bg-moss-50 text-moss-600 border-moss-200',
    earth: 'bg-earth-50 text-earth-600 border-earth-200',
  };

  return (
    <div className={cn(
      'rounded-organic p-3 border transition-all duration-200 hover:shadow-soft',
      colorClasses[color]
    )}>
      <div className="flex items-center gap-2 text-xs mb-1 opacity-70">
        <Icon className="w-4 h-4" />
        {label}
      </div>
      <p className="font-semibold text-base">{value}</p>
    </div>
  );
}

// 获取天气图标
function getWeatherIcon(code: number) {
  if (code === 100) return Sun;
  if (code <= 104) return Cloud;
  if (code >= 300 && code <= 399) return CloudRain;
  if (code >= 400 && code <= 499) return CloudSnow;
  return Cloud;
}

// 天气背景组件 - 自然渐变
export function WeatherBackground({ weatherCode }: { weatherCode: number }) {
  const getGradient = () => {
    if (weatherCode === 100) {
      return 'from-sunrise-100 via-linen-100 to-sage-50';
    }
    if (weatherCode <= 104) {
      return 'from-sky-100 via-mist-50 to-sage-50';
    }
    if (weatherCode >= 300 && weatherCode <= 399) {
      return 'from-sky-200 via-mist-100 to-sage-100';
    }
    return 'from-sky-100 via-mist-50 to-sage-50';
  };

  return (
    <div className={cn(
      'absolute inset-0 bg-gradient-to-br opacity-30 -z-10',
      getGradient()
    )} />
  );
}

interface ForecastCardProps {
  forecast: {
    date: string;
    temperature_max: number;
    temperature_min: number;
    weather: string;
    weather_code: number;
    precipitation_probability: number;
  };
  isToday?: boolean;
}

export function ForecastCard({ forecast, isToday }: ForecastCardProps) {
  const WeatherIcon = getWeatherIcon(forecast.weather_code);
  const weekday = new Date(forecast.date).toLocaleDateString('zh-CN', { weekday: 'short' });

  return (
    <motion.div
      whileHover={{ scale: 1.05, y: -2 }}
      transition={{ duration: 0.2 }}
      className={cn(
        'nature-card p-4 text-center min-w-[100px] cursor-default',
        isToday && 'ring-2 ring-moss-400/50 bg-moss-500/5'
      )}
    >
      <p className="text-sage-600 text-sm mb-3 font-medium">
        {isToday ? '今天' : weekday}
      </p>
      <div className="text-4xl mb-2">
        <WeatherIcon />
      </div>
      <p className="text-sage-500 text-xs mb-2">{forecast.weather}</p>
      <div className="flex items-center justify-center gap-2 text-sm">
        <span className="text-sunrise-500 font-medium">{Math.round(forecast.temperature_max)}°</span>
        <span className="text-sky-500">{Math.round(forecast.temperature_min)}°</span>
      </div>
      {forecast.precipitation_probability > 0 && (
        <p className="text-sky-500 text-xs mt-2 flex items-center justify-center gap-1">
          <Droplets className="w-3 h-3" />
          {forecast.precipitation_probability}%
        </p>
      )}
    </motion.div>
  );
}

// AQI 指示器 - 自然风格
export function AQIIndicator({ aqi }: { aqi: number }) {
  const getAQIInfo = () => {
    if (aqi <= 50) return { level: '优', color: 'bg-moss-500', text: 'text-moss-600', bg: 'bg-moss-50' };
    if (aqi <= 100) return { level: '良', color: 'bg-sunrise-400', text: 'text-sunrise-600', bg: 'bg-sunrise-50' };
    if (aqi <= 150) return { level: '轻度', color: 'bg-linen-400', text: 'text-linen-600', bg: 'bg-linen-50' };
    if (aqi <= 200) return { level: '中度', color: 'bg-earth-500', text: 'text-earth-600', bg: 'bg-earth-50' };
    return { level: '重度', color: 'bg-gray-500', text: 'text-gray-600', bg: 'bg-gray-50' };
  };

  const info = getAQIInfo();

  return (
    <div className="nature-card p-4">
      <div className="flex items-center gap-3">
        <div className={cn('w-12 h-12 rounded-full flex items-center justify-center', info.color)}>
          <span className="text-white font-bold">{aqi}</span>
        </div>
        <div>
          <p className={cn('font-semibold', info.text)}>空气质量 {info.level}</p>
          <p className="text-sage-500 text-sm">AQI 指数</p>
        </div>
      </div>
    </div>
  );
}

// 紫外线指示器 - 自然风格
export function UVIndicator({ uvIndex }: { uvIndex: number }) {
  const getUVLevel = () => {
    if (uvIndex <= 2) return { level: '弱', color: 'bg-moss-400', text: 'text-moss-600' };
    if (uvIndex <= 5) return { level: '中等', color: 'bg-sunrise-400', text: 'text-sunrise-600' };
    if (uvIndex <= 7) return { level: '较强', color: 'bg-earth-400', text: 'text-earth-600' };
    if (uvIndex <= 10) return { level: '很强', color: 'bg-linen-500', text: 'text-linen-700' };
    return { level: '极强', color: 'bg-gray-500', text: 'text-gray-600' };
  };

  const level = getUVLevel();

  return (
    <div className="nature-card p-4">
      <div className="flex items-center gap-3">
        <div className={cn('w-12 h-12 rounded-full flex items-center justify-center', level.color)}>
          <span className="text-white font-bold">{uvIndex}</span>
        </div>
        <div>
          <p className={cn('font-semibold', level.text)}>紫外线 {level.level}</p>
          <p className="text-sage-500 text-sm">UV 指数</p>
        </div>
      </div>
    </div>
  );
}

export default WeatherCard;
