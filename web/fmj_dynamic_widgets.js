console.log("🔵 [FMJ] Script chargé !");

import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "FMJ.DynamicModelDownloader",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "FMJModelDownloader") return;
        
        console.log("🟡 [FMJ] Node détecté");
        
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        
        nodeType.prototype.onNodeCreated = function() {
            const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            
            const self = this;
            let lastProfile = null;
            let currentModels = [];
            
            // Menu contextuel personnalisé
            const origGetExtraMenuOptions = this.getExtraMenuOptions;
            this.getExtraMenuOptions = function(_, options) {
                if (origGetExtraMenuOptions) {
                    origGetExtraMenuOptions.apply(this, arguments);
                }
                
                if (currentModels.length > 0) {
                    // Ajouter un séparateur
                    options.unshift(null);
                    
                    // Ajouter le titre
                    options.unshift({
                        content: `📦 Modèles disponibles (${currentModels.length})`,
                        disabled: true
                    });
                    
                    // Ajouter chaque modèle comme option
                    currentModels.forEach(modelName => {
                        options.unshift({
                            content: `📥 ${modelName}`,
                            callback: () => {
                                const modelWidget = self.widgets.find(w => w.name === "model_name");
                                if (modelWidget) {
                                    modelWidget.value = modelName;
                                    self.setDirtyCanvas(true, true);
                                    console.log(`[FMJ] Modèle sélectionné: ${modelName}`);
                                }
                            }
                        });
                    });
                }
            };
            
            async function updateModels() {
                const profileWidget = self.widgets.find(w => w.name === "json_profile");
                const modelWidget = self.widgets.find(w => w.name === "model_name");
                
                if (!profileWidget || !modelWidget) return;
                if (profileWidget.value === lastProfile) return;
                
                lastProfile = profileWidget.value;
                console.log(`[FMJ] Mise à jour pour: ${lastProfile}`);
                
                try {
                    const response = await fetch(`/fmj_get_models?filename=${encodeURIComponent(lastProfile)}`);
                    const data = await response.json();
                    
                    if (data.models && data.models.length > 0) {
                        currentModels = data.models;
                        modelWidget.value = data.models[0];
                        
                        self.setDirtyCanvas(true, true);
                        console.log(`[FMJ] ✅ ${data.models.length} modèles chargés`);
                    }
                } catch (error) {
                    console.error("[FMJ] Erreur:", error);
                }
            }
            
            const intervalId = setInterval(updateModels, 500);
            
            const oldRemoved = self.onRemoved;
            self.onRemoved = function() {
                clearInterval(intervalId);
                if (oldRemoved) oldRemoved.apply(this, arguments);
            };
            
            return result;
        };
    }
});