import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, useMotionValue, useSpring, AnimatePresence } from 'framer-motion';

const PARTICLE_COLORS = ['#D8B4FE', '#A78BFA', '#C084FC', '#DDD6FE'];
const MAX_PARTICLES   = 24;
const LIFETIME_MS     = 500;

const CustomCursor = () => {
  const [isVisible,  setIsVisible]  = useState(false);
  const [isPointer,  setIsPointer]  = useState(false);
  const [particles,  setParticles]  = useState([]);
  const lastEmit = useRef(0);
  const pid      = useRef(0);

  // Zero-lag dot
  const dotX = useMotionValue(-200);
  const dotY = useMotionValue(-200);

  // Spring-lagged ring
  const ringX = useSpring(dotX, { stiffness: 170, damping: 22 });
  const ringY = useSpring(dotY, { stiffness: 170, damping: 22 });

  const emit = useCallback((x, y) => {
    const now = Date.now();
    if (now - lastEmit.current < 28) return;   // ~35 fps throttle
    lastEmit.current = now;

    const id     = pid.current++;
    const size   = Math.random() * 5 + 3;      // 3–8 px
    const angle  = Math.random() * Math.PI * 2;
    const speed  = Math.random() * 14 + 6;
    const color  = PARTICLE_COLORS[Math.floor(Math.random() * PARTICLE_COLORS.length)];

    const particle = {
      id, x, y, size, color,
      driftX: Math.cos(angle) * speed,
      driftY: Math.sin(angle) * speed - 5,    // slight upward bias
    };

    setParticles(prev => {
      const next = [...prev, particle];
      return next.length > MAX_PARTICLES ? next.slice(-MAX_PARTICLES) : next;
    });

    setTimeout(() => {
      setParticles(prev => prev.filter(p => p.id !== id));
    }, LIFETIME_MS);
  }, []);

  useEffect(() => {
    const onMove = (e) => {
      dotX.set(e.clientX);
      dotY.set(e.clientY);
      emit(e.clientX, e.clientY);
      if (!isVisible) setIsVisible(true);
    };
    const onOver = (e) => {
      const tag = e.target?.tagName?.toLowerCase();
      setIsPointer(
        ['a','button','input','textarea','select'].includes(tag) ||
        !!e.target?.closest('[data-cursor="pointer"]')
      );
    };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseover', onOver);
    document.addEventListener('mouseleave', () => setIsVisible(false));
    document.addEventListener('mouseenter', () => setIsVisible(true));
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseover', onOver);
    };
  }, [isVisible, dotX, dotY, emit]);

  // Skip on touch devices
  if (typeof window !== 'undefined' && window.matchMedia('(pointer: coarse)').matches) return null;
  if (!isVisible) return null;

  return (
    <>
      {/* ── Particle stream ── */}
      <AnimatePresence>
        {particles.map((p, i) => {
          const isSquare  = i % 4 === 0;
          const proximity = (i + 1) / particles.length; // head = 1, tail → 0
          return (
            <motion.div
              key={p.id}
              className="fixed top-0 left-0 pointer-events-none z-[9997]"
              style={{ translateX: '-50%', translateY: '-50%' }}
              initial={{ x: p.x, y: p.y, opacity: 0.9 * proximity, scale: 1 }}
              animate={{ x: p.x + p.driftX, y: p.y + p.driftY, opacity: 0, scale: 0.05 }}
              exit={{    opacity: 0, scale: 0 }}
              transition={{ duration: LIFETIME_MS / 1000, ease: 'easeOut' }}
            >
              <div style={{
                width:        p.size,
                height:       p.size,
                borderRadius: isSquare ? '3px' : '50%',
                background:   p.color,
                boxShadow:    `0 0 ${p.size * 2.5}px ${p.color}99`,
                filter:       'blur(0.5px)',
              }} />
            </motion.div>
          );
        })}
      </AnimatePresence>

      {/* ── Spring ring ── */}
      <motion.div
        className="fixed top-0 left-0 pointer-events-none z-[9998]"
        style={{ x: ringX, y: ringY, translateX: '-50%', translateY: '-50%' }}
      >
        <motion.div
          animate={{
            width:       isPointer ? 46 : 34,
            height:      isPointer ? 46 : 34,
            borderColor: isPointer ? '#7C3AED' : '#A78BFA',
            boxShadow:   isPointer
              ? '0 0 18px rgba(124,58,237,0.5)'
              : '0 0 12px rgba(167,139,250,0.45)',
          }}
          transition={{ type: 'spring', stiffness: 260, damping: 22 }}
          style={{ borderRadius: '50%', border: '1.5px solid' }}
        />
      </motion.div>

      {/* ── Center dot — dark purple, highly visible on light bg ── */}
      <motion.div
        className="fixed top-0 left-0 pointer-events-none z-[9999]"
        style={{ x: dotX, y: dotY, translateX: '-50%', translateY: '-50%' }}
      >
        <motion.div
          animate={{
            width:           isPointer ? 7 : 5,
            height:          isPointer ? 7 : 5,
            backgroundColor: isPointer ? '#7C3AED' : '#6D28D9',
            boxShadow:       isPointer
              ? '0 0 10px rgba(124,58,237,0.8)'
              : '0 0 8px rgba(109,40,217,0.6)',
          }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          style={{ borderRadius: '50%' }}
        />
      </motion.div>
    </>
  );
};

export default CustomCursor;
