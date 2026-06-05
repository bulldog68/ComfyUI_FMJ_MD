# 🌀FMJ Smart Model Manager

Gestionnaire intelligent de téléchargement de modèles pour ComfyUI avec profils JSON dynamiques et mise à jour automatique.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Créer un profil JSON](#-créer-un-profil-json)
- [Exemples de profils](#-exemples-de-profils)
- [Actions disponibles](#-actions-disponibles)
- [FAQ](#-faq)

---

## ✨ Fonctionnalités

- 📊 **Vérification automatique** : Identifie instantanément les modèles manquants.
- ⬇️ **Téléchargement intelligent** : Téléchargement individuel ou en masse avec barre de progression native.
- 📁 **Profils multiples** : Gérez différents workflows avec des fichiers JSON séparés.
- 🔄 **Mise à jour dynamique** : Changement de profil sans redémarrage de ComfyUI.
- ✅ **Validation automatique** : Crée les dossiers manquants et vérifie l'intégrité.
- 📈 **Rapports détaillés** : Suivi en temps réel des opérations dans l'interface.
- 🎯 **Menu contextuel** : Sélection rapide des modèles par clic droit sur le node.

---

## 📦 Installation

### Méthode 1 : Installation manuelle

1. Clonez le repository dans `ComfyUI/custom_nodes/` :
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/bulldog68/ComfyUI_FMJ_MD.git
```
2. Redémarrez ComfyUI.

### Méthode 2 : Via ComfyUI Manager
1. Ouvrez **ComfyUI Manager** > **Install Custom Nodes**.
2. Recherchez **"FMJ Smart Model Manager"**.
3. Cliquez sur **Install** et redémarrez ComfyUI.

---

## 🎯 Utilisation

### Interface du node

| Paramètre | Type | Description |
|-----------|------|-------------|
| **json_profile** | Menu déroulant | Sélectionnez le profil JSON à utiliser. |
| **action** | Menu déroulant | Choisissez l'action à effectuer (Vérifier, Télécharger 1, Télécharger tous). |
| **model_name** | Champ texte | Nom du modèle. **Faites un clic droit sur le node** pour voir la liste complète. |
| **force_redownload** | Checkbox | Force le téléchargement même si le fichier existe déjà. |

### Workflow typique

#### 1️ Vérification initiale
- `json_profile`: "SDXL_Workflow.json"
- `action`: "🔍 1. Vérifier les manquants"
- Cliquez sur **Queue Prompt** → Le rapport s'affiche dans la sortie.

#### 2️ Téléchargement en masse
- `json_profile`: "SDXL_Workflow.json"
- `action`: "⬇️⬇️ 3. Télécharger TOUS les manquants"
- Le node télécharge automatiquement tous les modèles absents en une seule opération.

---

## 📝 Créer un profil JSON

Créez un fichier `.json` dans le dossier `ComfyUI_FMJ_MD/json_lists/`.

### Structure de base
```json
{
    "Nom_du_Modele_1": {
        "url": "https://huggingface.co/user/repo/resolve/main/model.safetensors",
        "folder": "checkpoints"
    },
    "Nom_du_Modele_2": {
        "url": "https://civitai.com/api/download/models/12345",
        "folder": "loras/SDXL"
    }
}
```

### Dossiers supportés
`checkpoints`, `loras`, `vae`, `controlnet`, `clip`, `unet`, `upscale_models`, `embeddings`, `diffusers`.

*Astuce : Vous pouvez créer des sous-dossiers (ex: `"folder": "loras/SDXL/Realistic"`).*

---

## 💡 Exemples de profils

### Profil SDXL complet (`SDXL_Workflow.json`)
```json
{
    "SDXL_Base_1.0": {
        "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
        "folder": "checkpoints"
    },
    "SDXL_Refiner_1.0": {
        "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors",
        "folder": "checkpoints"
    },
    "Add_Detail_LoRA": {
        "url": "https://huggingface.co/vladmandic/sd-models/resolve/main/add_detail.safetensors",
        "folder": "loras"
    }
}
```

### Profil Flux (`Flux_Workflow.json`)
```json
{
    "Flux1_Dev": {
        "url": "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors",
        "folder": "unet"
    },
    "Flux_AE": {
        "url": "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors",
        "folder": "vae"
    },
    "Flux_Clip_L": {
        "url": "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors",
        "folder": "clip"
    }
}
```

---

## 🎬 Actions disponibles

### 🔍 Action 1 : Vérifier les manquants

**Description** : Analyse tous les modèles du profil et affiche un rapport détaillé

**Sortie** :
- ✅ Liste des modèles présents
- ❌ Liste des modèles manquants
- 📊 Statistiques complètes

### ⬇️ Action 2 : Télécharger le modèle sélectionné

**Description** : Télécharge un modèle spécifique

**Paramètres** :
- `model_name` : Nom exact du modèle (clic droit pour voir la liste)
- `force_redownload` : Cochez pour écraser un modèle existant

**Sortie** :
- ✅ Confirmation de téléchargement réussi
-  Chemin complet du fichier
- 💾 Taille du fichier téléchargé

### ⬇️️ Action 3 : Télécharger TOUS les manquants

**Description** : Télécharge automatiquement tous les modèles manquants

**Avantages** :
-  Rapide et efficace
- 📊 Rapport détaillé pour chaque modèle
- 🔄 Continue même en cas d'erreur sur un modèle
- 💾 Nettoie les fichiers corrompus

---

## ❓ FAQ

### Le node ne détecte pas mes fichiers JSON
1. Vérifiez que les fichiers sont bien dans `ComfyUI_FMJ_MD/json_lists/`.
2. Assurez-vous que l'extension est bien `.json` (minuscules).
3. Validez la syntaxe JSON sur [JSONLint](https://jsonlint.com/).

### Comment obtenir l'URL de téléchargement ?
- **HuggingFace** : Page du modèle > "Files and versions" > Clic droit sur le fichier > "Copy link address".
- **Civitai** : Utilisez l'URL de téléchargement direct (bouton Download > Copy download URL).

### Un téléchargement échoue
Vérifiez :
- ✅ Votre connexion internet
- ✅ L'URL (testez-la dans un navigateur)
- ✅ L'espace disque disponible
- ✅ Les permissions d'écriture sur le dossier ComfyUI

### Le champ model_name ne se met pas à jour
Changez de `json_profile`, attendez 1 seconde, puis faites un **clic droit sur le node**. La liste des modèles disponibles apparaîtra dans le menu contextuel.

### Puis-je utiliser des liens Civitai ?
Oui, mais utilisez les URLs de téléchargement direct. Certains modèles nécessitent une authentification.

---

## 🐛 Debug

### Activer les logs détaillés

Lancez ComfyUI depuis un terminal :
```bash
cd ComfyUI
python main.py
```

Les messages `[FMJ]` apparaissent pour chaque opération :
```text
[FMJ] Mise à jour pour: SDXL_Workflow.json
[FMJ] ✅ 21 modèles chargés
[FMJ] Téléchargement de 'SDXL_Base_1.0'...
[FMJ] ✅ Téléchargement terminé
```

### Erreurs courantes

**Erreur 500** : Problème de syntaxe JSON ou chemin incorrect
**Erreur 404** : URL incorrecte ou modèle supprimé
**Permission denied** : Problème de droits d'écriture

---

## 📄 License

Apache-2.0 license - Utilisez ce code comme bon vous semble !

Copyright (c) 2026 FMJ

---

## 🤝 Contributing

Les contributions sont les bienvenues !

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 🙏 Remerciements

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - Pour cette incroyable interface
- La communauté ComfyUI pour le support et les retours

---

**⭐ Si vous aimez ce projet, n'oubliez pas de mettre une étoile sur GitHub !**
