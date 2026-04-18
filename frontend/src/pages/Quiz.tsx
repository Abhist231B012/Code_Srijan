import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const questions = [
  {
    id: 'loanAmount',
    title: 'How much loan are you looking for?',
    type: 'number',
    placeholder: 'e.g. 50000',
    prefix: '₹'
  },
  {
    id: 'monthlyIncome',
    title: 'What is your monthly income?',
    type: 'number',
    placeholder: 'e.g. 25000',
    prefix: '₹'
  },
  {
    id: 'age',
    title: 'How old are you?',
    type: 'number',
    placeholder: 'e.g. 28'
  },
  {
    id: 'hasLoans',
    title: 'Do you currently have any active loans or credit cards?',
    type: 'boolean',
    options: [
      { label: 'Yes, I do', value: true },
      { label: 'No, I don\'t', value: false }
    ]
  },
  {
    id: 'employmentType',
    title: 'What best describes your employment?',
    type: 'select',
    options: [
      { label: 'Salaried', value: 'Salaried' },
      { label: 'Self Employed', value: 'Self_Employed' },
      { label: 'Daily Wage', value: 'Daily_Wage' },
      { label: 'Unemployed', value: 'Unemployed' }
    ]
  },
  {
    id: 'stableIncome',
    title: 'How stable or predictable is your income?',
    type: 'select',
    options: [
      { label: 'Very Stable (Fixed Salary)', value: 'very_stable' },
      { label: 'Somewhat Stable', value: 'somewhat_stable' },
      { label: 'Fluctuates Monthly', value: 'fluctuates' },
      { label: 'Unpredictable', value: 'unpredictable' }
    ]
  },
  {
    id: 'upiUsage',
    title: 'How often do you use UPI or digital payments per month?',
    type: 'number',
    placeholder: 'e.g. 15'
  }
];

export const Quiz: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleNext = async (value: any) => {
    const currentQ = questions[currentStep];
    const newAnswers = { ...answers, [currentQ.id]: value };
    setAnswers(newAnswers);

    if (currentStep < questions.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      await submitQuiz(newAnswers);
    }
  };

  const submitQuiz = async (finalAnswers: Record<string, any>) => {
    setIsLoading(true);
    try {
      const payload = {
        LOAN_AMOUNT_RS: Number(finalAnswers.loanAmount),
        ANNUAL_INCOME_RS: Number(finalAnswers.monthlyIncome) * 12,
        AGE_YEARS: Number(finalAnswers.age),
        TOTAL_PREV_APPLICATIONS: finalAnswers.hasLoans ? 1 : 0,
        EMPLOYMENT_TYPE: finalAnswers.employmentType,
        upi_transactions_per_month: Number(finalAnswers.upiUsage),
        include_shap: false
      };

      const response = await apiService.predictGuest(payload);
      navigate('/results', { state: { result: response } });
    } catch (error: any) {
      console.error("Failed to submit quiz", error);
      alert(`Error: ${error.message || "Failed to submit. Ensure backend is running on http://127.0.0.1:8000"}`);
      setIsLoading(false);
    }
  };

  const currentQ = questions[currentStep];

  return (
    <div style={{
      minHeight: '100vh',
      background: '#000',
      color: '#fff',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '20px'
    }}>
      <div style={{ width: '100%', maxWidth: '600px', position: 'relative' }}>
        
        {/* Progress Bar */}
        <div style={{ width: '100%', height: '2px', background: 'rgba(255,255,255,0.1)', marginBottom: '60px' }}>
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${((currentStep) / questions.length) * 100}%` }}
            style={{ height: '100%', background: 'white' }}
          />
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.4 }}
          >
            <h2 style={{ 
              fontSize: '2rem', 
              fontFamily: 'var(--font-heading)',
              fontWeight: 600,
              marginBottom: '40px',
              lineHeight: 1.3
            }}>
              {currentQ.title}
            </h2>

            {currentQ.type === 'number' && (
              <NumberInput 
                question={currentQ} 
                onNext={handleNext} 
                isLoading={isLoading}
              />
            )}

            {(currentQ.type === 'boolean' || currentQ.type === 'select') && (
              <OptionsInput 
                question={currentQ} 
                onNext={handleNext} 
                isLoading={isLoading}
              />
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

const NumberInput = ({ question, onNext, isLoading }: any) => {
  const [val, setVal] = useState('');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        borderBottom: '2px solid rgba(255,255,255,0.2)',
        paddingBottom: '10px'
      }}>
        {question.prefix && <span style={{ fontSize: '2rem', marginRight: '10px', color: 'rgba(255,255,255,0.5)' }}>{question.prefix}</span>}
        <input
          type="number"
          autoFocus
          value={val}
          onChange={(e) => setVal(e.target.value)}
          placeholder={question.placeholder}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && val) onNext(val);
          }}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'white',
            fontSize: '2rem',
            outline: 'none',
            width: '100%',
            fontFamily: 'var(--font-body)'
          }}
        />
      </div>
      <button
        onClick={() => val && onNext(val)}
        disabled={!val || isLoading}
        style={{
          alignSelf: 'flex-start',
          padding: '12px 32px',
          background: 'white',
          color: 'black',
          border: 'none',
          borderRadius: '100px',
          fontSize: '16px',
          fontWeight: 600,
          cursor: val && !isLoading ? 'pointer' : 'not-allowed',
          opacity: val && !isLoading ? 1 : 0.5,
          marginTop: '20px'
        }}
      >
        {isLoading ? 'Submitting...' : 'Next'}
      </button>
    </div>
  );
};

const OptionsInput = ({ question, onNext, isLoading }: any) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {question.options.map((opt: any, idx: number) => (
        <motion.button
          key={idx}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => !isLoading && onNext(opt.value)}
          disabled={isLoading}
          style={{
            padding: '20px 24px',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
            color: 'white',
            fontSize: '1.2rem',
            textAlign: 'left',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            fontFamily: 'var(--font-body)',
            transition: 'background 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
        >
          {opt.label}
        </motion.button>
      ))}
    </div>
  );
};
