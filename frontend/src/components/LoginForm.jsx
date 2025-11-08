import React, { useEffect, useState } from 'react';
import { authService, captchaService, protectionService } from '../services/api';

const LoginForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [showCaptcha, setShowCaptcha] = useState(false);
  const [captchaImage, setCaptchaImage] = useState(null);
  const [captchaValue, setCaptchaValue] = useState('');
  const [captchaLoading, setCaptchaLoading] = useState(false);
  const [checkingProtection, setCheckingProtection] = useState(false);
  const [protectionRequired, setProtectionRequired] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (name === 'username') {
      // Réinitialiser l'état CAPTCHA lorsqu'on change d'utilisateur
      setShowCaptcha(false);
      setCaptchaImage(null);
      setCaptchaValue('');
      setProtectionRequired(false);
    }
  };

  const loadCaptcha = async () => {
    try {
      setCaptchaLoading(true);
      const data = await captchaService.generate();
      setCaptchaImage(data.image_data);
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('Erreur chargement CAPTCHA', e);
    } finally {
      setCaptchaLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const payload = showCaptcha || captchaValue
        ? { ...formData, captcha: captchaValue }
        : { ...formData };
      const result = await authService.login(payload);
      setMessage({ 
        type: 'success', 
        text: `Connexion réussie! Bienvenue ${result.username}` 
      });
      // Reset CAPTCHA on success
      setShowCaptcha(false);
      setCaptchaImage(null);
      setCaptchaValue('');
      if (onSuccess) onSuccess(result);
    } catch (error) {
      const errorData = error.response?.data;
      
      // Gérer le cas du compte verrouillé
      if (errorData?.locked) {
        setMessage({ 
          type: 'error', 
          text: `🔒 ${errorData.message || 'Compte verrouillé'}`,
          locked: true,
          remaining_minutes: errorData.remaining_minutes
        });
      } else if (errorData?.captcha_required) {
        setMessage({ 
          type: 'error', 
          text: errorData.error || 'Veuillez résoudre le CAPTCHA'
        });
        if (!showCaptcha) setShowCaptcha(true);
        if (!captchaImage) await loadCaptcha();
      } else {
        // Afficher le message d'erreur avec tentatives restantes
        const errorText = errorData?.error || 'Erreur de connexion';
        const attemptsInfo = errorData?.attempts_left !== null && errorData?.attempts_left !== undefined
          ? ` (${errorData.attempts_left} tentative(s) restante(s))`
          : '';
        
        setMessage({ 
          type: 'error', 
          text: errorText + attemptsInfo
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const checkProtection = async () => {
    const username = formData.username?.trim();
    if (!username) return;
    try {
      setCheckingProtection(true);
      const status = await protectionService.getProtectionStatus(username);
      setProtectionRequired(!!status?.protection_enabled);
    } catch (e) {
      // Ignorer si l'utilisateur n'existe pas (le backend renvoie 404)
      setProtectionRequired(false);
    } finally {
      setCheckingProtection(false);
    }
  };

  // Afficher le CAPTCHA uniquement quand username + password sont remplis et que la protection est active
  useEffect(() => {
    const hasBothFields = Boolean(formData.username?.trim()) && Boolean(formData.password);
    if (protectionRequired && hasBothFields) {
      setShowCaptcha(true);
      if (!captchaImage && !captchaLoading) {
        // Charger une seule fois dès que nécessaire
        loadCaptcha();
      }
    } else {
      // Cacher sinon
      if (showCaptcha) setShowCaptcha(false);
      if (captchaImage) setCaptchaImage(null);
      if (captchaValue) setCaptchaValue('');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [protectionRequired, formData.username, formData.password]);

  return (
    <div className="card">
      <h2 style={{ marginBottom: '20px', color: '#111827' }}>🔑 Connexion</h2>
      
      {message && (
        <div className={`alert alert-${message.type === 'success' ? 'success' : 'error'}`}>
          {message.text}
          {message.locked && message.remaining_minutes > 0 && (
            <div style={{ marginTop: '10px', fontSize: '0.9em' }}>
              ⏱️ Temps restant: {message.remaining_minutes} minute(s)
            </div>
          )}
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
            onBlur={checkProtection}
            placeholder="Votre nom d'utilisateur"
            required
          />
          {checkingProtection && (
            <div style={{ marginTop: 6, fontSize: '0.85em', color: '#6b7280' }}>
              Vérification de la protection…
            </div>
          )}
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

        {/* CAPTCHA section (affiché à la demande ou si requis) */}
        {showCaptcha && (
          <div className="form-group">
            <label>CAPTCHA</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              {captchaImage ? (
                <img 
                  src={captchaImage} 
                  alt="CAPTCHA" 
                  style={{ height: 48, border: '1px solid #e5e7eb', borderRadius: 4 }}
                />
              ) : (
                <div style={{ height: 48, width: 160, background: '#f3f4f6', borderRadius: 4 }} />
              )}
              <button
                type="button"
                className="btn btn-secondary"
                onClick={loadCaptcha}
                disabled={captchaLoading}
              >
                {captchaLoading ? 'Chargement…' : (captchaImage ? 'Rafraîchir' : 'Afficher')}
              </button>
            </div>
            <input
              type="text"
              name="captcha"
              className="form-control"
              value={captchaValue}
              onChange={(e) => setCaptchaValue(e.target.value)}
              placeholder="Entrez le code CAPTCHA"
              autoComplete="off"
            />
          </div>
        )}

        <button
          type="submit"
          className="btn btn-primary"
          disabled={
            loading || (
              protectionRequired && Boolean(formData.username?.trim()) && Boolean(formData.password) && !captchaValue
            )
          }
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Connexion...
            </>
          ) : (
            'Se connecter'
          )}
        </button>

        {/* Le bouton manuel pour afficher le CAPTCHA est retiré pour respecter la règle: afficher seulement quand les deux champs sont remplis */}
      </form>
    </div>
  );
};

export default LoginForm;

