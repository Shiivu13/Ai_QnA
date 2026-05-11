import React, { useRef, useState } from 'react';
import { Play, Pause, Volume2, Maximize, RotateCcw } from 'lucide-react';

const VideoPlayer = ({ src, poster }) => {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);

  const togglePlay = () => {
    if (videoRef.current.paused) {
      videoRef.current.play();
      setIsPlaying(true);
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  };

  const handleProgress = () => {
    const currentProgress = (videoRef.current.currentTime / videoRef.current.duration) * 100;
    setProgress(currentProgress);
  };

  return (
    <div className="relative group rounded-xl overflow-hidden glass-card bg-black shadow-2xl">
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        onTimeUpdate={handleProgress}
        className="w-full aspect-video object-cover"
        onClick={togglePlay}
      />
      
      {/* Controls Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-4">
        <div className="flex flex-col gap-3">
          {/* Progress Bar */}
          <div className="w-full h-1 bg-slate-700 rounded-full cursor-pointer overflow-hidden">
            <div 
              className="h-full bg-indigo-500 transition-all duration-100" 
              style={{ width: `${progress}%` }}
            />
          </div>

          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <button onClick={togglePlay} className="hover:text-indigo-400 transition-colors">
                {isPlaying ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" />}
              </button>
              <button className="hover:text-indigo-400 transition-colors">
                <RotateCcw size={18} />
              </button>
              <Volume2 size={18} className="text-slate-400" />
            </div>
            
            <div className="flex items-center gap-4 text-xs font-mono text-slate-300">
              <span>00:00 / 12:45</span>
              <Maximize size={18} className="cursor-pointer hover:text-indigo-400 transition-colors" />
            </div>
          </div>
        </div>
      </div>

      {/* Play Icon in Middle */}
      {!isPlaying && (
        <div 
          onClick={togglePlay}
          className="absolute inset-0 flex items-center justify-center cursor-pointer group-hover:scale-110 transition-transform"
        >
          <div className="bg-indigo-600/20 backdrop-blur-md p-6 rounded-full border border-indigo-500/50">
            <Play size={40} className="text-white fill-white ml-1" />
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoPlayer;
