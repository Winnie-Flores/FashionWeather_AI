'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Heart, 
  Star, 
  Sun, 
  Cloud, 
  CloudRain, 
  Snowflake, 
  Wind,
  MapPin,
  Shirt,
  Eye,
  Sparkles
} from 'lucide-react';
import { cn } from '@/utils';
import Image from 'next/image';

interface OutfitItem {
  name?: string;
  type?: string;
  color?: string;
  image_url?: string;
}

interface OutfitCollageCardProps {
  id?: string | number;
  top?: OutfitItem;
  bottom?: OutfitItem;
  pants?: OutfitItem;
  shoes?: OutfitItem;
  jacket?: OutfitItem;
  scene?: string;
  weather?: string;
  temperature?: number;
  reason?: string;
  score?: number;
  onClick?: () => void;
  showDetails?: boolean;
}

// 天气图标映射
const WeatherIcon = ({ weather, className }: { weather: string; className?: string }) => {
  const w = weather?.toLowerCase() || '';
  if (w.includes('雨')) return <CloudRain className={className} />;
  if (w.includes('雪')) return <Snowflake className={className} />;
  if (w.includes('阴')) return <Cloud className={className} />;
  if (w.includes('风')) return <Wind className={className} />;
  return <Sun className={className} />;
};

// 场景颜色映射
const sceneColors: Record<string, { bg: string; text: string }> = {
  '通勤': { bg: 'bg-sky-100', text: 'text-sky-700' },
  '约会': { bg: 'bg-sunrise-100', text: 'text-sunset-600' },
  '日常': { bg: 'bg-moss-100', text: 'text-forest-600' },
  '运动': { bg: 'bg-emerald-100', text: 'text-emerald-700' },
  '派对': { bg: 'bg-purple-100', text: 'text-purple-700' },
  '旅行': { bg: 'bg-earth-100', text: 'text-earth-700' },
  '商务': { bg: 'bg-gray-100', text: 'text-gray-700' },
};

// 获取默认图片
const DEFAULT_IMAGE = '/images/default-clothes.png';

// 单品图片组件
function OutfitItemImage({ 
  item, 
  className,
  alt 
}: { 
  item?: OutfitItem; 
  className?: string;
  alt?: string;
}) {
  const [imageError, setImageError] = useState(false);
  
  const getImageUrl = () => {
    if (!item?.image_url || imageError) return null;
    if (item.image_url.startsWith('http')) return item.image_url;
    const path = item.image_url.startsWith('/') ? item.image_url : `/${item.image_url}`;
    return `http://localhost:8000${path}`;
  };

  const imageUrl = getImageUrl();

  if (imageUrl) {
    return (
      <div className={cn('relative w-full h-full overflow-hidden', className)}>
        <Image
          src={imageUrl}
          alt={alt || item?.name || '衣服图片'}
          fill
          className="object-cover"
          sizes="(max-width: 768px) 50vw, 33vw"
          onError={() => setImageError(true)}
          loading="lazy"
        />
        {/* 渐变遮罩 */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300" />
      </div>
    );
  }

  // 无图片时的占位
  return (
    <div className={cn('w-full h-full flex items-center justify-center bg-gradient-to-br from-sage-50 to-linen-100', className)}>
      <Shirt className="w-8 h-8 text-sage-300" />
    </div>
  );
}

// 主要穿搭拼贴卡片组件
export function OutfitCollageCard({ 
  id,
  top, 
  bottom, 
  pants, 
  shoes, 
  jacket,
  scene,
  weather,
  temperature,
  reason,
  score,
  onClick,
  showDetails = true
}: OutfitCollageCardProps) {
  const [isFavorited, setIsFavorited] = useState(false);

  // 获取穿搭数据
  const outfitData = {
    top: top || (jacket && !top ? jacket : top),
    bottom: bottom || pants,
    shoes: shoes,
  };

  const hasImages = outfitData.top?.image_url || outfitData.bottom?.image_url || outfitData.shoes?.image_url;
  
  const sceneStyle = scene ? sceneColors[scene] || sceneColors['日常'] : null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ y: -8, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={cn(
        'relative w-64 md:w-72 flex-shrink-0 cursor-pointer',
        'rounded-3xl overflow-hidden',
        'bg-white/80 backdrop-blur-xl',
        'shadow-[0_8px_30px_rgb(0,0,0,0.08)]',
        'hover:shadow-[0_20px_50px_rgb(0,0,0,0.15)]',
        'transition-all duration-300 ease-out',
        'border border-white/50'
      )}
    >
      {/* 卡片顶部渐变装饰 */}
      <div className="absolute top-0 left-0 right-0 h-20 bg-gradient-to-b from-moss-100/30 to-transparent pointer-events-none z-10" />
      
      {/* 收藏按钮 */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={(e) => {
          e.stopPropagation();
          setIsFavorited(!isFavorited);
        }}
        className={cn(
          'absolute top-3 right-3 z-20 p-2 rounded-full',
          'transition-all duration-200 backdrop-blur-md',
          isFavorited 
            ? 'bg-sunrise-500/90 text-white shadow-lg' 
            : 'bg-white/60 text-sage-500 hover:bg-white/80'
        )}
      >
        <Heart className={cn('w-4 h-4', isFavorited && 'fill-current')} />
      </motion.button>

      {/* 天气+温度标签 */}
      {weather && (
        <div className="absolute top-3 left-3 z-20 flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-white/70 backdrop-blur-md shadow-sm">
          <WeatherIcon weather={weather} className="w-3.5 h-3.5 text-sky-600" />
          {temperature && (
            <span className="text-xs font-semibold text-forest-700">{temperature}°</span>
          )}
        </div>
      )}

      {/* 穿搭拼贴图区域 */}
      <div className="relative w-full aspect-[3/4] bg-gradient-to-br from-linen-50 via-sage-50 to-moss-50">
        {/* 主图：上衣 */}
        <div className="absolute top-0 left-0 right-0 h-[52%] p-1.5">
          <div className="relative w-full h-full rounded-2xl overflow-hidden shadow-inner">
            <OutfitItemImage 
              item={outfitData.top} 
              alt="上衣"
              className="rounded-2xl"
            />
            {/* 标签 */}
            <div className="absolute bottom-2 left-2 px-2 py-1 bg-black/40 backdrop-blur-sm rounded-lg">
              <span className="text-[10px] text-white/90 font-medium">上装</span>
            </div>
          </div>
        </div>

        {/* 下装 + 鞋子 */}
        <div className="absolute bottom-0 left-0 right-0 h-[48%] flex gap-1.5 p-1.5 pt-0">
          {/* 裤子 */}
          <div className="flex-1 h-full rounded-2xl overflow-hidden shadow-inner">
            <OutfitItemImage 
              item={outfitData.bottom} 
              alt="下装"
              className="rounded-2xl"
            />
            <div className="absolute bottom-2 left-2 px-2 py-1 bg-black/40 backdrop-blur-sm rounded-lg">
              <span className="text-[10px] text-white/90 font-medium">下装</span>
            </div>
          </div>
          
          {/* 鞋子 */}
          <div className="flex-1 h-full rounded-2xl overflow-hidden shadow-inner">
            <OutfitItemImage 
              item={outfitData.shoes} 
              alt="鞋子"
              className="rounded-2xl"
            />
            <div className="absolute bottom-2 left-2 px-2 py-1 bg-black/40 backdrop-blur-sm rounded-lg">
              <span className="text-[10px] text-white/90 font-medium">鞋履</span>
            </div>
          </div>
        </div>

        {/* 无图片提示 */}
        {!hasImages && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center p-4">
              <Sparkles className="w-10 h-10 text-moss-300 mx-auto mb-2" />
              <p className="text-sm text-sage-500">暂无穿搭图片</p>
            </div>
          </div>
        )}

        {/* 渐变遮罩 */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent pointer-events-none" />
      </div>

      {/* 卡片底部信息 */}
      {showDetails && (
        <div className="relative p-4 bg-white/60 backdrop-blur-xl">
          {/* 场景标签 */}
          {scene && (
            <div className="flex items-center gap-2 mb-2">
              {sceneStyle && (
                <span className={cn(
                  'px-2.5 py-1 rounded-full text-xs font-medium',
                  sceneStyle.bg,
                  sceneStyle.text
                )}>
                  {scene}
                </span>
              )}
              {score && (
                <div className="flex items-center gap-0.5">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={cn(
                        'w-3 h-3',
                        i < Math.floor(score / 2)
                          ? 'text-sunrise-400 fill-sunrise-400'
                          : 'text-sage-200'
                      )}
                    />
                  ))}
                  <span className="text-[10px] text-sage-500 ml-0.5">{score.toFixed(1)}</span>
                </div>
              )}
            </div>
          )}

          {/* 推荐理由 */}
          {reason && (
            <p className="text-xs text-sage-600 leading-relaxed line-clamp-2">
              {reason}
            </p>
          )}

          {/* 查看更多 */}
          <div className="flex items-center justify-center gap-1 mt-3 text-xs text-moss-600 font-medium">
            <Eye className="w-3 h-3" />
            <span>查看详情</span>
          </div>
        </div>
      )}
    </motion.div>
  );
}

// 简约版拼贴卡片（用于列表）
export function OutfitCollageMini({ 
  top, 
  bottom, 
  shoes,
  onClick 
}: { 
  top?: OutfitItem;
  bottom?: OutfitItem;
  shoes?: OutfitItem;
  onClick?: () => void;
}) {
  return (
    <motion.div
      whileHover={{ scale: 1.05, y: -4 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={cn(
        'relative w-full aspect-square cursor-pointer',
        'rounded-2xl overflow-hidden',
        'bg-gradient-to-br from-sage-50 to-linen-100',
        'shadow-soft hover:shadow-lifted',
        'transition-all duration-200'
      )}
    >
      {/* 上衣 */}
      <div className="absolute top-0 left-0 right-0 h-1/2 p-1">
        <div className="relative w-full h-full rounded-xl overflow-hidden">
          <OutfitItemImage item={top} alt="上衣" className="rounded-xl" />
        </div>
      </div>
      
      {/* 下装 + 鞋子 */}
      <div className="absolute bottom-0 left-0 right-0 h-1/2 flex gap-0.5 p-1 pt-0">
        <div className="flex-1 rounded-xl overflow-hidden">
          <OutfitItemImage item={bottom} alt="下装" className="rounded-xl" />
        </div>
        <div className="flex-1 rounded-xl overflow-hidden">
          <OutfitItemImage item={shoes} alt="鞋子" className="rounded-xl" />
        </div>
      </div>
    </motion.div>
  );
}

export default OutfitCollageCard;
