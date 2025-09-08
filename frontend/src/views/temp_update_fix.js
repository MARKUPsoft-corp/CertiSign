    // Mettre à jour le template via l'API
    await TemplateService.updateTemplate(editingTemplate.value.id, templateData);
    
    // Récupérer le template mis à jour depuis l'API pour avoir l'aperçu mis à jour
    const updatedTemplate = await TemplateService.getTemplate(editingTemplate.value.id);
    
    // Mettre à jour le template dans la liste locale
    const index = templates.value.findIndex(t => t.id === editingTemplate.value.id);
    if (index !== -1) {
      templates.value[index] = {
        ...templates.value[index],
        name: templateData.name,
        qrSize: templateData.qr_size,
        pageApplication: templateData.page_application,
        preview_document: updatedTemplate.preview_document // Mettre à jour l'aperçu
      };
    }
