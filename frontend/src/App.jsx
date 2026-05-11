import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Brain, ArrowRight, Sparkles,
  FileText, Music, Video, Zap, MessageSquare, PlayCircle,
} from 'lucide-react';
import CustomCursor from './components/CustomCursor';
import UploadSection from './components/UploadSection';
import ProcessingResults from './components/ProcessingResults';
import './index.css';

/* ────────────────────────────────────────
   Floating Decorative Blobs
   ──────────────────────────────────────── */
const Blob = ({ style, color, size = 64, rotate = 12, opacity = 0.85 }) => (
  <motion.div
    animate={{ y: [0, -10, 0], rotate: [rotate, rotate + 6, rotate] }}
    transition={{ duration: 5 + Math.random() * 3, repeat: Infinity, ease: 'easeInOut' }}
    className="absolute pointer-events-none"
    style={{
      width: size,
      height: size,
      borderRadius: '28%',
      background: color,
      opacity,
      ...style,
    }}
  />
);

/* ────────────────────────────────────────
   Stat Card
   ──────────────────────────────────────── */
const StatCard = ({ value, label }) => (
  <div className="card flex flex-col items-center justify-center gap-1 px-10 py-5">
    <span
      className="text-2xl font-bold font-mono"
      style={{
        background: 'linear-gradient(135deg,#7C3AED,#A78BFA)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
      }}
    >
      {value}
    </span>
    <span className="text-ink-muted text-xs tracking-wide text-center">{label}</span>
  </div>
);

/* ────────────────────────────────────────
   Feature Chip
   ──────────────────────────────────────── */
const FeatureChip = ({ icon: Icon, label, color }) => (
  <div
    className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium border"
    style={{
      background: `${color}18`,
      borderColor: `${color}44`,
      color,
    }}
  >
    <Icon size={13} />
    {label}
  </div>
);

/* ────────────────────────────────────────
   APP
   ──────────────────────────────────────── */
const App = () => {
  const [processingResult, setProcessingResult] = useState(null);

  const handleProcessingComplete = (data) => {
    setProcessingResult(data);
    // Smooth scroll to results
    setTimeout(() => {
      window.scrollTo({ top: 800, behavior: 'smooth' });
    }, 100);
  };

  return (
    <div className="min-h-screen bg-bg-base overflow-x-hidden">
      <CustomCursor />

      {/* ══════════════ NAVBAR ══════════════ */}
      <motion.header
        initial={{ opacity: 0, y: -14 }}
        animate={{ opacity: 1,  y:   0 }}
        transition={{ duration: 0.45 }}
        className="sticky top-0 z-50 bg-bg-base/80 backdrop-blur-md border-b border-border"
      >
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5" data-cursor="pointer">
            <div className="w-8 h-8 rounded-lg bg-primary-light border border-primary-border flex items-center justify-center">
              <Brain size={16} className="text-primary" />
            </div>
            <span className="font-bold text-ink tracking-tight text-[15px]">
              AI<span className="text-primary">QnA</span>
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-9 text-sm text-ink-muted">
            <a href="#features" data-cursor="pointer" className="hover:text-ink transition-colors duration-200 font-medium tracking-wide">Features</a>
          </nav>
        </div>
      </motion.header>

      {/* ══════════════ HERO SECTION ══════════════ */}
      <section className="relative max-w-6xl mx-auto px-6 pt-16 pb-12 flex flex-col items-center text-center overflow-visible">

        {/* ── Floating decorative blobs ── */}
        <Blob color="#A78BFA" size={72} rotate={15}  opacity={0.55} style={{ top: '8%',  left:  '3%'  }} />
        <Blob color="#C4B5FD" size={40} rotate={-20} opacity={0.40} style={{ top: '30%', left:  '8%'  }} />
        <Blob color="#D4B896" size={52} rotate={30}  opacity={0.55} style={{ top: '12%', right: '4%'  }} />
        <Blob color="#E8D5B0" size={36} rotate={-10} opacity={0.50} style={{ top: '55%', right: '2%'  }} />
        <Blob color="#DDD6FE" size={44} rotate={20}  opacity={0.45} style={{ bottom: '8%', left: '5%' }} />
        <Blob color="#C9A96E" size={30} rotate={40}  opacity={0.40} style={{ bottom: '12%', right: '6%' }} />

        {/* ── Main Content ── */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y:  0  }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
          className="flex flex-col items-center w-full"
        >
          {/* Badge */}
          <div className="mb-7">
            <span className="badge-purple">
              <Sparkles size={12} />
              Powered by Gemini 3.1 Flash + Local RAG
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-[60px] font-extrabold leading-[1.1] tracking-tight mb-6 max-w-4xl text-ink">
            AI-Powered <span className="gradient-text">Document & Media</span><br />Intelligence
          </h1>

          {/* Sub-headline */}
          <p className="text-ink-body text-lg max-w-2xl mb-10 leading-relaxed">
            Upload PDFs, audio, or video — get instant summaries, timestamped transcripts, and chat with your content using a private, local RAG engine.
          </p>

          {/* CTA Buttons - Using the new UploadSection */}
          <div className="flex flex-wrap items-center justify-center gap-4 mb-12">
            <UploadSection onProcessingComplete={handleProcessingComplete} />
          </div>

          {/* Feature chips */}
          <div id="features" className="flex flex-wrap justify-center gap-2 mb-16 pt-8">
            <FeatureChip icon={FileText} label="PDF Analysis"       color="#9F7AEA" />
            <FeatureChip icon={Music}    label="Audio Transcription" color="#C084FC" />
            <FeatureChip icon={Video}    label="Video Intelligence"  color="#A78BFA" />
            <FeatureChip icon={Zap}      label="RAG Chat Engine"     color="#7C3AED" />
          </div>
        </motion.div>

        {/* ── Results Display ── */}
        <ProcessingResults data={processingResult} />

        {/* ── Stat Cards ── */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl mb-20">
          <StatCard value="100%"  label="Free Tier"    />
          <StatCard value="< 2s"  label="Avg Response" />
          <StatCard value="3"     label="File Formats" />
        </div>

        {/* ── Future Feature Placeholders ── */}
        {!processingResult && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
            <div
              className="card p-8 flex flex-col items-center text-center gap-4 min-h-[260px] justify-center"
              style={{ border: '1.5px dashed #C4B5FD' }}
            >
              <div className="w-12 h-12 rounded-2xl bg-primary-light flex items-center justify-center">
                <MessageSquare size={24} style={{ color: '#9F7AEA' }} />
              </div>
              <span className="badge-purple">AI Chat Engine</span>
              <h3 className="text-ink font-bold text-lg">RAG Chatbot Interface</h3>
              <p className="text-ink-muted text-sm max-w-xs leading-relaxed">Ask questions about your uploaded documents. Source-grounded answers.</p>
            </div>
            <div
              className="card p-8 flex flex-col items-center text-center gap-4 min-h-[260px] justify-center"
              style={{ border: '1.5px dashed #C4B5FD' }}
            >
              <div className="w-12 h-12 rounded-2xl bg-primary-light flex items-center justify-center">
                <PlayCircle size={24} style={{ color: '#9F7AEA' }} />
              </div>
              <span className="badge-purple">Timestamped Transcripts</span>
              <h3 className="text-ink font-bold text-lg">Multimedia Player</h3>
              <p className="text-ink-muted text-sm max-w-xs leading-relaxed">Watch and read in sync. Automatic timestamp indexing.</p>
            </div>
          </div>
        )}
      </section>
    </div>
  );
};

export default App;
