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
  // Configuração para manter compatibilidade com estilos
  transpilePackages: [],
};

module.exports = nextConfig;
