'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shirt,
  Plus,
  Search,
  Filter,
  Grid,
  List,
  X,
  Check,
  Loader2,
} from 'lucide-react';
import { ClothesCard, UploadZone, AnalysisResult, FilterBar } from '@/components';
import { useWardrobe, useAuth } from '@/hooks';
import { cn } from '@/utils';
import type { Clothes, ClothesAnalysis } from '@/types';

export default function WardrobePage() {
  const { isAuthenticated } = useAuth();
  const {
    clothes,
    total,
    page,
    pageSize,
    filters,
    setPage,
    setFilters,
    resetFilters,
    refresh,
    uploadClothes,
    uploadClothesWithAnalysis,
    deleteClothes,
    analyzeClothes,
  } = useWardrobe();

  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showUpload, setShowUpload] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false); // 添加衣服保存中的状态
  const [analysisResult, setAnalysisResult] = useState<ClothesAnalysis | null>(null);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  const handleUpload = useCallback(async (file: File) => {
    if (!isAuthenticated) {
      window.location.href = '/login';
      return;
    }

    setUploading(true);
    setPreviewImage(URL.createObjectURL(file));

    try {
      // 先分析图片
      const analysisRes = await analyzeClothes(file);
      if (analysisRes.success) {
        setAnalysisResult(analysisRes.analysis);
      }
    } catch (error) {
      console.error('上传失败:', error);
    } finally {
      setUploading(false);
    }
  }, [isAuthenticated, analyzeClothes]);

  const handleConfirmAdd = useCallback(async (correctedAnalysis?: any) => {
    if (!previewImage) {
      console.error('[Wardrobe] 没有预览图片，无法添加');
      return;
    }

    // 使用用户修正后的数据或原始分析结果
    const finalAnalysis = correctedAnalysis || analysisResult;
    if (!finalAnalysis) {
      console.error('[Wardrobe] 没有分析结果，无法添加');
      return;
    }

    console.log('[Wardrobe] 开始添加衣服:', finalAnalysis);
    setSaving(true);

    try {
      // 从 previewImage blob URL 创建 File 对象
      const response = await fetch(previewImage);
      const blob = await response.blob();
      const file = new File([blob], 'clothes.jpg', { type: 'image/jpeg' });

      console.log('[Wardrobe] 图片文件准备完成，开始上传...');

      // 使用最终确认的分析结果（可能经过用户修正）
      const result = await uploadClothesWithAnalysis(file, finalAnalysis);
      
      console.log('[Wardrobe] 上传结果:', result);

      if (result.success) {
        console.log('[Wardrobe] ✅ 衣服添加成功!', result.clothes);
        
        // ✅ 清理所有状态
        setShowUpload(false);       // 关闭上传模态框
        setPreviewImage(null);      // 清空预览图
        setAnalysisResult(null);    // 清空分析结果
        
        // ✅ 刷新衣橱列表
        await refresh();
        
        // ✅ 显示成功提示（使用原生 alert 作为临时方案）
        alert('✅ 已成功添加到衣橱！');
      } else {
        console.error('[Wardrobe] ❌ 添加失败:', result.error);
        alert('❌ 添加失败: ' + (result.error || '未知错误'));
      }
    } catch (error) {
      console.error('[Wardrobe] ❌ 确认添加失败:', error);
      alert('❌ 添加失败: ' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setSaving(false);
    }
  }, [previewImage, analysisResult, uploadClothesWithAnalysis, refresh]);

  const handleCancelUpload = () => {
    setShowUpload(false);
    setPreviewImage(null);
    setAnalysisResult(null);
  };

  const handleDelete = async (id: number) => {
    if (confirm('确定要删除这件衣服吗？')) {
      const result = await deleteClothes(id);
      if (result.success) {
        console.log('[Wardrobe] ✅ 衣服删除成功!');
      } else {
        console.error('[Wardrobe] ❌ 删除失败:', result.error);
        alert('删除失败: ' + (result.error || '未知错误'));
      }
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="glass-card p-8 text-center max-w-md">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            <Shirt className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            登录管理衣橱
          </h2>
          <p className="text-gray-600 mb-6">
            登录后，您可以上传衣服图片，AI将自动识别分类
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
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
                <Shirt className="w-8 h-8" />
                我的衣橱
              </h1>
              <p className="opacity-90">共 {total} 件衣服</p>
            </div>
            <button
              onClick={() => setShowUpload(true)}
              className="flex items-center gap-2 px-4 py-2 bg-white text-blue-600 rounded-xl font-medium hover:bg-gray-100 transition-colors"
            >
              <Plus className="w-5 h-5" />
              添加衣服
            </button>
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* 工具栏 */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-xl transition-all',
                showFilters
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-white text-gray-700 shadow-sm'
              )}
            >
              <Filter className="w-4 h-4" />
              筛选
              {Object.values(filters).some(Boolean) && (
                <span className="w-2 h-2 bg-blue-500 rounded-full" />
              )}
            </button>
          </div>
          
          <div className="flex items-center gap-2 bg-white rounded-xl p-1 shadow-sm">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                'p-2 rounded-lg transition-all',
                viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400'
              )}
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                'p-2 rounded-lg transition-all',
                viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400'
              )}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 筛选器 */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <FilterBar
                filters={filters}
                onFilterChange={setFilters}
                onReset={resetFilters}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* 衣服列表 */}
        {clothes.length === 0 ? (
          <div className="glass-card p-12 text-center">
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
              <Shirt className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              衣橱空空如也
            </h3>
            <p className="text-gray-600 mb-6">
              点击上方按钮上传衣服图片，AI将自动识别分类
            </p>
            <button
              onClick={() => setShowUpload(true)}
              className="btn-primary inline-flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              添加第一件衣服
            </button>
          </div>
        ) : (
          <div className={cn(
            'grid gap-4',
            viewMode === 'grid'
              ? 'grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5'
              : 'grid-cols-1'
          )}>
            <AnimatePresence>
              {clothes.map((item) => (
                <ClothesCard
                  key={item.id}
                  clothes={item}
                  onDelete={handleDelete}
                />
              ))}
            </AnimatePresence>
          </div>
        )}

        {/* 分页 */}
        {total > pageSize && (
          <div className="flex justify-center gap-2 mt-8">
            {Array.from({ length: Math.ceil(total / pageSize) }).map((_, i) => (
              <button
                key={i}
                onClick={() => setPage(i + 1)}
                className={cn(
                  'w-10 h-10 rounded-xl font-medium transition-all',
                  page === i + 1
                    ? 'bg-blue-500 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-100'
                )}
              >
                {i + 1}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 上传模态框 */}
      <AnimatePresence>
        {showUpload && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={handleCancelUpload}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="glass-card w-full max-w-lg max-h-[90vh] overflow-y-auto p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-800">添加衣服</h3>
                <button
                  onClick={handleCancelUpload}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {!previewImage ? (
                <UploadZone onUpload={handleUpload} loading={uploading} />
              ) : (
                <div className="space-y-4">
                  {/* 预览图 */}
                  <div className="relative aspect-square rounded-xl overflow-hidden bg-gray-100">
                    <img
                      src={previewImage}
                      alt="预览"
                      className="w-full h-full object-contain"
                    />
                  </div>

                  {/* 分析结果 */}
                  {analysisResult && (
                    <AnalysisResult
                      analysis={analysisResult}
                      onConfirm={handleConfirmAdd}
                      onCancel={handleCancelUpload}
                      saving={saving}
                    />
                  )}
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* FAB 按钮 */}
      <button
        onClick={() => setShowUpload(true)}
        className="fixed right-4 bottom-24 md:right-8 md:bottom-8 w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 text-white shadow-lg shadow-blue-500/30 flex items-center justify-center hover:shadow-xl hover:scale-105 transition-all z-40"
      >
        <Plus className="w-6 h-6" />
      </button>
    </div>
  );
}
