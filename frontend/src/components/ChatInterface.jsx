import React, { useState } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import api from '../services/api';

const ChatInterface = ({ filename, onTimestampClick }) => {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hi! I have analyzed the document. Ask me anything about it!' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userQuery = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userQuery }]);
    setIsLoading(true);

    try {
      const response = await api.post('/api/chat', {
        filename: filename,
        query: userQuery
      });
      
      setMessages(prev => [...prev, { role: 'ai', content: response.data.answer }]);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages(prev => [...prev, { role: 'ai', content: "Sorry, I encountered an error answering that." }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper to parse and render text with clickable timestamps
  const renderMessageContent = (content) => {
    if (!onTimestampClick) return content;

    // Split text by timestamps like [1.5s - 2.5s]
    const splitRegex = /(\[\d+(?:\.\d+)?s?\s*-\s*\d+(?:\.\d+)?s?\])/g;
    const parts = content.split(splitRegex);

    return parts.map((part, i) => {
      // Use a fresh stateless regex to test each part to avoid lastIndex bugs
      const isTimestamp = /^\[\d+(?:\.\d+)?s?\s*-\s*\d+(?:\.\d+)?s?\]$/.test(part);
      
      if (isTimestamp) {
        // Extract both numbers as start and end
        const match = part.match(/\[(\d+(?:\.\d+)?)[s]?\s*-\s*(\d+(?:\.\d+)?)[s]?\]/);
        if (match) {
          const startTime = parseFloat(match[1]);
          const endTime = parseFloat(match[2]);
          return (
            <button
              key={i}
              onClick={() => onTimestampClick(startTime, endTime)}
              className="inline-flex items-center gap-1 font-mono text-[12px] font-bold text-primary bg-primary-light hover:bg-[#D8B4FE] px-2 py-0.5 rounded-md transition-colors mx-1 align-baseline border border-primary/20"
            >
              ▶ {part}
            </button>
          );
        }
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="w-full flex flex-col bg-white rounded-2xl border border-border overflow-hidden shadow-sm h-[500px]">
      <div className="bg-bg-subtle px-4 py-3 border-b border-border flex items-center gap-2">
        <Bot size={18} className="text-primary" />
        <span className="text-sm font-semibold text-ink">RAG Chat Engine</span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-bg-base/30">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'ai' && (
              <div className="w-8 h-8 rounded-full bg-primary-light flex items-center justify-center flex-shrink-0 mt-1">
                <Bot size={14} className="text-primary" />
              </div>
            )}
            <div 
              className={`px-4 py-3 rounded-2xl max-w-[80%] text-[15px] leading-relaxed shadow-sm ${
                msg.role === 'user' 
                  ? 'bg-ink text-white rounded-tr-sm' 
                  : 'bg-white border border-border rounded-tl-sm text-ink-body'
              }`}
            >
              {renderMessageContent(msg.content)}
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-border flex items-center justify-center flex-shrink-0 mt-1">
                <User size={14} className="text-ink-muted" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-primary-light flex items-center justify-center flex-shrink-0 mt-1">
              <Bot size={14} className="text-primary" />
            </div>
            <div className="px-4 py-3 rounded-2xl bg-white border border-border shadow-sm rounded-tl-sm flex items-center gap-2 text-primary">
              <Loader2 size={16} className="animate-spin" />
              <span className="text-xs font-medium">Thinking...</span>
            </div>
          </div>
        )}
      </div>

      <div className="p-3 bg-white border-t border-border">
        <form onSubmit={handleSend} className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your document..."
            className="w-full bg-bg-base text-ink placeholder-ink-light px-4 py-3 rounded-xl border border-transparent focus:border-primary-border focus:bg-white focus:outline-none transition-all pr-12 text-[15px]"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-2 bg-primary text-white rounded-lg disabled:opacity-50 hover:bg-primary-hover transition-colors shadow-sm"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
