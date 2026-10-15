/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['cosmoastral.com.br'],
  },
  // Manter compatibilidade com imports
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, './src'),
    };
    return config;
  },
  // Proxy da API no mesmo site (necessário para o cookie de login no modo NEXT_PUBLIC_AUTH_MODE=cookie).
  // Defina BACKEND_URL (ex.: https://seu-backend.railway.app) e deixe NEXT_PUBLIC_API_URL vazio.
  async rewrites() {
    const backend = process.env.BACKEND_URL;
    return backend ? [{ source: '/api/:path*', destination: `${backend.replace(/\/$/, '')}/api/:path*` }] : [];
  },
  // Configuração para manter compatibilidade com estilos
  transpilePackages: [],
};

module.exports = nextConfig;
