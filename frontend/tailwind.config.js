/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // ========== 亲生物设计（Biophilic Design）色彩系统 ==========
      colors: {
        // 主色调 - 自然绿色系
        moss: {
          50: '#f7faf5',
          100: '#edf4e5',
          200: '#d5e7c4',
          300: '#b5d49a',
          400: '#8fc06a',
          500: '#6eab47',
          600: '#538933',
          700: '#416b28',
          800: '#365525',
          900: '#2d4521',
        },
        // 鼠尾草绿 - 柔和自然
        sage: {
          50: '#f6f8f4',
          100: '#e9efe6',
          200: '#d2ddd0',
          300: '#b3c4ad',
          400: '#91a888',
          500: '#778f6b',
          600: '#5f7554',
          700: '#4b5d43',
          800: '#3e4c38',
          900: '#343f2f',
        },
        // 森林绿 - 沉稳自然
        forest: {
          50: '#f0f5f1',
          100: '#dce9df',
          200: '#bad2c0',
          300: '#8eb698',
          400: '#629670',
          500: '#457952',
          600: '#356040',
          700: '#2b4d34',
          800: '#253f2d',
          900: '#1f3427',
        },
        // 天空蓝 - 清新自然
        sky: {
          50: '#f4f9fd',
          100: '#e6f2fa',
          200: '#c8e1f3',
          300: '#9ec9e8',
          400: '#6eabdb',
          500: '#4b8fc7',
          600: '#3274ab',
          700: '#2a5e8e',
          800: '#264f74',
          900: '#23435f',
        },
        // 亚麻米色 - 温暖自然
        linen: {
          50: '#fdfcfa',
          100: '#faf6f0',
          200: '#f5ebe0',
          300: '#eedcc9',
          400: '#e5c7aa',
          500: '#d9ad85',
          600: '#cc9468',
          700: '#a97850',
          800: '#886143',
          900: '#705039',
        },
        // 土壤棕 - 大地色
        earth: {
          50: '#faf8f6',
          100: '#f3ede7',
          200: '#e6d9cd',
          300: '#d4bfaa',
          400: '#bfa082',
          500: '#ab8565',
          600: '#9a6f54',
          700: '#7f5843',
          800: '#69493a',
          900: '#573e31',
        },
        // 晨雾白 - 柔和背景
        mist: {
          50: '#f8fafb',
          100: '#f1f4f6',
          200: '#e2e8ed',
          300: '#ccd6de',
          400: '#a8b8c4',
          500: '#8598a7',
          600: '#6a7d8a',
          700: '#576671',
          800: '#4b555d',
          900: '#40484f',
        },
        // 暖阳橙 - 点缀色
        sunrise: {
          50: '#fff8f0',
          100: '#ffefdb',
          200: '#ffd9af',
          300: '#ffbd7a',
          400: '#ff9b44',
          500: '#f87c1f',
          600: '#d45f11',
          700: '#b04810',
          800: '#8f3a10',
          900: '#753111',
        },
        // 保留原有主色调（兼容）
        primary: {
          50: '#f0f9f4',
          100: '#d9f0e4',
          200: '#b3e0c9',
          300: '#7fc9a7',
          400: '#4aab81',
          500: '#2d8f62',
          600: '#1f7350',
          700: '#1a5c41',
          800: '#174b35',
          900: '#153f2e',
        },
        // 保留次要色
        secondary: {
          50: '#fdfcfa',
          100: '#faf6f0',
          200: '#f5ebe0',
          300: '#eedcc9',
          400: '#e5c7aa',
          500: '#d9ad85',
          600: '#cc9468',
          700: '#a97850',
          800: '#886143',
          900: '#705039',
        },
        // 保留强调色
        accent: {
          50: '#fff8f0',
          100: '#ffefdb',
          200: '#ffd9af',
          300: '#ffbd7a',
          400: '#ff9b44',
          500: '#f87c1f',
          600: '#d45f11',
          700: '#b04810',
          800: '#8f3a10',
          900: '#753111',
        },
        // 成功绿
        success: {
          50: '#f4f9f5',
          100: '#e3f0e6',
          200: '#c7e0cd',
          300: '#9fc9a9',
          400: '#6eac7d',
          500: '#4a905c',
          600: '#367548',
          700: '#2c5d3b',
          800: '#264c33',
          900: '#22402d',
        },
      },
      
      // 字体
      fontFamily: {
        sans: ['"Nunito"', '"PingFang SC"', '"Microsoft YaHei"', 'system-ui', 'sans-serif'],
        display: ['"Nunito"', 'sans-serif'],
      },
      
      // 动画 - 更柔和自然
      animation: {
        'float': 'float 4s ease-in-out infinite',
        'breathe': 'breathe 4s ease-in-out infinite',
        'drift': 'drift 8s ease-in-out infinite',
        'sway': 'sway 3s ease-in-out infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
      },
      
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        breathe: {
          '0%, 100%': { transform: 'scale(1)', opacity: '1' },
          '50%': { transform: 'scale(1.03)', opacity: '0.95' },
        },
        drift: {
          '0%, 100%': { transform: 'translateX(0px) translateY(0px)' },
          '25%': { transform: 'translateX(5px) translateY(-3px)' },
          '50%': { transform: 'translateX(0px) translateY(-6px)' },
          '75%': { transform: 'translateX(-5px) translateY(-3px)' },
        },
        sway: {
          '0%, 100%': { transform: 'rotate(-2deg)' },
          '50%': { transform: 'rotate(2deg)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      
      // 背景渐变
      backgroundImage: {
        'gradient-nature': 'linear-gradient(135deg, #f6f8f4 0%, #e9efe6 50%, #f4f9fd 100%)',
        'gradient-sunrise': 'linear-gradient(135deg, #ffefdb 0%, #ffd9af 50%, #fff8f0 100%)',
        'gradient-mist': 'linear-gradient(180deg, #f8fafb 0%, #f1f4f6 50%, #e2e8ed 100%)',
        'gradient-forest': 'linear-gradient(135deg, #f0f5f1 0%, #dce9df 50%, #f6f8f4 100%)',
        'gradient-sunset': 'linear-gradient(135deg, #ffefdb 0%, #eedcc9 50%, #f6f8f4 100%)',
      },
      
      // 阴影 - 更柔和自然
      boxShadow: {
        'nature': '0 4px 20px -3px rgba(45, 69, 33, 0.08), 0 8px 24px -4px rgba(45, 69, 33, 0.06)',
        'soft': '0 2px 12px -2px rgba(45, 69, 33, 0.06), 0 4px 16px -3px rgba(45, 69, 33, 0.04)',
        'warm': '0 4px 16px -4px rgba(201, 148, 104, 0.2)',
        'card': '0 2px 12px -2px rgba(45, 69, 33, 0.05)',
        'lifted': '0 8px 30px -6px rgba(45, 69, 33, 0.12)',
      },
      
      // 圆角 - 更有机
      borderRadius: {
        'organic': '16px',
        'leaf': '24px',
      },
      
      // 间距
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      
      // 透明度
      extend: {
        opacity: {
          '15': '0.15',
          '25': '0.25',
          '35': '0.35',
        },
      },
    },
  },
  plugins: [],
}
