'use client';

import React, { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  Cloud,
  Sun,
  Wind,
  Droplets,
  Thermometer,
  Eye,
  TrendingUp,
  MapPin,
  Leaf,
} from 'lucide-react';
import {
  WeatherCard,
  ForecastCard,
  AQIIndicator,
  UVIndicator,
  DressingTips,
} from '@/components';
import { useWeather } from '@/hooks';
import { weatherApi } from '@/services/api';
import { weatherCodeToIcon } from '@/utils';
import { SafeEChart } from '@/components/ECharts';

export default function WeatherDetailPage() {
  const { weather, forecast, hourlyWeather, loading, currentCity } = useWeather();
  const [advice, setAdvice] = useState<any[]>([]);
  const [aqiInfo, setAqiInfo] = useState<any>(null);
  const [city, setCity] = useState(currentCity);

  // 设置城市
  useEffect(() => {
    if (currentCity) {
      setCity(currentCity);
    }
  }, [currentCity]);

  // 获取穿衣建议和 AQI
  useEffect(() => {
    if (weather) {
      const fetchData = async () => {
        try {
          const adviceRes = await weatherApi.getDressingAdvice({
            city: currentCity,
            temperature: weather.temperature,
            humidity: weather.humidity,
            weather_type: weather.weather,
            wind_speed: weather.wind_speed,
            uv_index: weather.uv_index,
          });
          setAdvice(adviceRes.data.advice || []);
        } catch (error) {
          console.error('获取建议失败:', error);
        }
        
        try {
          const aqiRes = await weatherApi.getAQI(weather?.aqi || 50);
          setAqiInfo(aqiRes.data);
        } catch (error) {
          console.error('获取AQI失败:', error);
        }
      };
      fetchData();
    }
  }, [weather, currentCity]);

  // 温度趋势图配置 - 自然风格
  const getTemperatureChartOption = () => {
    const hours = hourlyWeather.slice(0, 24).map((h: any) => h.hour);
    const temps = hourlyWeather.slice(0, 24).map((h: any) => h.temperature);

    return {
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}°C',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#c8e6c9',
        borderWidth: 1,
        textStyle: {
          color: '#2e4a35',
        },
      },
      xAxis: {
        type: 'category',
        data: hours,
        axisLabel: {
          color: '#6b8068',
        },
        axisLine: {
          lineStyle: {
            color: '#d4e6d4',
          },
        },
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}°C',
          color: '#6b8068',
        },
        splitLine: {
          lineStyle: {
            color: '#f0f5f0',
          },
        },
      },
      series: [
        {
          name: '温度',
          type: 'line',
          data: temps,
          smooth: true,
          lineStyle: {
            width: 3,
            color: '#6eab47',
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(110, 171, 71, 0.3)' },
                { offset: 1, color: 'rgba(110, 171, 71, 0.05)' },
              ],
            },
          },
          itemStyle: {
            color: '#6eab47',
          },
        },
      ],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '3%',
        containLabel: true,
      },
    };
  };

  // 湿度图配置
  const getHumidityChartOption = () => {
    const hours = hourlyWeather.slice(0, 24).map((h: any) => h.hour);
    const humidity = hourlyWeather.slice(0, 24).map((h: any) => h.precipitation_probability);

    return {
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}%',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#bbdefb',
        borderWidth: 1,
        textStyle: {
          color: '#1565c0',
        },
      },
      xAxis: {
        type: 'category',
        data: hours,
        axisLabel: {
          color: '#6b8068',
        },
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: {
          formatter: '{value}%',
          color: '#6b8068',
        },
        splitLine: {
          lineStyle: {
            color: '#f0f5f0',
          },
        },
      },
      series: [
        {
          name: '降雨概率',
          type: 'bar',
          data: humidity,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: '#6eab47' },
                { offset: 1, color: '#4caf50' },
              ],
            },
            borderRadius: [6, 6, 0, 0],
          },
        },
      ],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '3%',
        containLabel: true,
      },
    };
  };

  // 雷达图配置
  const getRadarChartOption = () => {
    return {
      tooltip: {},
      radar: {
        indicator: [
          { name: '温度舒适度', max: 100 },
          { name: '风力影响', max: 100 },
          { name: '紫外线强度', max: 100 },
          { name: '湿度舒适度', max: 100 },
          { name: '空气清新度', max: 100 },
        ],
        shape: 'polygon',
        splitNumber: 4,
        axisName: {
          color: '#4a5d4a',
        },
        splitLine: {
          lineStyle: {
            color: '#d4e6d4',
          },
        },
        splitArea: {
          areaStyle: {
            color: ['rgba(110, 171, 71, 0.02)', 'rgba(110, 171, 71, 0.05)', 'rgba(110, 171, 71, 0.08)', 'rgba(110, 171, 71, 0.12)'],
          },
        },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: [
                weather ? (weather.temperature > 20 && weather.temperature < 26 ? 90 : 70) : 80,
                weather ? (100 - weather.wind_speed * 5) : 85,
                weather ? (100 - weather.uv_index * 10) : 80,
                weather ? (100 - Math.abs(weather.humidity - 50) * 2) : 85,
                weather ? (100 - weather.aqi / 2) : 90,
              ],
              name: '穿衣舒适度',
              lineStyle: {
                color: '#6eab47',
                width: 2,
              },
              areaStyle: {
                color: 'rgba(110, 171, 71, 0.25)',
              },
              itemStyle: {
                color: '#6eab47',
              },
            },
          ],
        },
      ],
    };
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-dots text-moss-500">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-20 md:pb-8">
      {/* 头部 - 自然渐变 */}
      <section className="gradient-hero p-6 border-b border-sage-200/50">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-moss-500 to-forest-600 
                            flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-sage-500" />
              <span className="text-lg text-forest-800">{city}</span>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gradient mb-2">天气预报</h1>
          <p className="text-sage-600">实时天气数据与未来预报</p>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* 当前天气 */}
        {weather && <WeatherCard weather={weather} />}

        {/* 穿衣建议 */}
        {advice.length > 0 && (
          <section>
            <h2 className="text-xl font-bold text-forest-800 mb-4 flex items-center gap-2">
              <Thermometer className="w-5 h-5 text-sunrise-500" />
              穿衣建议
            </h2>
            <DressingTips tips={advice} />
          </section>
        )}

        {/* 温度趋势图 */}
        {hourlyWeather.length > 0 && (
          <section className="nature-card p-6">
            <h2 className="text-xl font-bold text-forest-800 mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-moss-500" />
              温度趋势
            </h2>
            <div className="h-64">
              <SafeEChart option={getTemperatureChartOption()} style={{ height: '100%', width: '100%' }} />
            </div>
          </section>
        )}

        {/* 降雨概率图 */}
        {hourlyWeather.length > 0 && (
          <section className="nature-card p-6">
            <h2 className="text-xl font-bold text-forest-800 mb-4 flex items-center gap-2">
              <Droplets className="w-5 h-5 text-sky-500" />
              降雨概率
            </h2>
            <div className="h-64">
              <SafeEChart option={getHumidityChartOption()} style={{ height: '100%', width: '100%' }} />
            </div>
          </section>
        )}

        {/* 穿衣舒适度雷达图 */}
        <section className="nature-card p-6">
          <h2 className="text-xl font-bold text-forest-800 mb-4 flex items-center gap-2">
            <Sun className="w-5 h-5 text-sunrise-500" />
            穿衣舒适度
          </h2>
          <div className="h-72">
            <SafeEChart option={getRadarChartOption()} style={{ height: '100%', width: '100%' }} />
          </div>
        </section>

        {/* 7日预报 */}
        {forecast.length > 0 && (
          <section>
            <h2 className="text-xl font-bold text-forest-800 mb-4 flex items-center gap-2">
              <Cloud className="w-5 h-5 text-sky-500" />
              7日天气预报
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3">
              {forecast.slice(0, 7).map((day, index) => (
                <ForecastCard key={index} forecast={day} isToday={index === 0} />
              ))}
            </div>
          </section>
        )}

        {/* 空气质量与紫外线 */}
        <div className="grid md:grid-cols-2 gap-4">
          {weather && <AQIIndicator aqi={weather.aqi} />}
          {weather && <UVIndicator uvIndex={weather.uv_index} />}
        </div>

        {/* 详细指标 */}
        {weather && (
          <section className="nature-card p-6">
            <h2 className="text-xl font-bold text-forest-800 mb-4">详细指标</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <DetailItem
                icon={Thermometer}
                label="体感温度"
                value={`${Math.round(weather.feels_like)}°C`}
                color="sunrise"
              />
              <DetailItem
                icon={Droplets}
                label="湿度"
                value={`${weather.humidity}%`}
                color="sky"
              />
              <DetailItem
                icon={Wind}
                label="风速"
                value={`${weather.wind_speed} m/s`}
                color="sage"
              />
              <DetailItem
                icon={Leaf}
                label="AQI指数"
                value={weather.aqi.toString()}
                color="moss"
              />
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

function DetailItem({ icon: Icon, label, value, color }: { icon: any; label: string; value: string; color?: string }) {
  const colorMap: Record<string, string> = {
    sunrise: 'from-sunrise-50 to-sunrise-100 text-sunrise-600',
    sky: 'from-sky-50 to-sky-100 text-sky-600',
    sage: 'from-sage-50 to-sage-100 text-sage-600',
    moss: 'from-moss-50 to-moss-100 text-moss-600',
  };
  
  return (
    <div className={`text-center p-4 rounded-organic bg-gradient-to-br ${colorMap[color || 'sage']}`}>
      <Icon className="w-6 h-6 mx-auto mb-2 opacity-70" />
      <p className="text-sage-500 text-sm mb-1">{label}</p>
      <p className="text-xl font-bold text-forest-800">{value}</p>
    </div>
  );
}
