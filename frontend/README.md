# Frontend React - Crypto Lab

Application React moderne pour le TP SSAD de cryptographie classique.

## 🚀 Démarrage Rapide

### 1. Installer les dépendances
```bash
npm install
```

### 2. Lancer le serveur de développement
```bash
npm run dev
```

L'application sera accessible sur: http://localhost:3000

### 3. Build de production
```bash
npm run build
```

## 📁 Structure du Projet

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx          # En-tête de l'application
│   │   ├── RegisterForm.jsx    # Formulaire d'inscription
│   │   ├── LoginForm.jsx       # Formulaire de connexion
│   │   └── AttackPanel.jsx     # Panel d'attaques
│   ├── services/
│   │   └── api.js              # Services API axios
│   ├── App.jsx                 # Composant principal
│   ├── main.jsx                # Point d'entrée
│   └── index.css               # Styles globaux
├── public/                     # Assets statiques
├── index.html                  # HTML principal
├── vite.config.js              # Configuration Vite
└── package.json                # Dépendances npm
```

## 🛠️ Technologies

- **React 18**: Bibliothèque UI
- **Vite**: Build tool moderne et rapide
- **Axios**: Client HTTP pour API calls
- **CSS personnalisé**: Design moderne sans framework lourd

## 🔌 Configuration API

Le proxy Vite redirige automatiquement les requêtes `/api` vers Django (http://127.0.0.1:8000).

Configuration dans `vite.config.js`:
```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    }
  }
}
```

## 📡 Endpoints API Utilisés

### Authentification
- `POST /api/regester/` - Inscription utilisateur
- `POST /api/login/` - Connexion utilisateur
- `GET /api/user/<username>/` - Informations utilisateur

### Attaques
- `POST /api/attack/bruteforce/` - Attaque force brute
- `POST /api/attack/dictionary/` - Attaque dictionnaire
- `POST /api/attack/combined/` - Attaque combinée
- `GET /api/attack/statistics/` - Statistiques attaques

## 🎨 Fonctionnalités

### Onglet Inscription
- Formulaire d'inscription avec choix d'algorithme
- Sélection automatique des paramètres par défaut
- Validation en temps réel
- Messages de succès/erreur

### Onglet Connexion
- Authentification avec déchiffrement
- Guide des algorithmes supportés
- Feedback immédiat

### Onglet Attaques
- 3 types d'attaques: Dictionnaire, Force Brute, Combinée
- Affichage en temps réel des résultats
- Statistiques détaillées (temps, tentatives, vitesse)
- Sauvegarde automatique des résultats

### Onglet À Propos
- Informations sur le projet
- Technologies utilisées
- Guide complet

## 🔧 Développement

### Lancer en mode développement
```bash
npm run dev
```
Hot reload activé - les changements sont appliqués automatiquement.

### Linter
```bash
npm run lint
```

### Preview du build
```bash
npm run build
npm run preview
```

## 🚨 Prérequis

- Node.js >= 16
- npm >= 8
- Backend Django en cours d'exécution sur http://127.0.0.1:8000

## 📝 Notes

- Le serveur Django doit être lancé **avant** le frontend React
- CORS est configuré dans Django (`settings.py`)
- Les tokens CSRF sont gérés automatiquement par Django

## 🔗 Liens Utiles

- Documentation React: https://react.dev
- Documentation Vite: https://vitejs.dev
- Documentation Axios: https://axios-http.com

## 🎓 Projet Académique

**TP SSAD - USTHB**  
Système de Sécurité et d'Aide à la Décision  
Réalisation d'une boîte d'outils de cryptographie classique
