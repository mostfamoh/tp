import React, { useState } from 'react';
import Header from './components/Header';
import RegisterForm from './components/RegisterForm';
import LoginForm from './components/LoginForm';
import AttackPanel from './components/AttackPanel';
import ProtectionPanel from './components/ProtectionPanel';
import SteganographyPanel from './components/SteganographyPanel';
import MessagingPanel from './components/MessagingPanel';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('register');
  const [loggedInUser, setLoggedInUser] = useState(null);

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
            className={`tab ${activeTab === 'protection' ? 'active' : ''}`}
            onClick={() => setActiveTab('protection')}
          >
            🛡️ Protection
          </button>
          <button
            className={`tab ${activeTab === 'stego' ? 'active' : ''}`}
            onClick={() => setActiveTab('stego')}
          >
            🔐 Stéganographie
          </button>
          <button
            className={`tab ${activeTab === 'messaging' ? 'active' : ''}`}
            onClick={() => setActiveTab('messaging')}
          >
            💬 Messagerie
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
                    <strong>3. Protection:</strong> Activez la protection contre les attaques répétées.
                  </p>
                  <p style={{ marginBottom: '12px' }}>
                    <strong>4. Attaques:</strong> Lancez des attaques pour craquer les mots de passe.
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
                setLoggedInUser(result.username);
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

          {activeTab === 'protection' && (
            <div className="grid grid-2">
              <ProtectionPanel username={loggedInUser} />
              
              <div className="card">
                <h3 style={{ marginBottom: '16px', color: '#111827' }}>
                  🔒 Qu'est-ce que la protection ?
                </h3>
                <div style={{ color: '#6b7280', lineHeight: '1.6' }}>
                  <p style={{ marginBottom: '12px' }}>
                    La protection limite les tentatives de connexion pour ralentir les attaques.
                  </p>
                  
                  <div style={{ marginBottom: '16px' }}>
                    <strong style={{ color: '#111827' }}>Comment ça fonctionne :</strong>
                    <ul style={{ marginTop: '8px', marginLeft: '20px' }}>
                      <li>Maximum de <strong>3 tentatives</strong> échouées</li>
                      <li>Verrouillage automatique pour <strong>30 minutes</strong></li>
                      <li>Compteur réinitialisé après connexion réussie</li>
                    </ul>
                  </div>
                  
                  <div style={{ 
                    backgroundColor: '#dcfce7', 
                    padding: '12px', 
                    borderRadius: '6px', 
                    marginTop: '16px',
                    border: '1px solid #10b981'
                  }}>
                    <strong style={{ color: '#065f46' }}>✅ Avantages:</strong>
                    <ul style={{ marginTop: '8px', marginLeft: '20px', color: '#065f46' }}>
                      <li>Protection contre les attaques par force brute</li>
                      <li>Ralentissement considérable des attaquants</li>
                      <li>Notification des tentatives suspectes</li>
                    </ul>
                  </div>
                  
                  <div style={{ 
                    backgroundColor: '#fee2e2', 
                    padding: '12px', 
                    borderRadius: '6px', 
                    marginTop: '16px',
                    border: '1px solid #dc2626'
                  }}>
                    <strong style={{ color: '#991b1b' }}>⚠️ Impact:</strong>
                    <ul style={{ marginTop: '8px', marginLeft: '20px', color: '#991b1b' }}>
                      <li>Attaque dictionnaire: de 5s à plusieurs heures</li>
                      <li>Force brute: peut devenir impossible en temps réaliste</li>
                      <li>Protection efficace contre les scripts automatisés</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'stego' && (
            <div className="grid grid-2">
              <SteganographyPanel />
              
              <div className="card">
                <h3 style={{ marginBottom: '16px', color: '#111827' }}>
                  🔐 Qu'est-ce que la stéganographie ?
                </h3>
                <div style={{ color: '#6b7280', lineHeight: '1.6' }}>
                  <p style={{ marginBottom: '12px' }}>
                    La stéganographie est l'art de cacher des messages secrets dans des supports apparemment anodins (texte, images, audio...).
                  </p>
                  
                  <div style={{ marginBottom: '16px' }}>
                    <strong style={{ color: '#111827' }}>Méthodes disponibles :</strong>
                    <ul style={{ marginTop: '8px', marginLeft: '20px' }}>
                      <li><strong>Case-Based</strong> : Casse des lettres (MAJ/min) ✅ Recommandé</li>
                      <li><strong>WhiteSpace</strong> : Espaces et tabulations invisibles</li>
                      <li><strong>Zero-Width</strong> : Caractères Unicode invisibles</li>
                      <li><strong>LSB Image</strong> : Modification des bits de pixels</li>
                    </ul>
                  </div>
                  
                  <div style={{ 
                    backgroundColor: '#dbeafe', 
                    padding: '12px', 
                    borderRadius: '6px', 
                    marginTop: '16px',
                    border: '1px solid #3b82f6'
                  }}>
                    <strong style={{ color: '#1e40af' }}>🆚 Cryptographie vs Stéganographie:</strong>
                    <ul style={{ marginTop: '8px', marginLeft: '20px', color: '#1e40af' }}>
                      <li><strong>Cryptographie</strong> : Rend le message illisible (chiffrement)</li>
                      <li><strong>Stéganographie</strong> : Cache l'existence du message</li>
                      <li><strong>Combiné</strong> : Chiffrer puis cacher = double protection !</li>
                    </ul>
                  </div>
                  
                  <div style={{ 
                    backgroundColor: '#fef3c7', 
                    padding: '12px', 
                    borderRadius: '6px', 
                    marginTop: '16px',
                    border: '1px solid #f59e0b'
                  }}>
                    <strong style={{ color: '#92400e' }}>💡 Capacité :</strong>
                    <ul style={{ marginTop: '8px', marginLeft: '20px', color: '#92400e' }}>
                      <li><strong>Texte</strong> : 1 caractère caché = 8 lettres nécessaires (case-based)</li>
                      <li><strong>Image 400×300</strong> : Jusqu'à 45,000 caractères !</li>
                      <li><strong>Recommandation</strong> : Utiliser max 50% de la capacité</li>
                    </ul>
                  </div>

                  <div style={{ 
                    backgroundColor: '#dcfce7', 
                    padding: '12px', 
                    borderRadius: '6px', 
                    marginTop: '16px',
                    border: '1px solid #10b981'
                  }}>
                    <strong style={{ color: '#065f46' }}>🎓 Cas d'usage :</strong>
                    <ul style={{ marginTop: '8px', marginLeft: '20px', color: '#065f46' }}>
                      <li>Communication secrète (espionnage)</li>
                      <li>Watermarking numérique (DRM)</li>
                      <li>Preuve d'authenticité</li>
                      <li>Stockage caché de données sensibles</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'messaging' && (
            <div className="grid grid-2">
              <MessagingPanel />
              
              <div className="card">
                <h3 style={{ marginBottom: '16px', color: '#111827' }}>
                  💬 Communication Sécurisée & Attaque MITM
                </h3>
                <div style={{ color: '#6b7280', lineHeight: '1.6' }}>
                  <p style={{ marginBottom: '12px' }}>
                    Démonstration interactive de communication chiffrée entre Alice et Bob, 
                    avec simulation d'attaque Man-in-the-Middle (MITM).
                  </p>
                  
                  <div style={{ marginBottom: '16px' }}>
                    <strong style={{ color: '#111827' }}>Mode Normal :</strong>
                    <ul style={{ marginTop: '8px', marginLeft: '20px' }}>
                      <li>Alice chiffre un message avec une clé</li>
                      <li>Bob déchiffre avec la même clé</li>
                      <li>Communication sécurisée ✅</li>
                    </ul>
                  </div>
                  
                  <div style={{ marginBottom: '16px' }}>
                    <strong style={{ color: '#111827' }}>Attaque MITM :</strong>
                    <ul style={{ marginTop: '8px', marginLeft: '20px' }}>
                      <li><strong>Étape 1</strong> : Alice envoie un message chiffré</li>
                      <li><strong>Étape 2</strong> : Eve intercepte et déchiffre</li>
                      <li><strong>Étape 3</strong> : Eve modifie et re-chiffre</li>
                      <li><strong>Étape 4</strong> : Bob reçoit un message altéré ⚠️</li>
                    </ul>
                  </div>
                  
                  <div style={{ 
                    backgroundColor: '#fee2e2', 
                    padding: '12px', 
                    borderRadius: '6px', 
                    marginTop: '16px',
                    border: '1px solid #ef4444'
                  }}>
                    <strong style={{ color: '#991b1b' }}>🚨 Vulnérabilité MITM :</strong>
                    <ul style={{ marginTop: '8px', marginLeft: '20px', color: '#991b1b' }}>
                      <li>L'attaquant est positionné entre émetteur et récepteur</li>
                      <li>Peut lire, modifier ou remplacer les messages</li>
                      <li>Les victimes ne détectent pas l'interception</li>
                      <li><strong>Protection</strong> : Authentification, signatures numériques</li>
                    </ul>
                  </div>
                  
                  <div style={{ 
                    backgroundColor: '#dbeafe', 
                    padding: '12px', 
                    borderRadius: '6px', 
                    marginTop: '16px',
                    border: '1px solid #3b82f6'
                  }}>
                    <strong style={{ color: '#1e40af' }}>🎓 Valeur Pédagogique :</strong>
                    <ul style={{ marginTop: '8px', marginLeft: '20px', color: '#1e40af' }}>
                      <li>Comprendre les étapes de chiffrement/déchiffrement</li>
                      <li>Visualiser le processus cryptographique</li>
                      <li>Identifier les failles de sécurité</li>
                      <li>Importance de l'authentification mutuelle</li>
                    </ul>
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
