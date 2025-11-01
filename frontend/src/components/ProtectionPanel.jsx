import React, { useState, useEffect } from 'react';
import { protectionService } from '../services/api';

const ProtectionPanel = ({ username }) => {
  const [protectionStatus, setProtectionStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const loadProtectionStatus = async () => {
    if (!username) return;
    
    try {
      const status = await protectionService.getProtectionStatus(username);
      setProtectionStatus(status);
    } catch (error) {
      console.error('Erreur lors du chargement du statut:', error);
    }
  };

  useEffect(() => {
    loadProtectionStatus();
    // Actualiser le statut toutes les 30 secondes
    const interval = setInterval(loadProtectionStatus, 30000);
    return () => clearInterval(interval);
  }, [username]);

  const handleToggleProtection = async () => {
    setLoading(true);
    setMessage(null);

    try {
      const result = await protectionService.toggleProtection(
        username, 
        !protectionStatus.protection_enabled
      );
      
      setMessage({ 
        type: 'success', 
        text: result.message 
      });
      
      // Recharger le statut
      await loadProtectionStatus();
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.error || 'Erreur lors du changement de protection' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUnlock = async () => {
    setLoading(true);
    setMessage(null);

    try {
      const result = await protectionService.unlockAccount(username);
      
      setMessage({ 
        type: 'success', 
        text: result.message 
      });
      
      // Recharger le statut
      await loadProtectionStatus();
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.error || 'Erreur lors du déverrouillage' 
      });
    } finally {
      setLoading(false);
    }
  };

  if (!username) {
    return (
      <div className="card">
        <h2 style={{ marginBottom: '20px', color: '#111827' }}>🛡️ Protection du Compte</h2>
        <p style={{ color: '#6B7280' }}>Veuillez vous connecter pour gérer la protection de votre compte.</p>
      </div>
    );
  }

  if (!protectionStatus) {
    return (
      <div className="card">
        <h2 style={{ marginBottom: '20px', color: '#111827' }}>🛡️ Protection du Compte</h2>
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <span className="spinner"></span>
          <p>Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 style={{ marginBottom: '20px', color: '#111827' }}>🛡️ Protection du Compte</h2>
      
      {message && (
        <div className={`alert alert-${message.type === 'success' ? 'success' : 'error'}`}>
          {message.text}
        </div>
      )}

      <div style={{ marginBottom: '20px' }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          padding: '15px',
          backgroundColor: protectionStatus.protection_enabled ? '#DEF7EC' : '#FEF3C7',
          borderRadius: '8px',
          marginBottom: '15px'
        }}>
          <div>
            <strong style={{ fontSize: '1.1em' }}>
              État: {protectionStatus.protection_enabled ? '🟢 Activée' : '🟡 Désactivée'}
            </strong>
            <p style={{ margin: '5px 0 0 0', fontSize: '0.9em', color: '#4B5563' }}>
              {protectionStatus.protection_enabled 
                ? 'Compte protégé contre les tentatives de connexion répétées'
                : 'Aucune protection active - risque d\'attaque par force brute'}
            </p>
          </div>
          <button
            onClick={handleToggleProtection}
            disabled={loading}
            className={`btn ${protectionStatus.protection_enabled ? 'btn-secondary' : 'btn-primary'}`}
            style={{ minWidth: '120px' }}
          >
            {loading ? (
              <span className="spinner"></span>
            ) : (
              protectionStatus.protection_enabled ? 'Désactiver' : 'Activer'
            )}
          </button>
        </div>

        {protectionStatus.protection_enabled && (
          <div style={{ 
            padding: '15px',
            backgroundColor: '#F3F4F6',
            borderRadius: '8px',
            marginBottom: '15px'
          }}>
            <h3 style={{ fontSize: '1em', marginBottom: '10px' }}>📊 Statistiques</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div>
                <span style={{ color: '#6B7280', fontSize: '0.9em' }}>Tentatives échouées:</span>
                <strong style={{ display: 'block', fontSize: '1.2em', color: '#1F2937' }}>
                  {protectionStatus.failed_attempts} / 3
                </strong>
              </div>
              <div>
                <span style={{ color: '#6B7280', fontSize: '0.9em' }}>Statut du compte:</span>
                <strong style={{ 
                  display: 'block', 
                  fontSize: '1.2em', 
                  color: protectionStatus.is_locked ? '#DC2626' : '#059669' 
                }}>
                  {protectionStatus.is_locked ? '🔒 Verrouillé' : '✅ Actif'}
                </strong>
              </div>
            </div>

            {protectionStatus.is_locked && (
              <div style={{ 
                marginTop: '15px',
                padding: '10px',
                backgroundColor: '#FEE2E2',
                borderLeft: '4px solid #DC2626',
                borderRadius: '4px'
              }}>
                <strong style={{ color: '#991B1B' }}>
                  ⚠️ Compte verrouillé pour {protectionStatus.remaining_minutes} minute(s)
                </strong>
                <p style={{ margin: '5px 0 10px 0', fontSize: '0.9em', color: '#7F1D1D' }}>
                  Trop de tentatives de connexion échouées détectées.
                </p>
                <button
                  onClick={handleUnlock}
                  disabled={loading}
                  className="btn btn-primary"
                  style={{ fontSize: '0.9em' }}
                >
                  {loading ? <span className="spinner"></span> : 'Déverrouiller maintenant'}
                </button>
              </div>
            )}

            {protectionStatus.last_failed_attempt && !protectionStatus.is_locked && (
              <div style={{ marginTop: '10px', fontSize: '0.85em', color: '#6B7280' }}>
                Dernière tentative échouée: {new Date(protectionStatus.last_failed_attempt).toLocaleString('fr-FR')}
              </div>
            )}
          </div>
        )}

        <div style={{ 
          padding: '15px',
          backgroundColor: '#EFF6FF',
          borderRadius: '8px',
          borderLeft: '4px solid #3B82F6'
        }}>
          <h3 style={{ fontSize: '1em', marginBottom: '10px', color: '#1E40AF' }}>ℹ️ Comment ça fonctionne ?</h3>
          <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.9em', color: '#1F2937' }}>
            <li>Après <strong>3 tentatives</strong> de mot de passe incorrectes</li>
            <li>Le compte est verrouillé pendant <strong>30 minutes</strong></li>
            <li>Les attaques par force brute sont ainsi ralenties considérablement</li>
            <li>Vous pouvez déverrouiller manuellement votre compte à tout moment</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ProtectionPanel;
