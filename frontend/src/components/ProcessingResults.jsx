import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import { FileText, Headphones, Clock, CheckCircle2, Play } from 'lucide-react';
import MediaViewer from './MediaViewer';
import ChatInterface from './ChatInterface';
import api from '../services/api';

const ProcessingResults = ({ data }) => {
  if (!data) return null;

  const isPdf = data.type === 'pdf';
  const playerRef = useRef(null);

  const activeListenerRef = useRef(null);

  const handleTimestampClick = (start, end) => {
    const player = playerRef.current;
    if (!player) return;

    // Clean up previous event listener
    if (activeListenerRef.current) {
      player.removeEventListener('timeupdate', activeListenerRef.current);
      activeListenerRef.current = null;
    }

    const safeStart = parseFloat(start) || 0;
    const safeEnd = parseFloat(end) || 0;

    const playSegment = () => {
      // Direct assignment works best in most browsers
      player.currentTime = safeStart;
      
      // Small timeout allows the browser to process the seek before playing
      setTimeout(() => {
        player.play().catch(e => console.error("Playback failed:", e));
      }, 50);

      // Stop at end time
      if (safeEnd > safeStart) {
        const listener = () => {
          if (player.currentTime >= safeEnd) {
            player.pause();
            player.removeEventListener('timeupdate', listener);
            activeListenerRef.current = null;
          }
        };
        activeListenerRef.current = listener;
        player.addEventListener('timeupdate', listener);
      }
    };

    // If metadata is ready, play immediately. Otherwise wait for it.
    if (player.readyState >= 1) {
      playSegment();
    } else {
      player.addEventListener('loadedmetadata', playSegment, { once: true });
    }
  };

  // Helper to format file URL using our API baseURL
  const fileUrl = `${api.defaults.baseURL}/uploads/${data.filename}`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="w-full max-w-5xl mx-auto mt-12 mb-20"
    >
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Column: Media / Summary */}
        <div className="flex flex-col gap-6">
          <div className="card p-8 relative overflow-hidden">
            {/* Subtle background icon */}
            <div className="absolute -right-8 -top-8 opacity-[0.03] text-primary pointer-events-none">
              {isPdf ? <FileText size={200} /> : <Headphones size={200} />}
            </div>

            <div className="flex items-center gap-3 mb-6 relative z-10">
              <div className="w-10 h-10 rounded-xl bg-primary-light flex items-center justify-center text-primary shadow-sm">
                {isPdf ? <FileText size={20} /> : <Headphones size={20} />}
              </div>
              <div>
                <h3 className="text-ink font-bold text-lg leading-tight">
                  {isPdf ? 'Document Analysis' : 'Media Intelligence'}
                </h3>
                <p className="text-ink-muted text-[13px] flex items-center gap-1 mt-0.5">
                  <CheckCircle2 size={13} className="text-green-500" />
                  Processed: {data.filename}
                </p>
              </div>
            </div>

            <div className="w-full h-px bg-border mb-6" />

            {isPdf ? (
              <div className="space-y-4 relative z-10">
                <h4 className="text-ink font-semibold text-sm uppercase tracking-wider flex items-center gap-2">
                  <FileText size={14} className="text-primary" />
                  Executive Summary
                </h4>
                <div className="text-ink-body text-[15px] leading-relaxed whitespace-pre-wrap bg-bg-base/60 p-6 rounded-2xl border border-border/60 shadow-inner">
                  {data.summary || "No summary available."}
                </div>
              </div>
            ) : (
              <div className="space-y-6 relative z-10">
                <MediaViewer 
                  ref={playerRef} 
                  fileUrl={fileUrl} 
                  isVideo={data.filename.endsWith('.mp4')} 
                />

                <div className="space-y-3">
                  <h4 className="text-ink font-semibold text-sm uppercase tracking-wider flex items-center gap-2">
                    <Clock size={14} className="text-primary" />
                    Timestamped Transcript
                  </h4>
                  <div className="max-h-[300px] overflow-y-auto space-y-3 pr-2 custom-scrollbar bg-bg-base/30 rounded-xl p-2 border border-border/30">
                    {data?.segments && data.segments.length > 0 ? (
                      data.segments.map((segment, idx) => (
                        <div 
                          key={idx}
                          className="group flex gap-4 p-4 rounded-xl border border-border/50 bg-white hover:border-primary-border/60 hover:shadow-sm transition-all duration-200"
                        >
                          <button
                            onClick={() => handleTimestampClick(segment.start, segment.end)}
                            className="flex-shrink-0 flex items-center gap-1 font-mono text-[11px] font-bold text-primary bg-primary-light hover:bg-[#D8B4FE] px-2.5 py-1.5 h-fit rounded-lg transition-colors"
                          >
                            <Play size={10} />
                            {segment.start.toFixed(1)}s - {segment.end.toFixed(1)}s
                          </button>
                          <p className="text-ink-body text-[14px] leading-relaxed pt-0.5">
                            {segment.text}
                          </p>
                        </div>
                      ))
                    ) : (
                      <p className="text-ink-muted text-sm italic p-4 text-center">No segments found.</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Chat Interface */}
        <div className="flex flex-col">
          <ChatInterface 
            filename={data.filename} 
            onTimestampClick={!isPdf ? handleTimestampClick : null} 
          />
        </div>

      </div>
    </motion.div>
  );
};

export default ProcessingResults;
