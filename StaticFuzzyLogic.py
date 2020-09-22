import numpy as np
import skfuzzy as fuzz 
from skfuzzy import control as ctrl  
import csv
import pandas as pd


#Import the database
data=pd.read_csv("base.csv",index_col=None)

#Extract highest and lowest value of each feature

#Intervention
highestNbIntervention=data["NombreInterventions"].max()
lowestNbIntervention=data["NombreInterventions"].min()

#Moyenne prix
highestMoyPrix=data["MoyennePrix"].max()
lowestMoyPrix=data["MoyennePrix"].min()

#Nombre phtos before/after
highestNbPhoto=data["NombrePhotosBA"].max()
lowestNbPhoto=data["NombrePhotosBA"].min()

#Nombre de medecins dans l'equipe
highestNbMdcn=data["NombreMedecins"].max()
lowestNbMdcn=data["NombreMedecins"].min() 

#Moyenne d'années d'experience dans l'equipe
highestMoyExperience=data["MoyenneAnneesExperience"].max()
lowestMoyExperience=data["MoyenneAnneesExperience"].min()

#Temoignage takes 0 if it doesn't exist and 1 if it does


# New Antecedent objects hold universe variables and membership
Interventions = ctrl.Antecedent(np.arange(lowestNbIntervention, highestNbIntervention+1, 1), 'Interventions')
Prix = ctrl.Antecedent(np.arange(lowestMoyPrix, highestMoyPrix+1, 1), 'Prix')
Photos = ctrl.Antecedent(np.arange(lowestNbPhoto, highestNbPhoto+1, 1), 'Photos')
Medecins = ctrl.Antecedent(np.arange(lowestNbMdcn, highestNbMdcn+1, 1), 'Medecins')
Experience = ctrl.Antecedent(np.arange(lowestMoyExperience, highestMoyExperience+1, 1), 'Experience')
Temoignage = ctrl.Antecedent(np.arange(0, 2, 1), 'Temoignage')

# New Conseuent object hold universe variables and membership
Score = ctrl.Consequent(np.arange(0, 101, 0.1), 'Score')




# Custom membership functions can be built interactively with a familiar,
# Pythonic API
Interventions['bad'] = fuzz.trimf(Interventions.universe, [lowestNbIntervention, lowestNbIntervention,highestNbIntervention ])
Interventions['good'] = fuzz.trimf(Interventions.universe, [lowestNbIntervention, highestNbIntervention, highestNbIntervention])

Prix['bad'] = fuzz.trimf(Prix.universe, [lowestMoyPrix, highestMoyPrix,highestMoyPrix])
Prix['good'] = fuzz.trimf(Prix.universe, [lowestMoyPrix, lowestMoyPrix, highestMoyPrix])

Photos['bad'] = fuzz.trimf(Photos.universe, [lowestNbPhoto, lowestNbPhoto,highestNbPhoto ])
Photos['good'] = fuzz.trimf(Photos.universe, [lowestNbPhoto, highestNbPhoto, highestNbPhoto])

Medecins['bad'] = fuzz.trimf(Medecins.universe, [lowestNbMdcn, lowestNbMdcn,highestNbMdcn ])
Medecins['good'] = fuzz.trimf(Medecins.universe, [lowestNbMdcn, highestNbMdcn, highestNbMdcn])

Experience['bad'] = fuzz.trimf(Experience.universe, [lowestMoyExperience, lowestMoyExperience,highestMoyExperience ])
Experience['good'] = fuzz.trimf(Experience.universe, [lowestMoyExperience, highestMoyExperience, highestMoyExperience])

Temoignage['bad']=fuzz.trimf(Temoignage.universe, [0, 0,1 ])
Temoignage['good'] = fuzz.trimf(Temoignage.universe, [0, 1, 1])

Score["dismal"]=fuzz.trimf(Score.universe,[0,0,15])
Score["poor"]=fuzz.trimf(Score.universe,[0,15,30])
Score["mediocre"]=fuzz.trimf(Score.universe,[15,30,45])
Score["average"]=fuzz.trimf(Score.universe,[30,45,60])
Score["decent"]=fuzz.trimf(Score.universe,[45,60,75])
Score["good"]=fuzz.trimf(Score.universe,[60,75,90])
Score["excellent"]=fuzz.trimf(Score.universe,[90,100,100])

#Define the rules automatically
rules=[]
features=["Interventions","Prix","Photos","Medecins","Experience","Temoignage"]
classes=["bad","good"]
def rule (i,*args):
    return "ctrl.Rule(" +(" & ".join(["%s['%s']" % (features[i],classes[args[i]]) for i in range(len(args)) ])) 

def score_class(argument):
    switcher = {
        0: "dismal",
        1: "poor",
        2: "mediocre",
        3: "average",
        4: "decent",
        5: "good",
        6: "excellent",
    }
    return switcher.get(argument)



i = 0
for a in range(0, 2):
    for b in range(0, 2):
        for c in range(0, 2):
            for d in range(0, 2):
                for e in range(0, 2):
                    for f in range(0,2):
                        count=a+b+c+d+e+f
                        rules.append(eval(rule(i, a, b, c, d, e,f)+" , Score['%s'])" %score_class(count)))
                        i += 1
scoring_ctrl = ctrl.ControlSystem(rules)
scoring = ctrl.ControlSystemSimulation(scoring_ctrl)

#Our inputs extracted from the database
scores=[] #table of scores of each row of the database
for i in data.itertuples():
    scoring.input['Interventions'] = i[2]
    scoring.input['Prix'] = i[3]
    scoring.input['Photos'] = i[4]
    scoring.input['Medecins'] = i[5]
    scoring.input['Experience'] = i[6]
    scoring.input['Temoignage'] = i[7]
    scoring.compute()
    scores.append(scoring.output['Score'])
    
#add new column to dataset and sort rows 
data['Scores']=scores
data=data.sort_values(by=['Scores'],ascending=False)
print(data)

data.to_csv('sortedbase.csv', encoding='UTF-8',index=False)