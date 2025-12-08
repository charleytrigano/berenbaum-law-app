from backend.dropbox_utils import load_database, save_database

class Database:
    def __init__(self):
        self.db = load_database()

    # ------------------------
    # CLIENTS
    # ------------------------
    def list_clients(self):
        return self.db.get("clients", [])

    def get_client(self, dossier_num):
        for c in self.db.get("clients", []):
            if str(c.get("Dossier N")) == str(dossier_num):
                return c
        return None

    def update_client(self, dossier_num, new_data: dict):
        updated = False
        for i, c in enumerate(self.db["clients"]):
            if str(c.get("Dossier N")) == str(dossier_num):
                self.db["clients"][i].update(new_data)
                updated = True
                break
        if updated:
            save_database(self.db)

    def add_client(self, data):
        self.db["clients"].append(data)
        save_database(self.db)

    def delete_client(self, dossier_num):
        self.db["clients"] = [
            c for c in self.db["clients"] if str(c["Dossier N"]) != str(dossier_num)
        ]
        save_database(self.db)

    # ------------------------
    # VISA TABLE
    # ------------------------
    def visa_table(self):
        return self.db.get("visa", [])

    # ------------------------
    # ESCROW
    # ------------------------
    def get_escrow_clients(self):
        return [
            c for c in self.db["clients"]
            if c["Escrow"] or c["Escrow_a_reclamer"] or c["Escrow_reclame"]
        ]
