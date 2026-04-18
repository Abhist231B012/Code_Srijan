import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Lock, ArrowRight, User, Activity } from 'lucide-react';

export const Register: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      navigate('/');
    }, 1500);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 'calc(100vh - 160px)',
        padding: '20px 0'
      }}
    >
      <div className="glass" style={{
        padding: '40px',
        borderRadius: 'var(--radius-lg)',
        width: '100%',
        maxWidth: '440px',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Glow effect */}
        <div style={{
          position: 'absolute',
          bottom: '-50px',
          left: '-50px',
          width: '150px',
          height: '150px',
          background: 'var(--accent-blue)',
          filter: 'blur(80px)',
          opacity: 0.2,
          borderRadius: '50%',
          zIndex: 0
        }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '24px' }}>
            <div style={{
              width: '56px', height: '56px',
              borderRadius: '16px',
              background: 'var(--accent-neon)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 0 30px var(--accent-neon-glow)'
            }}>
              <Activity color="#000" size={32} />
            </div>
          </div>

          <h2 style={{ textAlign: 'center', fontSize: '28px', marginBottom: '8px' }}>
            Join Elevate
          </h2>
          <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '32px' }}>
            Create an account to start your financial journey.
          </p>

          <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            <div style={{ position: 'relative' }}>
              <User color="var(--text-secondary)" size={20} style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)' }} />
              <input 
                type="text"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '16px 16px 16px 48px',
                  background: 'rgba(0,0,0,0.2)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'white',
                  fontSize: '16px',
                  fontFamily: 'var(--font-body)',
                  outline: 'none',
                  transition: 'all 0.2s ease'
                }}
                onFocus={(e) => e.target.style.borderColor = 'var(--accent-neon)'}
                onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
              />
            </div>

            <div style={{ position: 'relative' }}>
              <Mail color="var(--text-secondary)" size={20} style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)' }} />
              <input 
                type="email"
                placeholder="Email Address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '16px 16px 16px 48px',
                  background: 'rgba(0,0,0,0.2)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'white',
                  fontSize: '16px',
                  fontFamily: 'var(--font-body)',
                  outline: 'none',
                  transition: 'all 0.2s ease'
                }}
                onFocus={(e) => e.target.style.borderColor = 'var(--accent-neon)'}
                onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
              />
            </div>

            <div style={{ position: 'relative' }}>
              <Lock color="var(--text-secondary)" size={20} style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)' }} />
              <input 
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '16px 16px 16px 48px',
                  background: 'rgba(0,0,0,0.2)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'white',
                  fontSize: '16px',
                  fontFamily: 'var(--font-body)',
                  outline: 'none',
                  transition: 'all 0.2s ease'
                }}
                onFocus={(e) => e.target.style.borderColor = 'var(--accent-neon)'}
                onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
              />
            </div>

            <button 
              type="submit"
              disabled={loading}
              style={{
                background: 'var(--accent-neon)',
                color: '#000',
                border: 'none',
                padding: '16px',
                borderRadius: 'var(--radius-sm)',
                fontSize: '16px',
                fontWeight: '600',
                fontFamily: 'var(--font-body)',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                marginTop: '16px',
                boxShadow: '0 4px 20px var(--accent-neon-glow)',
                transition: 'all 0.2s ease',
                opacity: loading ? 0.8 : 1
              }}
            >
              {loading ? 'Creating Account...' : 'Sign Up'}
              {!loading && <ArrowRight size={20} />}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: '32px', color: 'var(--text-secondary)', fontSize: '14px' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--accent-neon)', textDecoration: 'none', fontWeight: '600' }}>
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
