import ldap  # Importation du module LDAP pour interagir avec un serveur LDAP

def is_certificate_revoked(crl_url, serial_number):
    """
    Vérifie si un certificat est révoqué via une requête LDAP.

    Args:
        crl_url (str): L'URL du point de distribution de la CRL (LDAP).
        serial_number (str): Le numéro de série du certificat (sous forme de chaîne).

    Returns:
        bool: True si le certificat est révoqué, False sinon.
    """
    try:
        # Extraction des informations de l'URL LDAP
        uri_parts = crl_url.split('/')  # Découpe l'URL en une liste d'éléments
        ldap_server = uri_parts[2]  # Récupère le serveur LDAP à partir de l'URL (ex: ldap.example.com)
        base_dn = '/'.join(uri_parts[3:])  # Construit le DN de base à partir du reste de l'URL
        
        # Connexion au serveur LDAP
        ldap_connection = ldap.initialize(f"ldap://{ldap_server}")  # Initialise la connexion avec le serveur LDAP
        ldap_connection.protocol_version = 3  # Définit la version du protocole LDAP (LDAPv3)
        
        # Construction du filtre de recherche
        search_filter = f"(&(objectClass=certificateRevocationList)(serialNumber={serial_number}))"
        # Ce filtre recherche un objet de type 'certificateRevocationList' ayant le numéro de série spécifié

        # Recherche LDAP
        results = ldap_connection.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter)
        # Effectue une recherche récursive (SCOPE_SUBTREE) dans le LDAP à partir de base_dn avec le filtre search_filter

        # Retourne True si le certificat est trouvé (donc révoqué), sinon False
        return bool(results)  # Si des résultats sont trouvés, cela signifie que le certificat est révoqué

    except ldap.LDAPError:
        return False  # En cas d'erreur (serveur inaccessible, mauvais DN, etc.), retourner False (certificat non révoqué)

    finally:
        if 'ldap_connection' in locals():  # Vérifie si la connexion a été créée
            ldap_connection.unbind_s()  # Ferme proprement la connexion LDAP

# Exemple d'utilisation
crl_url = "ldap://ldap.camgovca.cm:389/ou=dp2p1,ou=crldp,ou=Cameroon Government Certification Authority,o=ANTIC CA,c=CM"
# URL du serveur LDAP contenant la liste de révocation des certificats (CRL)

serial_number = "6565"  # Numéro de série du certificat sous forme de chaîne

# Vérifie si le certificat est révoqué et affiche le résultat
if is_certificate_revoked(crl_url, serial_number):
    print("Le certificat est révoqué.")
else:
    print("Le certificat n'est pas révoqué.")
