/** @type {import('next').NextConfig} */
const BACKEND_URL = 'https://the-evolution-of-todo-app-phase-iv-rho.vercel.app';

const nextConfig = {
  reactStrictMode: true,
  // Direct backend URL for production - browser calls backend directly (no proxy)
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.VERCEL ? BACKEND_URL : (process.env.NEXT_PUBLIC_API_BASE_URL || ''),
  },
  // Performance optimizations for faster dev server
  swcMinify: true,

  // Aggressive optimizations for development
  experimental: {
    // Use Turbopack for MUCH faster compilation (Next.js 14+)
    turbo: {
      // Optimize package imports
      resolveAlias: {
        // Reduce resolution overhead
      },
    },
    // Faster refresh
    optimizePackageImports: ['axios', '@better-auth/react', 'react', 'react-dom'],
  },

  // Disable source maps in development for MUCH faster builds
  productionBrowserSourceMaps: false,

  // TypeScript optimizations
  typescript: {
    // Skip type checking during build (faster, but less safe)
    // You can still run type checking separately: npm run type-check
    ignoreBuildErrors: false, // Keep false for safety, but speeds up if true
  },

  // ESLint optimizations
  eslint: {
    // Skip ESLint during build for faster compilation
    ignoreDuringBuilds: true, // Speeds up significantly
  },

  // Faster webpack compilation
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // Aggressive dev optimizations
      config.optimization = {
        ...config.optimization,
        removeAvailableModules: false,
        removeEmptyChunks: false,
        splitChunks: false,
        // Disable minification in dev
        minimize: false,
      };

      // Faster file watching
      config.watchOptions = {
        poll: false, // Disable polling (faster on Windows)
        aggregateTimeout: 200, // Reduced timeout
        ignored: [
          /node_modules/,
          /\.next/,
          /\.git/,
        ],
      };

      // Reduce module resolution overhead
      config.resolve.symlinks = false;
      config.resolve.cache = true;
    }
    return config;
  },
  async rewrites() {
    const vercelBackend = 'https://the-evolution-of-todo-app-phase-iv-rho.vercel.app';
    const raw = (process.env.API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || '').trim().replace(/\s+/g, '');
    const backendUrl = raw.startsWith('http') ? raw : (process.env.VERCEL ? vercelBackend : 'http://localhost:8000');
    return [
      { source: '/api/:path*', destination: `${backendUrl}/api/:path*` },
    ];
  },
}

module.exports = nextConfig
