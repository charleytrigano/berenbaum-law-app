import json
from backend.dropbox_utils import load_database, save_database

print("🔧 Réparation du JSON en cours...")

db = load_database()
clients = db.get("clients", [])

status_fix = {
    "Dossier_envoye": "Dossier envoye",
    "Dossier envoyé": "Dossier envoye",

    "Dossier accepté": "Dossier accepte",
    "Dossier Accepté": "Dossier accepte",

    "Dossier refusé": "Dossier refuse",
    "Dossier Refusé": "Dossier refuse",

    "Dossier annulé": "Dossier Annule",
    "Dossier Annulé": "Dossier Annule",
}

def normalize_bool(x):
    return str(x).lower() in ["true", "1", "yes", "oui"]

new_clients = []

for c in clients:
    c = c.copy()

    # Corriger colonnes statut
    for old, new in status_fix.items():
        if old in c:
            c[new] = normalize_bool(c[old])
            del c[old]

    # Convertir colonnes manquantes
    for col in ["Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE"]:
        if col not in c:
            c[col] = False
        else:
            c[col] = normalize_bool(c[col])

    new_clients.append(c)

db["clients"] = new_clients
save_database(db)

print("✔ JSON réparé avec succès !")
