'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Star, Sparkles, ShoppingBag, Info, Heart, Loader2, Leaf } from 'lucide-react';
import { cn } from '@/utils';
import type { OutfitRecommendation, OutfitItem } from '@/types';
import { favoritesApi } from '@/services/api';
import toast from 'react-hot-toast';
import { useRouter } from 'next/navigation';
import { useUserStore } from '@/store';

interface OutfitCardProps {
  recommendation: OutfitRecommendation;
  date?: string;
  showWeather?: boolean;
  weather?: any;
  onFavorite?: () => void;
}

export function OutfitCard({ recommendation, date, showWeather, weather, onFavorite }: OutfitCardProps) {
  const [favoriting, setFavoriting] = useState(false);
  const [isFavorited, setIsFavorited] = useState(false);
  const router = useRouter();
  const token = useUserStore((state) => state.token);

  // 检查是否已收藏
  useEffect(() => {
    if (!recommendation.id) return;
    
    const checkFavoriteStatus = async () => {
      try {
        const res = await favoritesApi.check(recommendation.id!);
        setIsFavorited(res.data.is_favorited);
      } catch (error) {
        // 忽略错误
      }
    };
    
    if (token) {
      checkFavoriteStatus();
    }
  }, [recommendation.id, token]);

  const handleFavorite = async () => {
    // 检查登录状态
    if (!token) {
      toast.error('请先登录');
      router.push('/login');
      return;
    }

    if (isFavorited) {
      toast.success('已经收藏过了');
      return;
    }

    // 检查 outfit_id 是否存在
    if (!recommendation.id) {
      console.error('[收藏] 缺少 outfit_id:', recommendation);
      toast.error('收藏失败：缺少穿搭ID');
      return;
    }

    setFavoriting(true);
    try {
      // 使用新的收藏 API
      await favoritesApi.add({
        outfit_id: recommendation.id,
        outfit_data: recommendation,
        weather: weather?.weather || weather?.text || '未知',
        scene: recommendation.scene,
        temperature: weather?.temperature || weather?.temp || undefined,
      });

      // 触发收藏成功
      setIsFavorited(true);
      toast.success('收藏成功！');
      
      // 通知父组件刷新
      if (onFavorite) {
        onFavorite();
      }

      // 触发页面刷新统计数据
      window.dispatchEvent(new Event('wardrobe-updated'));
    } catch (error: any) {
      console.error('收藏失败详情:', error.response?.data || error);
      toast.error(error.response?.data?.detail || '收藏失败，请重试');
    } finally {
      setFavoriting(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="nature-card overflow-hidden"
    >
      {/* 头部 - 自然渐变 */}
      <div className="gradient-hero p-5 border-b border-sage-200/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-moss-500 to-forest-600 
                            flex items-center justify-center shadow-warm">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-semibold text-forest-800">今日穿搭推荐</span>
              <p className="text-xs text-sage-500">根据天气与衣橱智能搭配</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {date && (
              <span className="text-sm text-sage-600 bg-white/50 px-3 py-1 rounded-full">
                {date}
              </span>
            )}
            {/* 收藏按钮 */}
            <button
              onClick={handleFavorite}
              disabled={favoriting || isFavorited}
              className={cn(
                'p-2 rounded-full transition-all duration-200',
                isFavorited
                  ? 'bg-sunrise-100 text-sunrise-500'
                  : 'hover:bg-sage-100 text-sage-500'
              )}
              title={isFavorited ? '已收藏' : '收藏这套穿搭'}
            >
              {favoriting ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Heart className={cn('w-5 h-5', isFavorited && 'fill-current')}>
                  {isFavorited && (
                    <motion.path
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                    />
                  )}
                </Heart>
              )}
            </button>
          </div>
        </div>
        
        {/* 评分 */}
        <div className="flex items-center gap-2 mt-4">
          <div className="flex">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={cn(
                  'w-5 h-5',
                  i < Math.floor(recommendation.score / 2)
                    ? 'text-sunrise-400 fill-sunrise-400'
                    : 'text-sage-200'
                )}
              />
            ))}
          </div>
          <span className="text-sm text-sage-600">
            {recommendation.score.toFixed(1)} 分
          </span>
          <span className="text-xs text-sage-400">穿搭评分</span>
        </div>
      </div>

      {/* 穿搭展示 */}
      <div className="p-6">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          {recommendation.top && (
            <OutfitItemCard item={recommendation.top} label="上衣" />
          )}
          {recommendation.pants && (
            <OutfitItemCard item={recommendation.pants} label="裤子" />
          )}
          {recommendation.shoes && (
            <OutfitItemCard item={recommendation.shoes} label="鞋子" />
          )}
          {recommendation.jacket && (
            <OutfitItemCard item={recommendation.jacket} label="外套" />
          )}
        </div>

        {/* 推荐理由 - 手写便签风格 */}
        <div className="bg-gradient-to-br from-linen-50 to-sage-50 rounded-organic p-4 mb-4 border border-sage-200/50">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-moss-100 flex items-center justify-center flex-shrink-0">
              <Leaf className="w-4 h-4 text-forest-600" />
            </div>
            <div>
              <p className="text-forest-700 font-medium mb-2 flex items-center gap-2">
                <Info className="w-4 h-4" />
                穿搭建议
              </p>
              <p className="text-sage-600 text-sm leading-relaxed whitespace-pre-line">
                {recommendation.reason}
              </p>
            </div>
          </div>
        </div>

        {/* 小贴士 */}
        {recommendation.tips && recommendation.tips.length > 0 && (
          <div className="space-y-3">
            <p className="text-sage-700 font-medium flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-moss-500" />
              搭配小贴士
            </p>
            {recommendation.tips.map((tip, index) => (
              <motion.div 
                key={index} 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start gap-2 text-sm text-sage-600"
              >
                <span className="text-moss-500 mt-0.5">•</span>
                {tip}
              </motion.div>
            ))}
          </div>
        )}

        {/* 场景标签 */}
        <div className="flex items-center gap-3 mt-5 pt-4 border-t border-sage-200/50">
          <ShoppingBag className="w-4 h-4 text-sage-500" />
          <span className="text-sage-600 text-sm">适合场景：</span>
          <span className="tag">{recommendation.scene}</span>
        </div>
      </div>
    </motion.div>
  );
}

interface OutfitItemCardProps {
  item: OutfitItem;
  label: string;
}

function OutfitItemCard({ item, label }: OutfitItemCardProps) {
  const [imageError, setImageError] = useState(false);
  
  // 构建完整的图片 URL
  const getImageUrl = () => {
    if (!item.image_url) return null;
    // 如果已经是完整 URL，直接返回
    if (item.image_url.startsWith('http')) return item.image_url;
    // 确保以 / 开头
    const path = item.image_url.startsWith('/') ? item.image_url : `/${item.image_url}`;
    return `http://localhost:8000${path}`;
  };
  
  const imageUrl = getImageUrl();
  
  const handleImageError = () => {
    console.warn('[OutfitItemCard] 图片加载失败:', imageUrl);
    setImageError(true);
  };
  
  return (
    <motion.div
      whileHover={{ scale: 1.03, y: -2 }}
      transition={{ duration: 0.2 }}
      className="text-center group"
    >
      <div className="relative w-full aspect-square rounded-leaf overflow-hidden 
                      bg-gradient-to-br from-linen-100 to-sage-50 mb-3 
                      shadow-soft group-hover:shadow-lifted transition-shadow duration-300">
        {/* 图片 - 仅在有 URL 且未出错时显示 */}
        {imageUrl && !imageError ? (
          <img
            src={imageUrl}
            alt={item.name}
            className="w-full h-full object-cover"
            onError={handleImageError}
          />
        ) : null}
        
        {/* Fallback emoji - 图片加载失败或无图片时显示 */}
        <div 
          className={cn(
            "absolute inset-0 flex items-center justify-center text-5xl",
            imageUrl && !imageError && "opacity-0"
          )}
        >
          {getClothesEmoji(item.type)}
        </div>
        
        {/* 柔和渐变遮罩 */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
      <p className="text-xs text-sage-500 font-medium">{label}</p>
      <p className="text-sm font-semibold text-forest-800 truncate">{item.name}</p>
      <p className="text-xs text-sage-400">{item.color}</p>
    </motion.div>
  );
}

// 获取衣服 Emoji
function getClothesEmoji(type: string) {
  const emojiMap: Record<string, string> = {
    'T恤': '👕',
    '衬衫': '👔',
    '卫衣': '🧥',
    '毛衣': '🧶',
    '外套': '🧥',
    '夹克': '🧥',
    '大衣': '🧥',
    '牛仔裤': '👖',
    '裤子': '👖',
    '短裤': '🩳',
    '裙子': '👗',
    '运动鞋': '👟',
    '皮鞋': '👞',
    '凉鞋': '🩴',
    '帽子': '🧢',
  };
  return emojiMap[type] || '👕';
}

// 穿搭方案卡片
interface OutfitPlanCardProps {
  onClick?: () => void;
  isSelected?: boolean;
}

export function OutfitPlanCard({ onClick, isSelected }: OutfitPlanCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={cn(
        'nature-card p-4 cursor-pointer transition-all duration-200',
        isSelected && 'ring-2 ring-moss-400/50'
      )}
    >
      <div className="flex items-center gap-4">
        <div className="grid grid-cols-3 gap-2 w-24">
          {[1, 2, 3].map((i) => (
            <div key={i} className="aspect-square bg-gradient-to-br from-linen-100 to-sage-100 rounded-lg" />
          ))}
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-forest-800 mb-1">穿搭方案</h4>
          <p className="text-sm text-sage-500 mb-2">适合日常通勤</p>
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 text-sunrise-400 fill-sunrise-400" />
            <span className="text-sm text-sage-600">8.5</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// 穿衣建议标签
interface DressingTipProps {
  tips: Array<{ type: string; level: string; suggestion: string }>;
}

export function DressingTips({ tips }: DressingTipProps) {
  return (
    <div className="space-y-3">
      {tips.map((tip, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
          className="nature-card p-4"
        >
          <div className="flex items-start gap-3">
            <span className="text-3xl">{getTipEmoji(tip.type)}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-semibold text-forest-800">{tip.level}</span>
                <span className={cn(
                  'text-xs px-2 py-0.5 rounded-full',
                  getTipBgColor(tip.type)
                )}>
                  {tip.type}
                </span>
              </div>
              <p className="text-sm text-sage-600">{tip.suggestion}</p>
            </div>
          </div>
        </motion.div>
      ))}
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

function getTipBgColor(type: string): string {
  const colorMap: Record<string, string> = {
    'cold': 'bg-sky-100 text-sky-700',
    'cool': 'bg-earth-100 text-earth-700',
    'comfortable': 'bg-moss-100 text-moss-700',
    'hot': 'bg-sunrise-100 text-sunrise-700',
    'rain': 'bg-sky-100 text-sky-700',
    'snow': 'bg-mist-100 text-mist-700',
    'windy': 'bg-sage-100 text-sage-700',
    'uv': 'bg-sunrise-100 text-sunrise-700',
    'humid': 'bg-sky-100 text-sky-700',
    'dry': 'bg-linen-100 text-linen-700',
  };
  return colorMap[type] || 'bg-sage-100 text-sage-700';
}

export default OutfitCard;
