'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, X, Trash2, Edit2, Filter, Search, 
  Shirt, Tag, Palette, Layers, Sun, Check, 
  Thermometer, Clock, Sparkles, AlertCircle, ChevronDown
} from 'lucide-react';
import { cn } from '@/utils';
import type { Clothes, ClothesAnalysis } from '@/types';

interface ClothesCardProps {
  clothes: Clothes;
  onDelete?: (id: number) => void;
  onEdit?: (clothes: Clothes) => void;
}

export function ClothesCard({ clothes, onDelete, onEdit }: ClothesCardProps) {
  const [imageError, setImageError] = useState(false);
  
  // 调试日志
  console.log('[ClothesCard] 渲染衣服:', { 
    id: clothes.id, 
    name: clothes.name,
    image_url: clothes.image_url,
    type: clothes.type 
  });
  
  // 构建完整的图片 URL（确保使用 http://localhost:8000 作为基础）
  const getImageUrl = () => {
    if (!clothes.image_url) return null;
    // 如果已经是完整 URL，直接返回
    if (clothes.image_url.startsWith('http')) return clothes.image_url;
    // 否则拼接后端地址
    return `http://localhost:8000${clothes.image_url}`;
  };
  
  const imageUrl = getImageUrl();
  
  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="glass-card overflow-hidden group"
    >
      {/* 图片 */}
      <div className="relative aspect-square bg-gray-100">
        {imageUrl && !imageError ? (
          <img
            src={imageUrl}
            alt={clothes.name || '衣服'}
            className="w-full h-full object-cover"
            onError={() => {
              console.error('[ClothesCard] 图片加载失败:', imageUrl);
              setImageError(true);
            }}
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-5xl bg-gray-50">
            {getClothesEmoji(clothes.type)}
            {imageError && imageUrl && (
              <span className="text-xs text-gray-400 mt-2">图片加载失败</span>
            )}
          </div>
        )}
        
        {/* 操作按钮 */}
        <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {onEdit && (
            <button
              onClick={() => onEdit(clothes)}
              className="p-2 bg-white/90 rounded-lg text-gray-600 hover:text-blue-600 transition-colors"
            >
              <Edit2 className="w-4 h-4" />
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(clothes.id)}
              className="p-2 bg-white/90 rounded-lg text-gray-600 hover:text-red-600 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* 信息 */}
      <div className="p-3">
        <h4 className="font-medium text-gray-800 truncate mb-1">
          {clothes.name || '未命名'}
        </h4>
        <div className="flex flex-wrap gap-1">
          {clothes.type && (
            <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">
              {clothes.type}
            </span>
          )}
          {clothes.color && (
            <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">
              {clothes.color}
            </span>
          )}
        </div>
        {clothes.season && (
          <div className="flex items-center gap-1 mt-2 text-xs text-gray-500">
            <Sun className="w-3 h-3" />
            {clothes.season}
          </div>
        )}
      </div>
    </motion.div>
  );
}

// 上传组件
interface UploadZoneProps {
  onUpload: (file: File) => void;
  loading?: boolean;
}

export function UploadZone({ onUpload, loading }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      onUpload(file);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
    }
  };

  return (
    <motion.div
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={cn(
        'border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer',
        isDragging
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
      )}
    >
      <input
        type="file"
        accept="image/*"
        onChange={handleChange}
        className="hidden"
        id="clothes-upload"
        disabled={loading}
      />
      <label htmlFor="clothes-upload" className="cursor-pointer">
        {loading ? (
          <div className="loading-dots mx-auto text-blue-500">
            <span></span>
            <span></span>
            <span></span>
          </div>
        ) : (
          <>
            <Upload className="w-12 h-12 mx-auto text-gray-400 mb-3" />
            <p className="text-gray-600 font-medium mb-1">
              点击或拖拽上传衣服图片
            </p>
            <p className="text-gray-400 text-sm">
              支持 JPG、PNG、WebP 格式
            </p>
          </>
        )}
      </label>
    </motion.div>
  );
}

// 分析结果展示 - 支持用户修正
interface AnalysisResultProps {
  analysis: ClothesAnalysis;
  onConfirm: (corrected: ClothesAnalysis) => void;
  onCancel: () => void;
  saving?: boolean; // 添加保存中状态
}

export function AnalysisResult({ analysis, onConfirm, onCancel, saving = false }: AnalysisResultProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedAnalysis, setEditedAnalysis] = useState<ClothesAnalysis>(analysis);
  
  // 当 analysis 更新时同步 editedAnalysis
  useEffect(() => {
    setEditedAnalysis(analysis);
  }, [analysis]);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    setIsEditing(false);
  };

  const handleConfirm = () => {
    onConfirm(editedAnalysis);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-500';
    if (confidence >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getConfidenceText = (confidence: number) => {
    if (confidence >= 0.8) return '高置信度';
    if (confidence >= 0.6) return '中等置信度';
    return '低置信度，请核对';
  };

  // 选项配置
  const typeOptions = ['T恤', '衬衫', '卫衣', '毛衣', '外套', '羽绒服', '牛仔裤', '休闲裤', '短裤', '裙子', '连衣裙', '运动鞋', '皮鞋', '靴子', '凉鞋', '帽子', '配饰'];
  const colorOptions = ['黑色', '白色', '灰色', '深灰色', '浅灰色', '深蓝色', '浅蓝色', '蓝色', '红色', '酒红色', '绿色', '军绿色', '棕色', '卡其色', '米白色', '粉色', '紫色', '黄色', '橙色'];
  const materialOptions = ['棉质', '涤纶', '羊毛', '羊绒', '针织', '牛仔布', '皮革', 'PU皮', '丝绸', '羽绒', '帆布', '亚麻', '莫代尔'];
  const thicknessOptions = ['极薄', '薄', '中等', '厚', '加绒', '羽绒级'];
  const styleOptions = ['休闲', '商务', '运动', '街头', '简约', '复古', '正式', '甜美', '帅气', '中性'];
  const seasonOptions = ['春', '夏', '秋', '冬', '四季通用'];
  const genderOptions = ['男', '女', '中性'];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-500" />
          AI 分析结果
        </h3>
        {!isEditing && (
          <button
            onClick={handleEdit}
            className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            <Edit2 className="w-4 h-4" />
            修正
          </button>
        )}
      </div>
      
      {isEditing ? (
        // 编辑模式
        <div className="space-y-4 mb-6">
          <EditableField 
            label="类型" 
            value={editedAnalysis.type} 
            options={typeOptions}
            onChange={(v) => setEditedAnalysis({...editedAnalysis, type: v})}
          />
          <EditableField 
            label="颜色" 
            value={editedAnalysis.color} 
            options={colorOptions}
            onChange={(v) => setEditedAnalysis({...editedAnalysis, color: v})}
          />
          <EditableField 
            label="材质" 
            value={editedAnalysis.material} 
            options={materialOptions}
            onChange={(v) => setEditedAnalysis({...editedAnalysis, material: v})}
          />
          <EditableField 
            label="厚度" 
            value={editedAnalysis.thickness} 
            options={thicknessOptions}
            onChange={(v) => setEditedAnalysis({...editedAnalysis, thickness: v})}
          />
          <EditableField 
            label="风格" 
            value={editedAnalysis.style} 
            options={styleOptions}
            onChange={(v) => setEditedAnalysis({...editedAnalysis, style: v})}
          />
          <EditableField 
            label="季节" 
            value={editedAnalysis.season || '四季通用'} 
            options={seasonOptions}
            onChange={(v) => setEditedAnalysis({...editedAnalysis, season: v})}
          />
          <EditableField 
            label="性别" 
            value={editedAnalysis.gender || '中性'} 
            options={genderOptions}
            onChange={(v) => setEditedAnalysis({...editedAnalysis, gender: v})}
          />
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-gray-500 mb-1 block">最低温度(°C)</label>
              <input
                type="number"
                value={editedAnalysis.temperature_min || 10}
                onChange={(e) => setEditedAnalysis({...editedAnalysis, temperature_min: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">最高温度(°C)</label>
              <input
                type="number"
                value={editedAnalysis.temperature_max || 25}
                onChange={(e) => setEditedAnalysis({...editedAnalysis, temperature_max: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
              />
            </div>
          </div>
        </div>
      ) : (
        // 展示模式
        <div className="grid grid-cols-2 gap-4 mb-6">
          <AnalysisItem icon={Shirt} label="类型" value={analysis.type} />
          <AnalysisItem icon={Palette} label="颜色" value={analysis.color} />
          <AnalysisItem icon={Layers} label="材质" value={analysis.material} />
          <AnalysisItem icon={Sun} label="厚度" value={analysis.thickness} />
          <AnalysisItem icon={Sparkles} label="风格" value={analysis.style || '未知'} />
          <AnalysisItem icon={Clock} label="季节" value={analysis.season || '四季通用'} />
        </div>
      )}
      
      {/* 置信度显示 */}
      <div className={`rounded-xl p-3 mb-4 ${analysis.confidence < 0.6 ? 'bg-yellow-50' : 'bg-blue-50'}`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            {analysis.confidence < 0.6 && <AlertCircle className="w-4 h-4 text-yellow-500" />}
            <span className="text-sm text-gray-600">
              {analysis.confidence < 0.6 ? '⚠️ ' + getConfidenceText(analysis.confidence) : 'AI 置信度'}
            </span>
          </div>
          <span className="text-sm font-medium text-blue-600">
            {(analysis.confidence * 100).toFixed(0)}%
          </span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className={`h-full rounded-full transition-all ${getConfidenceColor(analysis.confidence)}`}
            style={{ width: `${analysis.confidence * 100}%` }}
          />
        </div>
        {analysis.notes && (
          <p className="text-xs text-gray-500 mt-2">{analysis.notes}</p>
        )}
      </div>

      <div className="flex gap-3">
        <button
          onClick={onCancel}
          disabled={saving}
          className="flex-1 btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          取消
        </button>
        {isEditing ? (
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Check className="w-4 h-4" />
            保存修正
          </button>
        ) : (
          <button
            onClick={handleConfirm}
            disabled={saving}
            className="flex-1 btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                添加中...
              </>
            ) : (
              '添加到衣橱'
            )}
          </button>
        )}
      </div>
    </motion.div>
  );
}

// 可编辑字段组件
interface EditableFieldProps {
  label: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
}

function EditableField({ label, value, options, onChange }: EditableFieldProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');

  const filteredOptions = options.filter(opt => 
    opt.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <label className="text-xs text-gray-500 mb-1 block">{label}</label>
      <div className="relative">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm text-left flex items-center justify-between bg-white hover:border-blue-300 transition-colors"
        >
          <span>{value || '请选择'}</span>
          <ChevronDown className={cn('w-4 h-4 transition-transform', isOpen && 'rotate-180')} />
        </button>
        
        {isOpen && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-hidden">
            <div className="p-2 border-b border-gray-100">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="搜索..."
                className="w-full px-2 py-1 text-sm border border-gray-200 rounded focus:outline-none focus:border-blue-300"
              />
            </div>
            <div className="max-h-32 overflow-y-auto">
              {filteredOptions.map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => {
                    onChange(option);
                    setIsOpen(false);
                    setSearch('');
                  }}
                  className={cn(
                    'w-full px-3 py-2 text-left text-sm hover:bg-blue-50 transition-colors',
                    option === value && 'bg-blue-50 text-blue-600'
                  )}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

interface AnalysisItemProps {
  icon: React.ElementType;
  label: string;
  value: string;
}

function AnalysisItem({ icon: Icon, label, value }: AnalysisItemProps) {
  return (
    <div className="bg-gray-50 rounded-xl p-3">
      <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
        <Icon className="w-4 h-4" />
        {label}
      </div>
      <p className="font-medium text-gray-800">{value || '未知'}</p>
    </div>
  );
}

// 筛选器
interface FilterBarProps {
  filters: {
    type?: string;
    color?: string;
    season?: string;
    style?: string;
  };
  onFilterChange: (filters: any) => void;
  onReset: () => void;
}

export function FilterBar({ filters, onFilterChange, onReset }: FilterBarProps) {
  const types = ['T恤', '衬衫', '卫衣', '毛衣', '外套', '裤子', '裙子', '鞋子', '配饰'];
  const colors = ['黑色', '白色', '灰色', '蓝色', '红色', '绿色', '棕色', '卡其色', '粉色'];
  const seasons = ['春季', '夏季', '秋季', '冬季', '四季通用'];
  const styles = ['休闲', '商务', '运动', '街头', '简约', '复古'];

  const activeCount = Object.values(filters).filter(Boolean).length;

  return (
    <div className="glass-card p-4 mb-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-600" />
          <span className="font-medium text-gray-800">筛选</span>
          {activeCount > 0 && (
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
              {activeCount}
            </span>
          )}
        </div>
        {activeCount > 0 && (
          <button
            onClick={onReset}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            重置
          </button>
        )}
      </div>

      <div className="space-y-3">
        <FilterSection
          label="类型"
          options={types}
          value={filters.type}
          onChange={(v) => onFilterChange({ ...filters, type: v })}
        />
        <FilterSection
          label="颜色"
          options={colors}
          value={filters.color}
          onChange={(v) => onFilterChange({ ...filters, color: v })}
        />
        <FilterSection
          label="季节"
          options={seasons}
          value={filters.season}
          onChange={(v) => onFilterChange({ ...filters, season: v })}
        />
        <FilterSection
          label="风格"
          options={styles}
          value={filters.style}
          onChange={(v) => onFilterChange({ ...filters, style: v })}
        />
      </div>
    </div>
  );
}

interface FilterSectionProps {
  label: string;
  options: string[];
  value?: string;
  onChange: (value: string | undefined) => void;
}

function FilterSection({ label, options, value, onChange }: FilterSectionProps) {
  return (
    <div>
      <p className="text-sm text-gray-600 mb-2">{label}</p>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option}
            onClick={() => onChange(value === option ? undefined : option)}
            className={cn(
              'px-3 py-1 rounded-full text-sm transition-all',
              value === option
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            )}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
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
    '牛仔裤': '👖',
    '裤子': '👖',
    '短裤': '🩳',
    '裙子': '👗',
    '运动鞋': '👟',
    '皮鞋': '👞',
    '凉鞋': '🩴',
    '帽子': '🧢',
    '配饰': '💍',
  };
  return emojiMap[type] || '👕';
}

export default ClothesCard;
