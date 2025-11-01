import React, { useState } from 'react';
import { authService } from '../services/api';

const LoginForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const result = await authService.login(formData);
      setMessage({ 
        type: 'success', 
        text: `Connexion réussie! Bienvenue ${result.username}` 
      });
      if (onSuccess) onSuccess(result);
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.error || 'Erreur de connexion'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 style={{ marginBottom: '20px', color: '#111827' }}>🔑 Connexion</h2>
      
      {message && (
        <div className={`alert alert-${message.type === 'success' ? 'success' : 'error'}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="login-username">Nom d'utilisateur</label>
          <input
            type="text"
            id="login-username"
            name="username"
            className="form-control"
            value={formData.username}
            onChange={handleChange}
            placeholder="Votre nom d'utilisateur"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="login-password">Mot de passe</label>
          <input
            type="password"
            id="login-password"
            name="password"
            className="form-control"
            value={formData.password}
            onChange={handleChange}
            placeholder="Votre mot de passe"
            required
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner"></span>
              Connexion...
            </>
          ) : (
            'Se connecter'
          )}
        </button>
      </form>
    </div>
  );
};

export default LoginForm;
