'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/router';
import {
  User,
  Mail,
  Calendar,
  Shirt,
  Settings,
  LogOut,
  Edit2,
  Save,
  Star,
  X,
  ChevronRight,
  Sparkles,
  MapPin,
  Leaf,
  Flower2,
} from 'lucide-react';
import { OutfitCollageCard } from '@/components/Outfit/OutfitCollageCard';
import { useAuth } from '@/hooks';
import { authApi, profileApi, favoritesApi } from '@/services/api';
import { cn } from '@/utils';
import toast from 'react-hot-toast';

interface ProfileStats {
  clothes_count: number;
  favorites_count: number;
}

interface RecentFavorite {
  id: number;
  outfit_id: string;
  occasion: string;
  weather: string;
  created_at: string;
  outfit_data?: any;
}

export default function ProfilePage() {
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    email: user?.email || '',
    gender: user?.gender || '',
    style_preference: user?.style_preference || '',
    bio: user?.bio || '',
  });
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(true);
  const [stats, setStats] = useState<ProfileStats>({
    clothes_count: 0,
    favorites_count: 0,
  });
  const [recentFavorites, setRecentFavorites] = useState<RecentFavorite[]>([]);
  const [loadingFavorites, setLoadingFavorites] = useState(false);

  // 获取统计数据
  const fetchStats = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      setStatsLoading(true);
      const res = await profileApi.getStats();
      setStats(res.data);
    } catch (error) {
      console.error('获取统计数据失败:', error);
      // 使用衣橱 hook 中的数据作为备选
      const clothesCount = localStorage.getItem('clothes_count');
      if (clothesCount) {
        setStats(prev => ({ ...prev, clothes_count: parseInt(clothesCount) }));
      }
    } finally {
      setStatsLoading(false);
    }
  }, [isAuthenticated]);

  // 获取最近收藏
  const fetchRecentFavorites = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      setLoadingFavorites(true);
      const res = await favoritesApi.getList(1, 6);
      setRecentFavorites(res.data?.items || res.data || []);
    } catch (error) {
      console.error('获取最近收藏失败:', error);
    } finally {
      setLoadingFavorites(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchStats();
      fetchRecentFavorites();
    }
  }, [isAuthenticated, fetchStats, fetchRecentFavorites]);

  // 同步衣橱数量
  useEffect(() => {
    const handleWardrobeUpdate = () => {
      fetchStats();
    };
    
    window.addEventListener('wardrobe-updated', handleWardrobeUpdate);
    return () => window.removeEventListener('wardrobe-updated', handleWardrobeUpdate);
  }, [fetchStats]);

  const handleSave = async () => {
    setLoading(true);
    try {
      await authApi.updateProfile(formData);
      toast.success('保存成功！');
      setEditing(false);
    } catch (error) {
      toast.error('保存失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      email: user?.email || '',
      gender: user?.gender || '',
      style_preference: user?.style_preference || '',
      bio: user?.bio || '',
    });
    setEditing(false);
  };

  const navigateTo = (path: string) => {
    router.push(path);
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-nature">
        {/* 装饰植物 */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 0.6, x: 0 }}
          className="absolute top-20 left-10 pointer-events-none hidden md:block"
        >
          <Leaf className="w-24 h-24 text-forest-200 rotate-[-30deg]" />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 0.6, x: 0 }}
          transition={{ delay: 0.2 }}
          className="absolute bottom-20 right-10 pointer-events-none hidden md:block"
        >
          <Flower2 className="w-20 h-20 text-sage-200 rotate-[20deg]" />
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="nature-card p-8 text-center max-w-md w-full"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring' }}
            className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-moss-400 to-forest-500 flex items-center justify-center shadow-warm"
          >
            <User className="w-10 h-10 text-white" />
          </motion.div>
          <h2 className="text-2xl font-bold text-forest-800 mb-3">
            登录查看个人中心
          </h2>
          <p className="text-sage-600 mb-8">
            登录后管理您的个人资料和偏好设置
          </p>
          <a 
            href="/login" 
            className="btn-primary inline-flex items-center justify-center gap-2 w-full"
          >
            立即登录
            <ChevronRight className="w-4 h-4" />
          </a>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-20 md:pb-8 bg-gradient-nature">
      {/* 装饰植物 */}
      <motion.div
        initial={{ opacity: 0, x: -30 }}
        animate={{ opacity: 0.5, x: 0 }}
        className="absolute top-40 left-8 pointer-events-none hidden lg:block"
      >
        <Leaf className="w-32 h-32 text-forest-200 rotate-[-20deg] animate-sway" />
      </motion.div>
      <motion.div
        initial={{ opacity: 0, x: 30 }}
        animate={{ opacity: 0.5, x: 0 }}
        transition={{ delay: 0.3 }}
        className="absolute top-60 right-12 pointer-events-none hidden lg:block"
      >
        <Flower2 className="w-24 h-24 text-sage-200 rotate-[15deg] animate-sway animation-delay-1000" />
      </motion.div>
      
      {/* 头部 */}
      <section className="relative bg-gradient-to-br from-forest-600 via-forest-500 to-moss-500 p-6 md:p-8 text-white overflow-hidden">
        {/* 背景装饰 */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-4 right-10">
            <Leaf className="w-40 h-40 text-white rotate-12" />
          </div>
          <div className="absolute bottom-2 left-1/4">
            <Flower2 className="w-24 h-24 text-white -rotate-12" />
          </div>
        </div>
        
        <div className="max-w-7xl mx-auto relative">
          <motion.h1 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-2xl md:text-3xl font-bold mb-6 flex items-center gap-3"
          >
            <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <User className="w-5 h-5" />
            </div>
            个人中心
          </motion.h1>
          
          {/* 用户信息卡片 */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="nature-card p-5 md:p-6"
          >
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-5">
              <motion.div 
                whileHover={{ scale: 1.05 }}
                className="w-20 h-20 rounded-2xl bg-gradient-to-br from-moss-400 to-forest-500 flex items-center justify-center text-white text-3xl font-bold shadow-warm flex-shrink-0"
              >
                {user?.username?.[0]?.toUpperCase() || 'U'}
              </motion.div>
              <div className="flex-1 w-full">
                <h2 className="text-xl md:text-2xl font-bold text-forest-800 mb-1">{user?.username}</h2>
                <p className="text-sage-600 text-sm flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  注册于 {new Date(user?.created_at || '').toLocaleDateString('zh-CN')}
                </p>
                {user?.style_preference && (
                  <span className="inline-flex items-center gap-1 mt-2 px-3 py-1 bg-moss-50 text-moss-700 rounded-full text-sm font-medium">
                    <Leaf className="w-3 h-3" />
                    风格：{user.style_preference}
                  </span>
                )}
              </div>
              {!editing && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setEditing(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-forest-500 text-white rounded-xl hover:bg-forest-600 transition-all shadow-md hover:shadow-lg w-full sm:w-auto justify-center"
                >
                  <Edit2 className="w-4 h-4" />
                  编辑资料
                </motion.button>
              )}
            </div>
          </motion.div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8 space-y-6">
        {/* 编辑表单 */}
        {editing ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="nature-card p-6"
          >
            <h3 className="text-lg font-semibold text-forest-800 mb-5 flex items-center gap-2">
              <Edit2 className="w-5 h-5 text-moss-500" />
              编辑个人资料
            </h3>
            
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  <Mail className="w-4 h-4 inline mr-1" />
                  邮箱
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="input-field"
                  placeholder="输入邮箱"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  性别
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {['男', '女', '保密'].map((g) => (
                    <motion.button
                      key={g}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setFormData({ ...formData, gender: g })}
                      className={cn(
                        'py-3 rounded-xl transition-all font-medium',
                        formData.gender === g
                          ? 'bg-gradient-to-r from-moss-500 to-forest-500 text-white shadow-md'
                          : 'bg-sage-50 text-sage-700 hover:bg-sage-100'
                      )}
                    >
                      {g}
                    </motion.button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  <Sparkles className="w-4 h-4 inline mr-1" />
                  穿搭风格
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {['简约', '休闲', '运动', '商务', '街头', '复古'].map((style) => (
                    <motion.button
                      key={style}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setFormData({ ...formData, style_preference: style })}
                      className={cn(
                        'py-2.5 px-3 rounded-xl text-sm transition-all font-medium',
                        formData.style_preference === style
                          ? 'bg-gradient-to-r from-moss-500 to-forest-500 text-white shadow-md'
                          : 'bg-sage-50 text-sage-700 hover:bg-sage-100'
                      )}
                    >
                      {style}
                    </motion.button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  个人简介
                </label>
                <textarea
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  className="input-field resize-none"
                  rows={3}
                  placeholder="介绍一下自己..."
                />
              </div>

              <div className="flex flex-col sm:flex-row gap-3 pt-2">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleCancel}
                  className="btn-secondary flex items-center justify-center gap-2 order-2 sm:order-1"
                >
                  <X className="w-4 h-4" />
                  取消
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSave}
                  disabled={loading}
                  className={cn(
                    'btn-primary flex items-center justify-center gap-2 order-1 sm:order-2',
                    loading && 'opacity-70 cursor-not-allowed'
                  )}
                >
                  <Save className="w-4 h-4" />
                  保存修改
                </motion.button>
              </div>
            </div>
          </motion.div>
        ) : (
          <>
            {/* 统计卡片 - 双列布局 */}
            <div className="grid grid-cols-2 gap-4">
              {/* 衣服数量 */}
              <motion.button
                whileHover={{ scale: 1.02, y: -4 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => navigateTo('/wardrobe')}
                className="nature-card p-5 text-center relative group overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-moss-50/80 to-forest-50/80 opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative">
                  <motion.div 
                    whileHover={{ rotate: 5 }}
                    className="w-14 h-14 mx-auto mb-3 rounded-2xl bg-gradient-to-br from-moss-400 to-forest-500 flex items-center justify-center shadow-warm group-hover:shadow-lg transition-shadow"
                  >
                    <Shirt className="w-7 h-7 text-white" />
                  </motion.div>
                  {statsLoading ? (
                    <div className="h-8 w-16 mx-auto bg-sage-100 rounded-lg animate-pulse" />
                  ) : (
                    <p className="text-3xl font-bold text-forest-800 mb-1">{stats.clothes_count}</p>
                  )}
                  <p className="text-sm text-sage-600">我的衣橱</p>
                </div>
                <ChevronRight className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-moss-500 opacity-0 group-hover:opacity-100 transition-opacity" />
              </motion.button>

              {/* 收藏穿搭 */}
              <motion.button
                whileHover={{ scale: 1.02, y: -4 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => navigateTo('/favorites')}
                className="nature-card p-5 text-center relative group overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-sunrise-50/80 to-sunrise-100/50 opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative">
                  <motion.div 
                    whileHover={{ rotate: -5 }}
                    className="w-14 h-14 mx-auto mb-3 rounded-2xl bg-gradient-to-br from-sunrise-400 to-sunset-500 flex items-center justify-center shadow-warm group-hover:shadow-lg transition-shadow"
                  >
                    <Star className="w-7 h-7 text-white" />
                  </motion.div>
                  {statsLoading ? (
                    <div className="h-8 w-16 mx-auto bg-sage-100 rounded-lg animate-pulse" />
                  ) : (
                    <p className="text-3xl font-bold text-forest-800 mb-1">{stats.favorites_count}</p>
                  )}
                  <p className="text-sm text-sage-600">收藏搭配</p>
                </div>
                <ChevronRight className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-sunrise-500 opacity-0 group-hover:opacity-100 transition-opacity" />
              </motion.button>
            </div>

            {/* 最近收藏 - 时尚穿搭拼贴卡片 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="nature-card p-5"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-forest-800 flex items-center gap-2">
                  <Star className="w-5 h-5 text-sunrise-500" />
                  我的收藏穿搭
                </h3>
                <motion.button
                  whileHover={{ x: 4 }}
                  onClick={() => navigateTo('/favorites')}
                  className="text-sm text-moss-600 hover:text-moss-700 flex items-center gap-1 font-medium"
                >
                  查看全部
                  <ChevronRight className="w-4 h-4" />
                </motion.button>
              </div>
              
              {loadingFavorites ? (
                <div className="flex items-center justify-center py-12">
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-8 h-8 border-3 border-moss-400 border-t-transparent rounded-full animate-spin" />
                    <p className="text-sm text-sage-500">加载穿搭中...</p>
                  </div>
                </div>
              ) : recentFavorites.length > 0 ? (
                <div className="relative">
                  {/* 横向滚动容器 */}
                  <div className="overflow-x-auto pb-4 -mx-2 px-2 scrollbar-hide">
                    <div className="flex gap-4">
                      {recentFavorites.slice(0, 6).map((fav, index) => {
                        const outfitData = fav.outfit_data || {};
                        return (
                          <motion.div
                            key={fav.id || fav.outfit_id}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                          >
                            <OutfitCollageCard
                              id={fav.id}
                              top={outfitData.top}
                              bottom={outfitData.bottom}
                              pants={outfitData.pants}
                              shoes={outfitData.shoes}
                              jacket={outfitData.jacket}
                              scene={fav.occasion || outfitData.scene}
                              weather={fav.weather}
                              temperature={outfitData.temperature}
                              reason={outfitData.reason}
                              score={outfitData.score}
                              onClick={() => navigateTo(`/favorites?id=${fav.id}`)}
                              showDetails={true}
                            />
                          </motion.div>
                        );
                      })}
                    </div>
                  </div>
                  
                  {/* 滚动提示 */}
                  {recentFavorites.length > 2 && (
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-12 h-full bg-gradient-to-l from-white/90 to-transparent pointer-events-none hidden md:block" />
                  )}
                </div>
              ) : (
                <div className="text-center py-12 bg-gradient-to-br from-linen-50 to-sage-50 rounded-2xl">
                  <motion.div
                    animate={{ 
                      y: [0, -8, 0],
                      rotate: [-5, 5, -5]
                    }}
                    transition={{ 
                      repeat: Infinity, 
                      duration: 3,
                      ease: "easeInOut"
                    }}
                    className="inline-block"
                  >
                    <Sparkles className="w-16 h-16 text-moss-300 mb-4" />
                  </motion.div>
                  <p className="text-forest-600 font-medium mb-1">还没有收藏任何穿搭</p>
                  <p className="text-sage-500 text-sm mb-4">去发现适合你的时尚搭配吧</p>
                  <motion.button
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => navigateTo('/recommend')}
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-moss-500 to-forest-500 text-white rounded-full shadow-md hover:shadow-lg transition-all font-medium"
                  >
                    <Sparkles className="w-4 h-4" />
                    获取AI推荐
                  </motion.button>
                </div>
              )}
            </motion.div>

            {/* 快速操作入口 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="nature-card p-4"
            >
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <motion.button
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => navigateTo('/wardrobe')}
                  className="flex items-center gap-3 p-4 bg-gradient-to-r from-moss-50 to-sage-50 rounded-2xl hover:from-moss-100 hover:to-sage-100 transition-all shadow-sm hover:shadow-md"
                >
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-moss-500 to-forest-500 flex items-center justify-center shadow-md flex-shrink-0">
                    <Shirt className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-left min-w-0">
                    <p className="font-semibold text-forest-800 truncate">我的衣橱</p>
                    <p className="text-xs text-sage-600">{stats.clothes_count} 件衣服</p>
                  </div>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => navigateTo('/recommend')}
                  className="flex items-center gap-3 p-4 bg-gradient-to-r from-sunrise-50 to-sunrise-100 rounded-2xl hover:from-sunrise-100 hover:to-sunrise-150 transition-all shadow-sm hover:shadow-md"
                >
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-sunrise-400 to-sunset-500 flex items-center justify-center shadow-md flex-shrink-0">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-left min-w-0">
                    <p className="font-semibold text-forest-800 truncate">AI 推荐</p>
                    <p className="text-xs text-sage-600">获取新穿搭</p>
                  </div>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => navigateTo('/weather')}
                  className="flex items-center gap-3 p-4 bg-gradient-to-r from-sky-50 to-mist-50 rounded-2xl hover:from-sky-100 hover:to-mist-100 transition-all shadow-sm hover:shadow-md"
                >
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-sky-400 to-sky-500 flex items-center justify-center shadow-md flex-shrink-0">
                    <MapPin className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-left min-w-0">
                    <p className="font-semibold text-forest-800 truncate">天气设置</p>
                    <p className="text-xs text-sage-600">管理城市</p>
                  </div>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => navigateTo('/chat')}
                  className="flex items-center gap-3 p-4 bg-gradient-to-r from-moss-50 to-moss-100 rounded-2xl hover:from-moss-100 hover:to-moss-150 transition-all shadow-sm hover:shadow-md"
                >
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-forest-500 to-moss-600 flex items-center justify-center shadow-md flex-shrink-0">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-left min-w-0">
                    <p className="font-semibold text-forest-800 truncate">AI 助手</p>
                    <p className="text-xs text-sage-600">智能咨询</p>
                  </div>
                </motion.button>
              </div>
            </motion.div>

            {/* 偏好设置 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="nature-card p-5"
            >
              <h3 className="text-lg font-semibold text-forest-800 mb-4 flex items-center gap-2">
                <Settings className="w-5 h-5 text-sage-500" />
                偏好设置
              </h3>
              
              <div className="space-y-2">
                <motion.button
                  whileHover={{ x: 4 }}
                  onClick={() => setEditing(true)}
                  className="w-full flex items-center justify-between p-4 bg-sage-50 rounded-2xl hover:bg-sage-100 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-moss-100 to-moss-200 flex items-center justify-center">
                      <User className="w-5 h-5 text-moss-600" />
                    </div>
                    <span className="text-sage-700 font-medium">个人信息</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sage-400 text-sm">{user?.username || ''}</span>
                    <ChevronRight className="w-4 h-4 text-sage-400" />
                  </div>
                </motion.button>
                
                <motion.button
                  whileHover={{ x: 4 }}
                  onClick={() => setEditing(true)}
                  className="w-full flex items-center justify-between p-4 bg-sage-50 rounded-2xl hover:bg-sage-100 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sunrise-100 to-sunrise-200 flex items-center justify-center">
                      <Sparkles className="w-5 h-5 text-sunset-600" />
                    </div>
                    <span className="text-sage-700 font-medium">穿搭风格</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sage-400 text-sm">{user?.style_preference || '未设置'}</span>
                    <ChevronRight className="w-4 h-4 text-sage-400" />
                  </div>
                </motion.button>
                
                <motion.button
                  whileHover={{ x: 4 }}
                  onClick={() => navigateTo('/weather')}
                  className="w-full flex items-center justify-between p-4 bg-sage-50 rounded-2xl hover:bg-sage-100 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-100 to-sky-200 flex items-center justify-center">
                      <MapPin className="w-5 h-5 text-sky-600" />
                    </div>
                    <span className="text-sage-700 font-medium">默认城市</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sage-400 text-sm">北京</span>
                    <ChevronRight className="w-4 h-4 text-sage-400" />
                  </div>
                </motion.button>
              </div>
            </motion.div>

            {/* 操作按钮 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="nature-card p-5"
            >
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={logout}
                className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-sage-50 to-earth-50 text-earth-600 rounded-2xl hover:from-sage-100 hover:to-earth-100 transition-all font-medium"
              >
                <LogOut className="w-5 h-5" />
                退出登录
              </motion.button>
            </motion.div>
          </>
        )}
      </div>
    </div>
  );
}
