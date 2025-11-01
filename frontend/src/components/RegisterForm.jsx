import React, { useState } from 'react';
import { authService } from '../services/api';

const RegisterForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    algorithm: 'cesar',
    key_param: '3',
    email: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [encryptionSteps, setEncryptionSteps] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Auto-update key_param based on algorithm
    if (name === 'algorithm') {
      const defaultKeys = {
        'cesar': '3',
        'affine': '5,8',
        'plaiyfair': 'KEYWORD',
        'hill': 'SECRET'  // Changé pour accepter texte
      };
      setFormData(prev => ({
        ...prev,
        key_param: defaultKeys[value] || ''
      }));
      setEncryptionSteps(null);  // Reset steps when algorithm changes
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const result = await authService.register(formData);
      setMessage({ type: 'success', text: `Utilisateur créé avec succès! Mot de passe chiffré: ${result.encrypted_password}` });
      
      // Afficher les étapes de chiffrement si disponibles
      if (result.encryption_steps) {
        setEncryptionSteps(result.encryption_steps);
      }
      
      if (onSuccess) onSuccess(result);
      
      // Reset form
      setTimeout(() => {
        setFormData({
          username: '',
          password: '',
          algorithm: 'cesar',
          key_param: '3',
          email: ''
        });
        setMessage(null);
      }, 3000);
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.error || 'Erreur lors de l\'inscription'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 style={{ marginBottom: '20px', color: '#111827' }}>📝 Inscription Utilisateur</h2>
      
      {message && (
        <div className={`alert alert-${message.type === 'success' ? 'success' : 'error'}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Nom d'utilisateur</label>
          <input
            type="text"
            id="username"
            name="username"
            className="form-control"
            value={formData.username}
            onChange={handleChange}
            placeholder="test_user ou demo_user"
            required
          />
          <small style={{ color: '#6b7280', fontSize: '12px' }}>
            Préfixes autorisés: test_*, demo_*, tmp_*
          </small>
        </div>

        <div className="form-group">
          <label htmlFor="password">Mot de passe (clair)</label>
          <input
            type="text"
            id="password"
            name="password"
            className="form-control"
            value={formData.password}
            onChange={handleChange}
            placeholder="Mot de passe à chiffrer"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="algorithm">Algorithme de chiffrement</label>
          <select
            id="algorithm"
            name="algorithm"
            className="form-select"
            value={formData.algorithm}
            onChange={handleChange}
          >
            <option value="cesar">César (décalage)</option>
            <option value="affine">Affine (Y = aX + b mod 26)</option>
            <option value="plaiyfair">Playfair (matrice 5×5)</option>
            <option value="hill">Hill (matrice 2×2)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="key_param">Paramètre de clé</label>
          <input
            type="text"
            id="key_param"
            name="key_param"
            className="form-control"
            value={formData.key_param}
            onChange={handleChange}
            placeholder="Exemple: 3 pour César, 5,8 pour Affine"
            required
          />
          <small style={{ color: '#6b7280', fontSize: '12px' }}>
            César: nombre (ex: 3), Affine: a,b (ex: 5,8), Playfair: mot-clé (ex: KEYWORD), Hill: mot-clé (ex: SECRET)
          </small>
        </div>

        <div className="form-group">
          <label htmlFor="email">Email (optionnel)</label>
          <input
            type="email"
            id="email"
            name="email"
            className="form-control"
            value={formData.email}
            onChange={handleChange}
            placeholder="user@example.com"
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner"></span>
              Création en cours...
            </>
          ) : (
            'Créer l\'utilisateur'
          )}
        </button>
      </form>

      {/* Affichage des étapes de chiffrement */}
      {encryptionSteps && (
        <div style={{
          marginTop: '24px',
          padding: '20px',
          backgroundColor: '#f0f9ff',
          borderRadius: '8px',
          border: '2px solid #3b82f6'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '16px', color: '#1e40af', fontSize: '18px' }}>
            🔐 Étapes de Chiffrement
          </h3>
          
          <div style={{ 
            backgroundColor: 'white', 
            padding: '16px', 
            borderRadius: '6px',
            marginBottom: '12px'
          }}>
            <strong>Texte original:</strong> {encryptionSteps.original_text}
          </div>

          {encryptionSteps.steps && encryptionSteps.steps.length > 0 && (
            <div style={{ marginBottom: '12px' }}>
              <strong style={{ display: 'block', marginBottom: '8px' }}>📋 Détails du chiffrement:</strong>
              {encryptionSteps.steps.map((step, index) => (
                <div key={index} style={{
                  backgroundColor: 'white',
                  padding: '12px',
                  borderRadius: '4px',
                  marginBottom: '8px',
                  borderLeft: '4px solid #3b82f6'
                }}>
                  <div style={{ fontSize: '14px', color: '#1e40af', fontWeight: 'bold', marginBottom: '4px' }}>
                    Étape {index + 1}
                  </div>
                  <div style={{ fontSize: '13px', color: '#374151' }}>
                    {step}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div style={{ 
            backgroundColor: '#dcfce7', 
            padding: '16px', 
            borderRadius: '6px',
            border: '2px solid #16a34a'
          }}>
            <strong style={{ color: '#166534' }}>✅ Texte chiffré final:</strong>
            <div style={{ 
              fontSize: '18px', 
              fontWeight: 'bold', 
              color: '#166534',
              fontFamily: 'monospace',
              marginTop: '8px'
            }}>
              {encryptionSteps.encrypted_text}
            </div>
          </div>

          {encryptionSteps.key_info && (
            <div style={{
              marginTop: '12px',
              padding: '12px',
              backgroundColor: '#fef3c7',
              borderRadius: '6px',
              fontSize: '13px',
              color: '#92400e'
            }}>
              <strong>🔑 Informations sur la clé:</strong>
              <pre style={{ 
                marginTop: '8px', 
                marginBottom: 0,
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace',
                fontSize: '12px'
              }}>
                {JSON.stringify(encryptionSteps.key_info, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RegisterForm;
