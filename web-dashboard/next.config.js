/** @type {import('next').NextConfig} */
const nextConfig = {
  basePath: '/zaloauto',  // 👈 quan trọng
  output: 'standalone',
  
  // Performance optimizations
  experimental: {
    optimizeCss: false, // Disable to avoid CSS processing errors
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },
  
  // Reduce bundle analysis overhead
  productionBrowserSourceMaps: false,
  
  // Optimize images
  images: {
    unoptimized: true
  },
  
  // Webpack configuration to handle module issues
  webpack: (config, { isServer }) => {
    // Handle critters module issue
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  },
};

export default nextConfig;
