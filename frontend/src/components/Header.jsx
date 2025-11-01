import React from 'react';

const Header = () => {
  return (
    <header style={{
      backgroundColor: '#4f46e5',
      color: 'white',
      padding: '20px 0',
      marginBottom: '30px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <div className="container">
        <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>
          🔐 Crypto Lab - Cryptographie Classique
        </h1>
        <p style={{ fontSize: '14px', opacity: 0.9 }}>
          TP SSAD - Système de Sécurité et d'Aide à la Décision | USTHB
        </p>
      </div>
    </header>
  );
};

export default Header;
