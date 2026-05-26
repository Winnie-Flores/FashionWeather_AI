'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Sparkles,
  RefreshCw,
  Home,
  Briefcase,
  Heart,
  Zap,
  PartyPopper,
  Plane,
  Shirt,
  AlertCircle,
  Leaf,
  Flower2,
} from 'lucide-react';
import { OutfitCard, OutfitPlanCard } from '@/components';
import { useRecommendation, useAuth, useWardrobe } from '@/hooks';
import { aiApi } from '@/services/api';
import { cn } from '@/utils';
import { useWeatherStore } from '@/store';
import type { OutfitRecommendation, SceneOption } from '@/types';

const sceneIcons: Record<string, any> = {
  daily: Home,
  work: Briefcase,
  date: Heart,
  sports: Zap,
  party: PartyPopper,
  travel: Plane,
};

export default function RecommendPage() {
  const { isAuthenticated } = useAuth();
  const { currentCity } = useWeatherStore();
  const { 
    clothes,
    total: wardrobeTotal,
    refresh: refreshWardrobe
  } = useWardrobe();
  const {
    todayRecommendation,
    scenes,
    selectedScene,
    setTodayRecommendation,
    setScenes,
    setSelectedScene,
    setSelectedStyle,
  } = useRecommendation();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendation, setRecommendation] = useState<OutfitRecommendation | null>(null);

  useEffect(() => {
    fetchScenes();
    if (isAuthenticated) {
      refreshWardrobe();
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      fetchTodayRecommendation();
    }
  }, [isAuthenticated, selectedScene, currentCity]);

  const fetchScenes = async () => {
    try {
      const res = await aiApi.getScenes();
      setScenes(res.data);
    } catch (error) {
      console.error('获取场景失败:', error);
    }
  };

  const fetchTodayRecommendation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await aiApi.getTodayRecommendation(currentCity || '北京', selectedScene);
      setRecommendation(res.data.data || res.data);
      setTodayRecommendation(res.data.data || res.data);
    } catch (error: any) {
      console.error('获取推荐失败:', error);
      setError(error?.response?.data?.detail || error?.message || '穿搭推荐生成失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleSceneChange = (scene: string) => {
    setSelectedScene(scene);
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="nature-card p-8 text-center max-w-md">
          <div className="w-16 h-16 mx-auto mb-4 rounded-organic bg-gradient-to-br from-moss-500 to-forest-600 
                          flex items-center justify-center shadow-warm">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-forest-800 mb-2">
            登录查看穿搭推荐
          </h2>
          <p className="text-sage-600 mb-6">
            登录后，我们将根据您的衣橱和今日天气，为您生成个性化穿搭方案
          </p>
          <a href="/login" className="btn-primary inline-block">
            立即登录
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-20 md:pb-8">
      {/* 头部 - 自然渐变 */}
      <section className="gradient-hero p-6 border-b border-sage-200/50 relative overflow-hidden">
        {/* 装饰 */}
        <div className="absolute top-4 right-10 opacity-10">
          <Flower2 className="w-20 h-20 text-forest-600 rotate-12" />
        </div>
        <div className="absolute bottom-4 right-32 opacity-10">
          <Leaf className="w-16 h-16 text-moss-500 -rotate-45" />
        </div>
        
        <div className="max-w-7xl mx-auto relative">
          <h1 className="text-3xl font-bold text-gradient mb-2 flex items-center gap-3">
            <div className="w-12 h-12 rounded-organic bg-gradient-to-br from-moss-500 to-forest-600 
                            flex items-center justify-center shadow-warm">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            AI 穿搭推荐
          </h1>
          <p className="text-sage-600">根据天气和您的衣橱，智能推荐最佳穿搭</p>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* 场景选择 - 自然胶囊风格 */}
        <section className="mb-6">
          <h2 className="text-lg font-semibold text-forest-800 mb-4">选择场景</h2>
          <div className="flex flex-wrap gap-3">
            {scenes.map((scene: SceneOption) => {
              const Icon = sceneIcons[scene.value] || Home;
              return (
                <motion.button
                  key={scene.value}
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => handleSceneChange(scene.value)}
                  className={cn(
                    'flex items-center gap-2 px-5 py-2.5 rounded-organic transition-all duration-200',
                    selectedScene === scene.value
                      ? 'bg-gradient-to-r from-moss-500 to-forest-600 text-white shadow-warm'
                      : 'bg-white/80 text-sage-700 hover:bg-sage-50 border border-sage-200'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {scene.label}
                </motion.button>
              );
            })}
          </div>
        </section>

        {/* 刷新按钮 */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-semibold text-forest-800">今日推荐</h2>
          <button
            onClick={fetchTodayRecommendation}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-organic 
                       bg-white/80 border border-sage-200 
                       hover:bg-white hover:border-sage-300 
                       shadow-card hover:shadow-soft transition-all duration-200 text-sage-700"
          >
            <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
            换一批
          </button>
        </div>

        {/* 推荐内容 */}
        {loading ? (
          <div className="nature-card p-8 animate-pulse">
            <div className="h-8 w-48 bg-sage-100 rounded-lg mb-4" />
            <div className="h-64 bg-sage-100 rounded-leaf" />
          </div>
        ) : error ? (
          <div className="nature-card p-8 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-earth-50 flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-earth-400" />
            </div>
            <p className="text-sage-700 mb-4 font-medium">
              {error}
            </p>
            <button
              onClick={fetchTodayRecommendation}
              className="btn-primary inline-flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              重新生成
            </button>
          </div>
        ) : wardrobeTotal === 0 ? (
          <div className="nature-card p-8 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-sage-50 flex items-center justify-center">
              <Shirt className="w-8 h-8 text-sage-400" />
            </div>
            <p className="text-sage-600 mb-4">
              您的衣橱还没有衣服，请先添加衣服
            </p>
            <p className="text-sm text-sage-400 mb-6">
              上传衣服图片，AI将自动识别分类
            </p>
            <a href="/wardrobe" className="btn-primary inline-flex items-center gap-2">
              <Shirt className="w-4 h-4" />
              去添加衣服
            </a>
          </div>
        ) : recommendation ? (
          <OutfitCard
            recommendation={recommendation}
            date={new Date().toLocaleDateString('zh-CN', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              weekday: 'long',
            })}
          />
        ) : (
          <div className="nature-card p-8 text-center">
            <Sparkles className="w-8 h-8 text-sunrise-400 mx-auto mb-4" />
            <p className="text-sage-600 mb-4">
              正在为您生成穿搭推荐...
            </p>
            <button
              onClick={fetchTodayRecommendation}
              className="btn-primary inline-flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              立即生成
            </button>
          </div>
        )}

        {/* 更多推荐方案 */}
        <section className="mt-8">
          <h2 className="text-lg font-semibold text-forest-800 mb-4">
            更多搭配方案
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <OutfitPlanCard key={i} />
            ))}
          </div>
        </section>

        {/* 穿搭知识 - 杂志风卡片 */}
        <section className="mt-8 nature-card p-6">
          <h2 className="text-lg font-semibold text-forest-800 mb-4 flex items-center gap-2">
            <Leaf className="w-5 h-5 text-moss-500" />
            穿搭小知识
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            <TipCard
              title="温度穿搭法则"
              content="温度在15-20°C时，建议穿薄外套或长袖；10-15°C时，加件毛衣或风衣；5-10°C时，羽绒服或棉衣是必备。"
              icon="🌡️"
            />
            <TipCard
              title="颜色搭配技巧"
              content="经典搭配：黑+白+灰永不出错；同色系穿搭显高级；互补色搭配吸睛亮眼。"
              icon="🎨"
            />
            <TipCard
              title="场合穿搭要点"
              content="职场：简约干练为主；约会：展现个人魅力；休闲：舒适自在最重要。"
              icon="✨"
            />
            <TipCard
              title="季节交替建议"
              content="春秋季遵循'洋葱式'穿搭，方便增减衣物；关注天气预报，提前准备。"
              icon="🍂"
            />
          </div>
        </section>
      </div>
    </div>
  );
}

function TipCard({ title, content, icon }: { title: string; content: string; icon: string }) {
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className="bg-gradient-to-br from-linen-50 to-sage-50 rounded-organic p-4 
                 border border-sage-200/50 hover:shadow-soft transition-shadow duration-200"
    >
      <div className="flex items-start gap-3">
        <span className="text-3xl">{icon}</span>
        <div>
          <h3 className="font-semibold text-forest-800 mb-2">{title}</h3>
          <p className="text-sm text-sage-600 leading-relaxed">{content}</p>
        </div>
      </div>
    </motion.div>
  );
}
