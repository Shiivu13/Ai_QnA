import React, { useState } from 'react';
import VideoPlayer from '../components/VideoPlayer';
import ChatBox from '../components/ChatBox';
import { motion } from 'framer-motion';
import { Share2, Bookmark, MoreHorizontal } from 'lucide-react';

const Dashboard = () => {
  const [activeVideoId, setActiveVideoId] = useState(1); // Demo ID

  return (
    <div className="flex flex-col lg:flex-row gap-8 h-full">
      {/* Left: Video Section */}
      <div className="flex-1 space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <VideoPlayer 
            src="https://www.w3schools.com/html/mov_bbb.mp4" 
            poster="https://peach.blender.org/wp-content/uploads/title_anouncement.jpg"
          />
        </motion.div>

        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">Introduction to Modern AI Architecture</h1>
            <p className="text-slate-400">Published on May 11, 2026 • 12,453 views</p>
          </div>
          <div className="flex gap-2">
            <ActionButton icon={<Share2 size={18} />} label="Share" />
            <ActionButton icon={<Bookmark size={18} />} label="Save" />
            <ActionButton icon={<MoreHorizontal size={18} />} />
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="font-bold mb-4 text-indigo-400 uppercase text-xs tracking-widest">Description</h3>
          <p className="text-slate-300 leading-relaxed">
            In this session, we explore the convergence of FastAPI, React, and Gemini to build agentic RAG systems. 
            We'll dive deep into how vector databases like FAISS enable real-time semantic search across video transcriptions.
          </p>
        </div>
      </div>

      {/* Right: AI Chat Section */}
      <div className="w-full lg:w-[400px] flex flex-col h-[600px] lg:h-auto">
        <ChatBox videoId={activeVideoId} />
      </div>
    </div>
  );
};

const ActionButton = ({ icon, label }) => (
  <button className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-slate-700">
    {icon}
    {label && <span>{label}</span>}
  </button>
);

export default Dashboard;
