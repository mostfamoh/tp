import React, { useState } from 'react';

const MessagingPanel = () => {
  const [activeTab, setActiveTab] = useState('normal'); // 'normal' or 'mitm'
  
  // Normal messaging state
  const [algorithm, setAlgorithm] = useState('caesar');
  const [key, setKey] = useState('3');
  const [message, setMessage] = useState('');
  const [encryptionSteps, setEncryptionSteps] = useState([]);
  const [encryptedMessage, setEncryptedMessage] = useState('');
  const [decryptionSteps, setDecryptionSteps] = useState([]);
  const [decryptedMessage, setDecryptedMessage] = useState('');
  
  // MITM state
  const [mitmMessage, setMitmMessage] = useState('');
  const [mitmAlgorithm, setMitmAlgorithm] = useState('caesar');
  const [mitmKey, setMitmKey] = useState('3');
  const [aliceToEve, setAliceToEve] = useState(null);
  const [eveIntercepted, setEveIntercepted] = useState(null);
  const [eveModified, setEveModified] = useState('');
  const [eveToBob, setEveToBob] = useState(null);
  const [bobReceived, setBobReceived] = useState(null);
  const [mitmAttackActive, setMitmAttackActive] = useState(false);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  // Get key parameters based on algorithm
  const getKeyParams = () => {
    switch (algorithm) {
      case 'caesar':
        return { shift: parseInt(key) || 0 };
      case 'affine':
        const [a, b] = key.split(',').map(x => parseInt(x.trim()) || 0);
        return { a: a || 5, b: b || 8 };
      case 'playfair':
        return { keyword: key || 'KEYWORD' };
      case 'hill':
        try {
          return { matrix: JSON.parse(key) };
        } catch {
          return { matrix: [[3, 3], [2, 5]] };
        }
      default:
        return {};
    }
  };

  // Encrypt message (Alice sends)
  const handleEncrypt = async () => {
    if (!message.trim()) {
      setNotification({ type: 'error', text: 'Veuillez entrer un message' });
      return;
    }

    setLoading(true);
    setNotification(null);
    setEncryptionSteps([]);
    setEncryptedMessage('');

    try {
      const keyParams = getKeyParams();
      
      const response = await fetch('http://localhost:8000/api/encrypt/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plaintext: message,
          algorithm: algorithm,
          key: keyParams
        })
      });

      const data = await response.json();

      if (response.ok) {
        setEncryptionSteps(data.steps || []);
        setEncryptedMessage(data.ciphertext);
        setNotification({ 
          type: 'success', 
          text: `✅ Alice a chiffré le message avec ${algorithm.toUpperCase()}` 
        });
      } else {
        setNotification({ type: 'error', text: data.error || 'Erreur de chiffrement' });
      }
    } catch (error) {
      setNotification({ type: 'error', text: 'Erreur de connexion au serveur' });
    } finally {
      setLoading(false);
    }
  };

  // Decrypt message (Bob receives)
  const handleDecrypt = async () => {
    if (!encryptedMessage.trim()) {
      setNotification({ type: 'error', text: 'Aucun message chiffré à déchiffrer' });
      return;
    }

    setLoading(true);
    setNotification(null);
    setDecryptionSteps([]);
    setDecryptedMessage('');

    try {
      const keyParams = getKeyParams();
      
      const response = await fetch('http://localhost:8000/api/decrypt/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ciphertext: encryptedMessage,
          algorithm: algorithm,
          key: keyParams
        })
      });

      const data = await response.json();

      if (response.ok) {
        setDecryptionSteps(data.steps || []);
        setDecryptedMessage(data.plaintext);
        setNotification({ 
          type: 'success', 
          text: `✅ Bob a déchiffré le message avec succès` 
        });
      } else {
        setNotification({ type: 'error', text: data.error || 'Erreur de déchiffrement' });
      }
    } catch (error) {
      setNotification({ type: 'error', text: 'Erreur de connexion au serveur' });
    } finally {
      setLoading(false);
    }
  };

  // MITM Attack - Step 1: Alice sends encrypted message
  const handleMitmAliceSend = async () => {
    if (!mitmMessage.trim()) {
      setNotification({ type: 'error', text: 'Veuillez entrer un message' });
      return;
    }

    setLoading(true);
    setNotification(null);

    try {
      const keyParams = getKeyParams();
      
      const response = await fetch('http://localhost:8000/api/encrypt/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plaintext: mitmMessage,
          algorithm: mitmAlgorithm,
          key: keyParams
        })
      });

      const data = await response.json();

      if (response.ok) {
        setAliceToEve({
          plaintext: mitmMessage,
          ciphertext: data.ciphertext,
          steps: data.steps,
          algorithm: mitmAlgorithm,
          key: mitmKey
        });
        setNotification({ 
          type: 'success', 
          text: `📤 Alice envoie le message chiffré...` 
        });
      }
    } catch (error) {
      setNotification({ type: 'error', text: 'Erreur lors de l\'envoi' });
    } finally {
      setLoading(false);
    }
  };

  // MITM Attack - Step 2: Eve intercepts
  const handleMitmEveIntercept = async () => {
    if (!aliceToEve) {
      setNotification({ type: 'error', text: 'Aucun message à intercepter' });
      return;
    }

    setLoading(true);

    try {
      const keyParams = getKeyParams();
      
      // Eve déchiffre le message intercepté
      const response = await fetch('http://localhost:8000/api/decrypt/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ciphertext: aliceToEve.ciphertext,
          algorithm: mitmAlgorithm,
          key: keyParams
        })
      });

      const data = await response.json();

      if (response.ok) {
        setEveIntercepted({
          ciphertext: aliceToEve.ciphertext,
          plaintext: data.plaintext,
          steps: data.steps
        });
        setMitmAttackActive(true);
        setNotification({ 
          type: 'warning', 
          text: `🕵️ Eve a intercepté et déchiffré le message !` 
        });
      }
    } catch (error) {
      setNotification({ type: 'error', text: 'Erreur d\'interception' });
    } finally {
      setLoading(false);
    }
  };

  // MITM Attack - Step 3: Eve modifies and re-encrypts
  const handleMitmEveModify = async () => {
    if (!eveModified.trim()) {
      setNotification({ type: 'error', text: 'Entrez le message modifié' });
      return;
    }

    setLoading(true);

    try {
      const keyParams = getKeyParams();
      
      const response = await fetch('http://localhost:8000/api/encrypt/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plaintext: eveModified,
          algorithm: mitmAlgorithm,
          key: keyParams
        })
      });

      const data = await response.json();

      if (response.ok) {
        setEveToBob({
          plaintext: eveModified,
          ciphertext: data.ciphertext,
          steps: data.steps
        });
        setNotification({ 
          type: 'warning', 
          text: `😈 Eve a modifié le message et l'a rechiffré !` 
        });
      }
    } catch (error) {
      setNotification({ type: 'error', text: 'Erreur de modification' });
    } finally {
      setLoading(false);
    }
  };

  // MITM Attack - Step 4: Bob receives and decrypts
  const handleMitmBobReceive = async () => {
    if (!eveToBob) {
      setNotification({ type: 'error', text: 'Aucun message à recevoir' });
      return;
    }

    setLoading(true);

    try {
      const keyParams = getKeyParams();
      
      const response = await fetch('http://localhost:8000/api/decrypt/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ciphertext: eveToBob.ciphertext,
          algorithm: mitmAlgorithm,
          key: keyParams
        })
      });

      const data = await response.json();

      if (response.ok) {
        setBobReceived({
          ciphertext: eveToBob.ciphertext,
          plaintext: data.plaintext,
          steps: data.steps
        });
        setNotification({ 
          type: 'info', 
          text: `📥 Bob a reçu et déchiffré le message (MODIFIÉ par Eve !)` 
        });
      }
    } catch (error) {
      setNotification({ type: 'error', text: 'Erreur de réception' });
    } finally {
      setLoading(false);
    }
  };

  // Reset MITM attack
  const resetMitm = () => {
    setAliceToEve(null);
    setEveIntercepted(null);
    setEveModified('');
    setEveToBob(null);
    setBobReceived(null);
    setMitmAttackActive(false);
    setNotification(null);
  };

  return (
    <div className="card">
      <h2 style={{ marginBottom: '20px', color: '#111827' }}>💬 Messagerie Sécurisée</h2>
      
      {/* Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '2px solid #e5e7eb' }}>
        <button
          onClick={() => setActiveTab('normal')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: activeTab === 'normal' ? '#3B82F6' : 'transparent',
            color: activeTab === 'normal' ? 'white' : '#6B7280',
            borderRadius: '5px 5px 0 0',
            cursor: 'pointer',
            fontWeight: activeTab === 'normal' ? 'bold' : 'normal'
          }}
        >
          👤 Communication Normale
        </button>
        <button
          onClick={() => setActiveTab('mitm')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: activeTab === 'mitm' ? '#EF4444' : 'transparent',
            color: activeTab === 'mitm' ? 'white' : '#6B7280',
            borderRadius: '5px 5px 0 0',
            cursor: 'pointer',
            fontWeight: activeTab === 'mitm' ? 'bold' : 'normal'
          }}
        >
          🕵️ Attaque MITM
        </button>
      </div>

      {/* Notification */}
      {notification && (
        <div
          style={{
            padding: '15px',
            marginBottom: '20px',
            borderRadius: '5px',
            backgroundColor: 
              notification.type === 'success' ? '#D1FAE5' :
              notification.type === 'error' ? '#FEE2E2' :
              notification.type === 'warning' ? '#FEF3C7' : '#DBEAFE',
            color: 
              notification.type === 'success' ? '#065F46' :
              notification.type === 'error' ? '#991B1B' :
              notification.type === 'warning' ? '#92400E' : '#1E40AF',
            border: `1px solid ${
              notification.type === 'success' ? '#34D399' :
              notification.type === 'error' ? '#F87171' :
              notification.type === 'warning' ? '#FCD34D' : '#60A5FA'
            }`
          }}
        >
          {notification.text}
        </div>
      )}

      {/* NORMAL COMMUNICATION TAB */}
      {activeTab === 'normal' && (
        <div>
          <h3 style={{ marginBottom: '15px', color: '#374151' }}>
            Alice 👩 → Bob 👨 (Communication Sécurisée)
          </h3>

          {/* Algorithm selection */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
              Algorithme de chiffrement :
            </label>
            <select
              value={algorithm}
              onChange={(e) => {
                setAlgorithm(e.target.value);
                // Reset default keys
                if (e.target.value === 'caesar') setKey('3');
                else if (e.target.value === 'affine') setKey('5,8');
                else if (e.target.value === 'playfair') setKey('KEYWORD');
                else if (e.target.value === 'hill') setKey('[[3,3],[2,5]]');
              }}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #D1D5DB',
                borderRadius: '5px',
                fontSize: '14px'
              }}
            >
              <option value="caesar">César (Décalage)</option>
              <option value="affine">Affine (a,b)</option>
              <option value="playfair">Playfair (Mot-clé)</option>
              <option value="hill">Hill (Matrice)</option>
            </select>
          </div>

          {/* Key input */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
              Clé :
            </label>
            <input
              type="text"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder={
                algorithm === 'caesar' ? 'Ex: 3' :
                algorithm === 'affine' ? 'Ex: 5,8' :
                algorithm === 'playfair' ? 'Ex: KEYWORD' :
                'Ex: [[3,3],[2,5]]'
              }
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #D1D5DB',
                borderRadius: '5px',
                fontSize: '14px',
                fontFamily: algorithm === 'hill' ? 'monospace' : 'inherit'
              }}
            />
          </div>

          {/* Message input */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
              📝 Message d'Alice :
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Entrez le message à envoyer à Bob..."
              rows={3}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #D1D5DB',
                borderRadius: '5px',
                fontSize: '14px'
              }}
            />
          </div>

          <button
            onClick={handleEncrypt}
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', marginBottom: '20px' }}
          >
            {loading ? '⏳ Chiffrement...' : '🔒 Alice Chiffre et Envoie'}
          </button>

          {/* Encryption Steps */}
          {encryptionSteps.length > 0 && (
            <div style={{
              padding: '15px',
              backgroundColor: '#EFF6FF',
              borderRadius: '5px',
              marginBottom: '20px',
              border: '2px solid #3B82F6'
            }}>
              <h4 style={{ color: '#1E40AF', marginBottom: '10px' }}>
                📋 Étapes de Chiffrement (Alice)
              </h4>
              {encryptionSteps.map((step, index) => (
                <div key={index} style={{
                  padding: '8px',
                  backgroundColor: 'white',
                  borderRadius: '3px',
                  marginBottom: '5px',
                  fontSize: '13px',
                  fontFamily: 'monospace'
                }}>
                  {index + 1}. {step}
                </div>
              ))}
            </div>
          )}

          {/* Encrypted Message */}
          {encryptedMessage && (
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                📡 Message chiffré (en transit) :
              </label>
              <div style={{
                padding: '15px',
                backgroundColor: '#FEF3C7',
                borderRadius: '5px',
                fontSize: '16px',
                fontFamily: 'monospace',
                fontWeight: 'bold',
                color: '#92400E',
                border: '2px solid #FCD34D',
                wordBreak: 'break-all'
              }}>
                {encryptedMessage}
              </div>
              
              <button
                onClick={handleDecrypt}
                className="btn btn-primary"
                disabled={loading}
                style={{ width: '100%', marginTop: '10px' }}
              >
                {loading ? '⏳ Déchiffrement...' : '🔓 Bob Déchiffre'}
              </button>
            </div>
          )}

          {/* Decryption Steps */}
          {decryptionSteps.length > 0 && (
            <div style={{
              padding: '15px',
              backgroundColor: '#ECFDF5',
              borderRadius: '5px',
              marginBottom: '20px',
              border: '2px solid #10B981'
            }}>
              <h4 style={{ color: '#065F46', marginBottom: '10px' }}>
                📋 Étapes de Déchiffrement (Bob)
              </h4>
              {decryptionSteps.map((step, index) => (
                <div key={index} style={{
                  padding: '8px',
                  backgroundColor: 'white',
                  borderRadius: '3px',
                  marginBottom: '5px',
                  fontSize: '13px',
                  fontFamily: 'monospace'
                }}>
                  {index + 1}. {step}
                </div>
              ))}
            </div>
          )}

          {/* Decrypted Message */}
          {decryptedMessage && (
            <div style={{
              padding: '15px',
              backgroundColor: '#D1FAE5',
              borderRadius: '5px',
              border: '2px solid #10B981'
            }}>
              <h4 style={{ color: '#065F46', marginBottom: '10px' }}>
                ✅ Message reçu par Bob :
              </h4>
              <div style={{
                fontSize: '18px',
                fontWeight: 'bold',
                color: '#065F46'
              }}>
                "{decryptedMessage}"
              </div>
            </div>
          )}
        </div>
      )}

      {/* MITM ATTACK TAB */}
      {activeTab === 'mitm' && (
        <div>
          <div style={{
            padding: '15px',
            backgroundColor: '#FEE2E2',
            borderRadius: '5px',
            marginBottom: '20px',
            border: '2px solid #EF4444'
          }}>
            <h3 style={{ color: '#991B1B', marginBottom: '10px' }}>
              ⚠️ Démonstration d'Attaque Man-In-The-Middle
            </h3>
            <p style={{ color: '#991B1B', fontSize: '14px', margin: 0 }}>
              Eve intercepte la communication entre Alice et Bob, déchiffre le message, le modifie, et le rechiffre avant de l'envoyer à Bob.
            </p>
          </div>

          {/* Algorithm and Key */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                Algorithme :
              </label>
              <select
                value={mitmAlgorithm}
                onChange={(e) => {
                  setMitmAlgorithm(e.target.value);
                  if (e.target.value === 'caesar') setMitmKey('3');
                  else if (e.target.value === 'affine') setMitmKey('5,8');
                  else if (e.target.value === 'playfair') setMitmKey('KEYWORD');
                  else if (e.target.value === 'hill') setMitmKey('[[3,3],[2,5]]');
                }}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '5px'
                }}
              >
                <option value="caesar">César</option>
                <option value="affine">Affine</option>
                <option value="playfair">Playfair</option>
                <option value="hill">Hill</option>
              </select>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                Clé :
              </label>
              <input
                type="text"
                value={mitmKey}
                onChange={(e) => setMitmKey(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '5px'
                }}
              />
            </div>
          </div>

          {/* Step 1: Alice sends */}
          <div style={{
            padding: '15px',
            backgroundColor: '#EFF6FF',
            borderRadius: '5px',
            marginBottom: '15px',
            border: '2px solid #3B82F6'
          }}>
            <h4 style={{ color: '#1E40AF', marginBottom: '10px' }}>
              📤 Étape 1 : Alice envoie un message
            </h4>
            <textarea
              value={mitmMessage}
              onChange={(e) => setMitmMessage(e.target.value)}
              placeholder="Message d'Alice à Bob..."
              rows={2}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #D1D5DB',
                borderRadius: '5px',
                marginBottom: '10px'
              }}
            />
            <button
              onClick={handleMitmAliceSend}
              className="btn btn-primary"
              disabled={loading}
              style={{ width: '100%' }}
            >
              {loading ? '⏳' : '👩 Alice chiffre et envoie'}
            </button>

            {aliceToEve && (
              <div style={{ marginTop: '10px' }}>
                <div style={{
                  padding: '10px',
                  backgroundColor: 'white',
                  borderRadius: '3px',
                  marginBottom: '5px'
                }}>
                  <strong>Message original :</strong> {aliceToEve.plaintext}
                </div>
                <div style={{
                  padding: '10px',
                  backgroundColor: '#FEF3C7',
                  borderRadius: '3px',
                  fontFamily: 'monospace'
                }}>
                  <strong>Chiffré :</strong> {aliceToEve.ciphertext}
                </div>
                {aliceToEve.steps && aliceToEve.steps.length > 0 && (
                  <details style={{ marginTop: '10px' }}>
                    <summary style={{ cursor: 'pointer', color: '#1E40AF', fontWeight: 'bold' }}>
                      Voir les étapes de chiffrement
                    </summary>
                    {aliceToEve.steps.map((step, i) => (
                      <div key={i} style={{
                        padding: '5px',
                        fontSize: '12px',
                        fontFamily: 'monospace',
                        backgroundColor: 'white',
                        marginTop: '3px',
                        borderRadius: '3px'
                      }}>
                        {i + 1}. {step}
                      </div>
                    ))}
                  </details>
                )}
              </div>
            )}
          </div>

          {/* Step 2: Eve intercepts */}
          {aliceToEve && (
            <div style={{
              padding: '15px',
              backgroundColor: '#FEF3C7',
              borderRadius: '5px',
              marginBottom: '15px',
              border: '2px solid #F59E0B'
            }}>
              <h4 style={{ color: '#92400E', marginBottom: '10px' }}>
                🕵️ Étape 2 : Eve intercepte et déchiffre
              </h4>
              <button
                onClick={handleMitmEveIntercept}
                className="btn"
                disabled={loading}
                style={{ width: '100%', backgroundColor: '#F59E0B', color: 'white' }}
              >
                {loading ? '⏳' : '🕵️ Eve intercepte le message'}
              </button>

              {eveIntercepted && (
                <div style={{ marginTop: '10px' }}>
                  <div style={{
                    padding: '10px',
                    backgroundColor: '#FEE2E2',
                    borderRadius: '3px',
                    marginBottom: '5px'
                  }}>
                    <strong>⚠️ Eve a déchiffré :</strong> {eveIntercepted.plaintext}
                  </div>
                  {eveIntercepted.steps && eveIntercepted.steps.length > 0 && (
                    <details style={{ marginTop: '10px' }}>
                      <summary style={{ cursor: 'pointer', color: '#92400E', fontWeight: 'bold' }}>
                        Voir les étapes de déchiffrement (Eve)
                      </summary>
                      {eveIntercepted.steps.map((step, i) => (
                        <div key={i} style={{
                          padding: '5px',
                          fontSize: '12px',
                          fontFamily: 'monospace',
                          backgroundColor: 'white',
                          marginTop: '3px',
                          borderRadius: '3px'
                        }}>
                          {i + 1}. {step}
                        </div>
                      ))}
                    </details>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Step 3: Eve modifies */}
          {eveIntercepted && (
            <div style={{
              padding: '15px',
              backgroundColor: '#FEE2E2',
              borderRadius: '5px',
              marginBottom: '15px',
              border: '2px solid #EF4444'
            }}>
              <h4 style={{ color: '#991B1B', marginBottom: '10px' }}>
                😈 Étape 3 : Eve modifie le message
              </h4>
              <textarea
                value={eveModified}
                onChange={(e) => setEveModified(e.target.value)}
                placeholder="Message modifié par Eve..."
                rows={2}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #991B1B',
                  borderRadius: '5px',
                  marginBottom: '10px'
                }}
              />
              <button
                onClick={handleMitmEveModify}
                className="btn"
                disabled={loading}
                style={{ width: '100%', backgroundColor: '#EF4444', color: 'white' }}
              >
                {loading ? '⏳' : '😈 Eve modifie et rechiffre'}
              </button>

              {eveToBob && (
                <div style={{ marginTop: '10px' }}>
                  <div style={{
                    padding: '10px',
                    backgroundColor: '#FEF3C7',
                    borderRadius: '3px',
                    fontFamily: 'monospace'
                  }}>
                    <strong>Rechiffré par Eve :</strong> {eveToBob.ciphertext}
                  </div>
                  {eveToBob.steps && eveToBob.steps.length > 0 && (
                    <details style={{ marginTop: '10px' }}>
                      <summary style={{ cursor: 'pointer', color: '#991B1B', fontWeight: 'bold' }}>
                        Voir les étapes de re-chiffrement (Eve)
                      </summary>
                      {eveToBob.steps.map((step, i) => (
                        <div key={i} style={{
                          padding: '5px',
                          fontSize: '12px',
                          fontFamily: 'monospace',
                          backgroundColor: 'white',
                          marginTop: '3px',
                          borderRadius: '3px'
                        }}>
                          {i + 1}. {step}
                        </div>
                      ))}
                    </details>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Step 4: Bob receives */}
          {eveToBob && (
            <div style={{
              padding: '15px',
              backgroundColor: '#DBEAFE',
              borderRadius: '5px',
              marginBottom: '15px',
              border: '2px solid #3B82F6'
            }}>
              <h4 style={{ color: '#1E40AF', marginBottom: '10px' }}>
                📥 Étape 4 : Bob reçoit et déchiffre
              </h4>
              <button
                onClick={handleMitmBobReceive}
                className="btn btn-primary"
                disabled={loading}
                style={{ width: '100%' }}
              >
                {loading ? '⏳' : '👨 Bob déchiffre le message'}
              </button>

              {bobReceived && (
                <div style={{ marginTop: '10px' }}>
                  <div style={{
                    padding: '10px',
                    backgroundColor: '#FEE2E2',
                    borderRadius: '3px',
                    marginBottom: '5px'
                  }}>
                    <strong>⚠️ Bob lit (MODIFIÉ) :</strong> {bobReceived.plaintext}
                  </div>
                  {bobReceived.steps && bobReceived.steps.length > 0 && (
                    <details style={{ marginTop: '10px' }}>
                      <summary style={{ cursor: 'pointer', color: '#1E40AF', fontWeight: 'bold' }}>
                        Voir les étapes de déchiffrement (Bob)
                      </summary>
                      {bobReceived.steps.map((step, i) => (
                        <div key={i} style={{
                          padding: '5px',
                          fontSize: '12px',
                          fontFamily: 'monospace',
                          backgroundColor: 'white',
                          marginTop: '3px',
                          borderRadius: '3px'
                        }}>
                          {i + 1}. {step}
                        </div>
                      ))}
                    </details>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Summary */}
          {bobReceived && (
            <div style={{
              padding: '15px',
              backgroundColor: '#FEE2E2',
              borderRadius: '5px',
              border: '2px solid #DC2626'
            }}>
              <h4 style={{ color: '#991B1B', marginBottom: '10px' }}>
                📊 Résumé de l'attaque MITM
              </h4>
              <div style={{ fontSize: '14px', color: '#991B1B', lineHeight: '1.8' }}>
                <p>✅ <strong>Alice a envoyé :</strong> "{aliceToEve.plaintext}"</p>
                <p>🕵️ <strong>Eve a intercepté et lu :</strong> "{eveIntercepted.plaintext}"</p>
                <p>😈 <strong>Eve a modifié en :</strong> "{eveToBob.plaintext}"</p>
                <p>❌ <strong>Bob a reçu :</strong> "{bobReceived.plaintext}"</p>
                <p style={{ marginTop: '10px', fontWeight: 'bold', color: '#DC2626' }}>
                  ⚠️ L'attaque MITM a réussi ! Bob pense que le message vient d'Alice, mais il a été modifié par Eve.
                </p>
              </div>
              <button
                onClick={resetMitm}
                className="btn"
                style={{ width: '100%', marginTop: '15px', backgroundColor: '#6B7280', color: 'white' }}
              >
                🔄 Réinitialiser l'attaque
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MessagingPanel;
