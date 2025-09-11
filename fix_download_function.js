// Correction pour la fonction downloadSignedDocument dans CollaboratorDashboard.vue
// Remplacer les lignes 1828-1850 par ce code :

    // Étape 1: Chercher le DocumentSignature correspondant au DocumentQRPosition
    console.log('Recherche du document signé pour l\'ID:', doc.id);
    console.log('Nom du document:', doc.name);
    
    // Essayer d'abord par document_id
    let signatureSearchUrl = `https://ppd.camgovca.cm/api/documents/signatures/?document_id=${doc.id}&organization_id=${organizationId}`;
    
    let signatureResponse = await axios.get(signatureSearchUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    console.log('Réponse recherche par ID:', signatureResponse.data);

    let signature;
    
    // Si aucune signature trouvée par ID, essayer par titre
    if (!signatureResponse.data.results || signatureResponse.data.results.length === 0) {
      console.log('Aucune signature trouvée par ID, recherche par titre...');
      
      // Rechercher toutes les signatures de l'organisation
      signatureSearchUrl = `https://ppd.camgovca.cm/api/documents/signatures/?organization_id=${organizationId}`;
      signatureResponse = await axios.get(signatureSearchUrl, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('Toutes les signatures de l\'organisation:', signatureResponse.data);

      // Filtrer par titre correspondant
      const matchingSignatures = signatureResponse.data.results.filter(sig => 
        sig.title === doc.name || sig.title === doc.document_name
      );

      if (matchingSignatures.length === 0) {
        throw new Error('Aucune signature trouvée pour ce document');
      }

      // Prendre la signature la plus récente
      signature = matchingSignatures.sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      )[0];
      
      console.log('Signature trouvée par titre:', signature);
    } else {
      // Prendre la première signature trouvée par ID
      signature = signatureResponse.data.results[0];
      console.log('Signature trouvée par ID:', signature);
    }
    
    // Étape 2: Télécharger le document signé en utilisant l'ID de la signature
    const downloadUrl = `https://ppd.camgovca.cm/api/documents/signatures/${signature.document_id}/download/`;
