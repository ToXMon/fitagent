import '@coinbase/onchainkit/styles.css';
import type { Metadata } from 'next';
import './globals.css';
import { Providers } from './providers';

export const metadata: Metadata = {
  title: process.env.NEXT_PUBLIC_ONCHAINKIT_PROJECT_NAME || 'FitAgent',
  description: 'Your AI nutrition companion - Transform meal tracking into an engaging conversation with dynamic NFT rewards',
  metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'),
  openGraph: {
    title: 'FitAgent - AI Nutrition Coach',
    description: 'Transform meal tracking into an engaging conversation with your AI nutrition coach. Earn rewards and evolve your NFT companion.',
    url: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000',
    siteName: 'FitAgent',
    images: [
      {
        url: '/VeniceAI_hero.png',
        width: 1200,
        height: 630,
        alt: 'FitAgent - AI Nutrition Coach with Dynamic NFTs',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'FitAgent - AI Nutrition Coach',
    description: 'Transform meal tracking with AI coaching and dynamic NFT rewards',
    images: ['/VeniceAI_hero.png'],
  },
  other: {
    'fc:frame': 'vNext',
    'fc:frame:image': `${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/VeniceAI_hero.png`,
    'fc:frame:button:1': 'Start Tracking',
    'fc:frame:button:1:action': 'post',
    'fc:frame:post_url': `${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/api/frame`,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-background dark">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
