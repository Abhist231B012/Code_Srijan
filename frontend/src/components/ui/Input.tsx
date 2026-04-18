import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', style, ...props }, ref) => {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px', width: '100%' }}>
        <label style={{ 
          fontSize: '14px', 
          fontWeight: '500', 
          color: 'var(--text-secondary)',
          fontFamily: 'var(--font-heading)'
        }}>
          {label}
        </label>
        <div style={{ position: 'relative' }}>
          <input
            ref={ref}
            className={`custom-input ${className}`}
            style={{
              width: '100%',
              background: 'var(--bg-dark)',
              border: `1px solid ${error ? 'var(--danger)' : 'var(--border-color)'}`,
              borderRadius: 'var(--radius-sm)',
              padding: '12px 16px',
              color: 'var(--text-primary)',
              fontSize: '16px',
              fontFamily: 'var(--font-body)',
              outline: 'none',
              transition: 'all 0.2s ease',
              ...style
            }}
            {...props}
          />
          <style>{`
            .custom-input:focus {
              border-color: var(--accent-neon);
              box-shadow: 0 0 0 1px var(--accent-neon);
            }
          `}</style>
        </div>
        {error && (
          <span style={{ color: 'var(--danger)', fontSize: '12px', marginTop: '4px' }}>
            {error}
          </span>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
