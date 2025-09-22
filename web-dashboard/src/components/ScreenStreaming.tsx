'use client';

import { useState, useRef, useEffect } from 'react';
import { Monitor, Play, Square, RotateCcw, Download, Maximize2, Minimize2, Settings, Wifi, WifiOff } from 'lucide-react';

interface ScreenStreamingProps {
  deviceId: string;
  deviceName?: string;
  isConnected?: boolean;
  isStreaming?: boolean;
  streamUrl?: string;
  onStartStream?: () => void;
  onStopStream?: () => void;
  onRotateScreen?: () => void;
  onTakeScreenshot?: () => void;
  onOpenSettings?: () => void;
}

export default function ScreenStreaming({
  deviceId,
  deviceName = 'Unknown Device',
  isConnected = false,
  isStreaming = false,
  streamUrl,
  onStartStream,
  onStopStream,
  onRotateScreen,
  onTakeScreenshot,
  onOpenSettings
}: ScreenStreamingProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [quality, setQuality] = useState<'low' | 'medium' | 'high'>('medium');
  const [showControls, setShowControls] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Handle fullscreen
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Auto-hide controls in fullscreen
  useEffect(() => {
    if (isFullscreen) {
      const timer = setTimeout(() => setShowControls(false), 3000);
      return () => clearTimeout(timer);
    } else {
      setShowControls(true);
    }
  }, [isFullscreen]);

  const qualitySettings = {
    low: { width: 480, height: 854, bitrate: '500kbps' },
    medium: { width: 720, height: 1280, bitrate: '1Mbps' },
    high: { width: 1080, height: 1920, bitrate: '2Mbps' }
  };

  return (
    <div 
      ref={containerRef}
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 overflow-hidden ${
        isFullscreen ? 'fixed inset-0 z-50 rounded-none' : ''
      }`}
      onMouseMove={() => isFullscreen && setShowControls(true)}
    >
      {/* Header */}
      <div className={`flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 transition-opacity duration-300 ${
        isFullscreen && !showControls ? 'opacity-0' : 'opacity-100'
      }`}>
        <div className="flex items-center space-x-3">
          <Monitor className="h-5 w-5 text-gray-600 dark:text-gray-400" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {deviceName}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {deviceId}
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className={`h-2 w-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {isConnected ? 'Kết nối' : 'Mất kết nối'}
            </span>
            {isConnected ? <Wifi className="h-4 w-4 text-green-500" /> : <WifiOff className="h-4 w-4 text-red-500" />}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Quality Selector */}
          <select
            value={quality}
            onChange={(e) => setQuality(e.target.value as 'low' | 'medium' | 'high')}
            className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="low">Thấp (480p)</option>
            <option value="medium">Trung bình (720p)</option>
            <option value="high">Cao (1080p)</option>
          </select>
          
          <button
            onClick={onOpenSettings}
            className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            title="Cài đặt"
          >
            <Settings className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Stream Content */}
      <div className="relative bg-black">
        {isStreaming && streamUrl ? (
          <video
            ref={videoRef}
            src={streamUrl}
            autoPlay
            muted
            className="w-full h-auto max-h-96 object-contain"
            style={{
              aspectRatio: `${qualitySettings[quality].width}/${qualitySettings[quality].height}`
            }}
          />
        ) : (
          <div 
            className="flex flex-col items-center justify-center text-white bg-gray-900"
            style={{
              aspectRatio: `${qualitySettings[quality].width}/${qualitySettings[quality].height}`,
              minHeight: '300px'
            }}
          >
            <Monitor className="h-16 w-16 mb-4 text-gray-600" />
            <h3 className="text-xl font-medium mb-2">
              {!isConnected ? 'Thiết bị chưa kết nối' : 
               !isStreaming ? 'Chưa bắt đầu stream' : 'Đang tải...'}
            </h3>
            <p className="text-gray-400 text-center max-w-md">
              {!isConnected ? 'Vui lòng kiểm tra kết nối thiết bị' :
               !isStreaming ? 'Nhấn nút Play để bắt đầu xem màn hình thiết bị' :
               'Đang thiết lập kết nối stream...'}
            </p>
          </div>
        )}
        
        {/* Stream Info Overlay */}
        {isStreaming && (
          <div className={`absolute top-4 left-4 bg-black bg-opacity-50 text-white px-3 py-1 rounded text-sm transition-opacity duration-300 ${
            isFullscreen && !showControls ? 'opacity-0' : 'opacity-100'
          }`}>
            <div>Chất lượng: {qualitySettings[quality].width}x{qualitySettings[quality].height}</div>
            <div>Bitrate: {qualitySettings[quality].bitrate}</div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className={`flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-900 transition-opacity duration-300 ${
        isFullscreen && !showControls ? 'opacity-0' : 'opacity-100'
      }`}>
        <div className="flex items-center space-x-2">
          {!isStreaming ? (
            <button
              onClick={onStartStream}
              disabled={!isConnected}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-colors"
            >
              <Play className="h-4 w-4" />
              <span>Bắt đầu</span>
            </button>
          ) : (
            <button
              onClick={onStopStream}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 flex items-center space-x-2 transition-colors"
            >
              <Square className="h-4 w-4" />
              <span>Dừng</span>
            </button>
          )}
          
          <button
            onClick={onRotateScreen}
            disabled={!isConnected}
            className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Xoay màn hình"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
          
          <button
            onClick={onTakeScreenshot}
            disabled={!isConnected}
            className="px-3 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Chụp màn hình"
          >
            <Download className="h-4 w-4" />
          </button>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleFullscreen}
            className="px-3 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            title={isFullscreen ? 'Thoát toàn màn hình' : 'Toàn màn hình'}
          >
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </button>
        </div>
      </div>
      
      {/* Status Bar */}
      <div className={`px-4 py-2 bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-400 transition-opacity duration-300 ${
        isFullscreen && !showControls ? 'opacity-0' : 'opacity-100'
      }`}>
        <div className="flex items-center justify-between">
          <span>
            Trạng thái: {!isConnected ? 'Mất kết nối' : isStreaming ? 'Đang stream' : 'Sẵn sàng'}
          </span>
          
          {isStreaming && (
            <span className="flex items-center space-x-2">
              <div className="h-2 w-2 bg-red-500 rounded-full animate-pulse"></div>
              <span>LIVE</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}