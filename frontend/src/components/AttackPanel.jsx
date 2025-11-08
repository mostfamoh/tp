import React, { useState } from 'react';
import { attackService } from '../services/api';

const AttackPanel = () => {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [attackType, setAttackType] = useState('bruteforce');
  const [dictionaryType, setDictionaryType] = useState('digits6');
  const [plainTarget, setPlainTarget] = useState('');

  const handleAttack = async (type) => {
    if (!username.trim()) {
      alert('Veuillez entrer un nom d\'utilisateur');
      return;
    }

    setLoading(true);
    setResult(null);
    setAttackType(type);

    try {
      let data;
      if (type === 'bruteforce') {
        data = await attackService.bruteforce(username);
      } else if (type === 'dictionary') {
        data = await attackService.dictionary(username, 120, 0, dictionaryType);
      } else if (type === 'combined') {
        data = await attackService.combined(username);
      }
      setResult(data);
    } catch (error) {
      setResult({
        error: error.response?.data?.error || error.message || 'Erreur lors de l\'attaque'
      });
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    if (seconds < 1) return `${(seconds * 1000).toFixed(2)} ms`;
    return `${seconds.toFixed(4)} secondes`;
  };

  const getConfidenceBadge = (confidence) => {
    switch(confidence) {
      case 'high': return { emoji: '🟢', text: 'HAUTE', color: '#10b981', bg: '#d1fae5' };
      case 'medium': return { emoji: '🟡', text: 'MOYENNE', color: '#f59e0b', bg: '#fef3c7' };
      case 'low': return { emoji: '🔴', text: 'FAIBLE', color: '#ef4444', bg: '#fee2e2' };
      default: return { emoji: '⚪', text: 'INCONNUE', color: '#6b7280', bg: '#f3f4f6' };
    }
  };

  const formatKey = (key) => {
    if (!key) return 'N/A';
    if (typeof key === 'object') {
      if (key.shift !== undefined) return `Shift: ${key.shift}`;
      if (key.a !== undefined && key.b !== undefined) return `a=${key.a}, b=${key.b}`;
      if (key.keyword) return `Mot-clé: "${key.keyword}"`;
      if (key.matrix) return `Matrice: ${JSON.stringify(key.matrix)}`;
    }
    return JSON.stringify(key);
  };

  return (
    <div className="card">
      <h2 style={{ marginBottom: '20px', color: '#111827' }}>⚔️ Système d'Attaques</h2>

      <div className="form-group">
        <label htmlFor="attack-username">Utilisateur cible</label>
        <input
          type="text"
          id="attack-username"
          className="form-control"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Nom d'utilisateur à attaquer"
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="dictionary-type">Type de dictionnaire (pour attaque dictionnaire)</label>
        <select
          id="dictionary-type"
          className="form-control"
          value={dictionaryType}
          onChange={(e) => setDictionaryType(e.target.value)}
          disabled={loading}
          style={{ padding: '10px' }}
        >
          <option value="012">🔢 Petit - {'{0,1,2}'}³ (27 entrées) - RAPIDE</option>
          <option value="test">🧪 Test - Mots de passe communs (50 entrées)</option>
          <option value="digits3">🔢 Moyen - {'{0-9}'}³ (1,000 entrées)</option>
          <option value="digits6">🔢 Grand - {'{0-9}'}⁶ (1,000,000 entrées) ⚠️ LENT</option>
          <option value="default">📚 Par défaut (27 entrées)</option>
        </select>
        <small style={{ color: '#6b7280', display: 'block', marginTop: '4px' }}>
          {dictionaryType === 'digits6' && '⚠️ Le dictionnaire {0-9}⁶ peut prendre 5-60 secondes'}
          {dictionaryType === '012' && '✅ Idéal pour les mots de passe du type 012, 111, 222, etc.'}
          {dictionaryType === 'digits3' && '✅ Pour les mots de passe à 3 chiffres (000-999)'}
          {dictionaryType === 'test' && 'ℹ️ Mots de passe communs pour tests rapides'}
        </small>
      </div>

  <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
        <button
          onClick={() => handleAttack('dictionary')}
          className="btn btn-primary"
          disabled={loading}
        >
          {loading && attackType === 'dictionary' ? (
            <>
              <span className="spinner"></span>
              Attaque en cours...
            </>
          ) : (
            '📚 Attaque Dictionnaire'
          )}
        </button>

        <button
          onClick={() => handleAttack('bruteforce')}
          className="btn btn-secondary"
          disabled={loading}
        >
          {loading && attackType === 'bruteforce' ? (
            <>
              <span className="spinner"></span>
              Attaque en cours...
            </>
          ) : (
            '💪 Force Brute'
          )}
        </button>

        <button
          onClick={() => handleAttack('combined')}
          className="btn btn-outline"
          disabled={loading}
        >
          {loading && attackType === 'combined' ? (
            <>
              <span className="spinner"></span>
              Attaque en cours...
            </>
          ) : (
            '🔄 Combinée'
          )}
        </button>
      </div>

      {/* Plaintext brute-force quick tester */}
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="plain-target">Tester bruteforce (chaîne cible directe)</label>
        <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
          <input
            id="plain-target"
            type="text"
            className="form-control"
            value={plainTarget}
            onChange={(e) => setPlainTarget(e.target.value)}
            placeholder="Entrez '012' ou '123456'"
            disabled={loading}
          />
          <button
            onClick={async () => {
              if (!plainTarget.trim()) return alert('Entrez une chaîne cible');
              setLoading(true);
              setResult(null);
              try {
                const data = await attackService.plainBruteforce(plainTarget);
                setResult(data);
              } catch (err) {
                setResult({ error: err.message || 'Erreur' });
              } finally {
                setLoading(false);
              }
            }}
            className="btn btn-accent"
            disabled={loading}
          >
            {loading ? 'En cours...' : '🔎 Brute (Plain)'}
          </button>
        </div>
      </div>

      {result && (
        <div style={{ marginTop: '24px' }}>
          {result.error ? (
            <div style={{ 
              padding: '16px', 
              backgroundColor: '#fee2e2', 
              border: '2px solid #ef4444',
              borderRadius: '8px',
              color: '#991b1b'
            }}>
              <h4 style={{ marginTop: 0, marginBottom: '8px' }}>❌ Erreur</h4>
              <p style={{ margin: 0 }}>{result.error}</p>
            </div>
          ) : (
            <>
              {/* En-tête du rapport */}
              <div style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                padding: '20px',
                borderRadius: '12px 12px 0 0',
                marginBottom: '0'
              }}>
                <h2 style={{ margin: 0, fontSize: '24px' }}>
                  📊 Rapport d'Attaque Complet
                </h2>
                <p style={{ margin: '8px 0 0 0', opacity: 0.9 }}>
                  Analyse détaillée de l'attaque {attackType}
                </p>
              </div>

              {/* Section 1: Informations sur la cible */}
              <div style={{ 
                backgroundColor: '#f9fafb', 
                padding: '20px', 
                borderLeft: '4px solid #667eea',
                marginBottom: '16px'
              }}>
                <h3 style={{ marginTop: 0, marginBottom: '16px', color: '#111827', fontSize: '18px' }}>
                  🎯 1. Informations sur la Cible
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div style={{ 
                    backgroundColor: 'white', 
                    padding: '12px', 
                    borderRadius: '6px',
                    border: '1px solid #e5e7eb'
                  }}>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
                      Utilisateur Attaqué
                    </div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827' }}>
                      👤 {result.target_username || username}
                    </div>
                  </div>
                  <div style={{ 
                    backgroundColor: 'white', 
                    padding: '12px', 
                    borderRadius: '6px',
                    border: '1px solid #e5e7eb'
                  }}>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
                      Algorithme de Chiffrement
                    </div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827' }}>
                      🔐 {(result.algorithm || 'N/A').toUpperCase()}
                    </div>
                  </div>
                  <div style={{ 
                    backgroundColor: 'white', 
                    padding: '12px', 
                    borderRadius: '6px',
                    border: '1px solid #e5e7eb'
                  }}>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
                      Mode d'Attaque
                    </div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827' }}>
                      ⚔️ {(result.mode || attackType).toUpperCase()}
                    </div>
                  </div>
                  <div style={{ 
                    backgroundColor: 'white', 
                    padding: '12px', 
                    borderRadius: '6px',
                    border: '1px solid #e5e7eb'
                  }}>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
                      Texte Chiffré
                    </div>
                    <div style={{ 
                      fontSize: '14px', 
                      fontWeight: 'bold', 
                      color: '#111827',
                      fontFamily: 'monospace'
                    }}>
                      🔒 {result.encrypted_target || 'Non fourni'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Section 2: Statistiques de Performance */}
              <div style={{ 
                backgroundColor: '#eff6ff', 
                padding: '20px', 
                borderLeft: '4px solid #3b82f6',
                marginBottom: '16px'
              }}>
                <h3 style={{ marginTop: 0, marginBottom: '16px', color: '#111827', fontSize: '18px' }}>
                  ⚡ 2. Statistiques de Performance
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px' }}>
                  <div style={{ 
                    backgroundColor: 'white', 
                    padding: '16px', 
                    borderRadius: '8px',
                    textAlign: 'center',
                    border: '2px solid #3b82f6'
                  }}>
                    <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#3b82f6' }}>
                      {result.attempts?.toLocaleString() || 0}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                      🔄 Tentatives
                    </div>
                  </div>
                  <div style={{ 
                    backgroundColor: 'white', 
                    padding: '16px', 
                    borderRadius: '8px',
                    textAlign: 'center',
                    border: '2px solid #10b981'
                  }}>
                    <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#10b981' }}>
                      {formatTime(result.time_sec || result.time_elapsed || 0)}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                      ⏱️ Temps Total
                    </div>
                  </div>
                  <div style={{ 
                    backgroundColor: 'white', 
                    padding: '16px', 
                    borderRadius: '8px',
                    textAlign: 'center',
                    border: '2px solid #f59e0b'
                  }}>
                    <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#f59e0b' }}>
                      {result.matches_count || result.matches?.length || 0}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                      🎯 Candidats
                    </div>
                  </div>
                  <div style={{ 
                    backgroundColor: 'white', 
                    padding: '16px', 
                    borderRadius: '8px',
                    textAlign: 'center',
                    border: '2px solid #8b5cf6'
                  }}>
                    <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#8b5cf6' }}>
                      {result.attempts && result.time_sec ? 
                        Math.round(result.attempts / result.time_sec).toLocaleString() : 'N/A'}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                      ⚡ Clés/sec
                    </div>
                  </div>
                </div>

                {/* Explication des statistiques */}
                <div style={{ 
                  backgroundColor: 'white', 
                  padding: '12px', 
                  borderRadius: '6px',
                  fontSize: '13px',
                  color: '#4b5563'
                }}>
                  <strong>📖 Explication:</strong>
                  <ul style={{ marginTop: '8px', marginBottom: 0, paddingLeft: '20px' }}>
                    <li><strong>Tentatives:</strong> Nombre de clés de déchiffrement testées</li>
                    <li><strong>Temps:</strong> Durée totale de l'attaque (plus c'est rapide, mieux c'est)</li>
                    <li><strong>Candidats:</strong> Nombre de mots de passe possibles identifiés</li>
                    <li><strong>Clés/sec:</strong> Vitesse de l'attaque (performances du système)</li>
                  </ul>
                </div>

                {/* Informations du dictionnaire si disponibles */}
                {result.dictionary_info && (
                  <div style={{ 
                    backgroundColor: 'white', 
                    padding: '12px', 
                    borderRadius: '6px',
                    fontSize: '13px',
                    color: '#4b5563',
                    marginTop: '12px',
                    border: '2px solid #3b82f6'
                  }}>
                    <strong>📚 Dictionnaire utilisé:</strong>
                    <ul style={{ marginTop: '8px', marginBottom: 0, paddingLeft: '20px' }}>
                      <li><strong>Type:</strong> {result.dictionary_info.type}</li>
                      <li><strong>Taille:</strong> {result.dictionary_info.size?.toLocaleString()} entrées</li>
                      <li><strong>Chemin:</strong> <code style={{ fontSize: '11px', backgroundColor: '#f3f4f6', padding: '2px 4px', borderRadius: '3px' }}>{result.dictionary_info.path}</code></li>
                    </ul>
                  </div>
                )}
              </div>

              {/* Section 3: Statut de l'attaque */}
              <div style={{ 
                backgroundColor: result.timeout_reached || result.limit_reached ? '#fef3c7' : '#d1fae5', 
                padding: '20px', 
                borderLeft: `4px solid ${result.timeout_reached || result.limit_reached ? '#f59e0b' : '#10b981'}`,
                marginBottom: '16px'
              }}>
                <h3 style={{ marginTop: 0, marginBottom: '16px', color: '#111827', fontSize: '18px' }}>
                  📋 3. Statut de l'Attaque
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div style={{ 
                    backgroundColor: 'white', 
                    padding: '12px', 
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                  }}>
                    <div style={{ fontSize: '32px' }}>
                      {result.timeout_reached ? '⏱️' : '✅'}
                    </div>
                    <div>
                      <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#111827' }}>
                        Timeout
                      </div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>
                        {result.timeout_reached ? 
                          '⚠️ Temps maximum atteint' : 
                          '✅ Terminé dans les temps'}
                      </div>
                    </div>
                  </div>
                  <div style={{ 
                    backgroundColor: 'white', 
                    padding: '12px', 
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                  }}>
                    <div style={{ fontSize: '32px' }}>
                      {result.limit_reached ? '🛑' : '✅'}
                    </div>
                    <div>
                      <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#111827' }}>
                        Limite de Tentatives
                      </div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>
                        {result.limit_reached ? 
                          '⚠️ Limite atteinte' : 
                          '✅ Toutes les clés testées'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Avertissement si timeout ou limite */}
                {(result.timeout_reached || result.limit_reached) && (
                  <div style={{ 
                    marginTop: '12px', 
                    padding: '12px', 
                    backgroundColor: '#fef3c7',
                    border: '1px solid #f59e0b',
                    borderRadius: '6px',
                    fontSize: '13px',
                    color: '#92400e'
                  }}>
                    <strong>⚠️ Important:</strong> L'attaque s'est arrêtée avant de tester toutes les clés possibles. 
                    Le vrai mot de passe pourrait ne pas avoir été trouvé. 
                    <strong> Augmentez max_seconds ou limit pour continuer.</strong>
                  </div>
                )}
              </div>

              {/* Section 4: Candidats trouvés */}
              {result.matches && result.matches.length > 0 && (
                <div style={{ 
                  backgroundColor: '#f0fdf4', 
                  padding: '20px', 
                  borderLeft: '4px solid #10b981',
                  marginBottom: '16px'
                }}>
                  <h3 style={{ marginTop: 0, marginBottom: '16px', color: '#111827', fontSize: '18px' }}>
                    🔑 4. Candidats de Mot de Passe Trouvés
                  </h3>
                  
                  {/* compute best match */}
                  {(() => {
                    // Compute best match (first high confidence, else first result)
                    const best = (() => {
                      const high = result.matches.find(m => m.confidence === 'high');
                      if (high) return high;
                      // Prefer a candidate that has a numeric projection (A–J → 0–9)
                      const digitsCandidate = result.matches.find(m => m.candidate_plaintext_digits);
                      return digitsCandidate || result.matches[0];
                    })();
                    if (best) {
                      // show a prominent highlighted banner for the best match
                      const raw = (best.candidate_plaintext_raw ?? best.candidate_plaintext) || '';
                      const digits = best.candidate_plaintext_digits || null;
                      return (
                        <div style={{ marginBottom: '16px' }}>
                          <div style={{
                            background: 'linear-gradient(90deg, #10b98122, #10b98111)',
                            border: '2px solid #10b981',
                            padding: '12px 16px',
                            borderRadius: '8px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px'
                          }}>
                            <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#065f46' }}>⭐ Meilleur candidat</div>
                            <div style={{ fontSize: '20px', fontWeight: '900', color: '#064e3b', fontFamily: 'monospace' }}>{String(raw).toLowerCase()}</div>
                            {digits && (
                              <div style={{ fontSize: '16px', color: '#065f46', fontFamily: 'monospace' }}>
                                (= {digits})
                              </div>
                            )}
                            <div style={{ marginLeft: 'auto', fontSize: '13px', color: '#065f46' }}>{best.confidence?.toUpperCase() || ''}</div>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  })()}

                  {/* Statistiques rapides */}
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(3, 1fr)', 
                    gap: '12px',
                    marginBottom: '16px'
                  }}>
                    {['high', 'medium', 'low'].map(conf => {
                      const count = result.matches.filter(m => m.confidence === conf).length;
                      const badge = getConfidenceBadge(conf);
                      return (
                        <div key={conf} style={{ 
                          backgroundColor: 'white',
                          padding: '12px',
                          borderRadius: '6px',
                          textAlign: 'center',
                          border: `2px solid ${badge.color}`
                        }}>
                          <div style={{ fontSize: '24px', fontWeight: 'bold', color: badge.color }}>
                            {count}
                          </div>
                          <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                            {badge.emoji} Confiance {badge.text}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Liste des Top 10 candidats */}
                  <div style={{ 
                    backgroundColor: 'white', 
                    borderRadius: '8px',
                    overflow: 'hidden',
                    border: '1px solid #e5e7eb'
                  }}>
                    <div style={{ 
                      backgroundColor: '#111827', 
                      color: 'white', 
                      padding: '12px 16px',
                      fontWeight: 'bold'
                    }}>
                      🏆 Top {Math.min(10, result.matches.length)} Candidats (sur {result.matches.length} total)
                    </div>
                    
                    {result.matches.slice(0, 10).map((match, index) => {
                      const badge = getConfidenceBadge(match.confidence);
                      return (
                        <div 
                          key={index} 
                          style={{ 
                            padding: '16px',
                            borderBottom: index < Math.min(9, result.matches.length - 1) ? '1px solid #e5e7eb' : 'none',
                            backgroundColor: match.confidence === 'high' ? '#d1fae5' : 
                                           match.confidence === 'medium' ? '#fef3c7' : 'white',
                            transition: 'background-color 0.2s'
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
                            {/* Numéro */}
                            <div style={{ 
                              minWidth: '40px',
                              height: '40px',
                              borderRadius: '50%',
                              backgroundColor: badge.color,
                              color: 'white',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontWeight: 'bold',
                              fontSize: '18px'
                            }}>
                              {index + 1}
                            </div>

                            {/* Contenu */}
                            <div style={{ flex: 1 }}>
                              {/* Texte déchiffré (human-friendly lowercase) */}
                              <div style={{ marginBottom: '8px' }}>
                                <div style={{ fontSize: '11px', color: '#6b7280', marginBottom: '4px' }}>
                                  🔤 Texte Déchiffré:
                                </div>
                                <div style={{ 
                                  fontSize: '20px', 
                                  fontWeight: 'bold', 
                                  fontFamily: 'monospace',
                                  color: '#111827',
                                  letterSpacing: '1px',
                                  backgroundColor: 'rgba(255,255,255,0.7)',
                                  padding: '8px 12px',
                                  borderRadius: '4px',
                                  display: 'inline-block'
                                }}>
                                  {String(match.candidate_plaintext_raw ?? match.candidate_plaintext).toLowerCase()}
                                  {match.candidate_plaintext_digits && (
                                    <span style={{ marginLeft: '8px', fontSize: '14px', color: '#065f46' }}>
                                      (= {match.candidate_plaintext_digits})
                                    </span>
                                  )}
                                  {match.confidence === 'high' && (
                                    <span style={{ marginLeft: '12px', fontSize: '16px' }}>⭐</span>
                                  )}
                                </div>
                              </div>

                              {/* Clé utilisée */}
                              <div style={{ marginBottom: '8px' }}>
                                <div style={{ fontSize: '11px', color: '#6b7280', marginBottom: '4px' }}>
                                  🔑 Clé de Déchiffrement:
                                </div>
                                <code style={{ 
                                  backgroundColor: '#f3f4f6',
                                  padding: '6px 10px',
                                  borderRadius: '4px',
                                  fontSize: '13px',
                                  fontFamily: 'monospace',
                                  color: '#111827'
                                }}>
                                  {formatKey(match.candidate_key)}
                                </code>
                              </div>

                              {/* Niveau de confiance et notes */}
                              <div style={{ 
                                display: 'flex', 
                                gap: '12px', 
                                alignItems: 'center',
                                flexWrap: 'wrap'
                              }}>
                                <span style={{ 
                                  backgroundColor: badge.bg,
                                  color: badge.color,
                                  padding: '4px 12px',
                                  borderRadius: '12px',
                                  fontSize: '12px',
                                  fontWeight: 'bold'
                                }}>
                                  {badge.emoji} {badge.text}
                                </span>
                                <span style={{ fontSize: '12px', color: '#6b7280' }}>
                                  📝 {match.notes || 'Candidat valide'}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Message si plus de 10 résultats */}
                  {result.matches.length > 10 && (
                    <div style={{ 
                      marginTop: '12px', 
                      padding: '12px',
                      backgroundColor: 'white',
                      borderRadius: '6px',
                      textAlign: 'center',
                      fontSize: '13px',
                      color: '#6b7280'
                    }}>
                      ... et {result.matches.length - 10} autre(s) candidat(s) non affichés
                    </div>
                  )}
                </div>
              )}

              {/* Section 5: Recommandations */}
              <div style={{ 
                backgroundColor: '#fef3c7', 
                padding: '20px', 
                borderLeft: '4px solid #f59e0b',
                marginBottom: '16px'
              }}>
                <h3 style={{ marginTop: 0, marginBottom: '16px', color: '#111827', fontSize: '18px' }}>
                  💡 5. Que Faire Maintenant?
                </h3>
                
                {result.matches && result.matches.length > 0 ? (
                  <>
                    {result.matches.some(m => m.confidence === 'high') ? (
                      <div style={{ 
                        backgroundColor: '#d1fae5', 
                        padding: '16px', 
                        borderRadius: '8px',
                        border: '2px solid #10b981',
                        marginBottom: '12px'
                      }}>
                        <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#065f46', marginBottom: '8px' }}>
                          🎯 Succès! Candidat(s) avec Haute Confiance Trouvé(s)
                        </div>
                        <p style={{ margin: 0, fontSize: '14px', color: '#065f46' }}>
                          Le mot de passe le plus probable est: <strong style={{ fontSize: '16px' }}>
                            {
                              (() => {
                                const best = (() => {
                                  const high = result.matches.find(m => m.confidence === 'high');
                                  if (high) return high;
                                  const digitsCandidate = result.matches.find(m => m.candidate_plaintext_digits);
                                  return digitsCandidate || result.matches[0];
                                })();
                                if (!best) return 'N/A';
                                const raw = (best.candidate_plaintext_raw ?? best.candidate_plaintext) || '';
                                const digits = best.candidate_plaintext_digits || null;
                                return digits ? `${String(raw).toLowerCase()} (= ${digits})` : String(raw).toLowerCase();
                              })()
                            }
                          </strong>
                        </p>
                      </div>
                    ) : (
                      <div style={{ 
                        backgroundColor: '#fef3c7', 
                        padding: '16px', 
                        borderRadius: '8px',
                        border: '2px solid #f59e0b',
                        marginBottom: '12px'
                      }}>
                        <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#92400e', marginBottom: '8px' }}>
                          ⚠️ Aucun Candidat avec Haute Confiance
                        </div>
                        <p style={{ margin: 0, fontSize: '14px', color: '#92400e' }}>
                          Plusieurs candidats trouvés mais aucun avec haute confiance. Testez-les manuellement.
                        </p>
                      </div>
                    )}

                    <div style={{ 
                      backgroundColor: 'white', 
                      padding: '16px', 
                      borderRadius: '8px',
                      border: '1px solid #e5e7eb'
                    }}>
                      <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#111827', marginBottom: '12px' }}>
                        📋 Actions Recommandées:
                      </div>
                      <ol style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: '#4b5563' }}>
                        <li style={{ marginBottom: '8px' }}>
                          <strong>Essayer la connexion:</strong> Utilisez le candidat avec la plus haute confiance pour vous connecter
                        </li>
                        <li style={{ marginBottom: '8px' }}>
                          <strong>Tester manuellement:</strong> Si échec, essayez les autres candidats un par un
                        </li>
                        <li style={{ marginBottom: '8px' }}>
                          <strong>Noter la clé:</strong> Conservez la clé de déchiffrement pour référence
                        </li>
                        <li>
                          <strong>Analyse:</strong> Les candidats "high confidence" sont généralement corrects à 90%+
                        </li>
                      </ol>
                    </div>
                  </>
                ) : (
                  <div style={{ 
                    backgroundColor: '#fee2e2', 
                    padding: '16px', 
                    borderRadius: '8px',
                    border: '2px solid #ef4444'
                  }}>
                    <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#991b1b', marginBottom: '8px' }}>
                      ❌ Aucun Candidat Trouvé
                    </div>
                    <p style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#991b1b' }}>
                      L'attaque n'a trouvé aucun mot de passe valide.
                    </p>
                    <div style={{ fontSize: '13px', color: '#7f1d1d' }}>
                      <strong>Essayez:</strong>
                      <ul style={{ marginTop: '8px', marginBottom: 0, paddingLeft: '20px' }}>
                        <li>Une attaque par dictionnaire</li>
                        <li>Augmenter les limites de temps/tentatives</li>
                        <li>Vérifier que l'algorithme est correct</li>
                      </ul>
                    </div>
                  </div>
                )}
              </div>

              {/* Section 6: Interprétation des niveaux de confiance */}
              <div style={{ 
                backgroundColor: '#e0e7ff', 
                padding: '20px', 
                borderLeft: '4px solid #6366f1',
                borderRadius: '0 0 12px 12px'
              }}>
                <h3 style={{ marginTop: 0, marginBottom: '16px', color: '#111827', fontSize: '18px' }}>
                  📚 6. Guide d'Interprétation
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                  {[
                    { 
                      level: 'high', 
                      title: 'HAUTE CONFIANCE', 
                      desc: 'Très probablement le vrai mot de passe (texte valide, dans le dictionnaire, longueur appropriée)',
                      action: '➡️ Essayer en priorité'
                    },
                    { 
                      level: 'medium', 
                      title: 'CONFIANCE MOYENNE', 
                      desc: 'Pourrait être valide (texte alphabétique mais pas dans le dictionnaire)',
                      action: '➡️ Tester manuellement'
                    },
                    { 
                      level: 'low', 
                      title: 'FAIBLE CONFIANCE', 
                      desc: 'Probablement incorrect (charabia, texte trop court, caractères suspects)',
                      action: '➡️ Ignorer généralement'
                    }
                  ].map(item => {
                    const badge = getConfidenceBadge(item.level);
                    return (
                      <div key={item.level} style={{ 
                        backgroundColor: 'white',
                        padding: '16px',
                        borderRadius: '8px',
                        border: `2px solid ${badge.color}`
                      }}>
                        <div style={{ 
                          fontSize: '32px', 
                          textAlign: 'center',
                          marginBottom: '8px'
                        }}>
                          {badge.emoji}
                        </div>
                        <div style={{ 
                          fontSize: '14px', 
                          fontWeight: 'bold', 
                          color: badge.color,
                          textAlign: 'center',
                          marginBottom: '8px'
                        }}>
                          {item.title}
                        </div>
                        <div style={{ 
                          fontSize: '12px', 
                          color: '#4b5563',
                          marginBottom: '12px',
                          lineHeight: '1.5'
                        }}>
                          {item.desc}
                        </div>
                        <div style={{ 
                          fontSize: '11px', 
                          fontWeight: 'bold',
                          color: '#111827',
                          backgroundColor: '#f3f4f6',
                          padding: '6px',
                          borderRadius: '4px',
                          textAlign: 'center'
                        }}>
                          {item.action}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Notes additionnelles */}
              {result.notes && (
                <div style={{ 
                  marginTop: '16px',
                  padding: '12px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '8px',
                  border: '1px solid #e5e7eb',
                  fontSize: '13px',
                  color: '#6b7280'
                }}>
                  <strong>📝 Notes:</strong> {result.notes}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default AttackPanel;
