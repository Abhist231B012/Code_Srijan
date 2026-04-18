import React from 'react';
import { motion } from 'framer-motion';

interface ScoreRingProps {
  score: number; // 300 to 900
  size?: number;
}

export const ScoreRing: React.FC<ScoreRingProps> = ({ score, size = 200 }) => {
  const strokeWidth = size * 0.08;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  
  // Calculate percentage (300 to 900 -> 0 to 1)
  const normalizedScore = Math.max(300, Math.min(900, score));
  const percentage = (normalizedScore - 300) / 600;
  const strokeDashoffset = circumference - percentage * circumference;

  // Color based on score
  let color = 'var(--accent-neon)'; // Good
  if (score < 550) color = 'var(--danger)'; // Poor
  else if (score < 700) color = '#fbbf24'; // Average

  return (
    <div style={{ position: 'relative', width: size, height: size, margin: '0 auto' }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        {/* Background Ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="var(--bg-card-hover)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        {/* Progress Ring */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          style={{ filter: `drop-shadow(0 0 8px ${color}80)` }}
        />
      </svg>
      {/* Center Text */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <motion.span 
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          style={{ 
            fontFamily: 'var(--font-heading)', 
            fontSize: size * 0.25, 
            fontWeight: '800',
            color: 'var(--text-primary)'
          }}
        >
          {score}
        </motion.span>
        <span style={{ 
          fontFamily: 'var(--font-body)', 
          fontSize: size * 0.08, 
          color: 'var(--text-secondary)',
          textTransform: 'uppercase',
          letterSpacing: '1px'
        }}>
          Credit Score
        </span>
      </div>
    </div>
  );
};
