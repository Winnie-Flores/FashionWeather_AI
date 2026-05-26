'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Home,
  Cloud,
  Shirt,
  Sparkles,
  MessageCircle,
  User,
  Menu,
  X,
  LogOut,
  Leaf,
} from 'lucide-react';
import { cn } from '@/utils';
import { useAuth } from '@/hooks';

const navItems = [
  { href: '/', icon: Home, label: '首页' },
  { href: '/weather', icon: Cloud, label: '天气' },
  { href: '/recommend', icon: Sparkles, label: '推荐' },
  { href: '/wardrobe', icon: Shirt, label: '衣橱' },
  { href: '/chat', icon: MessageCircle, label: '聊天' },
  { href: '/profile', icon: User, label: '我的' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // 公开页面不显示导航
  if (['/login', '/register'].some(path => pathname?.startsWith(path))) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gradient-nature">
      {/* 顶部导航 */}
      <header
        className={cn(
          'fixed top-0 left-0 right-0 z-50 transition-all duration-500',
          scrolled
            ? 'bg-white/90 backdrop-blur-lg shadow-card'
            : 'bg-white/60 backdrop-blur-md'
        )}
      >
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-organic bg-gradient-to-br from-moss-500 to-forest-600 
                              flex items-center justify-center shadow-warm 
                              group-hover:shadow-lifted transition-all duration-300">
                <Leaf className="w-5 h-5 text-white transform group-hover:rotate-12 transition-transform duration-300" />
              </div>
              <span className="text-xl font-bold text-gradient hidden sm:block">
                FashionWeather AI
              </span>
            </Link>

            {/* 桌面导航 */}
            <div className="hidden md:flex items-center gap-1">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      'flex items-center gap-2 px-4 py-2 rounded-organic text-sm font-medium transition-all duration-200',
                      isActive
                        ? 'bg-moss-500/10 text-forest-700 border border-moss-400/30'
                        : 'text-sage-700 hover:bg-sage-100 hover:text-forest-700'
                    )}
                  >
                    <item.icon className={cn(
                      'w-4 h-4 transition-transform duration-200',
                      isActive ? 'scale-110' : ''
                    )} />
                    {item.label}
                  </Link>
                );
              })}
            </div>

            {/* 用户操作 */}
            <div className="flex items-center gap-3">
              {isAuthenticated ? (
                <>
                  <Link
                    href="/profile"
                    className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-organic text-sm font-medium 
                             text-sage-700 hover:bg-sage-100 transition-all duration-200"
                  >
                    <User className="w-4 h-4" />
                    个人中心
                  </Link>
                  <button
                    onClick={logout}
                    className="p-2 rounded-organic text-sage-600 hover:bg-sage-100 
                               hover:text-red-500 transition-all duration-200"
                    title="退出登录"
                  >
                    <LogOut className="w-5 h-5" />
                  </button>
                </>
              ) : (
                <Link
                  href="/login"
                  className="btn-primary text-sm"
                >
                  登录
                </Link>
              )}

              {/* 移动端菜单按钮 */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-organic text-sage-700 hover:bg-sage-100 transition-colors"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </nav>

        {/* 移动端菜单 */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="md:hidden bg-white/95 backdrop-blur-lg border-t border-sage-200/50"
            >
              <div className="px-4 py-4 space-y-1">
                {navItems.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className={cn(
                        'flex items-center gap-3 px-4 py-3 rounded-organic text-sm font-medium transition-all duration-200',
                        isActive
                          ? 'bg-moss-500/10 text-forest-700 border border-moss-400/30'
                          : 'text-sage-700 hover:bg-sage-100'
                      )}
                    >
                      <item.icon className="w-5 h-5" />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* 主内容 */}
      <main className="pt-16 pb-20 md:pb-0">
        {children}
      </main>

      {/* 移动端底部导航 */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 
                      bg-white/90 backdrop-blur-lg border-t border-sage-200/50 z-50">
        <div className="flex items-center justify-around py-2">
          {navItems.slice(0, 5).map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex flex-col items-center gap-1 px-3 py-2 rounded-organic transition-all duration-200',
                  isActive
                    ? 'text-forest-600'
                    : 'text-sage-500'
                )}
              >
                <div className={cn(
                  'p-2 rounded-full transition-all duration-200',
                  isActive ? 'bg-moss-500/10' : ''
                )}>
                  <item.icon className={cn(
                    'w-5 h-5',
                    isActive ? 'animate-float' : ''
                  )} />
                </div>
                <span className="text-xs font-medium">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
