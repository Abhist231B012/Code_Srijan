import React from 'react';
import { Link, useLocation } from 'react-router-dom';

export const Navbar: React.FC = () => {
  return (
    <nav style={{
      padding: '24px 48px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 100,
      background: 'transparent'
    }}>
      <Link to="/" style={{ 
        textDecoration: 'none', 
        display: 'flex', 
        alignItems: 'center', 
        gap: '12px' 
      }}>
        <div style={{
          width: '32px', height: '32px',
          border: '2px solid white',
          borderRadius: '4px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          position: 'relative'
        }}>
          <div style={{ width: '16px', height: '16px', border: '2px solid white', borderTop: 'none', borderRight: 'none' }}></div>
        </div>
        <h1 style={{ 
          fontSize: '24px', 
          margin: 0, 
          color: 'white', 
          fontFamily: 'var(--font-heading)',
          letterSpacing: '1px'
        }}>CRED</h1>
      </Link>
      
      <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
        <span style={{ color: 'rgba(255,255,255,0.7)', fontSize: '12px', letterSpacing: '2px', textTransform: 'uppercase' }}>
          CRED INDUSIND BANK RUPAY CREDIT CARD
        </span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', cursor: 'pointer' }}>
          <div style={{ width: '24px', height: '1px', background: 'white' }}></div>
          <div style={{ width: '24px', height: '1px', background: 'white' }}></div>
          <div style={{ width: '24px', height: '1px', background: 'white' }}></div>
        </div>
      </div>
    </nav>
  );
};
