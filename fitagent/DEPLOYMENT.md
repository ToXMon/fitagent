# FitAgent - Vercel Deployment Guide

## Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FToXMon%2Ffitagent%2Ftree%2Fmaster%2Ffitagent)

## Manual Deployment Steps

1. **Fork/Clone the repository**
   ```bash
   git clone https://github.com/ToXMon/fitagent.git
   cd fitagent/fitagent
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   - Copy `.env.example` to `.env.local`
   - Fill in your values:
     ```
     NEXT_PUBLIC_BASE_URL=https://your-app.vercel.app
     NEXT_PUBLIC_ONCHAINKIT_PROJECT_NAME=FitAgent
     NEXT_PUBLIC_ONCHAINKIT_API_KEY=your_coinbase_api_key
     ```

4. **Test locally**
   ```bash
   npm run dev
   ```

5. **Deploy to Vercel**
   - Connect your GitHub repository to Vercel
   - Set environment variables in Vercel dashboard
   - Deploy

## Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_BASE_URL` | Your deployed app URL | Yes |
| `NEXT_PUBLIC_ONCHAINKIT_PROJECT_NAME` | App name (e.g., "FitAgent") | Yes |
| `NEXT_PUBLIC_ONCHAINKIT_API_KEY` | Coinbase OnchainKit API key | Yes |

## Getting API Keys

### Coinbase OnchainKit API Key
1. Visit [Coinbase Cloud](https://www.coinbase.com/cloud)
2. Create an account/login
3. Generate an API key for OnchainKit
4. Add it to your environment variables

## Troubleshooting

### Build Errors
- Ensure all dependencies are installed with `npm install`
- Check that all environment variables are set
- Review build logs for specific error messages

### Runtime Errors
- Verify API keys are correct
- Check network connectivity for blockchain interactions
- Ensure images are properly uploaded to `/public` folder

## Features

- 🎯 **Food Photo Analysis** - Capture meals and analyze nutrition
- 🧠 **AI Coaching** - Venice AI-powered nutrition guidance  
- 🔗 **Web3 Integration** - OnchainKit + Base network
- 📱 **Mobile Optimized** - PWA-ready design
- 🎨 **Dynamic NFTs** - Fitness progress visualization

## Tech Stack

- **Frontend**: Next.js 15, React 18, TypeScript
- **Styling**: Tailwind CSS
- **Web3**: OnchainKit, wagmi, viem
- **Deployment**: Vercel
- **AI**: Venice AI integration (via backend)

## Project Structure

```
fitagent/
├── app/                 # Next.js app directory
├── components/          # React components
├── hooks/              # Custom React hooks
├── public/             # Static assets
├── providers/          # Context providers
└── types/              # TypeScript definitions
```