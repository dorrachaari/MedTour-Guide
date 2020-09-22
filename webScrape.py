import os
import pandas as pd
import numpy as np
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

########### our function #####################


# Read a file and convert each line to list items
def file_to_list(file_name):
    results =[]
    with open(file_name, 'rt') as f:
        for line in f:
            results.append(line.replace('\n', ''))
    return results

#collecter les noms des fichers qui contiennet dans un directory
def folder_name(directory):
    filenames= os.listdir (directory) # get all files' and folders' names in this directory
    siteCrawled = []
    for filename in filenames: # loop through all the files and folders
        filePath=os.path.join(os.path.abspath(directory), filename)
        if os.path.isdir(filePath): # check whether the current object is a folder or not
            siteCrawled.append(filePath)
    return siteCrawled


########## start web Scrape ##################


#collecter les nom des ficher dans "..\siteCrawled"
siteCrawled=folder_name("..\webCrawler\siteCrawled")
rows=[]
#travail à faire pour chaque ficher(ou agence)
for folder in siteCrawled:
    
    #read crawled.txt file
    allUrls=file_to_list(folder+"\crawled.txt")
    
    #extraction du url
    base_url=allUrls[0]
    print(base_url)
    #extraction du nom d'agence
    i=base_url.find('.')+1
    j=base_url[i:].find('.')
    nomAgence=base_url[i:i+j]
    print(nomAgence)
    
    #chercher le url qui contient les interventions et tarifs et l'existance de temoignage
    tarifUrl=''
    temoignage=0
    for url in allUrls:
        if(url.find("tarif")!=-1):
            tarifUrl=url
        elif(url.find("temoignage")!=-1):
            temoignage=1
        if(temoignage and tarifUrl):
            break
             
    #extraction Nombre d'interventions et Moyenne des prix
    nbInterventions=0
    prix=0
    if(tarifUrl):
        read_table = pd.read_html(tarifUrl)
        for table in read_table:
            colonnePrix=list(table.iloc[:,1].values)
            for ch in colonnePrix:
                ch=str(ch)
                fin=0
                if ch.find("$")!=-1:
                    fin=ch.index("$")
                elif ch.find("€")!=-1:
                    fin=ch.index("€")
                debut=fin
                while (not(ch[debut-1].isalpha()) and debut!=0):
                    debut-=1
                if(debut!=fin):
                    chainePrix=ch[debut:fin].replace(" ","")
                    #print(chainePrix)
                    prix+=int(chainePrix)
                    nbInterventions+=1
        moyPrix=prix//nbInterventions
    #remplissage de row(row sera une ligne dans la base)
    row=[]
    row.append(nomAgence)
    row.append(base_url)
    row.append(nbInterventions)
    row.append(moyPrix)
    row.append(temoignage)
    #rows contient des ligne de la base
    rows.append(row)


#creation et remplissage finale de la base
dataset=pd.DataFrame(rows,columns=["Agency_Name","url","Number_of_interventions","Price_Average","Reviews"])
#to csv file
dataset.to_csv('realbase.csv', encoding='UTF-8',index=False)
