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
  const [textShowStepsResult, setTextShowStepsResult] = useState(null);
  const [textExtractStepsResult, setTextExtractStepsResult] = useState(null);
  
  // Image steganography state
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [imageSecretMessage, setImageSecretMessage] = useState('');
  const [stegoImage, setStegoImage] = useState(null);
  const [extractedImageMessage, setExtractedImageMessage] = useState('');
  const [imageAnalysis, setImageAnalysis] = useState(null);
  const [imageLSBInfo, setImageLSBInfo] = useState(null);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  // Helper: resize image client-side to limit max dimension and reduce payload size
  const resizeImageFileToBase64 = (file, maxDim = 2048) => new Promise((resolve, reject) => {
    try {
      const img = new Image();
      const reader = new FileReader();
      reader.onload = (e) => {
        img.onload = () => {
          let { width, height } = img;
          const scale = Math.min(1, maxDim / Math.max(width, height));
          const newW = Math.round(width * scale);
          const newH = Math.round(height * scale);
          const canvas = document.createElement('canvas');
          canvas.width = newW;
          canvas.height = newH;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, newW, newH);
          const dataUrl = canvas.toDataURL('image/png');
          const base64 = dataUrl.split(',')[1];
          resolve({ base64, newW, newH, resized: scale < 1 });
        };
        img.onerror = (err) => reject(err);
        img.src = e.target.result;
      };
      reader.onerror = (err) => reject(err);
      reader.readAsDataURL(file);
    } catch (e) {
      reject(e);
    }
  });

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

  const handleShowTextSteps = async () => {
    if (!coverText.trim() || !secretMessage.trim()) {
      setMessage({ type: 'error', text: 'Veuillez remplir cover_text et secret_message' });
      return;
    }
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch('http://localhost:8000/api/stego/text/show-steps/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cover_text: coverText, secret_message: secretMessage, method: textMethod })
      });
      const data = await response.json();
      if (response.ok) {
        setTextShowStepsResult(data);
        // also set stego text for convenience
        if (data.trace && data.trace.stego_text) setStegoText(data.trace.stego_text);
        setMessage({ type: 'success', text: 'Étapes générées — voir la section détails ci-dessous.' });
      } else {
        setMessage({ type: 'error', text: data.error || 'Erreur serveur' });
      }
    } catch (e) {
      setMessage({ type: 'error', text: 'Erreur de connexion au serveur' });
    } finally {
      setLoading(false);
    }
  };

  const handleExtractTextSteps = async () => {
    if (!stegoText.trim()) {
      setMessage({ type: 'error', text: 'Veuillez entrer un texte stéganographié' });
      return;
    }
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch('http://localhost:8000/api/stego/text/extract-steps/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stego_text: stegoText, method: textMethod })
      });
      const data = await response.json();
      if (response.ok) {
        setTextExtractStepsResult(data);
        setMessage({ type: 'success', text: 'Étapes d\'extraction générées — voir la section détails ci-dessous.' });
      } else {
        setMessage({ type: 'error', text: data.error || 'Erreur serveur' });
      }
    } catch (e) {
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
      // Use object URL for lightweight preview
      try {
        const objUrl = URL.createObjectURL(file);
        setImagePreview(objUrl);
      } catch (_) {
        const reader = new FileReader();
        reader.onload = (ev) => setImagePreview(ev.target.result);
        reader.readAsDataURL(file);
      }
      
      // Auto analyze
      analyzeImage(file);
    }
  };

  const analyzeImage = async (file) => {
    try {
      const { base64 } = await resizeImageFileToBase64(file, 2048);
      const response = await fetch('http://localhost:8000/api/stego/analyze/image/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_data: base64 })
      });
      const data = await response.json();
      if (response.ok) {
        // Normalize keys to what UI expects
        setImageAnalysis({
          width: data.width,
          height: data.height,
          total_pixels: data.total_pixels,
          max_capacity: data.max_characters,
          recommended_capacity: data.recommended_message_length
        });
      }
    } catch (error) {
      console.error('Erreur analyse:', error);
    }
  };

  const handleHideTextInImage = async () => {
    if (!selectedImage || !imageSecretMessage.trim()) {
      setMessage({ type: 'error', text: 'Veuillez sélectionner une image et entrer un message' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const { base64, resized, newW, newH } = await resizeImageFileToBase64(selectedImage, 2048);
      const response = await fetch('http://localhost:8000/api/stego/image/hide/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_data: base64,
          secret_message: imageSecretMessage,
          method: 'lsb',
          auto_resize: true
        })
      });

      const data = await response.json();

      if (response.ok) {
        setStegoImage('data:image/png;base64,' + data.stego_image);
        const resizedInfo = data.resized ? ` (redimensionnée serveur: ${data.original_size} → ${data.new_size})` : (resized ? ` (redimensionnée client: ${newW}x${newH})` : '');
        setMessage({ 
          type: 'success', 
          text: `✅ Message caché dans l'image ! (${data.message_length} caractères, ${data.usage_percent}% utilisé)${resizedInfo}` 
        });
        // visualize LSB plane from returned stego image
        if (data.stego_image) {
          visualizeLSBFromBase64(data.stego_image);
        }
      } else {
        setMessage({ type: 'error', text: data.error || 'Erreur lors du traitement' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Erreur de traitement de l\'image' });
    } finally {
      setLoading(false);
    }
  };

  const visualizeLSBFromBase64 = (base64) => {
    // create image and canvas, then read pixels and extract LSBs for R,G,B
    try {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        const imageData = ctx.getImageData(0, 0, img.width, img.height);
        const data = imageData.data;
        const w = img.width;
        const h = img.height;
        // Build small preview matrix (limit size to avoid huge payload)
        const maxPreview = 64;
        const previewW = Math.min(w, maxPreview);
        const previewH = Math.min(h, maxPreview);
        const matrix = [];
        let bitsFlat = '';
        for (let y = 0; y < previewH; y++) {
          const row = [];
          for (let x = 0; x < previewW; x++) {
            const idx = (y * w + x) * 4;
            const r = data[idx];
            const g = data[idx+1];
            const b = data[idx+2];
            // LSB of R,G,B
            const rb = r & 1;
            const gb = g & 1;
            const bb = b & 1;
            // store as string 'r,g,b'
            row.push([rb, gb, bb]);
            bitsFlat += rb.toString() + gb.toString() + bb.toString();
          }
          matrix.push(row);
        }
        setImageLSBInfo({ width: w, height: h, previewW, previewH, matrix, bitsSample: bitsFlat.slice(0, 512) });
      };
      img.onerror = () => {};
      img.src = 'data:image/png;base64,' + base64;
    } catch (e) {
      console.error('visualizeLSB error', e);
    }
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

              <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
                <button
                  onClick={handleShowTextSteps}
                  className="btn btn-secondary"
                  disabled={loading}
                  style={{ flex: 1 }}
                >
                  📋 Montrer toutes les étapes (encodage)
                </button>
                <button
                  onClick={handleHideTextInText}
                  className="btn btn-primary"
                  disabled={loading}
                  style={{ flex: 1 }}
                >
                  {loading ? '⏳ Traitement...' : '🔒 Cacher le message'}
                </button>
              </div>

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

              {/* Detailed encoding trace (from backend) */}
              {textShowStepsResult && (
                <div style={{ marginTop: 16, background: '#F8FAFC', padding: 12, borderRadius: 6 }}>
                  <h4>Étapes d'encodage (détaillé)</h4>
                  <p><strong>Bits ({textShowStepsResult.trace.bits.length}):</strong></p>
                  <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', maxHeight: 180, overflow: 'auto' }}>{textShowStepsResult.trace.bits}</pre>
                  <p><strong>Emplacements disponibles:</strong> {textShowStepsResult.trace.available_slots} — <strong>utilisés:</strong> {textShowStepsResult.trace.used_slots}</p>
                  <p><strong>Stego text (aperçu):</strong></p>
                  <textarea readOnly value={textShowStepsResult.trace.stego_text} style={{ width: '100%', minHeight: 120 }} />
                  <h5>Simulation d'extraction</h5>
                  <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(textShowStepsResult.extraction_simulation, null, 2)}</pre>
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

              <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
                <button
                  onClick={handleExtractTextFromText}
                  className="btn btn-primary"
                  disabled={loading}
                  style={{ flex: 1 }}
                >
                  {loading ? '⏳ Extraction...' : '🔓 Extraire le message'}
                </button>
                <button
                  onClick={handleExtractTextSteps}
                  className="btn btn-secondary"
                  disabled={loading}
                  style={{ flex: 1 }}
                >
                  📋 Montrer étapes d'extraction
                </button>
              </div>

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
              {textExtractStepsResult && (
                <div style={{ marginTop: 16, background: '#F8FAFC', padding: 12, borderRadius: 6 }}>
                  <h4>Étapes d'extraction (détaillé)</h4>
                  <p><strong>Bits extraits:</strong></p>
                  <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', maxHeight: 160, overflow: 'auto' }}>{textExtractStepsResult.trace.bits}</pre>
                  <p><strong>Décodage (tentative):</strong> {textExtractStepsResult.trace.decoded}</p>
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
                  <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                    <button
                      onClick={() => {
                        if (stegoImage) {
                          const base64 = stegoImage.split(',')[1];
                          visualizeLSBFromBase64(base64);
                        } else if (selectedImage) {
                          const reader = new FileReader();
                          reader.onload = (e) => visualizeLSBFromBase64(e.target.result.split(',')[1]);
                          reader.readAsDataURL(selectedImage);
                        } else {
                          setMessage({ type: 'error', text: 'Aucune image disponible à visualiser' });
                        }
                      }}
                      className="btn btn-secondary"
                      style={{ flex: 1 }}
                    >
                      🧮 Montrer matrice LSB & bits (aperçu)
                    </button>
                    <button
                      onClick={() => { if (stegoImage) navigator.clipboard.writeText(stegoImage); setMessage({ type: 'success', text: 'Image base64 copiée' }); }}
                      className="btn"
                      style={{ flex: 1 }}
                    >
                      📋 Copier base64
                    </button>
                  </div>

                  {imageLSBInfo && (
                    <div style={{ marginTop: 16, background: '#F8FAFC', padding: 12, borderRadius: 6 }}>
                      <h4>Visualisation LSB (aperçu)</h4>
                      <p>Image: {imageLSBInfo.width}×{imageLSBInfo.height} — aperçu {imageLSBInfo.previewW}×{imageLSBInfo.previewH}</p>
                      <p><strong>Bits extrait (échantillon):</strong></p>
                      <pre style={{ maxHeight: 120, overflow: 'auto' }}>{imageLSBInfo.bitsSample}</pre>
                      <p><strong>Matrice R,G,B (aperçu):</strong></p>
                      <div style={{ overflow: 'auto', maxHeight: 320 }}>
                        <table style={{ borderCollapse: 'collapse', fontSize: 11 }}>
                          <tbody>
                            {imageLSBInfo.matrix.map((row, yi) => (
                              <tr key={yi}>
                                {row.map((cell, xi) => (
                                  <td key={xi} style={{ padding: 1, border: '1px solid #e5e7eb' }}>
                                    <span style={{ fontFamily: 'monospace' }}>{cell.join(',')}</span>
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
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
