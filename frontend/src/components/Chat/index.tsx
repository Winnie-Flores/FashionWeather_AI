'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User as UserIcon, Sparkles, RefreshCw } from 'lucide-react';
import { cn } from '@/utils';

interface Message {
  id: number;
  message: string;
  response?: string;
  isUser: boolean;
}

interface ChatInterfaceProps {
  messages: Message[];
  isLoading: boolean;
  onSend: (message: string) => void;
  suggestions?: string[];
}

export function ChatInterface({ messages, isLoading, onSend, suggestions }: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 pb-20">
        {messages.length === 0 && (
          <WelcomeMessage suggestions={suggestions || []} onSuggestionClick={onSend} />
        )}
        
        <AnimatePresence>
          {messages.map((msg, index) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                'flex gap-3',
                msg.isUser ? 'flex-row-reverse' : 'flex-row'
              )}
            >
              {/* 头像 */}
              <div className={cn(
                'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0',
                msg.isUser ? 'bg-blue-500' : 'bg-purple-500'
              )}>
                {msg.isUser ? (
                  <UserIcon className="w-5 h-5 text-white" />
                ) : (
                  <Bot className="w-5 h-5 text-white" />
                )}
              </div>

              {/* 消息内容 */}
              <div className={cn(
                'max-w-[75%] rounded-2xl p-4',
                msg.isUser
                  ? 'bg-blue-500 text-white rounded-tr-sm'
                  : 'glass-card rounded-tl-sm'
              )}>
                {msg.isUser ? (
                  <p className="whitespace-pre-wrap">{msg.message}</p>
                ) : (
                  <>
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-4 h-4 text-purple-500" />
                      <span className="text-sm font-medium text-purple-600">FashionWeather AI</span>
                    </div>
                    <p className="text-gray-700 whitespace-pre-wrap">{msg.response || msg.message}</p>
                  </>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* 加载指示器 */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3"
          >
            <div className="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="glass-card rounded-2xl rounded-tl-sm p-4">
              <div className="loading-dots text-blue-500">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <div className="fixed bottom-20 md:bottom-4 left-0 right-0 p-4 bg-gradient-to-t from-white via-white to-transparent">
        <div className="max-w-3xl mx-auto">
          <div className="glass-card flex items-center gap-3 p-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="问我任何关于穿搭和天气的问题..."
              className="flex-1 bg-transparent outline-none text-gray-800 placeholder-gray-400"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className={cn(
                'p-3 rounded-xl transition-all',
                input.trim() && !isLoading
                  ? 'bg-blue-500 text-white hover:bg-blue-600'
                  : 'bg-gray-200 text-gray-400'
              )}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// 欢迎消息
interface WelcomeMessageProps {
  suggestions: string[];
  onSuggestionClick: (message: string) => void;
}

function WelcomeMessage({ suggestions, onSuggestionClick }: WelcomeMessageProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-center py-12"
    >
      <motion.div
        animate={{ y: [0, -10, 0] }}
        transition={{ duration: 3, repeat: Infinity }}
        className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center"
      >
        <Bot className="w-10 h-10 text-white" />
      </motion.div>
      
      <h2 className="text-2xl font-bold text-gray-800 mb-2">
        你好，我是 FashionWeather AI
      </h2>
      <p className="text-gray-600 mb-8 max-w-md mx-auto">
        我可以帮你根据天气推荐穿搭、解答穿搭问题、管理你的衣橱。有什么可以帮到你的吗？
      </p>
      
      <div className="flex flex-wrap justify-center gap-3">
        {suggestions.map((suggestion, index) => (
          <motion.button
            key={index}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => onSuggestionClick(suggestion)}
            className="px-4 py-2 rounded-full bg-white shadow-soft hover:shadow-lg transition-all text-gray-700 hover:text-blue-600"
          >
            {suggestion}
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}

// 聊天建议标签
export function ChatSuggestions({ 
  suggestions, 
  onSuggestionClick 
}: { 
  suggestions: string[];
  onSuggestionClick: (message: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {suggestions.map((suggestion, index) => (
        <button
          key={index}
          onClick={() => onSuggestionClick(suggestion)}
          className="px-3 py-1.5 rounded-full bg-white shadow-sm hover:shadow-md transition-all text-sm text-gray-600 hover:text-blue-600 border border-gray-100"
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
}

export default ChatInterface;
