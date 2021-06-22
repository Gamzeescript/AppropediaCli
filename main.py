from flask import Flask, render_template, request, Response
from urllib.request import urlopen, Request
from decouple import config as config_decouple
import requests
import json
import csv
import os.path
import os
import re

def create_app(enviroment):
    app = Flask(__name__)
    app.config.from_object(enviroment)

    with app.app_context():
        db.init_app(app)
        db.create_all()

    return app

enviroment = config['development']
if config_decouple('PRODUCTION', default=False):
    enviroment = config['production']

app = create_app(enviroment)

#Funcion que convierte los datos en cadena de textos separadas en espacios
# Function to convert  
def listToString(s):    
    # initialize an empty string
    str1 = ""     
    # traverse in the string 
    for ele in s: 
        str1 += ele+" "       
    return str1

#Funcion que convierte los datos en cadena de textos separadas en |
# Function to convert  
def listToString2(s):     
    # initialize an empty string
    str1 = ""     
    # traverse in the string 
    for ele in s: 
        str1 += ele+"|"     
    return str1


#/--------------------ARREGLOS AUXILIARES--------------------/
#Arreglo donde guardara los datos extraidos de la cadena content
data = []
#Arreglo donde guardara los encabezados del archivo csv
header = ['image', 'caption', 'keywords', 'uses', 'instance-of', 'date-completed', 'date-published', 'date-updated', 'sdg']
#Arreglo donde guardara los nombres de las imagenes
images = []
#Arreglo donde guardara las caption de las imagenes
captions = []
#Arreglo donde guardara los keywords
keyAllArray = []
#Arreglo donde guardara las fechas de actualizaciones
updates = []

app = Flask(__name__, template_folder="template")


@app.route("/", methods = ["POST", "GET"])
def home():
    if request.method == "POST":
        param = request.form ["param"]
        escape = " "
        articulo = param.replace(escape, '%20')
        url = 'https://www.appropedia.org/w/api.php?action=query&prop=revisions&titles='+articulo+'&rvslots=*&rvprop=content&format=json'
        accessreq = Request(url, headers = {"User-Agent": "Mozilla/5.0"})
        leer = urlopen(accessreq)
        formatojson = json.loads(leer.read())
        milista = []
        for clave in formatojson.items():
            milista.append(clave)
        readytogo = "".join(str(milista))
        
        #mis regex
        #image and caption
        file = re.compile('\[File:.*?\]')      
        #keywords
        keywords = re.compile('(?<=\|keywords =)([^|]+)(?=\|)')
        #uses
        uses = re.compile('(?<=\|uses =)([^|]+)(?=\|)')
        #instance-of
        partoff = re.compile('(?<=\|part-of =)([^}]+)(?=\})')
        #date-completed
        completed = re.compile('(?<=\|completed =)([^}]+)(?=\})')
        #date-published
        published = re.compile('(?<=\|published =)([^|]+)(?=\|)')
        #date-updated
        update = re.compile('(?<=\=Update)([^=]+)(?=\=)')
        #sdg
        sdg = re.compile('(?<=\|sdg =)([^|]+)(?=\|)')

        #/--------------------EXTRACCION DE LA CADENA--------------------/
        #Variable que extrae el match o lo que acierta del regex file
        files = re.findall(file, readytogo)
        #Variable que extrae el match o lo que acierta del regex keywords
        keywordsAll = re.findall(keywords, readytogo)
        #Variable que extrae el match o lo que acierta del regex sdg
        SDGs = re.findall(sdg, readytogo)
        #Variable que extrae el match o lo que acierta del regex published
        datePublished = re.findall(published, readytogo)
        #Variable que extrae el match o lo que acierta del regex uses
        usesAll = re.findall(uses, readytogo)
        #Variable que extrae el match o lo que acierta del regex completed
        dateCompleted = re.findall(completed, readytogo)
        #Variable que extrae el match o lo que acierta del regex partof
        partedof = re.findall(partoff, readytogo)
        #Variable que extrae el match o lo que acierta del regex partof
        dateupdated = re.findall(update, readytogo)

                #/--------------------IMPRESION DE LA CADENA--------------------/
        #Imprimimos lo que se obtuvo en la variable files
        for a in files:
            string = str(a)[6:-1]
            b = string.split('|')
            b1 = b[0]
            images.append(b1)	
        #Imprimimos lo que se obtuvo en la variable files
        for k in files:
            string = str(a)[6:-1]
            l = string.split('|')
            l1 = b[2]
            l2 = str(l1)[7:]
            captions.append(l2)
        #Imprimimos lo que se obtuvo en la variable keywordsAll
        for c in keywordsAll:
            string = str(c)[1:-1]
            d = string.split(', ')
            for element in d:
                keyAllArray.append(element)
        #Imprimimos lo que se obtuvo en la variable usesAll
        for g in usesAll:
            string = str(g)[1:-1]
            data.append(string.rstrip())
        #Imprimimos lo que se obtuvo en la variable partedof
        for i in partedof:
            string = str(i)[1:-1]
            data.append(string.rstrip())
        #Imprimimos lo que se obtuvo en la variable dateCompleted
        for h in dateCompleted:
            string = str(h)[1:-1]
            data.append(string.rstrip())
        #Imprimimos lo que se obtuvo en la variable datePublished
        for f in datePublished:
            string = str(f)[1:-1]
            data.append(string.rstrip())
        #Imprimimos lo que se obtuvo en la variable updated	
        for j in dateupdated:
            string = str(j)[1:]
            k = string.split('\n')
            updates.append(k[0])
        #Imprimimos lo que se obtuvo en la variable SDGs
        for e in SDGs:
            string = str(e)[1:-1]
            data.append(string.rstrip())

        #/--------------------CONVERSION DE LISTAS EN CADENAS DE TEXTOS--------------------/
        #Variable donde guardara la conversion del arreglo images
        imagestr = listToString2(images)
        #Variable donde guardara la conversion del arreglo captions
        captionstr = listToString2(captions)
        #Variable donde guardara la conversion del arreglo keyAllArray
        keywordstr = listToString2(keyAllArray)
        #Variable donde guardara la conversion del arreglo updates
        updatestr = listToString2(updates)
        #Agregamos la cadena de texto en la posición determinada por el posicion del elemento image dentro del header
        data.insert(header.index('image'), str(imagestr)[:-1])
        #Agregamos la cadena de texto en la posición determinada por el posicion del elemento caption dentro del header
        data.insert(header.index('caption'), str(captionstr)[:-1])
        #Agregamos la cadena de texto en la posición determinada por el posicion del elemento keywords dentro del header
        data.insert(header.index('keywords'), str(keywordstr)[:-1])
        #Agregamos la cadena de texto en la posición determinada por el posicion del elemento date-updated dentro del header
        data.insert(header.index('date-updated'), str(updatestr)[:-1])
        #Variable donde guardara la conversion del arreglo header ()
        headerstr = listToString(header)
        #Variable donde guardara la conversion del NUEVO arreglo data
        datastr = listToString(data)
        #Imprimimos lo que se obtuvo en la variable headerstr	
        print(headerstr)
        #Imprimimos lo que se obtuvo en la variable datastr	
        print(datastr)


        csv = headerstr+'\n'+datastr+'\n'
        return Response(csv, mimetype="text/csv", headers={"Content-disposition":"attachment; filename=resultadobusqueda.csv"})
    else:
        return render_template("formulario.html")

if __name__ == "__main__":
    app.run(debug = True)