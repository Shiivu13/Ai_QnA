import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Bot, User } from 'lucide-react';
import axios from 'axios';

const ChatBox = ({ videoId }) => {
  const [messages, setMessages] = useState([
    { role: 'bot', content: 'Hello! I am your AI video assistant. Ask me anything about the video content.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || !videoId) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/v1/chat', {
        query: input,
        video_id: videoId
      });

      const botMessage = { role: 'bot', content: response.data.answer };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', content: 'Sorry, I encountered an error processing your request.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full glass-card overflow-hidden">
      <div className="p-4 border-b border-slate-800 font-bold flex items-center gap-2">
        <Bot size={20} className="text-indigo-400" />
        AI Video Chat
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <motion.div
            initial={{ opacity: 0, x: msg.role === 'user' ? 20 : -20 }}
            animate={{ opacity: 1, x: 0 }}
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[80%] p-3 rounded-2xl ${
              msg.role === 'user' 
                ? 'bg-indigo-600 text-white rounded-tr-none' 
                : 'bg-slate-800 text-slate-200 rounded-tl-none'
            }`}>
              <p className="text-sm">{msg.content}</p>
            </div>
          </motion.div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 p-3 rounded-2xl rounded-tl-none animate-pulse">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-slate-500 rounded-full" />
                <div className="w-2 h-2 bg-slate-500 rounded-full" />
                <div className="w-2 h-2 bg-slate-500 rounded-full" />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-slate-900/50 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask a question..."
          className="flex-1 bg-slate-800 border-none rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 transition-all outline-none"
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="bg-indigo-600 p-2 rounded-lg hover:bg-indigo-500 disabled:opacity-50 transition-colors"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
