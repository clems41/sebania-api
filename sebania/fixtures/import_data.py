# Reprise de l'ensemble des données en intégrant toutes les lignes (1 à 57) correctement
import json

# Données reformatées en dur, version complète
activites_data = """
ID	nom	default	categorie_default	mots_cles	niveau_complexite	unites
1	Production de plant	true	production	semis,pépinière,jeunes,plants,rempotage,bouturage	6	[4,9,10,11,13]
2	Travail du sol	true	production	préparation sol,labour,motoculteur,rotavateur,grelinette,Actisol,Canadien,tracteur,outil,engin	3	[]
3	Apport de MO (Amender)	true	production	compost,fumier,amendement,apport,mo,matière,organique,broyat,épandeur,tracteur,brouette,rateau	4	[1,16,18,19]
4	Fertilisation	true	production	engrais,nutriments,sol,apport,granulé,NPK,azote,oligo,oligoéléments,lisier	8	[1,14,16]
5	Paillage	true	production	paille,mulch,BRF,Broyat,couvrir	8	[1,6,7,16,18,19]
6	Bâchage	true	production	bâche,occultation,désherbage,plastique,tissée,enterrer	4	[6]
7	Semis direct	true	production	graines,ligne,plantation,volée,semoir,en place,monorang,multirang	8	[17]
8	Plantation	true	production	plants,repiquage,cultures,implantation,motte,jeune plant,godets	8	[17]
9	Gestion climatique	true	production	serre,température,ventilation,voilage,voile,thermique,ouvrant,moteur,portes,ouvrir	3	[]
10	Gestion des bioagresseurs	true	production	insectes,maladies,traitements,phyto,sanitaire,lutte,filets,pulvériser,mélange,dose	7	[]
11	Irrigation	true	production	arrosage,goutte,eau,tuyau,aspersion,planifier	7	[]
12	Désherbage	true	production	mauvaises,herbes,sarclage,binage,manuel,mechanique,pulvériser	7	[]
13	Taille	true	production	élagage,coupe,entretien,forme,égourmandage,effeuillage,étêtage	7	[]
14	Palissage	true	production	ficelle,tuteur,support,dérouler	7	[]
15	Destruction de culture	true	production	arrachage,broyage,roulage,nettoyage,engrais,verts	7	[]
16	Suivi de culture	true	production	observation,croissance,planning,planification,tour du champ,tour,regarder,checker	7	[]
17	Récolte	true	production	cueillette,maturité,rendement,poids,caisse,retirer,bottes	8	[1,2,3,5,12]
18	Nettoyage	true	production	outils,matériel,hygiène,propreté,parer,parage,nettoyeuse,laver,lavage,station,lavabo,process,eau,passe à l'eau,enlever,terre	1	[]
19	Livrer	true	commercialisation	transport,distribution,clients,camion,fourgon,livraison,apporter,donner	6	[1,2,3,5,12]
20	Stockage	true	commercialisation	chambre,froide,entrepôt,conservation,logistique,mise en caisse,emballage	6	[1,2,3,5,12]
21	Charger / Décharger	true	commercialisation	logistique,palettes,livraison,chercher	6	[1,2,3,5,12]
22	Communication / Marketing	true	commercialisation	réseaux,sociaux,clients,marketing,emails,courriers,presse,interview,radio,mail,mailling,list,whatsapp,message	1	[]
23	Marché	true	commercialisation	stand,vente,dépot,préparer	6	[1,2,3,5,12]
24	Vente directe	true	commercialisation	client,ferme,circuit,court,ferme,place,sur	6	[1,2,3,5,12]
25	Panier AMAP	true	commercialisation	abonnement,distribution,consommateurs,commandes	6	[1,2,3,5,12]
26	Gestion des stocks	true	commercialisation	inventaire,produits,suivi,logistique	5	[]
27	Préparation de commande	true	commercialisation	tri,pesée,conditionnement,cagettes,paniers,liste	6	[1,2,3,5,12]
28	Comptabilité	true	administratif	bilan,facturation,gestion,impôts	1	[]
29	Administratif	true	administratif	papier,déclarations,dossiers,impôts	1	[]
30	Planifier	true	administratif	agenda,planning,tâches,planification,calendrier,rotation,assolement	1	[]
31	Veille	true	administratif	informations,réglementations,tendances	1	[]
32	Achat / Commande	true	administratif	fournisseurs,approvisionnement,matériel	6	[1,2,3,4,5,12,14,19]
33	Ranger	true	général	outils,local,organisation,ordre,classer	3	[]
34	Accueil du public	true	général	visite,communication,pédagogie	3	[]
35	Réparer	true	général	bricolage,maintenance,outils	3	[]
36	Construire	true	général	bâtiment,abri,bricolage,serre,outils,aménagements	3	[]
37	Aménager	true	général	organisation,espace,infrastructure	3	[]
38	Entretenir	true	général	propreté,maintenance,suivi,tailler,élaguer	3	[]
39	Formation	true	général	apprentissage,stage,cours,études	1	[]
40	Accompagnement	true	général	pédagogie,conseil,suivi,aide	5	[]
41	Production de compost	true	général	déchets,fertilité,mo,matière,organique	2	[1,16,19]
42	Gestion des intrants	true	général	engrais,semences,stockage,mo,matière,organique,brf,essence,gasoil,phyto,produits,voiles	8	[1,14,16,19]
43	Réunions	true	général	équipe,planning,communication,discussions,rencontres	1	[]
44	Volailles	true	secondaire	poules,œufs,élevage,viande,oeufs	2	[1,2,5]
45	Floriculture	true	secondaire	fleurs,décoration,culture,bouquet	1	[]
46	Brassiculture	true	secondaire	bière,brassage,fermentation	2	[14]
47	Apiculture	true	secondaire	abeilles,miel,ruche	2	[1,2,5,14,19]
48	Champignons	true	secondaire	myciculture,substrat,cave	2	[1,2,5,14,19]
49	Boissons	true	secondaire	jus,sirop,fermentation,alccol	2	[1,2,5,14,19]
50	Conserves	true	secondaire	transformation,bocaux,stérilisation	2	[1,2,5,14,19]
51	Boulangerie	true	secondaire	pain,four,farine	2	[1,2,5,14,19]
52	Verger	true	secondaire	arbres,fruits,taille	2	[1,2,5,14,19]
53	Semences	true	secondaire	graines,reproduction,sélection,production	6	[1,5]
54	Atelier pédagogique	true	secondaire	scolaire,animation,formation	3	[]
55	Auxiliaires de culture	true	production	insectes,utiles,lutte,biologique,biodiversité	7	[]
56	Transformation	true	secondaire	atelier,produits,agroalimentaire,conserves	6	[1,2,5,9,10,12,14,19]
57	Activités syndicales	true	secondaire	syndicat,agriculture,droits,FNSEA,Conf,JA,Jeunes agriculteurs	1	[]
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
ID	nom
1	kg
2	pièces
3	bottes
4	plants
5	caisses
6	m²
7	m
8	hectares
9	pots
10	terrines
11	plaques
12	paniers
13	godets
14	litres
15	lignes
16	brouettes
17	planches
18	cm
19	tonnes
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
                elif "[" in value and "]" in value:
                    value = json.loads(value)
                output["fields"][row_labels[row_idx]] = value
            json_output_full.append(output)

        # Sauvegarde
        with open(output_path_full, "w", encoding="utf-8") as f:
            json.dump(json_output_full, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    get_data()
