import React, { useRef, useState } from 'react';
import { Upload, Loader2, AlertCircle } from 'lucide-react';
import api from '../services/api';

const UploadSection = ({ onProcessingComplete }) => {
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Step 1: Upload the file
      const uploadRes = await api.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const { filename } = uploadRes.data;
      const fileExt = filename.split('.').pop().toLowerCase();

      let resultData = null;

      // Step 2: Process based on file type
      if (fileExt === 'pdf') {
        const processRes = await api.post('/api/summarize-pdf', { filename });
        resultData = { type: 'pdf', ...processRes.data };
      } else if (['mp3', 'wav', 'mp4'].includes(fileExt)) {
        const processRes = await api.post('/api/transcribe-media', { filename });
        resultData = { type: 'media', ...processRes.data };
      } else {
        throw new Error("Unsupported file format.");
      }

      console.log("Backend Data Received:", resultData);
      onProcessingComplete(resultData);
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.response?.data?.detail || err.message || "Something went wrong.");
    } finally {
      setIsUploading(false);
      // Reset input
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".pdf,.mp3,.wav,.mp4"
      />
      
      <button
        onClick={handleUploadClick}
        disabled={isUploading}
        data-cursor="pointer"
        className={`btn-primary flex items-center gap-2 min-w-[200px] justify-center ${
          isUploading ? 'opacity-80' : ''
        }`}
      >
        {isUploading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Processing Intelligence...
          </>
        ) : (
          <>
            <Upload className="w-4 h-4" />
            Upload Knowledge
          </>
        )}
      </button>

      {error && (
        <div className="flex items-center gap-2 text-red-500 text-xs font-medium animate-pulse">
          <AlertCircle size={14} />
          {error}
        </div>
      )}
    </div>
  );
};

export default UploadSection;
