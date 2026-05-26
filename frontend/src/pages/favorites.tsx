'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/router';
import {
  ArrowLeft,
  Star,
  Trash2,
  Heart,
  ShoppingBag,
  Info,
  Sparkles,
  Loader2,
} from 'lucide-react';
import { favoritesApi } from '@/services/api';
import { useAuth } from '@/hooks';
import { cn } from '@/utils';
import toast from 'react-hot-toast';

interface FavoriteItem {
  id: number;
  name?: string;
  type?: string;
  color?: string;
  image_url?: string;
}

interface FavoriteOutfitData {
  id?: string;
  top?: FavoriteItem;
  pants?: FavoriteItem;
  shoes?: FavoriteItem;
  jacket?: FavoriteItem;
  accessories?: any[];
  reason?: string;
  score?: number;
  scene?: string;
  tips?: string[];
}

interface FavoriteOutfit {
  id: number;
  outfit_id: string;
  outfit_data: FavoriteOutfitData;
  scene: string;
  weather?: string;
  temperature?: string;
  created_at: string;
}

interface OutfitItemData {
  id: number;
  name: string;
  type: string;
  color: string;
  image_url: string;
}

export default function FavoritesPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [favorites, setFavorites] = useState<FavoriteOutfit[]>([]);
  const [removingId, setRemovingId] = useState<string | null>(null);

  // 获取收藏列表
  const fetchFavorites = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      setLoading(true);
      const res = await favoritesApi.getList(1, 100);
      setFavorites(res.data || []);
    } catch (error) {
      console.error('获取收藏列表失败:', error);
      toast.error('获取收藏列表失败');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchFavorites();
    }
  }, [isAuthenticated, fetchFavorites]);

  // 取消收藏
  const handleRemove = async (outfitId: string) => {
    setRemovingId(outfitId);
    try {
      await favoritesApi.remove(outfitId);
      setFavorites(prev => prev.filter(f => f.outfit_id !== outfitId));
      toast.success('已取消收藏');
      // 通知其他页面刷新
      window.dispatchEvent(new Event('wardrobe-updated'));
    } catch (error) {
      console.error('取消收藏失败:', error);
      toast.error('取消收藏失败');
    } finally {
      setRemovingId(null);
    }
  };

  // 获取图片完整 URL
  const getImageUrl = (imageUrl?: string) => {
    if (!imageUrl) return null;
    if (imageUrl.startsWith('http')) return imageUrl;
    // 确保以 / 开头
    const path = imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`;
    return `http://localhost:8000${path}`;
  };

  // 获取衣服 Emoji
  const getClothesEmoji = (type?: string) => {
    if (!type) return '👕';
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
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="glass-card p-8 text-center max-w-md">
          <Star className="w-16 h-16 mx-auto text-yellow-400 mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            登录查看收藏
          </h2>
          <p className="text-gray-600 mb-6">
            登录后可查看您收藏的穿搭方案
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
      {/* 头部 */}
      <section className="gradient-bg p-6 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-4 mb-4">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-white/10 rounded-xl transition-colors"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Star className="w-8 h-8" />
              我的收藏
            </h1>
          </div>
          <p className="opacity-90">共 {favorites.length} 套收藏穿搭</p>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {loading ? (
          // Loading 状态
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        ) : favorites.length === 0 ? (
          // 空状态
          <div className="glass-card p-12 text-center">
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-yellow-50 flex items-center justify-center">
              <Heart className="w-10 h-10 text-yellow-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              还没有收藏的穿搭
            </h3>
            <p className="text-gray-600 mb-6">
              去 AI 推荐页面，发现喜欢的穿搭并收藏它们
            </p>
            <a href="/recommend" className="btn-primary inline-flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              获取推荐
            </a>
          </div>
        ) : (
          // 收藏列表
          <div className="space-y-6">
            {favorites.map((favorite, index) => (
              <motion.div
                key={favorite.outfit_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass-card overflow-hidden"
              >
                {/* 头部 */}
                <div className="gradient-bg p-4 text-white">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Star className="w-5 h-5 text-yellow-300 fill-yellow-300" />
                      <span className="font-semibold">
                        {favorite.scene || favorite.outfit_data?.scene || '收藏穿搭'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm opacity-80">
                        {favorite.outfit_data?.score?.toFixed(1) || '0.0'} 分
                      </span>
                      <button
                        onClick={() => handleRemove(favorite.outfit_id)}
                        disabled={removingId === favorite.outfit_id}
                        className="p-2 hover:bg-white/10 rounded-lg transition-colors disabled:opacity-50"
                      >
                        {removingId === favorite.outfit_id ? (
                          <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                          <Trash2 className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* 穿搭展示 */}
                <div className="p-6">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                    {favorite.outfit_data?.top && (
                      <OutfitItemCard
                        item={favorite.outfit_data.top}
                        label="上衣"
                        getImageUrl={getImageUrl}
                        getEmoji={getClothesEmoji}
                      />
                    )}
                    {favorite.outfit_data?.pants && (
                      <OutfitItemCard
                        item={favorite.outfit_data.pants}
                        label="裤子"
                        getImageUrl={getImageUrl}
                        getEmoji={getClothesEmoji}
                      />
                    )}
                    {favorite.outfit_data?.shoes && (
                      <OutfitItemCard
                        item={favorite.outfit_data.shoes}
                        label="鞋子"
                        getImageUrl={getImageUrl}
                        getEmoji={getClothesEmoji}
                      />
                    )}
                    {favorite.outfit_data?.jacket && (
                      <OutfitItemCard
                        item={favorite.outfit_data.jacket}
                        label="外套"
                        getImageUrl={getImageUrl}
                        getEmoji={getClothesEmoji}
                      />
                    )}
                  </div>

                  {/* 推荐理由 */}
                  {favorite.outfit_data?.reason && (
                    <div className="bg-blue-50 rounded-xl p-4 mb-4">
                      <div className="flex items-start gap-3">
                        <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                        <div>
                          <p className="text-blue-800 font-medium mb-1">推荐理由</p>
                          <p className="text-blue-600 text-sm whitespace-pre-wrap">{favorite.outfit_data.reason}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* 场景和天气信息 */}
                  <div className="flex items-center gap-2 pt-4 border-t border-gray-100 flex-wrap">
                    <ShoppingBag className="w-4 h-4 text-gray-500" />
                    <span className="text-gray-600 text-sm">适合场景：</span>
                    <span className="tag">{favorite.scene || favorite.outfit_data?.scene}</span>
                    {favorite.weather && (
                      <>
                        <span className="text-gray-400">|</span>
                        <span className="text-gray-500 text-sm">{favorite.weather}</span>
                      </>
                    )}
                    {favorite.temperature && (
                      <>
                        <span className="text-gray-400">|</span>
                        <span className="text-gray-500 text-sm">{favorite.temperature}</span>
                      </>
                    )}
                    <span className="text-gray-400 text-sm ml-auto">
                      {new Date(favorite.created_at).toLocaleDateString('zh-CN')}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface OutfitItemCardProps {
  item: FavoriteItem;
  label: string;
  getImageUrl: (url?: string) => string | null;
  getEmoji: (type?: string) => string;
}

function OutfitItemCard({ item, label, getImageUrl, getEmoji }: OutfitItemCardProps) {
  const [imageError, setImageError] = useState(false);
  const imageUrl = getImageUrl(item.image_url);
  
  const handleImageError = () => {
    console.warn('[收藏图片] 加载失败:', imageUrl);
    setImageError(true);
  };

  return (
    <div className="text-center">
      <div className="relative w-full aspect-square rounded-xl overflow-hidden bg-gray-100 mb-2 shadow-soft">
        {/* 图片 */}
        {imageUrl && !imageError ? (
          <img
            src={imageUrl}
            alt={item.name || label}
            className="w-full h-full object-cover"
            onError={handleImageError}
          />
        ) : null}
        
        {/* Fallback emoji - 图片加载失败或无图片时显示 */}
        <div 
          className={cn(
            "absolute inset-0 flex items-center justify-center text-4xl bg-gradient-to-br from-gray-50 to-gray-100",
            imageUrl && !imageError && "opacity-0"  // 图片正常加载时隐藏 emoji
          )}
        >
          {getEmoji(item.type)}
        </div>
      </div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-medium text-gray-800 truncate">{item.name || '未知'}</p>
      <p className="text-xs text-gray-400">{item.color || ''}</p>
    </div>
  );
}
