/**
 * 安全 ECharts 组件 - 避免 Next.js SSR 问题
 * 使用原生 ECharts 代替 echarts-for-react，获得更好的兼容性
 */

'use client';

import React, { useEffect, useRef } from 'react';
import type { EChartsOption } from 'echarts';

interface SafeEChartProps {
  option: EChartsOption | any;
  style?: React.CSSProperties;
  className?: string;
}

export function SafeEChart({ option, style, className }: SafeEChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const instanceRef = useRef<any>(null);

  useEffect(() => {
    // 客户端才初始化
    if (!chartRef.current || typeof window === 'undefined') return;

    let mounted = true;

    const initChart = async () => {
      try {
        // 动态导入 echarts
        const echarts = await import('echarts');
        
        if (!mounted || !chartRef.current) return;

        // 如果已有实例，先销毁
        if (instanceRef.current) {
          instanceRef.current.dispose();
        }

        // 创建新的图表实例
        instanceRef.current = echarts.init(chartRef.current);
        instanceRef.current.setOption(option);

        // 响应式调整
        const handleResize = () => {
          instanceRef.current?.resize();
        };
        window.addEventListener('resize', handleResize);

        return () => {
          window.removeEventListener('resize', handleResize);
        };
      } catch (error) {
        console.error('[SafeEChart] 初始化失败:', error);
      }
    };

    initChart();

    return () => {
      mounted = false;
      if (instanceRef.current) {
        instanceRef.current.dispose();
        instanceRef.current = null;
      }
    };
  }, []);

  // 当 option 变化时更新图表
  useEffect(() => {
    if (instanceRef.current && option) {
      instanceRef.current.setOption(option, true);
    }
  }, [option]);

  return (
    <div
      ref={chartRef}
      style={style}
      className={className}
    />
  );
}

export default SafeEChart;
