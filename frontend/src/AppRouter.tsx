import React, { useState } from 'react';
import App from './App';
import ApiTest from './components/ApiTest';

const AppRouter: React.FC = () => {
  const [currentView, setCurrentView] = useState<'main' | 'api-test'>('main');

  const handleSwitchView = (view: 'main' | 'api-test') => {
    setCurrentView(view);
  };

  return (
    <div>
      {/* Navigation Bar */}
      <nav style={{ 
        padding: '10px 20px', 
        backgroundColor: '#f8f9fa', 
        borderBottom: '1px solid #dee2e6',
        display: 'flex',
        gap: '10px'
      }}>
        <button
          onClick={() => handleSwitchView('main')}
          style={{
            padding: '8px 16px',
            backgroundColor: currentView === 'main' ? '#007bff' : '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Main App
        </button>
        <button
          onClick={() => handleSwitchView('api-test')}
          style={{
            padding: '8px 16px',
            backgroundColor: currentView === 'api-test' ? '#007bff' : '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          API Test
        </button>
      </nav>

      {/* Current View */}
      {currentView === 'main' && <App />}
      {currentView === 'api-test' && <ApiTest />}
    </div>
  );
};

export default AppRouter;