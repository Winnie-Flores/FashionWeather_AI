'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { Mail, Lock, User, ArrowRight, Check, Leaf, Flower2 } from 'lucide-react';
import { useAuth } from '@/hooks';
import { cn } from '@/utils';
import toast from 'react-hot-toast';

export default function RegisterPage() {
  const router = useRouter();
  const { register, login } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    if (formData.password.length < 6) {
      setError('密码长度至少为6位');
      return;
    }

    setLoading(true);

    try {
      const result = await register({
        username: formData.username,
        password: formData.password,
        email: formData.email || undefined,
      });

      if (result.success) {
        toast.success('注册成功！正在登录...');
        // 自动登录
        await login(formData.username, formData.password);
        router.push('/');
      } else {
        setError(result.error || '注册失败');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* 自然渐变背景 */}
      <div className="absolute inset-0 bg-gradient-to-br from-sage-50 via-linen-100 to-sky-100" />
      
      {/* 装饰性植物图案 */}
      <div className="absolute top-16 right-16 w-28 h-28 opacity-[0.07]">
        <Leaf className="w-full h-full text-forest-600 -rotate-12" />
      </div>
      <div className="absolute top-20 left-12 w-20 h-20 opacity-[0.07]">
        <Flower2 className="w-full h-full text-moss-500" />
      </div>
      <div className="absolute bottom-20 right-1/4 w-24 h-24 opacity-[0.07]">
        <Leaf className="w-full h-full text-sage-500 rotate-30" />
      </div>
      <div className="absolute bottom-16 left-20 w-16 h-16 opacity-[0.07]">
        <Flower2 className="w-full h-full text-moss-400" />
      </div>

      {/* 柔和光晕 */}
      <div className="absolute top-1/4 right-1/3 w-72 h-72 bg-sage-200/20 rounded-full blur-3xl" />
      <div className="absolute bottom-1/3 left-1/4 w-80 h-80 bg-linen-200/30 rounded-full blur-3xl" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <motion.div
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 3, repeat: Infinity }}
            className="w-20 h-20 mx-auto mb-4 rounded-organic bg-gradient-to-br from-moss-500 to-forest-600 
                        flex items-center justify-center shadow-warm"
          >
            <svg className="w-10 h-10 text-white" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 4c-5 0-9 4-9 9 0 1.5.4 2.9 1 4.1A9 9 0 006 22c0 4.4 3.1 8.2 7.3 8.9a6 6 0 005.7 5.1 6 6 0 005.7-5.1A9 9 0 0032 22a9 9 0 00-6-8.9c.6-1.2 1-2.6 1-4.1 0-5-4-9-9-9z" fill="currentColor"/>
            </svg>
          </motion.div>
          <h1 className="text-3xl font-bold text-gradient mb-2">FashionWeather AI</h1>
          <p className="text-sage-600">智能天气穿搭助手</p>
        </div>

        {/* 表单 */}
        <div className="nature-card p-8">
          <h2 className="text-2xl font-bold text-forest-800 mb-6 text-center">
            创建账号
          </h2>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 bg-earth-50 border border-earth-200 rounded-organic text-earth-600 text-sm"
            >
              {error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-forest-800 mb-2">
                用户名
              </label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-sage-400" />
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="input-field pl-12"
                  placeholder="设置用户名"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-forest-800 mb-2">
                邮箱（选填）
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-sage-400" />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="input-field pl-12"
                  placeholder="用于找回密码"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-forest-800 mb-2">
                密码
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-sage-400" />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="input-field pl-12"
                  placeholder="设置密码（至少6位）"
                  required
                  minLength={6}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-forest-800 mb-2">
                确认密码
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-sage-400" />
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="input-field pl-12"
                  placeholder="再次输入密码"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={cn(
                'w-full btn-primary flex items-center justify-center gap-2',
                loading && 'opacity-70 cursor-not-allowed'
              )}
            >
              {loading ? (
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              ) : (
                <>
                  注册
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sage-600">
              已有账号？{' '}
              <Link href="/login" className="text-moss-600 hover:text-forest-700 font-medium">
                立即登录
              </Link>
            </p>
          </div>

          {/* 用户协议 */}
          <div className="natural-divider my-5" />
          <div className="flex items-start gap-2 p-3 bg-sage-50/50 rounded-organic border border-sage-200/50">
            <div className="w-5 h-5 rounded border border-sage-300 flex items-center justify-center flex-shrink-0 mt-0.5">
              <Check className="w-3 h-3 text-sage-400" />
            </div>
            <p className="text-xs text-sage-600">
              注册即表示同意我们的
              <a href="#" className="text-moss-600 hover:text-forest-700"> 服务条款</a>
              和
              <a href="#" className="text-moss-600 hover:text-forest-700"> 隐私政策</a>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
