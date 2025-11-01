import React, { useState } from 'react';

const SteganographyPanel = () => {
  const [activeSubTab, setActiveSubTab] = useState('text');
  const [textMode, setTextMode] = useState('hide'); // 'hide' or 'extract'
  const [imageMode, setImageMode] = useState('hide'); // 'hide' or 'extract'
  
  // Text steganography state
  const [coverText, setCoverText] = useState('');
  const [secretMessage, setSecretMessage] = useState('');
  const [textMethod, setTextMethod] = useState('case');
  const [stegoText, setStegoText] = useState('');
  const [extractedTextMessage, setExtractedTextMessage] = useState('');
  const [textAnalysis, setTextAnalysis] = useState(null);
  
  // Image steganography state
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [imageSecretMessage, setImageSecretMessage] = useState('');
  const [stegoImage, setStegoImage] = useState(null);
  const [extractedImageMessage, setExtractedImageMessage] = useState('');
  const [imageAnalysis, setImageAnalysis] = useState(null);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  // Text steganography handlers
  const handleHideTextInText = async () => {
    if (!coverText.trim() || !secretMessage.trim()) {
      setMessage({ type: 'error', text: 'Veuillez remplir tous les champs' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await fetch('http://localhost:8000/api/stego/text/hide/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cover_text: coverText,
          secret_message: secretMessage,
          method: textMethod
        })
      });

      const data = await response.json();

      if (response.ok) {
        setStegoText(data.stego_text);
        setMessage({ 
          type: 'success', 
          text: `✅ Message caché avec succès ! (${data.message_length} caractères)` 
        });
      } else {
        setMessage({ type: 'error', text: data.error || 'Erreur lors du traitement' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Erreur de connexion au serveur' });
    } finally {
      setLoading(false);
    }
  };

  const handleExtractTextFromText = async () => {
    if (!stegoText.trim()) {
      setMessage({ type: 'error', text: 'Veuillez entrer un texte stéganographié' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await fetch('http://localhost:8000/api/stego/text/extract/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stego_text: stegoText,
          method: textMethod
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setExtractedTextMessage(data.secret_message);
        setMessage({ 
          type: 'success', 
          text: `✅ Message extrait : "${data.secret_message}"` 
        });
      } else {
        setMessage({ type: 'error', text: data.error || 'Aucun message trouvé' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Erreur de connexion au serveur' });
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeCoverText = async () => {
    if (!coverText.trim()) {
      setMessage({ type: 'error', text: 'Veuillez entrer un texte à analyser' });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/stego/analyze/text/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cover_text: coverText })
      });

      const data = await response.json();
      if (response.ok) {
        setTextAnalysis(data);
        setMessage({ type: 'success', text: '✅ Analyse terminée' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Erreur lors de l\'analyse' });
    } finally {
      setLoading(false);
    }
  };

  // Image steganography handlers
  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target.result);
      reader.readAsDataURL(file);
      
      // Auto analyze
      analyzeImage(file);
    }
  };

  const analyzeImage = async (file) => {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const base64 = e.target.result.split(',')[1];
      try {
        const response = await fetch('http://localhost:8000/api/stego/analyze/image/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image_data: base64 })
        });

        const data = await response.json();
        if (response.ok) {
          setImageAnalysis(data);
        }
      } catch (error) {
        console.error('Erreur analyse:', error);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleHideTextInImage = async () => {
    if (!selectedImage || !imageSecretMessage.trim()) {
      setMessage({ type: 'error', text: 'Veuillez sélectionner une image et entrer un message' });
      return;
    }

    setLoading(true);
    setMessage(null);

    const reader = new FileReader();
    reader.onload = async (e) => {
      const base64 = e.target.result.split(',')[1];

      try {
        const response = await fetch('http://localhost:8000/api/stego/image/hide/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_data: base64,
            secret_message: imageSecretMessage,
            method: 'lsb'
          })
        });

        const data = await response.json();

        if (response.ok) {
          setStegoImage('data:image/png;base64,' + data.stego_image);
          setMessage({ 
            type: 'success', 
            text: `✅ Message caché dans l'image ! (${data.message_length} caractères, ${data.capacity_used}% utilisé)` 
          });
        } else {
          setMessage({ type: 'error', text: data.error || 'Erreur lors du traitement' });
        }
      } catch (error) {
        setMessage({ type: 'error', text: 'Erreur de connexion au serveur' });
      } finally {
        setLoading(false);
      }
    };

    reader.readAsDataURL(selectedImage);
  };

  const handleExtractTextFromImage = async () => {
    if (!selectedImage) {
      setMessage({ type: 'error', text: 'Veuillez sélectionner une image stéganographiée' });
      return;
    }

    setLoading(true);
    setMessage(null);

    const reader = new FileReader();
    reader.onload = async (e) => {
      const base64 = e.target.result.split(',')[1];

      try {
        const response = await fetch('http://localhost:8000/api/stego/image/extract/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_data: base64,
            method: 'lsb'
          })
        });

        const data = await response.json();

        if (response.ok && data.success) {
          setExtractedImageMessage(data.secret_message);
          setMessage({ 
            type: 'success', 
            text: `✅ Message extrait (${data.message_length} caractères)` 
          });
        } else {
          setMessage({ type: 'error', text: data.error || 'Aucun message trouvé' });
        }
      } catch (error) {
        setMessage({ type: 'error', text: 'Erreur de connexion au serveur' });
      } finally {
        setLoading(false);
      }
    };

    reader.readAsDataURL(selectedImage);
  };

  const downloadStegoImage = () => {
    if (stegoImage) {
      const link = document.createElement('a');
      link.href = stegoImage;
      link.download = 'stego_image.png';
      link.click();
    }
  };

  return (
    <div className="card">
      <h2 style={{ marginBottom: '20px', color: '#111827' }}>🔐 Stéganographie</h2>
      <p style={{ color: '#6B7280', marginBottom: '20px' }}>
        Cachez des messages secrets dans du texte ou des images
      </p>

      {/* Sub-tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '2px solid #e5e7eb' }}>
        <button
          onClick={() => setActiveSubTab('text')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: activeSubTab === 'text' ? '#3B82F6' : 'transparent',
            color: activeSubTab === 'text' ? 'white' : '#6B7280',
            borderRadius: '5px 5px 0 0',
            cursor: 'pointer',
            fontWeight: activeSubTab === 'text' ? 'bold' : 'normal'
          }}
        >
          📝 Texte
        </button>
        <button
          onClick={() => setActiveSubTab('image')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: activeSubTab === 'image' ? '#3B82F6' : 'transparent',
            color: activeSubTab === 'image' ? 'white' : '#6B7280',
            borderRadius: '5px 5px 0 0',
            cursor: 'pointer',
            fontWeight: activeSubTab === 'image' ? 'bold' : 'normal'
          }}
        >
          🖼️ Image
        </button>
      </div>

      {/* Messages */}
      {message && (
        <div
          style={{
            padding: '15px',
            marginBottom: '20px',
            borderRadius: '5px',
            backgroundColor: message.type === 'success' ? '#D1FAE5' : '#FEE2E2',
            color: message.type === 'success' ? '#065F46' : '#991B1B',
            border: `1px solid ${message.type === 'success' ? '#34D399' : '#F87171'}`
          }}
        >
          {message.text}
        </div>
      )}

      {/* TEXT STEGANOGRAPHY */}
      {activeSubTab === 'text' && (
        <div>
          {/* Mode selector */}
          <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <button
              onClick={() => setTextMode('hide')}
              className={textMode === 'hide' ? 'btn btn-primary' : 'btn'}
              style={{ flex: 1 }}
            >
              🔒 Cacher un message
            </button>
            <button
              onClick={() => setTextMode('extract')}
              className={textMode === 'extract' ? 'btn btn-primary' : 'btn'}
              style={{ flex: 1 }}
            >
              🔓 Extraire un message
            </button>
          </div>

          {/* Method selector */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
              Méthode :
            </label>
            <select
              value={textMethod}
              onChange={(e) => setTextMethod(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #D1D5DB',
                borderRadius: '5px',
                fontSize: '14px'
              }}
            >
              <option value="case">Case-Based (Casse des lettres) - ✅ Recommandé</option>
              <option value="whitespace">WhiteSpace (Espaces/Tabs)</option>
              <option value="zerowidth">Zero-Width (Unicode invisible)</option>
            </select>
          </div>

          {textMode === 'hide' ? (
            <>
              {/* Cover text */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                  Texte de couverture :
                </label>
                <textarea
                  value={coverText}
                  onChange={(e) => setCoverText(e.target.value)}
                  placeholder="Entrez le texte qui va servir de couverture..."
                  rows={4}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #D1D5DB',
                    borderRadius: '5px',
                    fontSize: '14px',
                    fontFamily: 'monospace'
                  }}
                />
                <button
                  onClick={handleAnalyzeCoverText}
                  className="btn"
                  style={{ marginTop: '5px', fontSize: '12px' }}
                  disabled={loading}
                >
                  📊 Analyser la capacité
                </button>
              </div>

              {/* Analysis results */}
              {textAnalysis && (
                <div style={{
                  padding: '15px',
                  backgroundColor: '#F3F4F6',
                  borderRadius: '5px',
                  marginBottom: '20px',
                  fontSize: '13px'
                }}>
                  <strong>📊 Analyse :</strong><br/>
                  - Caractères totaux : {textAnalysis.total_chars}<br/>
                  - Lettres : {textAnalysis.letter_count}<br/>
                  {textMethod === 'case' && (
                    <>- Capacité max : {textAnalysis.capacity_chars} caractères</>
                  )}
                  {(textMethod === 'whitespace' || textMethod === 'zerowidth') && (
                    <>- Capacité : Illimitée</>
                  )}
                </div>
              )}

              {/* Secret message */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                  Message secret à cacher :
                </label>
                <textarea
                  value={secretMessage}
                  onChange={(e) => setSecretMessage(e.target.value)}
                  placeholder="Entrez votre message secret..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #D1D5DB',
                    borderRadius: '5px',
                    fontSize: '14px'
                  }}
                />
                <small style={{ color: '#6B7280' }}>
                  {secretMessage.length} caractères
                </small>
              </div>

              <button
                onClick={handleHideTextInText}
                className="btn btn-primary"
                disabled={loading}
                style={{ width: '100%' }}
              >
                {loading ? '⏳ Traitement...' : '🔒 Cacher le message'}
              </button>

              {/* Result */}
              {stegoText && (
                <div style={{ marginTop: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                    ✅ Texte stéganographié :
                  </label>
                  <textarea
                    value={stegoText}
                    readOnly
                    rows={4}
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '2px solid #10B981',
                      borderRadius: '5px',
                      fontSize: '14px',
                      fontFamily: 'monospace',
                      backgroundColor: '#ECFDF5'
                    }}
                  />
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(stegoText);
                      setMessage({ type: 'success', text: '📋 Copié dans le presse-papier !' });
                    }}
                    className="btn"
                    style={{ marginTop: '5px' }}
                  >
                    📋 Copier
                  </button>
                </div>
              )}
            </>
          ) : (
            <>
              {/* Extract mode */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                  Texte stéganographié :
                </label>
                <textarea
                  value={stegoText}
                  onChange={(e) => setStegoText(e.target.value)}
                  placeholder="Collez le texte contenant un message caché..."
                  rows={4}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #D1D5DB',
                    borderRadius: '5px',
                    fontSize: '14px',
                    fontFamily: 'monospace'
                  }}
                />
              </div>

              <button
                onClick={handleExtractTextFromText}
                className="btn btn-primary"
                disabled={loading}
                style={{ width: '100%' }}
              >
                {loading ? '⏳ Extraction...' : '🔓 Extraire le message'}
              </button>

              {/* Extracted message */}
              {extractedTextMessage && (
                <div style={{ marginTop: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                    ✅ Message extrait :
                  </label>
                  <div style={{
                    padding: '15px',
                    border: '2px solid #10B981',
                    borderRadius: '5px',
                    backgroundColor: '#ECFDF5',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    color: '#065F46'
                  }}>
                    "{extractedTextMessage}"
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* IMAGE STEGANOGRAPHY */}
      {activeSubTab === 'image' && (
        <div>
          {/* Mode selector */}
          <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <button
              onClick={() => setImageMode('hide')}
              className={imageMode === 'hide' ? 'btn btn-primary' : 'btn'}
              style={{ flex: 1 }}
            >
              🔒 Cacher un message
            </button>
            <button
              onClick={() => setImageMode('extract')}
              className={imageMode === 'extract' ? 'btn btn-primary' : 'btn'}
              style={{ flex: 1 }}
            >
              🔓 Extraire un message
            </button>
          </div>

          {/* Image upload */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
              {imageMode === 'hide' ? 'Image de couverture :' : 'Image stéganographiée :'}
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #D1D5DB',
                borderRadius: '5px',
                fontSize: '14px'
              }}
            />
          </div>

          {/* Image preview */}
          {imagePreview && (
            <div style={{ marginBottom: '20px', textAlign: 'center' }}>
              <img
                src={imagePreview}
                alt="Preview"
                style={{
                  maxWidth: '100%',
                  maxHeight: '300px',
                  border: '2px solid #D1D5DB',
                  borderRadius: '5px'
                }}
              />
            </div>
          )}

          {/* Image analysis */}
          {imageAnalysis && (
            <div style={{
              padding: '15px',
              backgroundColor: '#F3F4F6',
              borderRadius: '5px',
              marginBottom: '20px',
              fontSize: '13px'
            }}>
              <strong>📊 Analyse de l'image :</strong><br/>
              - Dimensions : {imageAnalysis.width} × {imageAnalysis.height} pixels<br/>
              - Pixels totaux : {imageAnalysis.total_pixels.toLocaleString()}<br/>
              - Capacité maximale : {imageAnalysis.max_capacity.toLocaleString()} caractères<br/>
              - Capacité recommandée : {imageAnalysis.recommended_capacity.toLocaleString()} caractères
            </div>
          )}

          {imageMode === 'hide' ? (
            <>
              {/* Secret message for image */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                  Message secret à cacher :
                </label>
                <textarea
                  value={imageSecretMessage}
                  onChange={(e) => setImageSecretMessage(e.target.value)}
                  placeholder="Entrez votre message secret..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #D1D5DB',
                    borderRadius: '5px',
                    fontSize: '14px'
                  }}
                />
                <small style={{ color: '#6B7280' }}>
                  {imageSecretMessage.length} caractères
                  {imageAnalysis && ` (${((imageSecretMessage.length / imageAnalysis.max_capacity) * 100).toFixed(2)}% utilisé)`}
                </small>
              </div>

              <button
                onClick={handleHideTextInImage}
                className="btn btn-primary"
                disabled={loading || !selectedImage}
                style={{ width: '100%' }}
              >
                {loading ? '⏳ Traitement...' : '🔒 Cacher dans l\'image'}
              </button>

              {/* Result image */}
              {stegoImage && (
                <div style={{ marginTop: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                    ✅ Image stéganographiée :
                  </label>
                  <div style={{ textAlign: 'center' }}>
                    <img
                      src={stegoImage}
                      alt="Stego"
                      style={{
                        maxWidth: '100%',
                        maxHeight: '300px',
                        border: '2px solid #10B981',
                        borderRadius: '5px',
                        marginBottom: '10px'
                      }}
                    />
                  </div>
                  <button
                    onClick={downloadStegoImage}
                    className="btn btn-primary"
                    style={{ width: '100%' }}
                  >
                    💾 Télécharger l'image
                  </button>
                  <small style={{ display: 'block', marginTop: '10px', color: '#6B7280', textAlign: 'center' }}>
                    💡 L'image est visuellement identique à l'originale !
                  </small>
                </div>
              )}
            </>
          ) : (
            <>
              {/* Extract mode */}
              <button
                onClick={handleExtractTextFromImage}
                className="btn btn-primary"
                disabled={loading || !selectedImage}
                style={{ width: '100%' }}
              >
                {loading ? '⏳ Extraction...' : '🔓 Extraire le message'}
              </button>

              {/* Extracted message from image */}
              {extractedImageMessage && (
                <div style={{ marginTop: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                    ✅ Message extrait :
                  </label>
                  <div style={{
                    padding: '15px',
                    border: '2px solid #10B981',
                    borderRadius: '5px',
                    backgroundColor: '#ECFDF5',
                    fontSize: '14px',
                    color: '#065F46',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word'
                  }}>
                    {extractedImageMessage}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default SteganographyPanel;
