import React from 'react';
import { motion } from 'framer-motion';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, TrendingUp, Zap } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      exit={{ opacity: 0, y: -20 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}
    >
      <div style={{ textAlign: 'center', padding: '60px 0 40px' }}>
        <motion.h1 
          variants={itemVariants}
          style={{ fontSize: '48px', marginBottom: '16px' }}
        >
          AI-Powered <span className="text-gradient">Financial Inclusion</span>
        </motion.h1>
        <motion.p 
          variants={itemVariants}
          className="text-secondary" 
          style={{ fontSize: '20px', maxWidth: '600px', margin: '0 auto' }}
        >
          Score applicants instantly using traditional bureau history or alternative data footprint.
        </motion.p>
        <motion.div variants={itemVariants} style={{ marginTop: '40px' }}>
          <Button size="lg" onClick={() => navigate('/assess')}>
            Start Assessment
          </Button>
        </motion.div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        <motion.div variants={itemVariants}>
          <Card style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ color: 'var(--accent-neon)' }}><ShieldCheck size={32} /></div>
            <h3>Banked Path</h3>
            <p className="text-secondary">Traditional scoring using CIBIL data and LightGBM models for those with existing credit history.</p>
          </Card>
        </motion.div>
        
        <motion.div variants={itemVariants}>
          <Card style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ color: 'var(--accent-blue)' }}><TrendingUp size={32} /></div>
            <h3>Unbanked ML Path</h3>
            <p className="text-secondary">Income-based assessment for individuals with verified income but lacking formal bureau history.</p>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ color: '#fbbf24' }}><Zap size={32} /></div>
            <h3>Alternative Data</h3>
            <p className="text-secondary">Rule-based scoring utilizing UPI transactions and utility bill payments for the truly unbanked.</p>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
};
