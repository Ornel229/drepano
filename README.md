# Résultats de porteur (Hack2Skill)

Assistant web sur la **consanguinité et les maladies héréditaires** : il explique ce que change un lien de parenté entre partenaires (cousins, etc.) et, avec l'exemple de la drépanocytose, les résultats de porteur : explication des risques pour les enfants, arbre généalogique, calendrier des grossesses, fiche de consultation en PDF et assistant de discussion. Français et anglais.

**Application en ligne :** https://juniorb573.github.io/H2Skill/

> Cet outil informe, il ne remplace pas un conseil génétique. Il ne pose aucun diagnostic.

## Alignement avec le défi (consanguinité et maladies héréditaires)

| Attente du défi | Réponse de l'outil |
|---|---|
| Comprendre les risques liés à la consanguinité | Bloc « Pourquoi le lien de parenté compte » : part de gènes partagée, risque d'enfant atteint comparé à un couple non apparenté, pour une maladie fréquente et une maladie rare |
| Individus, familles, systèmes de santé | Parcours couple, arbre de famille (ancêtres communs), fiche PDF pour la consultation et appel au dépistage élargi des porteurs |
| Technologie culturellement adaptée | Ton sans jugement ni stigmatisation, aucun choix familial recommandé, français et anglais, lecture à voix haute |
| Respect de la vie privée | Aucune donnée enregistrée, aucun nom ; la parenté reste dans le navigateur (seul un code est envoyé au service d'IA s'il est activé) |

Méthode de calcul (simplifiée, pédagogique) : `r` = part de gènes partagée (cousins germains 1/8, cousins issus de germains 1/32, oncle-nièce 1/4). Si l'un des partenaires porte une variante, l'autre la porte avec la probabilité `r + (1 − r) × c` (`c` = fréquence des porteurs : 1/5 maladie fréquente, 1/100 maladie rare) ; le risque d'enfant atteint est ce nombre divisé par 4.

## Comment les pièces s'assemblent

```
Navigateur (GitHub Pages)                Service d'IA (optionnel)           Modèle
index.html  ── question, génotypes ──▶  worker/worker.js (Cloudflare)  ──▶  API Anthropic
  │  ◀── réponse contrôlée ───────────   calcule les risques, contrôle
  │                                      les entrées et les réponses
  └─ sans service d'IA : réponses préparées dans le navigateur
```

- **Le site** (`index.html`) fonctionne seul. L'assistant répond alors avec des réponses préparées.
- **Le service d'IA** (`worker/`) ajoute des réponses libres, encadrées. S'il est absent ou en erreur, le site revient aux réponses préparées.
- **Le prototype Streamlit** (fichiers Python à la racine) est la version initiale en Python, avec explication par IA validée par un garde-fou.

## Contenu du dépôt

| Fichier ou dossier | Rôle |
|---|---|
| `index.html` | Application web complète (HTML, CSS, JavaScript dans un seul fichier), publiée par GitHub Pages. |
| `worker/worker.js` | Service de l'assistant IA (Cloudflare Worker). Calcule les risques, détecte les urgences, appelle le modèle, contrôle la réponse. |
| `worker/wrangler.toml`, `package.json`, `.dev.vars.example` | Configuration et déploiement du service. |
| `worker/tests/worker.test.mjs` | 12 tests du service (génétique, parenté, urgences, garde-fou, origine, limite de débit, erreurs). |
| `app.py` | Prototype Streamlit (interface Python). |
| `genetique.py`, `textes.py`, `llm.py` | Moteur génétique, textes français et anglais avec quiz, appel au modèle d'IA. |
| `arbre.py`, `calendrier.py`, `fiche.py` | Arbre généalogique, risque cumulé, fiche de consultation. |
| `ai_explain.py`, `textes_ext.py` | Explication par IA avec garde-fou, textes des sections ajoutées. |
| `verif_modules.py`, `verif_projet.py` | Vérifications des modules Python. |
| `docs/Resultats_de_porteur_fonctionnalites.pdf` | Présentation PDF de toutes les fonctionnalités. |
| `.github/workflows/tests.yml` | Lance les vérifications à chaque envoi sur GitHub. |
| `.streamlit/secrets.toml.example`, `requirements.txt`, `.gitignore` | Configuration du prototype et fichiers à ne pas publier. |

`genetique.py`, `textes.py` et `llm.py` sont des versions recréées à partir de la façon dont `app.py` les utilise. Si vous avez déjà vos propres versions, gardez-les. De même, si votre service d'IA actuel fonctionne déjà, vous pouvez le garder à la place de `worker/worker.js`.

## 1. Publier le site (GitHub Pages)

1. Déposez le contenu de ce zip à la racine du dépôt H2Skill (`index.html` doit être à la racine).
2. Dans **Settings → Pages**, choisissez la branche `main` et le dossier `/ (root)`.
3. Attendez environ une minute, puis ouvrez le lien ci-dessus (Ctrl+Maj+R pour vider le cache).

## 2. Activer l'assistant IA (Cloudflare Worker)

Il faut un compte Cloudflare (l'offre gratuite suffit pour un prototype), Node.js 18 ou plus récent, et une clé d'API Anthropic (service payant à l'usage).

```
cd worker
npx wrangler login
npx wrangler secret put ANTHROPIC_API_KEY     # collez votre clé quand elle est demandée
npx wrangler deploy
```

1. Wrangler affiche l'adresse du service, par exemple `https://assistant.votre-sous-domaine.workers.dev`.
2. Si elle diffère de celle de la constante `AI_ENDPOINT` dans `index.html`, remplacez-la, puis publiez à nouveau le fichier.
3. Dans `worker/wrangler.toml`, `ALLOWED_ORIGINS` doit contenir l'adresse de votre site (déjà `https://juniorb573.github.io`). Le service refuse les autres origines.
4. Testez le service :

```
curl -s https://assistant.votre-sous-domaine.workers.dev \
  -H "Origin: https://juniorb573.github.io" -H "Content-Type: application/json" \
  -d '{"q":"Quel est notre risque ?","g1":"AS","g2":"AS","lang":"fr","h":[]}'
```

La réponse est de la forme `{"answer":"...","kind":"ok"}`. Sur le site, le bandeau de l'assistant passe de « Réponses préparées » à « IA encadrée ».

Réglages dans `wrangler.toml` : `MODEL` (modèle utilisé) et `RATE_LIMIT_PER_MIN` (demandes par minute et par adresse IP, 20 par défaut). Cette limite est propre à chaque instance du service : pour une limite stricte, ajoutez une règle de limitation dans le tableau de bord Cloudflare.

### Garde-fous du service

- Les pourcentages sont calculés par le code du service. Le modèle explique, il ne calcule pas.
- Les urgences (douleur, fièvre, difficulté à respirer) reçoivent un message fixe, sans appel au modèle.
- Les entrées sont validées : question de 400 caractères au plus, génotypes connus, 4 échanges d'historique au plus.
- Le texte de l'utilisateur et l'historique sont traités comme des données, jamais comme des instructions.
- Les réponses du modèle qui contiennent un diagnostic (« vous avez… », « votre enfant sera… ») ou une dose sont remplacées par un message sûr.
- Rien n'est enregistré : ni question, ni génotype, ni réponse.
- La clé d'API reste dans un secret Cloudflare. Elle n'apparaît jamais dans le dépôt ni dans le navigateur.

## 3. Lancer le prototype Streamlit

```
pip install -r requirements.txt
streamlit run app.py
```

Pour activer l'explication par IA, copiez `.streamlit/secrets.toml.example` en `.streamlit/secrets.toml` et renseignez la clé, ou définissez la variable d'environnement `ANTHROPIC_API_KEY`. Sans clé, l'application affiche un texte standard.

## 4. Vérifier

```
python verif_modules.py && python verif_projet.py     # modules Python
cd worker && node --test                              # service de l'assistant
```

## Vie privée

Par défaut, aucune donnée n'est enregistrée ni envoyée : tout reste dans le navigateur et disparaît à la fermeture de la page. Si le service d'IA est activé, seuls les génotypes choisis, la question et les quatre derniers échanges sont envoyés, sans nom ni identifiant, et ne sont pas conservés.
