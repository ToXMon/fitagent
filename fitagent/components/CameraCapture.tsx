'use client';

import { useState, useRef, useCallback, useEffect } from 'react';

interface CameraCaptureProps {
  onPhotosCapture: (files: File[]) => void;
  onCancel: () => void;
}

interface CapturedImage {
  id: string;
  file: File;
  url: string;
  type: 'food' | 'nutrition-label' | 'beverage';
  processing?: boolean;
}

export function CameraCapture({ onPhotosCapture, onCancel }: CameraCaptureProps) {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [capturedImages, setCapturedImages] = useState<CapturedImage[]>([]);
  const [isCapturing, setIsCapturing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<'food' | 'nutrition-label' | 'beverage'>('food');
  const [showTypeSelector, setShowTypeSelector] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Initialize camera
  useEffect(() => {
    const initCamera = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { 
            facingMode: 'environment', // Use back camera on mobile
            width: { ideal: 1920 },
            height: { ideal: 1080 }
          }
        });
        setStream(mediaStream);
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch (err) {
        console.error('Camera access error:', err);
        setError('Camera access denied. Please allow camera permissions or use file upload.');
      }
    };

    initCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;

    setIsCapturing(true);
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to blob and create file
    canvas.toBlob((blob) => {
      if (blob) {
        const timestamp = Date.now();
        const file = new File([blob], `meal-${timestamp}.jpg`, { type: 'image/jpeg' });
        const url = URL.createObjectURL(blob);
        
        const newImage: CapturedImage = {
          id: timestamp.toString(),
          file,
          url,
          type: selectedType,
          processing: false
        };

        setCapturedImages(prev => [...prev, newImage]);
        setShowTypeSelector(false);
      }
      setIsCapturing(false);
    }, 'image/jpeg', 0.9);
  }, [selectedType]);

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    Array.from(files).forEach(file => {
      if (file.type.startsWith('image/')) {
        const url = URL.createObjectURL(file);
        const newImage: CapturedImage = {
          id: Date.now().toString() + Math.random(),
          file,
          url,
          type: selectedType,
          processing: false
        };
        setCapturedImages(prev => [...prev, newImage]);
      }
    });
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [selectedType]);

  const removeImage = useCallback((id: string) => {
    setCapturedImages(prev => {
      const updated = prev.filter(img => img.id !== id);
      // Clean up object URL
      const imageToRemove = prev.find(img => img.id === id);
      if (imageToRemove) {
        URL.revokeObjectURL(imageToRemove.url);
      }
      return updated;
    });
  }, []);

  const handleComplete = useCallback(() => {
    const files = capturedImages.map(img => img.file);
    onPhotosCapture(files);
    
    // Clean up object URLs
    capturedImages.forEach(img => URL.revokeObjectURL(img.url));
  }, [capturedImages, onPhotosCapture]);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'food': return '🍽️';
      case 'nutrition-label': return '🏷️';
      case 'beverage': return '🥤';
      default: return '📷';
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'food': return 'Food Dish';
      case 'nutrition-label': return 'Nutrition Label';
      case 'beverage': return 'Beverage';
      default: return 'Photo';
    }
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center p-4 bg-black/80 text-white">
        <button
          onClick={onCancel}
          className="flex items-center space-x-2 text-white/80 hover:text-white"
        >
          <span>←</span>
          <span>Cancel</span>
        </button>
        <h2 className="font-semibold">Capture Meal</h2>
        <div className="w-16"></div>
      </div>

      {/* Camera View */}
      <div className="flex-grow relative">
        {error ? (
          <div className="flex flex-col items-center justify-center h-full p-4 text-white">
            <div className="text-6xl mb-4">📷</div>
            <p className="text-center mb-4">{error}</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="bg-fitagent-green-500 text-white px-6 py-3 rounded-lg"
            >
              Choose from Gallery
            </button>
          </div>
        ) : (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
            <canvas ref={canvasRef} className="hidden" />
            
            {/* Camera Controls */}
            <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
              {/* Type Selector */}
              {showTypeSelector && (
                <div className="mb-4 flex justify-center space-x-2">
                  {(['food', 'nutrition-label', 'beverage'] as const).map((type) => (
                    <button
                      key={type}
                      onClick={() => setSelectedType(type)}
                      className={`px-4 py-2 rounded-full text-sm flex items-center space-x-2 ${
                        selectedType === type
                          ? 'bg-fitagent-green-500 text-white'
                          : 'bg-white/20 text-white/80'
                      }`}
                    >
                      <span>{getTypeIcon(type)}</span>
                      <span>{getTypeLabel(type)}</span>
                    </button>
                  ))}
                </div>
              )}

              {/* Capture Controls */}
              <div className="flex justify-center items-center space-x-6">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-white"
                >
                  📁
                </button>
                
                <button
                  onClick={() => setShowTypeSelector(!showTypeSelector)}
                  className="text-white/80 text-sm"
                >
                  {getTypeIcon(selectedType)} {getTypeLabel(selectedType)}
                </button>
                
                <button
                  onClick={capturePhoto}
                  disabled={isCapturing}
                  className="w-16 h-16 bg-white rounded-full flex items-center justify-center disabled:opacity-50"
                >
                  {isCapturing ? (
                    <div className="w-8 h-8 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <div className="w-12 h-12 bg-fitagent-green-500 rounded-full"></div>
                  )}
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Captured Images */}
      {capturedImages.length > 0 && (
        <div className="bg-black/90 p-4">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-white font-medium">
              Captured ({capturedImages.length})
            </h3>
            <button
              onClick={handleComplete}
              className="bg-fitagent-green-500 text-white px-4 py-2 rounded-lg font-medium"
            >
              Analyze Meal
            </button>
          </div>
          
          <div className="flex space-x-3 overflow-x-auto">
            {capturedImages.map((image) => (
              <div key={image.id} className="relative flex-shrink-0">
                <img
                  src={image.url}
                  alt="Captured meal"
                  className="w-20 h-20 object-cover rounded-lg"
                />
                <div className="absolute -top-1 -right-1 bg-fitagent-green-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
                  {getTypeIcon(image.type)}
                </div>
                <button
                  onClick={() => removeImage(image.id)}
                  className="absolute -top-1 -left-1 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleFileUpload}
        className="hidden"
      />
    </div>
  );
}