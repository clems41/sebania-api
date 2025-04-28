# Reprise de l'ensemble des données en intégrant toutes les lignes (1 à 57) correctement
import json

# Données reformatées en dur, version complète
full_data = """
1	Production de plant	TRUE	production	TRUE	semis, pépinière, jeunes plants, rempotage, bouturage
2	Travail du sol	TRUE	production	TRUE	préparation sol, labour, motoculteur, rotavateur, grelinette, Actisol, Canadien, tracteur, outil, engin
3	Apport de MO (Amender)	TRUE	production	TRUE	compost,fumier,amendement,apport,mo,matière,organique,broyat,épandeur,tracteur,brouette,rateau
4	Fertilisation	TRUE	production	TRUE	engrais,nutriments,sol,apport,granulé,NPK,azote,oligo,oligoéléments,lisier
5	Paillage	TRUE	production	TRUE	paille,mulch,BRF,Broyat,couvrir
6	Bâchage	TRUE	production	TRUE	bâche,occultation,désherbage,plastique,tissée,enterrer
7	Semis direct	TRUE	production	TRUE	graines,ligne,plantation,volée,semoir, en place,monorang,multirang
8	Plantation	TRUE	production	TRUE	plants,repiquage,cultures,implantation,motte,jeune plant,godets
9	Gestion climatique	TRUE	production	TRUE	serre,température,ventilation,voilage,voile,thermique,ouvrant,moteur,portes
10	Gestion des bioagresseurs	TRUE	production	TRUE	insectes,maladies,traitements,phyto,sanitaire,lutte,filets,pulvériser,mélange,dose
11	Irrigation	TRUE	production	TRUE	arrosage,goutte,eau,tuyau,aspersion,planifier
12	Désherbage	TRUE	production	TRUE	mauvaises,herbes,sarclage,binage,manuel,mechanique,pulvériser
13	Taille	TRUE	production	TRUE	élagage,coupe,entretien,forme,égourmandage,effeuillage,étêtage
14	Palissage	TRUE	production	TRUE	ficelle,tuteur,support,dérouler
15	Destruction de culture	TRUE	production	TRUE	arrachage,broyage,rouage,nettoyage
16	Suivi de culture	TRUE	production	TRUE	observation,croissance,planning,plannification,tour du champ, tour, regarder,checker
17	Récolte	TRUE	production	TRUE	cueillette,maturité,rendement,poids,caisse,retirer,bottes
18	Nettoyage	TRUE	production	TRUE	outils,matériel,hygiène,propreté,parer,parage,nettoyeuse,laver,lavage,station,lavabo,process,eau,passe à l'eau, enlever,terre
19	Livrer	TRUE	commercialisation	FALSE	transport,distribution,clients,camion,fourgon,livraison,apporter,donner
20	Stockage	TRUE	commercialisation	FALSE	chambre,froide,entrepôt,conservation,logistique,mise en caisse, emballage
21	Charger / Décharger	TRUE	commercialisation	FALSE	logistique,palettes,livraison,chercher
22	Communiquer	TRUE	commercialisation	FALSE	réseaux,sociaux,clients,marketing,emails,courriers,presse,interview,radio,mail,mailling, list, whatsapp,message
23	Marché	TRUE	commercialisation	FALSE	stand,vente,dépot,préparer
24	Vente directe	TRUE	commercialisation	FALSE	client,ferme,circuit,court,ferme,place,sur
25	Panier AMAP	TRUE	commercialisation	FALSE	abonnement,distribution,consommateurs,commandes
26	Gestion des stocks	TRUE	commercialisation	FALSE	inventaire,produits,suivi,logistique
27	Préparation de commande	TRUE	commercialisation	FALSE	tri,pesée,conditionnement,cagettes,paniers,liste
28	Comptabilité	TRUE	administratif	FALSE	bilan,facturation,gestion,impôts
29	Administratif	TRUE	administratif	FALSE	papier,déclarations,dossiers,impôts
30	Planifier	TRUE	administratif	FALSE	agenda,planning,tâches,plannification,calendrier,rotation,assolement
31	Veille	TRUE	administratif	FALSE	informations,réglementations,tendances
32	Achat / Commande	TRUE	administratif	FALSE	fournisseurs,approvisionnement,matériel
33	Ranger	TRUE	général	FALSE	outils,local,organisation,ordre,classer
34	Accueil du public	TRUE	général	FALSE	visite,communication,pédagogie
35	Réparer	TRUE	général	FALSE	bricolage,maintenance,outils
36	Construire	TRUE	général	FALSE	bâtiment,abri,bricolage,serre,outils,aménagements
37	Aménager	TRUE	général	FALSE	organisation,espace,infrastructure
38	Entretenir	TRUE	général	FALSE	propreté,maintenance,suivi,tailler,élaguer
39	Formation	TRUE	général	FALSE	apprentissage,stage,cours,études
40	Accompagnement	TRUE	général	FALSE	pédagogie,conseil,suivi,aide
41	Production de compost	TRUE	général	FALSE	déchets,fertilité,mo,matière,organique
42	Gestion des intrants	TRUE	général	FALSE	engrais,semences,stockage,mo,matière,organique,brf,essence,gasoil,phyto,produits,voiles
43	Réunions	TRUE	général	FALSE	équipe,planning,communication,discussions,rencontres
44	Volailles	TRUE	secondaire	FALSE	poules,œufs,élevage,viande
45	Floriculture	TRUE	secondaire	FALSE	fleurs,décoration,culture,bouquet
46	Brassiculture	TRUE	secondaire	FALSE	bière,brassage,fermentation
47	Apiculture	TRUE	secondaire	FALSE	abeilles,miel,ruche
48	Champignons	TRUE	secondaire	FALSE	myciculture,substrat,cave
49	Boissons	TRUE	secondaire	FALSE	jus,sirop,fermentation,alccol
50	Conserves	TRUE	secondaire	FALSE	transformation,bocaux,stérilisation
51	Boulangerie	TRUE	secondaire	FALSE	pain,four,farine
52	Verger	TRUE	secondaire	FALSE	arbres,fruits,taille
53	Semences	TRUE	secondaire	FALSE	graines,reproduction,sélection,production
54	Atelier pédagogique	TRUE	secondaire	FALSE	scolaire,animation,formation
55	Auxiliaires de culture	TRUE	secondaire	FALSE	insectes,utiles,lutte,biologique,biodiversité
56	Transformation	TRUE	secondaire	FALSE	atelier,produits,agroalimentaire,conserves
57	Activités syndicales	TRUE	secondaire	FALSE	syndicat,agriculture,droits,FNSEA,Conf,JA,Jeunes agriculteurs
"""

# Traitement
lines = full_data.strip().split("\n")
rows = [line.split("\t") for line in lines]
model = "base.Activite"
output_path_full = "/mnt/data/activites.json"

# Construction du JSON
json_output_full = []
for row in rows:
    if len(row) != 6:
        continue
    pk, nom, default, categorie_default, need_culture, mots_cles = row
    json_output_full.append({
        "model": model,
        "pk": int(pk),
        "fields": {
            "nom": nom.strip(),
            "default": default.strip().upper() == "TRUE",
            "categorie_default": categorie_default.strip(),
            "need_culture": need_culture.strip().upper() == "TRUE",
            "mots_cles": mots_cles.strip()
        }
    })

# Sauvegarde
with open(output_path_full, "w", encoding="utf-8") as f:
    json.dump(json_output_full, f, ensure_ascii=False, indent=2)