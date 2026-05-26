'use client';

import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { MessageCircle, Trash2, Sparkles } from 'lucide-react';
import { ChatInterface } from '@/components';
import { useChatStore, useAuth, useWeather } from '@/hooks';
import { chatApi } from '@/services/api';

export default function ChatPage() {
  const { isAuthenticated } = useAuth();
  const { weather, loading: weatherLoading } = useWeather();
  const {
    messages,
    isLoading,
    suggestions,
    addMessage,
    setMessages,
    setLoading,
    setSuggestions,
    clearMessages,
  } = useChatStore();

  // 用于标记是否已经初始化过
  const initializedRef = useRef(false);

  useEffect(() => {
    if (isAuthenticated && !initializedRef.current) {
      initializedRef.current = true;
      fetchHistory();
    }
  }, [isAuthenticated]);

  // 每次进入页面都刷新建议
  useEffect(() => {
    fetchSuggestions();
  }, []);

  const fetchSuggestions = async () => {
    try {
      const res = await chatApi.getSuggestions();
      setSuggestions(res.data);
    } catch (error) {
      console.error('获取建议失败:', error);
      // 设置默认建议
      setSuggestions([
        '今天应该穿什么？',
        '明天天气怎么样？',
        '帮我推荐一套穿搭',
        '下周出差怎么穿搭？',
      ]);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await chatApi.getHistory(50);
      if (res.data && res.data.length > 0) {
        setMessages(res.data);
      }
    } catch (error) {
      console.error('获取历史记录失败:', error);
    }
  };

  const handleSend = async (message: string) => {
    if (!message.trim()) return;

    // 添加用户消息
    addMessage(message);
    setLoading(true);

    try {
      // 构建上下文
      const context: any = {};
      
      // 注入天气数据
      if (weather) {
        context.weather = weather;
        context.temperature = weather.temperature;
        context.city = weather.city || '';
        context.weather_text = weather.weather;
        context.humidity = weather.humidity;
        context.wind_speed = weather.wind_speed;
        context.feels_like = weather.feels_like || weather.temperature;
        context.uv_index = weather.uv_index;
        context.aqi = weather.aqi;
      }

      const res = await chatApi.sendMessage({
        message,
        context,
      });

      // 添加 AI 回复（使用正确的格式）
      addMessage(message, res.data.response);
      
      // 更新建议
      if (res.data.suggestions && res.data.suggestions.length > 0) {
        setSuggestions(res.data.suggestions);
      }
      
      // 打印意图类型（调试用）
      if (res.data.intent) {
        console.log('[Chat] 识别意图:', res.data.intent);
      }
    } catch (error: any) {
      console.error('发送消息失败:', error);
      addMessage(message, '抱歉，服务遇到了一点问题，请稍后再试～');
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (confirm('确定要清空聊天记录吗？这将清除所有对话历史。')) {
      try {
        await chatApi.clearHistory();
        clearMessages();
        fetchSuggestions(); // 清空后获取新建议
      } catch (error) {
        console.error('清空失败:', error);
      }
    }
  };

  return (
    <div className="h-[calc(100vh-4rem)] md:h-[calc(100vh-4rem)] flex flex-col">
      {/* 头部 */}
      <section className="gradient-bg p-4 text-white flex-shrink-0">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold">FashionWeather AI</h1>
              <p className="text-xs text-white/70">智能穿搭天气助手</p>
            </div>
          </div>
          {messages.length > 0 && (
            <button
              onClick={handleClearHistory}
              className="flex items-center gap-2 px-3 py-1.5 bg-white/20 rounded-lg text-sm hover:bg-white/30 transition-colors"
              title="清空对话历史"
            >
              <Trash2 className="w-4 h-4" />
              清空对话
            </button>
          )}
        </div>
      </section>

      {/* 当前天气提示 */}
      {weather && !weatherLoading && (
        <div className="bg-blue-50 px-4 py-2 text-sm text-blue-700 flex items-center gap-2 flex-shrink-0">
          <span>📍 {weather.city}</span>
          <span>•</span>
          <span>{weather.weather}</span>
          <span>•</span>
          <span>{weather.temperature}°C</span>
        </div>
      )}

      {/* 聊天内容 */}
      <div className="flex-1 overflow-hidden">
        <ChatInterface
          messages={messages}
          isLoading={isLoading}
          onSend={handleSend}
          suggestions={suggestions}
        />
      </div>
    </div>
  );
}
