  async getTemplate(templateId) {
    const token = AuthService.getToken();
    
    try {
      console.log("🔍 [DEBUG] Requête API pour template:", `${API_URL}/signature-templates/templates/${templateId}/`);
      const response = await axios.get(`${API_URL}/signature-templates/templates/${templateId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log("🔍 [DEBUG] Réponse API template:", response.data);
      return response.data;
    } catch (error) {
      console.error(`Erreur lors de la récupération du template ${templateId}:`, error);
      throw error;
    }
  }
