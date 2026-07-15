#!/bin/bash

# Nettoyer
rm -rf _build/

# Construction française
sphinx-build -b html -D language='fr' . _build/html/fr/

# Construction anglaise
sphinx-build -b html -D language='en' . _build/html/en/

# Créer une page d'accueil avec choix de langue
cat > _build/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BsplineQuantRegpy Documentation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: #f5f5f5;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        .lang-btn {
            display: inline-block;
            padding: 15px 40px;
            margin: 10px;
            background: #2980b9;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 18px;
        }
        .lang-btn:hover { background: #3498db; }
        .lang-btn.fr { background: #27ae60; }
        .lang-btn.fr:hover { background: #2ecc71; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 BsplineQuantRegpy Documentation</h1>
        <p>Choose your language / Choisissez votre langue</p>
        <br>
        <a href="en/index.html" class="lang-btn">🇬🇧 English</a>
        <a href="fr/index.html" class="lang-btn fr">🇫🇷 Français</a>
    </div>
</body>
</html>
EOF

echo "✅ Documentation build complete!"
echo "   - French: _build/html/fr/index.html"
echo "   - English: _build/html/en/index.html"
echo "   - Language selector: _build/html/index.html"