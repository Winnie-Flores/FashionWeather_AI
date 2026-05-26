/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false, // 禁用 StrictMode 避免开发环境 useEffect 双执行导致 API 请求翻倍
  images: {
    domains: ['localhost', '127.0.0.1'],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: '**',
      },
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
}

module.exports = nextConfig
