import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

interface CardProps extends Omit<HTMLMotionProps<"div">, "ref"> {
  glass?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, glass = true, className = '', style, ...props }) => {
  const baseStyle = {
    background: glass ? 'var(--glass-bg)' : 'var(--bg-card)',
    backdropFilter: glass ? 'blur(12px)' : 'none',
    WebkitBackdropFilter: glass ? 'blur(12px)' : 'none',
    border: '1px solid var(--border-color)',
    borderRadius: 'var(--radius-md)',
    padding: '24px',
    color: 'var(--text-primary)',
    overflow: 'hidden',
    position: 'relative' as const,
  };

  return (
    <motion.div
      style={{ ...baseStyle, ...style }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className={className}
      {...props}
    >
      {/* Subtle top highlight for 3D effect */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, height: '1px',
        background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)'
      }} />
      {children}
    </motion.div>
  );
};
