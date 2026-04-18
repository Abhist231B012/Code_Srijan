import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

export const Assess: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Using a simplified state for demonstration of the Banked path
  const [formData, setFormData] = useState({
    ANNUAL_INCOME_RS: 600000,
    LOAN_AMOUNT_RS: 250000,
    MONTHLY_EMI_RS: 10000,
    AGE_YEARS: 35,
    EMPLOYMENT_YEARS: 6.0,
    CIBIL_SCORE_SOURCE_2: 0.70,
    HAS_BUREAU_NPA_HISTORY: 0,
    CITY_TIER: 2
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: Number(value) }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.predict(formData);
      // Navigate to results page with data
      navigate('/results', { state: { result, inputData: formData } });
    } catch (err: any) {
      setError(err.message || 'Failed to score applicant.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      style={{ maxWidth: '800px', margin: '0 auto' }}
    >
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '32px', marginBottom: '8px' }}>Applicant Assessment</h2>
        <p className="text-secondary">Enter the loan applicant's details below.</p>
      </div>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <Input 
            label="Annual Income (₹)" 
            name="ANNUAL_INCOME_RS" 
            type="number" 
            value={formData.ANNUAL_INCOME_RS} 
            onChange={handleChange} 
          />
          <Input 
            label="Loan Amount (₹)" 
            name="LOAN_AMOUNT_RS" 
            type="number" 
            value={formData.LOAN_AMOUNT_RS} 
            onChange={handleChange} 
          />
          <Input 
            label="Monthly EMI (₹)" 
            name="MONTHLY_EMI_RS" 
            type="number" 
            value={formData.MONTHLY_EMI_RS} 
            onChange={handleChange} 
          />
          <Input 
            label="Age (Years)" 
            name="AGE_YEARS" 
            type="number" 
            value={formData.AGE_YEARS} 
            onChange={handleChange} 
          />
          <Input 
            label="Employment (Years)" 
            name="EMPLOYMENT_YEARS" 
            type="number" 
            step="0.1" 
            value={formData.EMPLOYMENT_YEARS} 
            onChange={handleChange} 
          />
          <Input 
            label="CIBIL Source 2 Score" 
            name="CIBIL_SCORE_SOURCE_2" 
            type="number" 
            step="0.01" 
            value={formData.CIBIL_SCORE_SOURCE_2} 
            onChange={handleChange} 
          />
          
          {error && (
            <div style={{ gridColumn: '1 / -1', color: 'var(--danger)', background: 'var(--danger-glow)', padding: '12px', borderRadius: '8px' }}>
              {error}
            </div>
          )}

          <div style={{ gridColumn: '1 / -1', marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
            <Button type="submit" size="lg" disabled={loading}>
              {loading ? 'Processing...' : 'Run Assessment'}
            </Button>
          </div>
        </form>
      </Card>
    </motion.div>
  );
};
