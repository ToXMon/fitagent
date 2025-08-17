'use client';

import { useMiniKit } from '@coinbase/onchainkit/minikit';
import { useAccount, useConnect, useDisconnect } from 'wagmi';
import { useState, useEffect } from 'react';
import { User, NutritionData, CoachingResponse, VitalityPoints } from '@/types';

/**
 * Custom hook that extends useMiniKit with FitAgent-specific context and functionality
 * Provides access to MiniKit frame context, wallet state, and app-specific data
 */
export function useFitAgent() {
  const miniKit = useMiniKit();
  const { address, isConnected } = useAccount();
  const { connect } = useConnect();
  const { disconnect } = useDisconnect();
  
  // App-specific state
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [vitalityPoints, setVitalityPoints] = useState<VitalityPoints>({
    total: 0,
    earned: 0,
    pending: 0,
    streakMultiplier: 1
  });

  // Initialize frame readiness when component mounts
  useEffect(() => {
    if (!miniKit.isFrameReady) {
      miniKit.setFrameReady();
    }
  }, [miniKit.isFrameReady, miniKit.setFrameReady]);

  // Load user data when wallet connects
  useEffect(() => {
    if (isConnected && address && !user) {
      loadUserProfile(address);
    }
  }, [isConnected, address, user]);

  const loadUserProfile = async (walletAddress: string) => {
    setIsLoading(true);
    try {
      // TODO: Implement API call to load user profile
      // For now, create a mock user
      const mockUser: User = {
        id: `user_${walletAddress.slice(-8)}`,
        email: '',
        walletAddress,
        createdAt: new Date(),
        preferences: {
          dietaryRestrictions: [],
          allergies: [],
          fitnessGoals: ['protein_tracking'],
          preferredMealTimes: [
            { start: '07:00', end: '09:00', label: 'breakfast' },
            { start: '12:00', end: '14:00', label: 'lunch' },
            { start: '18:00', end: '20:00', label: 'dinner' }
          ]
        },
        goals: {
          dailyProtein: 150, // grams
          dailyCalories: 2000,
          dailyCarbs: 200,
          dailyFats: 70
        },
        nftTokenId: undefined,
        currentLevel: 1 // Seedling level
      };
      setUser(mockUser);
    } catch (error) {
      console.error('Failed to load user profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const analyzePhoto = async (_imageFile: File): Promise<NutritionData | null> => {
    setIsLoading(true);
    try {
      // TODO: Implement photo analysis API call
      // For now, return mock data
      const mockNutritionData: NutritionData = {
        foodItems: [
          {
            name: 'Grilled Chicken Breast',
            quantity: 150,
            unit: 'grams',
            calories: 231,
            protein: 43.5,
            carbs: 0,
            fats: 5,
            confidence: 0.95
          }
        ],
        totalCalories: 231,
        macros: {
          protein: 43.5,
          carbs: 0,
          fats: 5,
          fiber: 0
        },
        micros: {
          vitamins: { 'B6': 0.9, 'B12': 0.3 },
          minerals: { 'Iron': 1.0, 'Zinc': 1.8 }
        },
        confidence: 0.95
      };
      return mockNutritionData;
    } catch (error) {
      console.error('Failed to analyze photo:', error);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const getAICoaching = async (nutritionData: NutritionData): Promise<CoachingResponse | null> => {
    setIsLoading(true);
    try {
      // TODO: Implement AI coaching API call
      // For now, return mock coaching response
      const mockCoaching: CoachingResponse = {
        message: "Great choice with the grilled chicken! You're getting excellent protein to support your fitness goals.",
        suggestions: [
          "Add some vegetables for fiber and micronutrients",
          "Consider a small portion of complex carbs for sustained energy",
          "You're on track to meet your daily protein goal!"
        ],
        goalProgress: {
          protein: {
            current: nutritionData.macros.protein,
            target: user?.goals.dailyProtein || 150,
            percentage: (nutritionData.macros.protein / (user?.goals.dailyProtein || 150)) * 100
          },
          calories: {
            current: nutritionData.totalCalories,
            target: user?.goals.dailyCalories || 2000,
            percentage: (nutritionData.totalCalories / (user?.goals.dailyCalories || 2000)) * 100
          }
        },
        encouragement: "You're building healthy habits! Keep up the great work! 💪"
      };
      return mockCoaching;
    } catch (error) {
      console.error('Failed to get AI coaching:', error);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const completeGoal = async (_goalType: 'protein' | 'calories', _value: number): Promise<boolean> => {
    setIsLoading(true);
    try {
      // TODO: Implement goal completion API call and blockchain transaction
      // For now, simulate VP earning
      const vpEarned = 50; // Base VP for goal completion
      setVitalityPoints(prev => ({
        ...prev,
        earned: prev.earned + vpEarned,
        total: prev.total + vpEarned
      }));
      return true;
    } catch (error) {
      console.error('Failed to complete goal:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    // MiniKit context and functions
    ...miniKit,
    
    // Wallet state
    address,
    isConnected,
    connect,
    disconnect,
    
    // App-specific state and functions
    user,
    isLoading,
    vitalityPoints,
    
    // App-specific functions
    loadUserProfile,
    analyzePhoto,
    getAICoaching,
    completeGoal,
    
    // Computed values
    isReady: miniKit.isFrameReady && !isLoading,
    hasUser: !!user,
    canAnalyzePhotos: miniKit.isFrameReady && isConnected,
  };
}