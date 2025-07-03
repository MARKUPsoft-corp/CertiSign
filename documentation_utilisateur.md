# Guide Utilisateur CertiSign

## Table des matières

1. [Introduction](#introduction)
2. [Première visite et inscription](#première-visite-et-inscription)
3. [Connexion](#connexion)
4. [Navigation dans l'interface](#navigation-dans-linterface)
5. [Rôles et permissions](#rôles-et-permissions)
6. [Signature de documents](#signature-de-documents)
7. [Gestion des documents (Collaborateurs)](#gestion-des-documents-collaborateurs)
8. [Administration (Administrateurs)](#administration-administrateurs)
9. [Profil utilisateur](#profil-utilisateur)
10. [Support et aide](#support-et-aide)

---

## 1. Introduction

CertiSign est une plateforme de signature électronique sécurisée qui permet de signer des documents PDF de manière légale et traçable. Cette application utilise des certificats numériques pour garantir l'authenticité et l'intégrité des signatures.

### Fonctionnalités principales
- ✅ Signature électronique sécurisée avec certificat numérique
- ✅ Vérification de l'authenticité des documents signés
- ✅ Gestion multi-utilisateurs avec différents rôles
- ✅ Traçabilité complète des actions
- ✅ Interface intuitive et responsive

---

## 2. Première visite et inscription

### 2.1 Accès à l'application

1. **Ouvrez votre navigateur** et accédez à l'adresse : `https://192.168.4.131/`
2. La **page d'accueil** s'affiche avec :
   - Une présentation de CertiSign
   - Les boutons "Se connecter" et "S'inscrire"
   - Des informations sur la sécurité de l'application

### 2.2 Création d'un compte

1. **Cliquez sur "S'inscrire"** dans la barre de navigation ou sur la page d'accueil
2. **Remplissez le formulaire d'inscription** :
   - **Nom** : Votre nom de famille
   - **Prénom** : Votre prénom
   - **Email** : Une adresse email valide (sera votre identifiant)
   - **Mot de passe** : Minimum 8 caractères, avec au moins :
     - Une majuscule
     - Une minuscule
     - Un chiffre
     - Un caractère spécial
   - **Confirmation du mot de passe** : Répétez le mot de passe
   - **Organisation** : Sélectionnez votre organisation dans la liste
   - **Rôle demandé** : Choisissez le rôle souhaité (sera validé par un administrateur)

3. **Acceptez les conditions d'utilisation** en cochant la case
4. **Cliquez sur "S'inscrire"**

### 2.3 Validation du compte

1. **Consultez votre boîte email** : Un email de confirmation vous a été envoyé
2. **Cliquez sur le lien de validation** dans l'email (valide pendant 24h)
3. Vous êtes redirigé vers la page de connexion avec un message de confirmation
4. **Attendez la validation** de votre compte par un administrateur de votre organisation

> ⚠️ **Note** : Votre compte doit être approuvé par un administrateur avant de pouvoir vous connecter

---

## 3. Connexion

### 3.1 Se connecter

1. **Accédez à la page de connexion** via le bouton "Se connecter"
2. **Entrez vos identifiants** :
   - Email
   - Mot de passe
3. **Cliquez sur "Se connecter"**

### 3.2 Mot de passe oublié

1. Sur la page de connexion, cliquez sur **"Mot de passe oublié ?"**
2. **Entrez votre adresse email**
3. **Consultez vos emails** pour le lien de réinitialisation
4. **Créez un nouveau mot de passe** en suivant les mêmes règles que lors de l'inscription

### 3.3 Déconnexion

- Cliquez sur votre **nom d'utilisateur** en haut à droite
- Sélectionnez **"Déconnexion"**

---

## 4. Navigation dans l'interface

### 4.1 Barre de navigation

La barre de navigation contient :
- **Logo CertiSign** : Retour à l'accueil
- **Tableau de bord** : Votre espace personnel
- **Documents** : Liste des documents (selon votre rôle)
- **Profil** : Vos informations personnelles
- **Sélecteur de langue** : FR/EN
- **Mode sombre/clair** : Changer le thème

### 4.2 Tableau de bord

Le tableau de bord affiche :
- **Statistiques** : Nombre de documents signés, en attente, etc.
- **Actions rapides** : Boutons selon votre rôle
- **Activité récente** : Dernières actions effectuées
- **Notifications** : Alertes et messages importants

---

## 5. Rôles et permissions

### 5.1 Signataire
- ✅ Voir les documents à signer
- ✅ Signer les documents assignés
- ✅ Consulter l'historique de ses signatures
- ❌ Créer ou modifier des documents

### 5.2 Collaborateur
- ✅ Toutes les permissions du signataire
- ✅ Créer et importer des documents
- ✅ Préparer les zones de signature
- ✅ Assigner des documents aux signataires
- ❌ Gérer les utilisateurs

### 5.3 Administrateur
- ✅ Toutes les permissions du collaborateur
- ✅ Gérer les utilisateurs de l'organisation
- ✅ Valider les nouveaux comptes
- ✅ Voir les statistiques détaillées
- ✅ Configurer les paramètres de l'organisation

---

## 6. Signature de documents

### 6.1 Accéder aux documents à signer

1. Depuis le **tableau de bord**, cliquez sur **"Documents à signer"**
2. Ou allez dans **"Documents"** > **"En attente de signature"**
3. La liste affiche :
   - Nom du document
   - Date d'envoi
   - Expéditeur
   - Date limite (si applicable)

### 6.2 Visualiser le document

1. **Cliquez sur un document** dans la liste
2. Le document PDF s'affiche avec :
   - Les zones de signature surlignées en bleu
   - Les informations du document à droite
   - Les boutons d'action en bas

### 6.3 Signer le document

1. **Préparez votre certificat** :
   - Assurez-vous d'avoir votre fichier de certificat (.p12/.pfx)
   - Connaissez le mot de passe de votre certificat

2. **Cliquez sur "Signer le document"**

3. **Chargez votre certificat** :
   - Cliquez sur **"Choisir un fichier"**
   - Sélectionnez votre certificat numérique
   - Entrez le **mot de passe du certificat**

4. **Vérifiez les informations** :
   - Nom du signataire (extrait du certificat)
   - Date et heure de signature
   - Emplacement de la signature sur le document

5. **Confirmez la signature** :
   - Cliquez sur **"Signer"**
   - Attendez la confirmation

6. **Téléchargez le document signé** :
   - Un QR code est ajouté au document
   - Cliquez sur **"Télécharger"** pour obtenir le PDF signé

### 6.4 Vérifier une signature

1. Accédez à **"Vérifier un document"**
2. **Uploadez le document** signé ou **scannez le QR code**
3. Les informations de signature s'affichent :
   - Validité de la signature
   - Identité du signataire
   - Date et heure de signature
   - Intégrité du document

---

## 7. Gestion des documents (Collaborateurs)

### 7.1 Créer un nouveau document

1. Allez dans **"Documents"** > **"Nouveau document"**
2. **Uploadez le fichier PDF** à faire signer
3. **Configurez le document** :
   - Titre
   - Description
   - Date limite (optionnel)

### 7.2 Placer les zones de signature

1. Le document s'affiche avec **l'éditeur de zones**
2. **Ajoutez des zones de signature** :
   - Cliquez sur **"Ajouter une zone"**
   - Cliquez et glissez sur le document pour créer la zone
   - Ajustez la taille si nécessaire
3. **Assignez les signataires** :
   - Pour chaque zone, sélectionnez un signataire
   - Définissez l'ordre de signature si nécessaire

### 7.3 Envoyer pour signature

1. **Vérifiez le récapitulatif** :
   - Signataires assignés
   - Zones de signature placées
   - Paramètres du document
2. **Cliquez sur "Envoyer"**
3. Les signataires reçoivent une notification par email

### 7.4 Suivre l'avancement

1. Dans **"Documents"** > **"En cours"**
2. Voyez le statut de chaque document :
   - Nombre de signatures obtenues
   - Signataires en attente
   - Actions possibles (relancer, annuler)

---

## 8. Administration (Administrateurs)

### 8.1 Gérer les utilisateurs

1. Accédez à **"Administration"** > **"Utilisateurs"**
2. **Validez les nouveaux comptes** :
   - Cliquez sur les comptes en attente
   - Vérifiez les informations
   - Approuvez ou rejetez
3. **Modifiez les rôles** :
   - Sélectionnez un utilisateur
   - Changez son rôle dans le menu déroulant
   - Sauvegardez

### 8.2 Statistiques et rapports

1. Dans **"Administration"** > **"Statistiques"**
2. Consultez :
   - Nombre de documents signés par période
   - Utilisateurs les plus actifs
   - Temps moyen de signature
   - Taux de complétion

### 8.3 Paramètres de l'organisation

1. **"Administration"** > **"Paramètres"**
2. Configurez :
   - Informations de l'organisation
   - Logo et personnalisation
   - Notifications par défaut
   - Paramètres de sécurité

---

## 9. Profil utilisateur

### 9.1 Voir et modifier son profil

1. Cliquez sur votre **nom** > **"Mon profil"**
2. **Modifiez vos informations** :
   - Photo de profil
   - Informations personnelles
   - Préférences de notification
3. **Sauvegardez les modifications**

### 9.2 Gérer son certificat

1. Dans **"Profil"** > **"Mon certificat"**
2. **Téléchargez votre certificat** pour une utilisation future
3. **Renouvelez** si nécessaire avant expiration

### 9.3 Historique d'activité

1. **"Profil"** > **"Historique"**
2. Consultez toutes vos actions :
   - Documents signés
   - Connexions
   - Modifications effectuées

---

## 10. Support et aide

### 10.1 Aide contextuelle

- Cliquez sur l'icône **"?"** présente sur chaque page
- Des infobulles s'affichent au survol des éléments

### 10.2 FAQ

Accédez à **"Aide"** > **"FAQ"** pour les questions fréquentes

### 10.3 Contact support

- Email : support@certisign.com
- Téléphone : +XX XX XX XX XX
- Chat en ligne : Disponible en bas à droite

### 10.4 Résolution des problèmes courants

**Problème de certificat** :
- Vérifiez que le fichier est au format .p12 ou .pfx
- Assurez-vous que le mot de passe est correct
- Vérifiez la date d'expiration

**Document non visible** :
- Rafraîchissez la page (F5)
- Vérifiez vos permissions
- Contactez l'expéditeur du document

**Erreur de signature** :
- Vérifiez votre connexion internet
- Essayez avec un autre navigateur
- Videz le cache du navigateur

---

## Conseils de sécurité

1. **Ne partagez jamais** votre mot de passe ou certificat
2. **Déconnectez-vous** après utilisation sur un ordinateur partagé
3. **Gardez votre certificat** dans un endroit sécurisé
4. **Utilisez un mot de passe fort** et unique
5. **Vérifiez l'URL** avant de vous connecter (https et certificat valide)

---

*Document mis à jour le : [Date du jour]*
*Version : 1.0* 