# Crypto Lab - Password Attack Simulator

A Django-based web application for simulating cryptographic attacks on classical ciphers (Caesar, Affine, Playfair, Hill). Built with Bootstrap 5 and vanilla JavaScript for an interactive user experience.

See also: docs/features_attack_protection_stego_mitm_messaging.md for a full tour of Attacks, Protections, Steganography, Messaging, and the MITM demo.

## 🚀 Features

- **User Management**: Register and login with encrypted passwords
- **Multiple Cipher Algorithms**: 
  - Caesar Cipher
  - Affine Cipher
  - Playfair Cipher
  - Hill Cipher (3×3)
- **Attack Modes**:
  - Brute Force Attack
  - Dictionary Attack
- **Modern UI**: Bootstrap 5 with responsive design
- **Real-time Results**: Ajax-based API calls with instant feedback
- **Safety Controls**: Only test accounts can be attacked

## 📋 Requirements

- Python 3.8+
- Django 5.2.7
- NumPy (for matrix operations)

## 🔧 Installation

1. Clonez le dépôt (ou placez-vous dans le répertoire du projet) :

```powershell
cd C:\Users\j\OneDrive\Desktop\ssad\tp
```

2. Créez et activez un environnement virtuel (recommandé) :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Installez les dépendances depuis `requirements.txt` :

```powershell
pip install -r requirements.txt
# Si vous n'avez pas encore de requirements.txt :
pip install django numpy Pillow
```

4. Appliquez les migrations Django :

```powershell
python manage.py migrate
```

5. Démarrez le serveur de développement :

```powershell
python manage.py runserver
```

6. Accédez à l'application

- Ouvrez votre navigateur à : http://127.0.0.1:8000/

7. (Optionnel) Si vous développez le frontend local (`frontend/`) :

```powershell
cd frontend
npm install
npm run dev
```

## 📖 Usage

### Web Interface
cd tp/frontend

1. **Install dependencies**
``` open another bash 
npm install 
```

2. **Start the development server**
```bash
npm run dev
```

The main interface is accessible at `http://127.0.0.1:8000/` and includes:

1. **User Registration**
   - Create users with different encryption algorithms
   - Specify encryption keys (shift, coefficients, keywords)
   - Use `test_*`, `demo_*`, or `tmp_*` prefix for attack testing

2. **User Login**
   - Authenticate using username and password
   - System decrypts and validates credentials

3. **User Lookup**
   - View encrypted password and key data
   - Useful for verification before attacks

4. **Brute Force Attack**
   - Try all possible keys for Caesar/Affine
   - Requires keyspace for Playfair
   - Set limits (attempts, timeout)

5. **Dictionary Attack**
   - Test passwords from a wordlist
   - Works with stored encryption keys
   - Faster than brute force for common passwords

### API Endpoints

All API endpoints are available under `/api/`:

#### Register User
```bash
POST /api/regester/
Content-Type: application/json

{
  "username": "test_alice",
  "password": "SECRET",
  "algorithm": "caesar",
  "key": {"shift": 3}
}
```

#### Login
```bash
POST /api/login/
Content-Type: application/json

{
  "username": "test_alice",
  "password": "SECRET"
}
```

#### Get User Info
```bash
GET /api/user/test_alice/
```

#### Brute Force Attack
```bash
POST /api/attack/full_bruteforce/
Content-Type: application/json

{
  "target_username": "test_alice",
  "mode": "bruteforce",
  "algorithm": "caesar",
  "limit": 1000,
  "max_seconds": 10
}
```

#### Dictionary Attack
```bash
POST /api/attack/full_dictionary/
Content-Type: application/json

{
  "target_username": "test_alice",
  "mode": "dictionary",
  "dictionary": ["PASSWORD", "SECRET", "HELLO"],
  "limit": 0,
  "max_seconds": 30
}
```

## 🔐 Security & Safety

### Test User Requirements

The attack runner enforces safety rules:

1. **test_users.txt**: Create this file in the project root with allowed test usernames (one per line)
2. **Username Prefixes**: If no test_users.txt exists, only usernames starting with `test_`, `demo_`, or `tmp_` can be attacked
3. **Purpose**: Prevents accidental attacks on production/real user accounts

### Example test_users.txt
```
test_alice
test_bob
demo_user
```

## 🎯 Attack Configuration

### Caesar Cipher
- **Keyspace**: 26 shifts (0-25)
- **Brute Force**: Very fast (~26 attempts)
- **Key Format**: `{"shift": 3}`

### Affine Cipher
- **Keyspace**: 12 valid 'a' values × 26 'b' values = 312 combinations
- **Brute Force**: Fast (~312 attempts)
- **Key Format**: `{"a": 5, "b": 8}`
- **Note**: 'a' must be coprime with 26

### Playfair Cipher
- **Keyspace**: User-provided keywords only (full permutation space infeasible)
- **Brute Force**: Requires `playfair_keyspace` parameter
- **Key Format**: `{"keyword": "MONARCHY"}`

### Hill Cipher
- **Keyspace**: 26^4 = 456,976 matrices (2×2) or uses keyword for 3×3
- **Brute Force**: Can be slow; use limits
- **Key Format**: `{"keyword": "HILLCIPHER"}` or `{"matrix": [[a,b],[c,d]]}`

## 📊 Attack Response Format

```json
{
  "target_username": "test_alice",
  "algorithm": "caesar",
  "mode": "bruteforce",
  "attempts": 26,
  "time_sec": 0.002,
  "limit_reached": false,
  "timeout_reached": false,
  "matches_count": 1,
  "matches": [
    {
      "candidate_plaintext": "SECRET",
      "candidate_key": {"shift": 3},
      "confidence": "high",
      "notes": "Alphabetic candidate"
    }
  ],
  "notes": ""
}
```

### Confidence Levels
- **high**: Plaintext matches dictionary word
- **medium**: Dictionary encryption matched
- **low**: Alphabetic candidate (length ≥ 3)

## 🎨 Frontend Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Feedback**: Loading spinners and instant results
- **Color-coded Results**: Easy identification of match confidence
- **Tabbed Interface**: Organized attack options
- **Form Validation**: Client-side checks before API calls

## 📁 Project Structure

```
ssad_tp1/
├── manage.py
├── db.sqlite3
├── test_users.txt                    # Safety whitelist
├── core/                             # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── crypto_lab/                       # Main Django app
│   ├── models.py                     # CustomUser model
│   ├── views.py                      # API endpoints + index view
│   ├── urls.py                       # URL routing
│   ├── templates/
│   │   └── crypto_lab/
│   │       └── index.html            # Main interface
│   └── static/
│       └── crypto_lab/
│           ├── css/
│           │   └── style.css         # Custom styles
│           └── js/
│               └── app.js            # Frontend logic
└── backend/
    └── cryptotoolbox/
        ├── __init__.py               # Encryption utilities
        ├── cyphers/
        │   ├── cesar.py
        │   ├── affine.py
        │   ├── plaiyfair.py
        │   └── hill.py
        └── attack/
            └── attack_runner.py      # Core attack engine
```

## 🧪 Testing

### Quick Test Scenario

1. **Register a test user**:
   - Username: `test_alice`
   - Password: `SECRET`
   - Algorithm: Caesar
   - Shift: 3

2. **Run brute force**:
   - Target: `test_alice`
   - Limit: 100
   - Max seconds: 10

3. **Expected Result**:
   - 26 attempts
   - 1 match found
   - Plaintext: `SECRET`
   - Key: `{"shift": 3}`
   - Confidence: high

### Using curl

```bash
# 1. Register user
curl -X POST http://127.0.0.1:8000/api/regester/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test_alice","password":"SECRET","algorithm":"caesar","key":{"shift":3}}'

# 2. Lookup user
curl http://127.0.0.1:8000/api/user/test_alice/

# 3. Run attack
curl -X POST http://127.0.0.1:8000/api/attack/full_bruteforce/ \
  -H "Content-Type: application/json" \
  -d '{"target_username":"test_alice","limit":100,"max_seconds":10}'
```

## ⚠️ Known Issues

- The original `full_brutforce` view has bugs (typos, undefined variables)
- New clean API endpoints bypass those issues
- Some cipher implementations have minor bugs (e.g., `cesar.py` has early returns in loops)
- The attack runner includes corrected implementations

## 🔮 Future Enhancements

- [ ] Progress streaming for long-running attacks
- [ ] Export results to CSV/JSON
- [ ] Visualization of keyspace coverage
- [ ] More cipher algorithms (Vigenère, RSA)
- [ ] Multi-threaded brute force
- [ ] Rate limiting and API authentication
- [ ] Admin dashboard for user management

## 📝 License

Educational use only. This tool is designed for learning about cryptographic vulnerabilities in classical ciphers.

## 🤝 Contributing

This is an educational project. Feel free to extend it with:
- Additional cipher algorithms
- More sophisticated attack strategies
- Performance optimizations
- Better visualization tools

## 📧 Support

For issues or questions, refer to the code comments or Django documentation.

---

**Remember**: Only attack systems you own or have explicit permission to test. This tool is for educational purposes only.
