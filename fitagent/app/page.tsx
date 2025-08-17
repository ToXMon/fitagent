'use client';

import { useEffect, useState } from 'react';
import {
  ConnectWallet,
  Wallet,
  WalletDropdown,
  WalletDropdownLink,
  WalletDropdownDisconnect,
} from '@coinbase/onchainkit/wallet';
import {
  Address,
  Avatar,
  Name,
  Identity,
  EthBalance,
} from '@coinbase/onchainkit/identity';
import { useFitAgent } from '@/hooks/useFitAgent';
import { ManualNutritionData } from '@/types';
import { CameraCapture } from '../components/CameraCapture';
import { ManualNutritionEntry } from '../components/ManualNutritionEntry';

export default function App() {
  const { isFrameReady, setFrameReady, isReady, user, vitalityPoints } = useFitAgent();
  const [showCamera, setShowCamera] = useState(false);
  const [showManualEntry, setShowManualEntry] = useState(false);

  // Initialize MiniKit frame readiness
  useEffect(() => {
    if (!isFrameReady) {
      setFrameReady();
    }
  }, [isFrameReady, setFrameReady]);

  const handlePhotoCapture = async (files: File[]) => {
    console.log('Photos captured:', files);
    setShowCamera(false);
    
    // TODO: Process photos with vision model and OCR
    // For now, show a processing message
    alert(`Processing ${files.length} image(s)... This will integrate with Venice AI and OCR soon!`);
  };

  const handleManualEntry = (nutritionData: ManualNutritionData) => {
    console.log('Manual nutrition entry:', nutritionData);
    setShowManualEntry(false);
    
    // TODO: Process manual nutrition data
    alert(`Added ${nutritionData.foodName} with ${nutritionData.protein}g protein!`);
  };

  return (
    <div className="flex flex-col min-h-screen font-sans bg-gradient-to-br from-fitagent-green-50 to-fitagent-orange-50 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="flex justify-between items-center p-4 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-b border-fitagent-green-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 relative">
            <img 
              src="/VeniceAI_app.webp" 
              alt="FitAgent Logo" 
              className="w-full h-full object-cover rounded-xl"
            />
            <div className="absolute inset-0 bg-gradient-to-br from-fitagent-green-500/20 to-fitagent-orange-500/20 rounded-xl"></div>
          </div>
          <div>
            <h1 className="text-xl font-bold text-fitagent-green-800 dark:text-white">FitAgent</h1>
            <p className="text-xs text-fitagent-green-600 dark:text-gray-400">AI Nutrition Coach</p>
          </div>
        </div>
        
        <div className="wallet-container">
          <Wallet>
            <ConnectWallet>
              <Avatar className="h-6 w-6" />
              <Name />
            </ConnectWallet>
            <WalletDropdown>
              <Identity className="px-4 pt-3 pb-2" hasCopyAddressOnClick>
                <Avatar />
                <Name />
                <Address />
                <EthBalance />
              </Identity>
              <WalletDropdownLink
                icon="wallet"
                href="https://keys.coinbase.com"
                target="_blank"
                rel="noopener noreferrer"
              >
                Wallet
              </WalletDropdownLink>
              <WalletDropdownDisconnect />
            </WalletDropdown>
          </Wallet>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow flex flex-col items-center justify-center p-4">
        {showCamera ? (
          <CameraCapture 
            onPhotosCapture={handlePhotoCapture}
            onCancel={() => setShowCamera(false)}
          />
        ) : showManualEntry ? (
          <ManualNutritionEntry
            onSubmit={handleManualEntry}
            onCancel={() => setShowManualEntry(false)}
          />
        ) : (
          <div className="max-w-md w-full space-y-6">
            {/* Hero Section */}
            <div className="text-center space-y-4">
              <div className="w-32 h-32 mx-auto relative">
                <img 
                  src="/VeniceAI_hero.png" 
                  alt="FitAgent AI Coach" 
                  className="w-full h-full object-cover rounded-3xl shadow-lg"
                />
                <div className="absolute inset-0 bg-gradient-to-br from-fitagent-green-500/10 to-fitagent-orange-500/10 rounded-3xl"></div>
                <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-fitagent-green-500 rounded-full flex items-center justify-center shadow-lg">
                  <span className="text-white text-sm">🍎</span>
                </div>
              </div>
              <h2 className="text-3xl font-bold text-fitagent-green-800 dark:text-white">
                Track Your Protein
              </h2>
              <p className="text-fitagent-green-600 dark:text-gray-300">
                Snap a photo of your meal and let AI analyze your nutrition instantly
              </p>
            </div>

            {/* Status Cards */}
            <div className="grid grid-cols-2 gap-4">
              {/* MiniKit Status */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-4 border border-fitagent-green-200 dark:border-gray-700">
                <div className="flex items-center space-x-2 mb-2">
                  <div className={`w-3 h-3 rounded-full ${
                    isReady ? 'bg-green-500' : 'bg-yellow-500'
                  }`}></div>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {isReady ? 'Ready' : 'Loading...'}
                  </span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">MiniKit Status</p>
              </div>

              {/* User Stats */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-4 border border-fitagent-green-200 dark:border-gray-700">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-fitagent-orange-500 font-bold">
                    {user ? vitalityPoints.total : '0'}
                  </span>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">VP</span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Level: {user?.currentLevel || 'Seedling'}
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={() => setShowCamera(true)}
                disabled={!isReady}
                className="w-full bg-gradient-to-r from-fitagent-green-500 to-fitagent-orange-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                <span className="text-xl">📸</span>
                <span>Capture Meal</span>
              </button>

              <button
                onClick={() => setShowManualEntry(true)}
                disabled={!isReady}
                className="w-full bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm text-fitagent-green-700 dark:text-gray-300 font-semibold py-3 px-6 rounded-2xl border border-fitagent-green-200 dark:border-gray-700 hover:bg-white dark:hover:bg-gray-800 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                <span className="text-lg">✏️</span>
                <span>Manual Entry</span>
              </button>
            </div>

            {/* Features Preview */}
            <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl p-4 border border-fitagent-green-200 dark:border-gray-700">
              <h3 className="font-semibold text-fitagent-green-800 dark:text-white mb-3">
                Coming Soon
              </h3>
              <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <div className="flex items-center space-x-2">
                  <span>🤖</span>
                  <span>AI Nutrition Coaching</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span>🎨</span>
                  <span>Dynamic NFT Evolution</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span>💰</span>
                  <span>VP Rewards & Staking</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span>🏆</span>
                  <span>Social Leaderboards</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="p-4 text-center text-xs text-gray-500 dark:text-gray-400 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm">
        <p>Powered by Base • Built with OnchainKit • ETHGlobal NYC 2025</p>
      </footer>
    </div>
  );
}
