import React, { useState } from 'react';
import Header from './components/Header';
import RegisterForm from './components/RegisterForm';
import LoginForm from './components/LoginForm';
import AttackPanel from './components/AttackPanel';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('register');

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f3f4f6' }}>
      <Header />
      
      <div className="container">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'register' ? 'active' : ''}`}
            onClick={() => setActiveTab('register')}
          >
            📝 Inscription
          </button>
          <button
            className={`tab ${activeTab === 'login' ? 'active' : ''}`}
            onClick={() => setActiveTab('login')}
          >
            🔑 Connexion
          </button>
          <button
            className={`tab ${activeTab === 'attacks' ? 'active' : ''}`}
            onClick={() => setActiveTab('attacks')}
          >
            ⚔️ Attaques
          </button>
          <button
            className={`tab ${activeTab === 'about' ? 'active' : ''}`}
            onClick={() => setActiveTab('about')}
          >
            ℹ️ À propos
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'register' && (
            <div className="grid grid-2">
              <RegisterForm onSuccess={(result) => {
                console.log('Utilisateur créé:', result);
              }} />
              
              <div className="card">
                <h3 style={{ marginBottom: '16px', color: '#111827' }}>
                  📚 Guide d'utilisation
                </h3>
                <div style={{ color: '#6b7280', lineHeight: '1.6' }}>
                  <p style={{ marginBottom: '12px' }}>
                    <strong>1. Inscription:</strong> Créez un utilisateur avec un algorithme de chiffrement.
                  </p>
                  <p style={{ marginBottom: '12px' }}>
                    <strong>2. Connexion:</strong> Testez le déchiffrement en vous connectant.
                  </p>
                  <p style={{ marginBottom: '12px' }}>
                    <strong>3. Attaques:</strong> Lancez des attaques pour craquer les mots de passe.
                  </p>
                  
                  <div style={{ 
                    backgroundColor: '#fef3c7', 
                    padding: '12px', 
                    borderRadius: '6px', 
                    marginTop: '16px',
                    border: '1px solid #f59e0b'
                  }}>
                    <strong style={{ color: '#92400e' }}>⚠️ Important:</strong>
                    <ul style={{ marginTop: '8px', marginLeft: '20px', color: '#92400e' }}>
                      <li>Utilisez des préfixes: test_*, demo_*, tmp_*</li>
                      <li>Les mots de passe sont chiffrés automatiquement</li>
                      <li>Chaque algorithme a ses propres paramètres</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'login' && (
            <div className="grid grid-2">
              <LoginForm onSuccess={(result) => {
                console.log('Connexion réussie:', result);
              }} />
              
              <div className="card">
                <h3 style={{ marginBottom: '16px', color: '#111827' }}>
                  🔐 Algorithmes supportés
                </h3>
                <div style={{ color: '#6b7280', lineHeight: '1.6' }}>
                  <div style={{ marginBottom: '16px' }}>
                    <strong style={{ color: '#111827' }}>César:</strong>
                    <p style={{ fontSize: '14px', marginTop: '4px' }}>
                      Décalage simple de l'alphabet. Clé: nombre (ex: 3)
                    </p>
                  </div>
                  
                  <div style={{ marginBottom: '16px' }}>
                    <strong style={{ color: '#111827' }}>Affine:</strong>
                    <p style={{ fontSize: '14px', marginTop: '4px' }}>
                      Y = (aX + b) mod 26. Clé: a,b (ex: 5,8)
                    </p>
                  </div>
                  
                  <div style={{ marginBottom: '16px' }}>
                    <strong style={{ color: '#111827' }}>Playfair:</strong>
                    <p style={{ fontSize: '14px', marginTop: '4px' }}>
                      Matrice 5×5 avec mot-clé. Clé: mot (ex: KEYWORD)
                    </p>
                  </div>
                  
                  <div style={{ marginBottom: '16px' }}>
                    <strong style={{ color: '#111827' }}>Hill:</strong>
                    <p style={{ fontSize: '14px', marginTop: '4px' }}>
                      Multiplication matricielle. Clé: matrice JSON
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'attacks' && (
            <div>
              <AttackPanel />
              
              <div className="card" style={{ marginTop: '20px' }}>
                <h3 style={{ marginBottom: '16px', color: '#111827' }}>
                  📊 Types d'attaques
                </h3>
                <div className="grid grid-2">
                  <div>
                    <h4 style={{ color: '#4f46e5', marginBottom: '8px' }}>
                      📚 Attaque Dictionnaire
                    </h4>
                    <p style={{ color: '#6b7280', fontSize: '14px', lineHeight: '1.6' }}>
                      Teste les mots de passe depuis un dictionnaire pré-établi.
                      Rapide mais limitée aux mots courants.
                    </p>
                    <div className="badge badge-info" style={{ marginTop: '8px' }}>
                      Recommandée en premier
                    </div>
                  </div>
                  
                  <div>
                    <h4 style={{ color: '#10b981', marginBottom: '8px' }}>
                      💪 Force Brute
                    </h4>
                    <p style={{ color: '#6b7280', fontSize: '14px', lineHeight: '1.6' }}>
                      Teste toutes les combinaisons possibles.
                      Lente mais exhaustive.
                    </p>
                    <div className="badge badge-warning" style={{ marginTop: '8px' }}>
                      Peut être très lent
                    </div>
                  </div>
                  
                  <div>
                    <h4 style={{ color: '#f59e0b', marginBottom: '8px' }}>
                      🔄 Attaque Combinée
                    </h4>
                    <p style={{ color: '#6b7280', fontSize: '14px', lineHeight: '1.6' }}>
                      Dictionnaire d'abord, puis force brute si échec.
                      Optimal pour la plupart des cas.
                    </p>
                    <div className="badge badge-success" style={{ marginTop: '8px' }}>
                      Meilleur compromis
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'about' && (
            <div className="card">
              <h2 style={{ marginBottom: '20px', color: '#111827' }}>
                ℹ️ À propos du projet
              </h2>
              
              <div style={{ color: '#6b7280', lineHeight: '1.8' }}>
                <h3 style={{ color: '#111827', marginBottom: '12px' }}>
                  TP SSAD - Cryptographie Classique
                </h3>
                <p style={{ marginBottom: '16px' }}>
                  Projet académique de réalisation d'une boîte d'outils de cryptographie 
                  classique avec système d'attaques.
                </p>
                
                <h4 style={{ color: '#111827', marginBottom: '8px' }}>
                  🎯 Objectifs
                </h4>
                <ul style={{ marginLeft: '20px', marginBottom: '16px' }}>
                  <li>Implémenter 4 algorithmes de chiffrement classique</li>
                  <li>Créer un système d'attaques (force brute et dictionnaire)</li>
                  <li>Développer une interface moderne avec React</li>
                  <li>Documenter mathématiquement les algorithmes</li>
                </ul>
                
                <h4 style={{ color: '#111827', marginBottom: '8px' }}>
                  🛠️ Technologies
                </h4>
                <div style={{ 
                  display: 'flex', 
                  gap: '8px', 
                  flexWrap: 'wrap',
                  marginBottom: '16px'
                }}>
                  <span className="badge badge-info">React 18</span>
                  <span className="badge badge-info">Django 5.2</span>
                  <span className="badge badge-info">Vite</span>
                  <span className="badge badge-info">Axios</span>
                  <span className="badge badge-info">NumPy</span>
                </div>
                
                <h4 style={{ color: '#111827', marginBottom: '8px' }}>
                  📚 Documentation
                </h4>
                <p style={{ marginBottom: '8px' }}>
                  Consultez le fichier <code style={{ 
                    backgroundColor: '#f3f4f6', 
                    padding: '2px 6px', 
                    borderRadius: '4px',
                    fontFamily: 'monospace'
                  }}>docs/algorithms.md</code> pour la documentation complète des algorithmes.
                </p>
                
                <div style={{ 
                  backgroundColor: '#dbeafe', 
                  padding: '16px', 
                  borderRadius: '8px', 
                  marginTop: '20px',
                  border: '1px solid #3b82f6'
                }}>
                  <strong style={{ color: '#1e40af' }}>🎓 USTHB - Université des Sciences et de la Technologie Houari Boumediene</strong>
                  <p style={{ color: '#1e40af', fontSize: '14px', marginTop: '8px' }}>
                    Système de Sécurité et d'Aide à la Décision
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
