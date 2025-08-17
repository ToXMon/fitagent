'use client';

import { useState } from 'react';
import { ManualNutritionData } from '@/types';

interface ManualNutritionEntryProps {
  onSubmit: (nutrition: ManualNutritionData) => void;
  onCancel: () => void;
  initialData?: Partial<ManualNutritionData>;
}

export function ManualNutritionEntry({ onSubmit, onCancel, initialData }: ManualNutritionEntryProps) {
  const [formData, setFormData] = useState<ManualNutritionData>({
    foodName: initialData?.foodName || '',
    servingSize: initialData?.servingSize || '',
    calories: initialData?.calories || 0,
    protein: initialData?.protein || 0,
    carbs: initialData?.carbs || 0,
    fats: initialData?.fats || 0,
    confidence: 1.0 // Manual entry is 100% confident
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.foodName.trim()) {
      newErrors.foodName = 'Food name is required';
    }
    
    if (!formData.servingSize.trim()) {
      newErrors.servingSize = 'Serving size is required';
    }
    
    if (formData.protein < 0) {
      newErrors.protein = 'Protein cannot be negative';
    }
    
    if (formData.calories < 0) {
      newErrors.calories = 'Calories cannot be negative';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const handleInputChange = (field: keyof ManualNutritionData, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Manual Entry
          </h2>
          <button
            onClick={onCancel}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Food Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Food Name *
            </label>
            <input
              type="text"
              value={formData.foodName}
              onChange={(e) => handleInputChange('foodName', e.target.value)}
              placeholder="e.g., Grilled Chicken Breast"
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-fitagent-green-500 focus:border-transparent ${
                errors.foodName ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
            />
            {errors.foodName && (
              <p className="text-red-500 text-xs mt-1">{errors.foodName}</p>
            )}
          </div>

          {/* Serving Size */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Serving Size *
            </label>
            <input
              type="text"
              value={formData.servingSize}
              onChange={(e) => handleInputChange('servingSize', e.target.value)}
              placeholder="e.g., 150g, 1 cup, 1 piece"
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-fitagent-green-500 focus:border-transparent ${
                errors.servingSize ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
            />
            {errors.servingSize && (
              <p className="text-red-500 text-xs mt-1">{errors.servingSize}</p>
            )}
          </div>

          {/* Nutrition Grid */}
          <div className="grid grid-cols-2 gap-4">
            {/* Calories */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Calories
              </label>
              <input
                type="number"
                min="0"
                step="1"
                value={formData.calories}
                onChange={(e) => handleInputChange('calories', parseInt(e.target.value) || 0)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-fitagent-green-500 focus:border-transparent ${
                  errors.calories ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
              />
              {errors.calories && (
                <p className="text-red-500 text-xs mt-1">{errors.calories}</p>
              )}
            </div>

            {/* Protein */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Protein (g) *
              </label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={formData.protein}
                onChange={(e) => handleInputChange('protein', parseFloat(e.target.value) || 0)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-fitagent-green-500 focus:border-transparent ${
                  errors.protein ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
              />
              {errors.protein && (
                <p className="text-red-500 text-xs mt-1">{errors.protein}</p>
              )}
            </div>

            {/* Carbs */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Carbs (g)
              </label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={formData.carbs}
                onChange={(e) => handleInputChange('carbs', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-fitagent-green-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            {/* Fats */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Fats (g)
              </label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={formData.fats}
                onChange={(e) => handleInputChange('fats', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-fitagent-green-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          {/* Protein Focus Message */}
          <div className="bg-fitagent-green-50 dark:bg-fitagent-green-900/20 border border-fitagent-green-200 dark:border-fitagent-green-800 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <span className="text-fitagent-green-600 dark:text-fitagent-green-400">💪</span>
              <p className="text-sm text-fitagent-green-700 dark:text-fitagent-green-300">
                Focus on protein for your fitness goals! Aim for {formData.protein}g per serving.
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-fitagent-green-500 text-white rounded-lg hover:bg-fitagent-green-600 transition-colors font-medium"
            >
              Add to Meal
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}