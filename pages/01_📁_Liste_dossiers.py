# ---------------------------------------------------
# 🎛️ Filtres avancés (dépendants)
# ---------------------------------------------------

st.subheader("🎛️ Filtres avancés")

# 1️⃣ CATEGORIES
categories = sorted(df["Catégories"].dropna().unique().tolist())
cat_select = st.selectbox("Catégorie", ["Toutes"] + categories)

# Filtrage dynamique colonne Catégories
if cat_select != "Toutes":
    df = df[df["Catégories"] == cat_select]

# 2️⃣ SOUS-CATEGORIES dépendantes
if cat_select != "Toutes":
    souscats = sorted(df[df["Catégories"] == cat_select]["Sous-catégories"].dropna().unique().tolist())
else:
    souscats = sorted(df["Sous-catégories"].dropna().unique().tolist())

souscat_select = st.selectbox("Sous-catégorie", ["Toutes"] + souscats)

# Filtrage dynamique colonne Sous-catégories
if souscat_select != "Toutes":
    df = df[df["Sous-catégories"] == souscat_select]

# 3️⃣ VISA dépendant des filtres précédents
if souscat_select != "Toutes":
    visas = sorted(df[df["Sous-catégories"] == souscat_select]["Visa"].dropna().unique().tolist())
elif cat_select != "Toutes":
    visas = sorted(df[df["Catégories"] == cat_select]["Visa"].dropna().unique().tolist())
else:
    visas = sorted(df["Visa"].dropna().unique().tolist())

visa_select = st.selectbox("Visa", ["Tous"] + visas)

if visa_select != "Tous":
    df = df[df["Visa"] == visa_select]
