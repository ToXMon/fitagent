// Core FitAgent types

export interface User {
  id: string;
  email: string;
  walletAddress: string;
  createdAt: Date;
  preferences: UserPreferences;
  goals: NutritionGoals;
  nftTokenId?: string;
  currentLevel: NFTLevel;
}

export interface UserPreferences {
  dietaryRestrictions: string[];
  allergies: string[];
  fitnessGoals: string[];
  preferredMealTimes: TimeSlot[];
}

export interface NutritionGoals {
  dailyProtein: number; // grams
  dailyCalories: number;
  dailyCarbs: number;
  dailyFats: number;
}

export interface TimeSlot {
  start: string; // HH:MM format
  end: string;   // HH:MM format
  label: string; // "breakfast", "lunch", "dinner", "snack"
}

export interface NutritionData {
  foodItems: FoodItem[];
  totalCalories: number;
  macros: MacroNutrients;
  micros: MicroNutrients;
  confidence: number;
}

export interface FoodItem {
  name: string;
  quantity: number;
  unit: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  confidence: number;
}

export interface MacroNutrients {
  protein: number;
  carbs: number;
  fats: number;
  fiber: number;
}

export interface MicroNutrients {
  vitamins: Record<string, number>;
  minerals: Record<string, number>;
}

export enum NFTLevel {
  Seedling = 1,
  Sprout = 2,
  Plant = 3,
  Tree = 4,
  ForestGuardian = 5,
}

export interface NFTMetadata {
  name: string;
  description: string;
  image: string;
  level: NFTLevel;
  daysActive: number;
  goalsCompleted: number;
  currentStreak: number;
  specialTraits: string[];
}

export interface CoachingResponse {
  message: string;
  suggestions: string[];
  goalProgress: GoalProgress;
  encouragement: string;
}

export interface GoalProgress {
  protein: {
    current: number;
    target: number;
    percentage: number;
  };
  calories: {
    current: number;
    target: number;
    percentage: number;
  };
}

export interface VitalityPoints {
  total: number;
  earned: number;
  pending: number;
  streakMultiplier: number;
}

// MiniKit-specific types
export interface MiniKitConfig {
  apiKey: string;
  chain: any; // wagmi chain type
  frameReady: boolean;
  manifestUrl?: string;
}

export interface FitAgentContext {
  user: User | null;
  isLoading: boolean;
  vitalityPoints: VitalityPoints;
  isReady: boolean;
  hasUser: boolean;
  canAnalyzePhotos: boolean;
}

export interface ManualNutritionData {
  foodName: string;
  servingSize: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  confidence: number;
}