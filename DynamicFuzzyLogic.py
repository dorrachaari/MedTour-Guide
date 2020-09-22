import skfuzzy as fuzz 
from skfuzzy import control as ctrl  
import csv
import pandas as pd
import numpy as np

def dismal(choosen):
        choosen.append("dismal")

def poor(selected,choosen):
        if (selected>=5):
                choosen.append("poor")

def mediocre(selected,choosen):
        if (selected>=3):
                choosen.append("mediocre")

def average(selected,choosen):
        if(selected%2==0):
                choosen.append("average")  

def decent(selected,choosen):
        if (selected>=3):
                choosen.append("decent")

def good(selected,choosen):
        if (selected>=5):
                choosen.append("good")

def excellent(choosen):
        choosen.append("excellent")

def rule (i,L,liste):
        classes=["bad","good"]
        return "ctrl.Rule(" +(" & ".join(["%s['%s']" % (liste[i],classes[L[i]]) for i in range(len(L)) ]))

def rank(liste):
        #Import the database
        data=pd.read_csv("base.csv",index_col=None)
        features=list(data.columns)
        nbFeature=len(liste)

        #Declaration of the consequent Score which ranges from  to 100
        Score = ctrl.Consequent(np.arange(0, 101, 0.1), 'Score')

        #Score_classes are "dismal","poor","mediocre","average","decent","good","excellent"
        choosen=[]#to store the classes of the scoore depending on the number of  features selected  
        dismal(choosen)    
        poor(nbFeature,choosen)
        mediocre(nbFeature,choosen)    
        average(nbFeature,choosen)
        decent(nbFeature,choosen)
        good(nbFeature,choosen)
        excellent(choosen)
        #the classes of the score are done being stored

        #Define the universe of each class of the consequent score
        a=0
        b=0
        c=100//nbFeature+1
        for m in choosen:
                Score[m]=fuzz.trimf(Score.universe,[a,b,c])#each class is being assigned to a universe
                a=b
                b=c
                if(m=="excellent"):
                        c=100
                else:
                        c=c+100//nbFeature+1
        #the assigment of the universes is done

        #Define the universe and the clases  of each antecedent (feaatures)
        for name in liste :
                highest=data[name].max()
                lowest=data[name].min()
                exec(name+"=ctrl.Antecedent(np.arange(lowest, highest+1, 1), name)")
                if ("prix" in name.lower()):
                        exec(name+"['bad'] = fuzz.trimf("+name+".universe, [lowest,highest,highest])")
                        exec(name+"['good'] = fuzz.trimf("+name+".universe, [lowest, lowest, highest])")
                else:
                        exec(name+"['bad'] = fuzz.trimf("+name+".universe, [lowest,lowest,highest])")
                        exec(name+"['good'] = fuzz.trimf("+name+".universe, [lowest, highest, highest])")
        #the antecedent are defined

        #automatically generates the rules
        rules=[]
        classes=["bad","good"]
         
        i=0
        for k in range (0,pow(2,nbFeature)):
                pas=pow(2,nbFeature)
                count=0
                L=[]
                for v in range(0,nbFeature):
                        pas=pas//2
                        if ((k // pas)%2 ==0):
                                L.append(0)
                        else :
                                count+=1
                                L.append(1)
                rules.append(eval(rule(i, L,liste)+" , Score['%s'])" %choosen[count]))
                i+=1
        scoring_ctrl = ctrl.ControlSystem(rules)
        scoring = ctrl.ControlSystemSimulation(scoring_ctrl)
        #the rules are done being generated

        #Our inputs extracted from the database
        scores=[] #table of scores of each row of the database
        for i in data.itertuples():
                for m in liste:
                        scoring.input[m] = i[features.index(m)+1]
                scoring.compute()
                scores.append(scoring.output['Score'])
        #add new column to dataset and sort rows 
        data['Scores']=scores
        data=data.sort_values(by=['Scores'],ascending=False)
        data.to_csv('sortedbase.csv', encoding='UTF-8',index=False)

