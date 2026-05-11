import React, { forwardRef } from 'react';

const MediaViewer = forwardRef(({ fileUrl, isVideo }, ref) => {
  return (
    <div className="w-full bg-white rounded-2xl border border-border overflow-hidden shadow-sm">
      <div className="bg-bg-subtle px-4 py-2 border-b border-border text-xs font-semibold text-ink-muted uppercase tracking-wider">
        Media Player
      </div>
      <div className="p-4 flex justify-center bg-bg-base/50">
        {isVideo ? (
          <video
            ref={ref}
            controls
            className="w-full max-h-[300px] rounded-lg shadow-sm"
            src={fileUrl}
          />
        ) : (
          <audio
            ref={ref}
            controls
            className="w-full"
            src={fileUrl}
          />
        )}
      </div>
    </div>
  );
});

export default MediaViewer;
