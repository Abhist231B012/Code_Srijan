import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

export const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div style={{
      minHeight: '100vh',
      background: '#000000',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      position: 'relative',
      overflow: 'hidden',
      color: 'white'
    }}>
      {/* Background pseudo-element for subtle gradient */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        background: 'radial-gradient(circle at center, rgba(30,30,30,1) 0%, rgba(0,0,0,1) 70%)',
        zIndex: 0
      }}></div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        style={{ 
          zIndex: 1, 
          textAlign: 'center', 
          maxWidth: '800px',
          padding: '0 20px'
        }}
      >
        <h1 style={{
          fontFamily: 'var(--font-heading)',
          fontSize: 'clamp(3rem, 8vw, 6rem)',
          fontWeight: 800,
          lineHeight: 1.1,
          letterSpacing: '-0.04em',
          marginBottom: '2rem'
        }}>
          crafted for the<br/>creditworthy
        </h1>
        
        <p style={{
          fontFamily: 'var(--font-body)',
          fontSize: 'clamp(1rem, 2vw, 1.25rem)',
          color: 'rgba(255, 255, 255, 0.7)',
          lineHeight: 1.6,
          maxWidth: '600px',
          margin: '0 auto 3rem auto'
        }}>
          CRED is a members-only club that enables the<br/>trustworthy to make financial progress
        </p>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate('/quiz')}
          style={{
            padding: '16px 40px',
            background: 'white',
            color: 'black',
            border: 'none',
            borderRadius: '100px',
            fontSize: '18px',
            fontWeight: 600,
            fontFamily: 'var(--font-body)',
            cursor: 'pointer',
            boxShadow: '0 4px 14px rgba(255,255,255,0.2)'
          }}
        >
          Check Eligibility
        </motion.button>
      </motion.div>
    </div>
  );
};
