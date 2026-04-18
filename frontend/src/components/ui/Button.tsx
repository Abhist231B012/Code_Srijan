import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

interface ButtonProps extends Omit<HTMLMotionProps<"button">, "ref"> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  fullWidth = false,
  className = '',
  ...props 
}) => {
  const baseStyles = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 'var(--radius-sm)',
    fontWeight: '600',
    fontFamily: 'var(--font-heading)',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    border: 'none',
    outline: 'none',
    width: fullWidth ? '100%' : 'auto',
  };

  const variants = {
    primary: {
      background: 'var(--accent-neon)',
      color: '#000',
      boxShadow: '0 0 15px var(--accent-neon-glow)',
    },
    secondary: {
      background: 'var(--bg-card-hover)',
      color: 'var(--text-primary)',
      border: '1px solid var(--border-color)',
    },
    outline: {
      background: 'transparent',
      color: 'var(--accent-neon)',
      border: '1px solid var(--accent-neon)',
    },
    danger: {
      background: 'var(--danger)',
      color: '#fff',
      boxShadow: '0 0 15px var(--danger-glow)',
    }
  };

  const sizes = {
    sm: { padding: '8px 16px', fontSize: '14px' },
    md: { padding: '12px 24px', fontSize: '16px' },
    lg: { padding: '16px 32px', fontSize: '18px' },
  };

  const style = {
    ...baseStyles,
    ...variants[variant],
    ...sizes[size],
  };

  return (
    <motion.button
      style={style as any}
      whileHover={{ scale: 1.02, filter: 'brightness(1.1)' }}
      whileTap={{ scale: 0.98 }}
      className={className}
      {...props}
    >
      {children}
    </motion.button>
  );
};
