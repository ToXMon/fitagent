/** @type {import('next').NextConfig} */
const nextConfig = {
    // Silence warnings
    // https://github.com/WalletConnect/walletconnect-monorepo/issues/1908
    webpack: (config) => {
      config.externals.push('pino-pretty', 'lokijs', 'encoding');
      return config;
    },
    
    // Enable static file serving for images
    images: {
      domains: ['localhost'],
      formats: ['image/webp', 'image/avif'],
    },
  };
  
  export default nextConfig;
  