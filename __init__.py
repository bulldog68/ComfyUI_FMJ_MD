import os
import json
import requests
import folder_paths
import comfy.utils
from server import PromptServer
from aiohttp import web

NODE_DIR = os.path.dirname(__file__)
JSON_DIR = os.path.join(NODE_DIR, "json_lists")

os.makedirs(JSON_DIR, exist_ok=True)

WEB_DIRECTORY = "./web"

@PromptServer.instance.routes.get("/fmj_get_models")
async def get_models_api(request):
    try:
        filename = request.rel_url.query.get("filename", "default_models.json")
        if "/" in filename or "\\" in filename:
            return web.json_response({"models": []}, status=200)
        
        filepath = os.path.join(JSON_DIR, filename)
        if not os.path.exists(filepath):
            return web.json_response({"models": []}, status=200)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            models = list(data.keys())
            return web.json_response({"models": models})
    except Exception as e:
        print(f"[FMJ] API ERREUR: {e}")
        return web.json_response({"models": []}, status=200)

def get_available_jsons():
    try:
        files = [f for f in os.listdir(JSON_DIR) if f.endswith('.json')]
        files.sort()
        return files if files else ["default_models.json"]
    except Exception as e:
        print(f"[FMJ] Erreur listage JSON: {e}")
        return ["default_models.json"]

def load_models(json_filename):
    filepath = os.path.join(JSON_DIR, json_filename)
    if not os.path.exists(filepath):
        if json_filename == "default_models.json":
            default_models = {
                "SDXL_Base_1.0": {
                    "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
                    "folder": "checkpoints"
                }
            }
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(default_models, f, indent=4)
            except Exception as e:
                print(f"❌ [FMJ] Impossible de créer {json_filename}: {e}")
            return default_models
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ [FMJ] ERREUR DE SYNTAXE dans {json_filename} ! Ligne {e.lineno}, Colonne {e.colno}")
        return {}
    except Exception as e:
        print(f"❌ [FMJ] Erreur lecture {json_filename}: {e}")
        return {}

class FMJModelDownloader:
    """
    🌀FMJ Smart Model Manager - Gestionnaire intelligent de modèles
    
    Ce node permet de gérer le téléchargement de modèles via des profils JSON.
    
    Fonctionnalités :
    - Vérification des modèles manquants
    - Téléchargement individuel ou en masse
    - Profils JSON personnalisables
    - Mise à jour dynamique de la liste des modèles
    
    Documentation complète : https://github.com/ton-repo/ComfyUI_FMJ_MD
    """
    
    def __init__(self):
        self.json_files = get_available_jsons()
        first_json = self.json_files[0] if self.json_files else "default_models.json"
        self.models = load_models(first_json)
        self.model_names = list(self.models.keys()) if self.models else [""]

    @classmethod
    def INPUT_TYPES(s):
        instance = s()
        return {
            "required": {
                "json_profile": (instance.json_files, {
                    "tooltip": "📁 Profil JSON contenant la liste des modèles à gérer"
                }),
                "action": (["🔍 1. Vérifier les manquants", "⬇️ 2. Télécharger le modèle sélectionné", "⬇️️ 3. Télécharger TOUS les manquants"], {
                    "tooltip": "🎯 Action à effectuer"
                }),
                "model_name": ("STRING", {
                    "default": instance.model_names[0] if instance.model_names else "",
                    "multiline": False,
                    "tooltip": "📝 Nom du modèle (clic droit pour voir la liste complète)"
                }),
                "force_redownload": ("BOOLEAN", {
                    "default": False, 
                    "tooltip": "⚠️ Forcer le téléchargement même si le fichier existe déjà"
                }),
            },
            "optional": {
                "trigger": ("*", {"tooltip": "🔘 Déclencheur optionnel pour enchaînement de workflows"})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status_report",)
    FUNCTION = "process_models"
    CATEGORY = "🌀FMJ"

    def get_model_path(self, model_info):
        target_folder = model_info.get("folder", "checkpoints").strip().strip('/\\')
        path_parts = target_folder.split('/')
        base_folder_name = path_parts[0]
        
        if base_folder_name in folder_paths.folder_names_and_paths:
            base_dir = folder_paths.folder_names_and_paths[base_folder_name][0][0]
            target_dir = os.path.join(base_dir, *path_parts[1:]) if len(path_parts) > 1 else base_dir
        else:
            target_dir = os.path.join(folder_paths.models_dir, target_folder)
            
        filename = model_info["url"].split('/')[-1].split('?')[0]
        return os.path.join(target_dir, filename), target_dir

    def process_models(self, json_profile, action, model_name, force_redownload, trigger=None):
        """
        Traite les actions sur les modèles
        
        Args:
            json_profile: Nom du fichier JSON de profil
            action: Action à effectuer (vérification, téléchargement unique ou multiple)
            model_name: Nom du modèle à télécharger
            force_redownload: Si True, retélécharge même si le fichier existe
            trigger: Déclencheur optionnel
            
        Returns:
            status_report: Rapport textuel de l'opération
        """
        models = load_models(json_profile)
        if not models:
            return (f"❌ ERREUR: Le profil '{json_profile}' est vide ou invalide.\n\n💡 Vérifiez que le fichier JSON existe dans le dossier json_lists.",)

        missing_models = []
        existing_models = []

        # Analyse des modèles présents/manquants
        for name, info in models.items():
            filepath, target_dir = self.get_model_path(info)
            try:
                os.makedirs(target_dir, exist_ok=True)
            except Exception:
                pass

            if os.path.exists(filepath) and not force_redownload:
                existing_models.append(name)
            else:
                missing_models.append(name)

        # Action 1: Vérification
        if action == "🔍 1. Vérifier les manquants":
            report = f"📊 --- RAPPORT DE VÉRIFICATION ---\n"
            report += f"📁 Profil: {json_profile}\n"
            report += f"📈 Total modèles: {len(models)}\n"
            report += f"--------------------------------------\n\n"
            report += f"✅ PRÉSENTS ({len(existing_models)}) :\n"
            if existing_models:
                for model in existing_models:
                    report += f"   ✓ {model}\n"
            else:
                report += f"   Aucun\n"
            report += f"\n❌ MANQUANTS ({len(missing_models)}) :\n"
            if missing_models:
                for model in missing_models:
                    report += f"   ✗ {model}\n"
            else:
                report += f"   🎉 Aucun (Tout est à jour !)"
            report += f"\n\n--------------------------------------"
            report += f"\n💡 Astuce: Utilisez l'action 3 pour télécharger tous les manquants"
            return (report,)

        # Action 2: Télécharger un modèle spécifique
        elif action == "⬇️ 2. Télécharger le modèle sélectionné":
            if model_name not in models:
                available = list(models.keys())
                return (f"❌ ERREUR: Modèle '{model_name}' introuvable dans {json_profile}\n\n"
                       f"📋 Modèles disponibles ({len(available)}):\n" + 
                       "\n".join([f"  • {m}" for m in available[:10]]) +
                       (f"\n  ... et {len(available)-10} autres" if len(available) > 10 else ""),)
            
            if model_name in existing_models and not force_redownload:
                return (f"ℹ️ INFORMATION\n\n"
                       f"Le modèle '{model_name}' est déjà présent localement.\n\n"
                       f"💡 Pour le retélécharger:\n"
                       f"   • Activez l'option 'force_redownload'\n"
                       f"   • Ou utilisez l'action 'Télécharger TOUS les manquants'")

            # Confirmation de téléchargement
            model_info = models[model_name]
            filepath, target_dir = self.get_model_path(model_info)
            
            report = f"🚀 --- TÉLÉCHARGEMENT EN COURS ---\n\n"
            report += f"📦 Modèle: {model_name}\n"
            report += f"📁 Destination: {target_dir}\n"
            report += f"🔗 URL: {model_info['url'][:80]}...\n"
            report += f"⚠️ Force download: {'Oui' if force_redownload else 'Non'}\n\n"
            report += f"⏳ Veuillez patienter..."
            
            print(f"\n{report}")
            
            try:
                self._download_single(model_name, model_info, silent=False)
                
                success_report = f"✅ --- TÉLÉCHARGEMENT RÉUSSI ---\n\n"
                success_report += f"📦 Modèle: {model_name}\n"
                success_report += f"💾 Taille: {os.path.getsize(filepath) / (1024*1024):.2f} MB\n"
                success_report += f"📍 Chemin: {filepath}\n\n"
                success_report += f"🎉 Le modèle est prêt à l'emploi !"
                
                print(success_report)
                return (success_report,)
                
            except Exception as e:
                error_report = f"❌ --- ÉCHEC DU TÉLÉCHARGEMENT ---\n\n"
                error_report += f"📦 Modèle: {model_name}\n"
                error_report += f"💥 Erreur: {str(e)}\n\n"
                error_report += f"💡 Vérifiez:\n"
                error_report += f"   • Votre connexion internet\n"
                error_report += f"   • L'URL du modèle\n"
                error_report += f"   • L'espace disque disponible"
                
                print(error_report)
                return (error_report,)

        # Action 3: Télécharger tous les manquants
        elif action == "⬇️⬇️ 3. Télécharger TOUS les manquants":
            if not missing_models:
                return (f"🎉 FÉLICITATIONS !\n\n"
                       f"Tous les modèles du profil '{json_profile}' sont déjà présents.\n\n"
                       f"📊 Statistiques:\n"
                       f"   ✅ Présents: {len(existing_models)}\n"
                       f"   ❌ Manquants: 0\n\n"
                       f"💡 Vous pouvez changer de profil pour vérifier d'autres modèles.")

            # Confirmation avant téléchargement en masse
            report = f"🚀 --- TÉLÉCHARGEMENT EN MASSE ---\n\n"
            report += f"📁 Profil: {json_profile}\n"
            report += f"📦 Modèles à télécharger: {len(missing_models)}/{len(models)}\n\n"
            report += f"📋 Liste des modèles:\n"
            for i, name in enumerate(missing_models, 1):
                report += f"   {i}. {name}\n"
            report += f"\n⏳ Démarrage dans 2 secondes...\n"
            report += f"--------------------------------------\n"
            
            print(f"\n{report}")
            
            success_count = 0
            failed_models = []
            detailed_report = report + "\n"
            
            for i, name in enumerate(missing_models, 1):
                try:
                    print(f"[{i}/{len(missing_models)}] Téléchargement de {name}...")
                    self._download_single(name, models[name], silent=True)
                    success_count += 1
                    detailed_report += f"✅ [{i}/{len(missing_models)}] {name}\n"
                except Exception as e:
                    failed_models.append((name, str(e)))
                    detailed_report += f"❌ [{i}/{len(missing_models)}] {name}: {str(e)[:50]}...\n"
            
            # Rapport final
            final_report = f"\n{'='*50}\n"
            final_report += f"🏁 --- TÉLÉCHARGEMENT TERMINÉ ---\n\n"
            final_report += f"📊 Résultats:\n"
            final_report += f"   ✅ Succès: {success_count}/{len(missing_models)}\n"
            if failed_models:
                final_report += f"   ❌ Échecs: {len(failed_models)}\n"
            final_report += f"\n💾 Modèles téléchargés:\n"
            for name in missing_models[:success_count]:
                final_report += f"   ✓ {name}\n"
            
            if failed_models:
                final_report += f"\n⚠️ Échecs:\n"
                for name, error in failed_models:
                    final_report += f"   ✗ {name}\n"
            
            final_report += f"\n{'='*50}\n"
            final_report += f"\n🎉 {success_count} modèle(s) prêt(s) à l'emploi !"
            
            print(final_report)
            return (final_report,)

        return ("❌ Action inconnue. Veuillez sélectionner une action valide.",)

    def _download_single(self, model_name, model_info, silent=False):
        filepath, target_dir = self.get_model_path(model_info)
        url = model_info["url"]

        if not silent:
            print(f"⬇️ [FMJ] Téléchargement de '{model_name}'...")
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, stream=True, headers=headers, allow_redirects=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            pbar = comfy.utils.ProgressBar(total_size)
            
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        pbar.update(len(chunk))
            
            if not silent:
                print(f"✅ [FMJ] Téléchargement terminé: {filepath}")
                print(f"   Taille: {downloaded / (1024*1024):.2f} MB")
            
            return f"OK"
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            raise e

NODE_CLASS_MAPPINGS = {
    "FMJModelDownloader": FMJModelDownloader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FMJModelDownloader": "🌀FMJ  Smart Model Manager"
}