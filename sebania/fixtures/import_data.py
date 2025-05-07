# Reprise de l'ensemble des données en intégrant toutes les lignes (1 à 57) correctement
import json

# Données reformatées en dur, version complète
activites_data = """
ID	nom	default	categorie_default	need_culture	mots_cles
1	Production de plant	true	production	true	semis,pépinière,jeunes,plants,rempotage,bouturage
2	Travail du sol	true	production	true	préparation sol,labour,motoculteur,rotavateur,grelinette,Actisol,Canadien,tracteur,outil,engin
3	Apport de MO (Amender)	true	production	true	compost,fumier,amendement,apport,mo,matière,organique,broyat,épandeur,tracteur,brouette,rateau
4	Fertilisation	true	production	true	engrais,nutriments,sol,apport,granulé,NPK,azote,oligo,oligoéléments,lisier
5	Paillage	true	production	true	paille,mulch,BRF,Broyat,couvrir
6	Bâchage	true	production	true	bâche,occultation,désherbage,plastique,tissée,enterrer
7	Semis direct	true	production	true	graines,ligne,plantation,volée,semoir,en place,monorang,multirang
8	Plantation	true	production	true	plants,repiquage,cultures,implantation,motte,jeune plant,godets
9	Gestion climatique	true	production	true	serre,température,ventilation,voilage,voile,thermique,ouvrant,moteur,portes,ouvrir
10	Gestion des bioagresseurs	true	production	true	insectes,maladies,traitements,phyto,sanitaire,lutte,filets,pulvériser,mélange,dose
11	Irrigation	true	production	true	arrosage,goutte,eau,tuyau,aspersion,planifier
12	Désherbage	true	production	true	mauvaises,herbes,sarclage,binage,manuel,mechanique,pulvériser
13	Taille	true	production	true	élagage,coupe,entretien,forme,égourmandage,effeuillage,étêtage
14	Palissage	true	production	true	ficelle,tuteur,support,dérouler
15	Destruction de culture	true	production	true	arrachage,broyage,roulage,nettoyage,engrais,verts
16	Suivi de culture	true	production	true	observation,croissance,planning,planification,tour du champ,tour,regarder,checker
17	Récolte	true	production	true	cueillette,maturité,rendement,poids,caisse,retirer,bottes
18	Nettoyage	true	production	true	outils,matériel,hygiène,propreté,parer,parage,nettoyeuse,laver,lavage,station,lavabo,process,eau,passe à l'eau,enlever,terre
19	Livrer	true	commercialisation	false	transport,distribution,clients,camion,fourgon,livraison,apporter,donner
20	Stockage	true	commercialisation	false	chambre,froide,entrepôt,conservation,logistique,mise en caisse,emballage
21	Charger / Décharger	true	commercialisation	false	logistique,palettes,livraison,chercher
22	Communication / Marketing	true	commercialisation	false	réseaux,sociaux,clients,marketing,emails,courriers,presse,interview,radio,mail,mailling,list,whatsapp,message
23	Marché	true	commercialisation	false	stand,vente,dépot,préparer
24	Vente directe	true	commercialisation	false	client,ferme,circuit,court,ferme,place,sur
25	Panier AMAP	true	commercialisation	false	abonnement,distribution,consommateurs,commandes
26	Gestion des stocks	true	commercialisation	false	inventaire,produits,suivi,logistique
27	Préparation de commande	true	commercialisation	false	tri,pesée,conditionnement,cagettes,paniers,liste
28	Comptabilité	true	administratif	false	bilan,facturation,gestion,impôts
29	Administratif	true	administratif	false	papier,déclarations,dossiers,impôts
30	Planifier	true	administratif	false	agenda,planning,tâches,planification,calendrier,rotation,assolement
31	Veille	true	administratif	false	informations,réglementations,tendances
32	Achat / Commande	true	administratif	false	fournisseurs,approvisionnement,matériel
33	Ranger	true	général	false	outils,local,organisation,ordre,classer
34	Accueil du public	true	général	false	visite,communication,pédagogie
35	Réparer	true	général	false	bricolage,maintenance,outils
36	Construire	true	général	false	bâtiment,abri,bricolage,serre,outils,aménagements
37	Aménager	true	général	false	organisation,espace,infrastructure
38	Entretenir	true	général	false	propreté,maintenance,suivi,tailler,élaguer
39	Formation	true	général	false	apprentissage,stage,cours,études
40	Accompagnement	true	général	false	pédagogie,conseil,suivi,aide
41	Production de compost	true	général	false	déchets,fertilité,mo,matière,organique
42	Gestion des intrants	true	général	false	engrais,semences,stockage,mo,matière,organique,brf,essence,gasoil,phyto,produits,voiles
43	Réunions	true	général	false	équipe,planning,communication,discussions,rencontres
44	Volailles	true	secondaire	false	poules,œufs,élevage,viande,oeufs
45	Floriculture	true	secondaire	false	fleurs,décoration,culture,bouquet
46	Brassiculture	true	secondaire	false	bière,brassage,fermentation
47	Apiculture	true	secondaire	false	abeilles,miel,ruche
48	Champignons	true	secondaire	false	myciculture,substrat,cave
49	Boissons	true	secondaire	false	jus,sirop,fermentation,alccol
50	Conserves	true	secondaire	false	transformation,bocaux,stérilisation
51	Boulangerie	true	secondaire	false	pain,four,farine
52	Verger	true	secondaire	false	arbres,fruits,taille
53	Semences	true	secondaire	false	graines,reproduction,sélection,production
54	Atelier pédagogique	true	secondaire	false	scolaire,animation,formation
55	Auxiliaires de culture	true	secondaire	false	insectes,utiles,lutte,biologique,biodiversité
56	Transformation	true	secondaire	false	atelier,produits,agroalimentaire,conserves
57	Activités syndicales	true	secondaire	false	syndicat,agriculture,droits,FNSEA,Conf,JA,Jeunes agriculteurs
""", "base.Activite", "activite_default.json"

cultures_data = """
ID	nom	default	categorie_default
1	Ail	true	racine
2	Artichaut	true	fruit
3	Asperge	true	racine
4	Aubergine	true	fruit
5	Betterave	true	racine
6	Blette	true	feuille
7	Brocoli	true	feuille
8	Butternut	true	fruit
9	Carotte	true	racine
10	Chou chinois	true	feuille
11	Chou frisé	true	feuille
12	Chou kale	true	feuille
13	Chou rouge	true	feuille
14	Chou-fleur	true	fruit
15	Concombre	true	fruit
16	Courge musquée	true	fruit
17	Courge spaghetti	true	fruit
18	Courgette	true	fruit
19	Céleri branche	true	feuille
20	Céleri-rave	true	racine
21	Endive	true	racine
22	Fenouil	true	feuille
23	Haricot vert	true	fruit
24	Laitue	true	feuille
25	Manioc	true	racine
26	Melon	true	fruit
27	Mâche	true	feuille
28	Navet	true	racine
29	Oignon	true	racine
30	Panais	true	racine
31	Pastèque	true	fruit
32	Patate douce	true	racine
33	Patidou	true	racine
34	Piment	true	fruit
35	Poireau	true	fruit
36	Poivron	true	fruit
37	Pomme de terre	true	racine
38	Potimarron	true	fruit
39	Potiron	true	fruit
40	Pâtisson	true	racine
41	Radis	true	racine
42	Roquette	true	feuille
43	Tomate	true	fruit
44	Épinard	true	feuille
45	Engrais verts	true	autres
46	Fleurs	true	autres
47	Radis noir	true	racine
48	Chou-rave	true	feuille
49	Salade	true	feuille
50	Mesclun	true	feuille
51	Herbes aromatiques	true	autres
52	Cébette	true	racine
53	Chou	true	feuille
""", "base.Culture", "culture_default.json"

methodes_data = """
ID	nom
1	Conventionnelle
2	Agriculture Biologique
3	Maraîchage Sol Vivant
4	Agriculture Bio-Dynamique
5	Bio-intensif
6	No-Dig
7	Permaculture
8	Agroforesterie
9	Agriculture de conservation des sols
10	Agriculture de précision
11	Agroécologie
12	Hydroponie
13	Aquaponie
14	Agriculture Syntropique
15	Agriculture régénératrice
16	Agriculture urbaine
""", "base.MethodeAgricole", "methode_agricole.json"

types_data = """
ID	nom
1	Plein champ
2	Tunnel fraisier
3	Tunnel plastique
4	Tunnel multi-chapelle
5	Serre en verre
""", "base.TypeParcelle", "type_parcelle.json"

unites_data = """
ID	nom	recolte_compatible
1	kg	true
2	pièces	true
3	bottes	true
4	plants	false
5	caisses	true
6	m²	false
7	mètres	false
8	hectares	false
9	pots	false
10	terrines	false
11	plaques	false
12	paniers	true
13	godets	false
14	litres	false
15	lignes	false
""", "base.Unite", "unite.json"

datas = [activites_data, cultures_data, methodes_data, types_data, unites_data]

def get_data():
    # Traitement
    for data in datas:
        dataset = data[0]
        model = data[1]
        output_file = data[2]
        lines = dataset.strip().split("\n")
        output_path_full = "./{}".format(output_file)

        # Construction du JSON
        json_output_full = []
        for idx, line in enumerate(lines):
            rows = line.split("\t")
            if idx == 0:
                row_labels = rows
                continue # en tête
            output = {
                "model": model,
                "pk": int(rows[0]),
                "fields": {}
            }
            for row_idx, row in enumerate(rows):
                if row_idx == 0:
                    continue # ID field
                value = row.strip()
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                output["fields"][row_labels[row_idx]] = value
            json_output_full.append(output)

        # Sauvegarde
        with open(output_path_full, "w", encoding="utf-8") as f:
            json.dump(json_output_full, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    get_data()
