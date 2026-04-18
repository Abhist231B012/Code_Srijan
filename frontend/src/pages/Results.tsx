import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useLocation, useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { ScoreRing } from '../components/ui/ScoreRing';
import { apiService } from '../services/api';

export const Results: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { result, inputData } = location.state || {};
  
  const [explanation, setExplanation] = useState<any>(null);
  const [loadingExp, setLoadingExp] = useState(false);

  useEffect(() => {
    if (!result) {
      navigate('/quiz');
      return;
    }
    
    const fetchExplanation = async () => {
      setLoadingExp(true);
      try {
        const exp = await apiService.explain(inputData);
        setExplanation(exp);
      } catch (err) {
        console.error("Failed to fetch explanation", err);
      } finally {
        setLoadingExp(false);
      }
    };
    
    fetchExplanation();
  }, [result, inputData, navigate]);

  if (!result) return null;

  const isApproved = result.decision === 'APPROVE';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '32px' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Assessment Results</h2>
        <div style={{
          padding: '8px 16px',
          borderRadius: '20px',
          background: isApproved ? 'rgba(57, 255, 20, 0.1)' : 'rgba(255, 51, 102, 0.1)',
          color: isApproved ? 'var(--accent-neon)' : 'var(--danger)',
          fontWeight: 'bold',
          border: `1px solid ${isApproved ? 'var(--accent-neon)' : 'var(--danger)'}`
        }}>
          {result.decision}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '32px' }}>
        {/* Left Column - Score */}
        <Card style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 20px' }}>
          <ScoreRing score={result.credit_score} />
          <div style={{ marginTop: '32px', width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span className="text-secondary">Scoring Path</span>
              <span style={{ fontWeight: '600' }}>{result.scoring_path}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span className="text-secondary">Default Probability</span>
              <span style={{ fontWeight: '600' }}>{result.default_probability.toFixed(1)}%</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span className="text-secondary">Band</span>
              <span style={{ fontWeight: '600', color: isApproved ? 'var(--accent-neon)' : 'var(--danger)' }}>
                {result.score_band}
              </span>
            </div>
          </div>
        </Card>

        {/* Right Column - Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <Card>
            <h3 style={{ marginBottom: '16px' }}>Reasoning</h3>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {result.reasoning.map((r: string, i: number) => (
                <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                  <div style={{ 
                    marginTop: '4px', width: '8px', height: '8px', 
                    borderRadius: '50%', background: 'var(--accent-blue)' 
                  }} />
                  <span style={{ lineHeight: '1.5' }}>{r}</span>
                </li>
              ))}
            </ul>
          </Card>

          <Card>
            <h3 style={{ marginBottom: '16px' }}>Key Factors (SHAP)</h3>
            {loadingExp ? (
              <p className="text-secondary">Analyzing impact factors...</p>
            ) : explanation ? (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                <div>
                  <h4 style={{ color: 'var(--accent-neon)', marginBottom: '12px' }}>Strengths</h4>
                  {Object.entries(explanation.strength_factors || {}).map(([key, val]: any) => (
                    <div key={key} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', marginBottom: '8px' }}>
                      <span className="text-secondary">{key.replace(/_/g, ' ')}</span>
                    </div>
                  ))}
                </div>
                <div>
                  <h4 style={{ color: 'var(--danger)', marginBottom: '12px' }}>Risks</h4>
                  {Object.entries(explanation.risk_factors || {}).map(([key, val]: any) => (
                    <div key={key} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', marginBottom: '8px' }}>
                      <span className="text-secondary">{key.replace(/_/g, ' ')}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-secondary">Explanation not available.</p>
            )}
          </Card>
          
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button variant="outline" onClick={() => navigate('/quiz')}>
              New Assessment
            </Button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
