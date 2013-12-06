#!/usr/bin/python

from sys import argv
from struct import pack
import requests
import json
import string
import re
import copy
import math

# VERSION 0.1

# TODO - legge inn stoette for kommado linje parametere for fylker, antall,
#        filnavn, etc..

shit = """{
    "sokeObjekt": {
        "lokasjon": {
            "fylke": [
                1
            ]
        }, 
        "objektTyper": [
            {
                "id": 105, 
                "antall": 1
            }
        ]
    }, 
    "resultater": [
        {
            "typeId": 105, 
            "statistikk": {
                "antallFunnet": 37674, 
                "antallReturnert": 1, 
                "totalStrekningslengde": 9730708.0, 
                "returnertStrekningslengde": 224.0
            }, 
            "vegObjekter": [
                {
                    "versjonsId": 1, 
                    "startDato": "Wed Jul 01 00:00:00 CEST 2009", 
                    "self": {
                        "typeId": 105, 
                        "typeNavn": "Fartsgrense", 
                        "uri": "/vegobjekter/objekt/234359814"
                    }, 
                    "definisjon": {
                        "typeId": 105, 
                        "typeNavn": "Fartsgrense", 
                        "uri": "/datakatalog/objekttyper/105"
                    }, 
                    "lokasjon": {
                        "fylke": {
                            "nummer": 1, 
                            "navn": "\u00d8STFOLD"
                        }, 
                        "vegReferanser": [
                            {
                                "status": "V", 
                                "nummer": 2930, 
                                "fylke": 1, 
                                "kommune": 4, 
                                "hp": 1, 
                                "fraMeter": 0, 
                                "tilMeter": 224, 
                                "kategori": "K"
                            }
                        ], 
                        "kommune": {
                            "nummer": 104, 
                            "navn": "MOSS"
                        }, 
                        "region": {
                            "nummer": 1, 
                            "navn": "\u00d8ST"
                        }, 
                        "geometriUtm33": "LINESTRING (253230.300048828 6601724.30004883, 253227 6601724.90002441, 253224.599975586 6601725.19995117, 253219.800048828 6601725.80004883, 253214 6601725.90002441, 253208.699951172 6601725.40002441, 253203.900024414 6601724.59997559, 253197.599975586 6601723.80004883, 253190.400024414 6601722.19995117, 253181.400024414 6601720.19995117, 253169.800048828 6601717.69995117, 253157.699951172 6601715.40002441, 253144.5 6601712.90002441, 253132.699951172 6601710.80004883, 253123.300048828 6601709, 253113.099975586 6601707.30004883, 253106.300048828 6601706.09997559, 253098.099975586 6601704.69995117, 253092.199951172 6601703.90002441, 253087.199951172 6601703.90002441, 253081.900024414 6601704.19995117, 253074.800048828 6601705.30004883, 253068.699951172 6601706.80004883, 253061.699951172 6601709.30004883, 253056.800048828 6601711.69995117, 253051.099975586 6601715, 253047.099975586 6601717.80004883, 253041.199951172 6601723, 253036.199951172 6601727.90002441, 253030.099975586 6601734.30004883, 253022.5 6601743.09997559)", 
                        "politiDistrikt": {
                            "nummer": 2, 
                            "navn": "\u00d8stfold"
                        }, 
                        "geometriWgs84": "LINESTRING (10.641823009706423 59.48117717910398, 10.64176423025647 59.48118061129804, 10.641721639404787 59.48118188593245, 10.641636459560116 59.481184437417284, 10.641534253950647 59.48118192278366, 10.641441542548163 59.481174329849004, 10.641357980901365 59.4811643442481, 10.641248014668545 59.48115347770905, 10.641123133659017 59.48113491725283, 10.640967031381521 59.4811117175739, 10.64076574374576 59.48108251192931, 10.640555422301826 59.481054803343504, 10.640325973454113 59.481024656189135, 10.640120702903637 59.48099891371759, 10.639957331972502 59.48097726802595, 10.639779761382483 59.480956047795814, 10.639661460467561 59.48094130303586, 10.639518746297957 59.48092394428955, 10.63941582249348 59.480913311505226, 10.63932781551792 59.480910370552685, 10.63923418263326 59.48090993865635, 10.639107941147993 59.48091561256554, 10.63899883644409 59.48092545523427, 10.638872735766281 59.48094372240208, 10.638783715384445 59.48096232860538, 10.638679569810208 59.480988523897466, 10.638605926024058 59.48101124227075, 10.63849606353537 59.48105433143393, 10.638402389387805 59.481095264474696, 10.63828761899683 59.481148981225914, 10.638143670280183 59.48122330395726)", 
                        "vegAvdeling": {
                            "nummer": 1, 
                            "navn": "\u00d8stfold"
                        }, 
                        "veglenker": [
                            {
                                "til": 1.0, 
                                "fra": 0.0, 
                                "direction": "AGAINST", 
                                "id": 1824314
                            }
                        ]
                    }, 
                    "modifisert": "2009-12-02T10:59:35+01:00", 
                    "egenskaper": [
                        {
                            "enumVerdi": {
                                "verdi": "30", 
                                "id": 2726, 
                                "kortVerdi": "30"
                            }, 
                            "verdi": "30", 
                            "definisjon": {
                                "uri": "/datakatalog/egenskapstype/2021"
                            }, 
                            "id": 2021, 
                            "navn": "Fartsgrense"
                        }, 
                        {
                            "enumVerdi": {
                                "verdi": "Nei", 
                                "id": 6699, 
                                "kortVerdi": "n"
                            }, 
                            "verdi": "Nei", 
                            "definisjon": {
                                "uri": "/datakatalog/egenskapstype/5125"
                            }, 
                            "id": 5125, 
                            "navn": "Utg\u00e5r_Variabel fartsgrense"
                        }
                    ], 
                    "objektTypeId": 105, 
                    "objektTypeNavn": "Fartsgrense", 
                    "objektId": 234359814, 
                    "strekningslengde": 224.0
                }
            ]
        }
    ], 
    "totaltAntallReturnert": 1
}"""

def sok( objektTyper, lokasjon=''):
    # Se https://www.vegvesen.no/nvdb/api/sok for definisjon av
    # objektliste (obligatorisk) og lokasjon (valgfritt).

    url = 'https://www.vegvesen.no/nvdb/api/sok'
    if lokasjon: # Valgfritt
        sok = { 'lokasjon' : lokasjon,
                'objektTyper' : objektTyper
                }
    else:
        sok = { 'objektTyper' : objektTyper }

    headers = { 'Accept' : 
                   'application/vnd.vegvesen.nvdb-v1+json' }

    sok = json.dumps(sok)

    # Fornuftig feilhaandtering maa tilpasses rammeverket 
    # som bruker funksjonen
    try:
        r = requests.get( url, params = { 'kriterie' : sok }, 
                         headers = headers,  verify = False )
                            # verify=False pga sertifikatfeil 
                            # akkurat naa (fikses snart?)
    except Exception, e:
       print str(e)
       return False

    # Har vi faatt det vi vil ha?
    if (r.status_code != 200) or (r.headers['content-type'] !=
                       'application/vnd.vegvesen.nvdb-v1+json'):
        print "Not the right kind of response: ", \
              r.status_code, " ", r.headers['content-type']
        return False
    else:
        return r.json()


                                        ###___ MAIN __###
fylker = [5]
if len(argv) > 1:
    fylker = map(int, argv[1:])

data1 = sok( [{'id': 105, 'antall': 1000000}], {'fylke': fylker} )
#data1 = json.loads(shit)

#print json.dumps(data1, indent=4)
#exit(1)

resultater = data1['resultater']

coords = []
print "fylke_" + str(resultater[0]['vegObjekter'][0]['lokasjon']['fylke']['nummer']) + ".bin"
outfile = open("fylke_" + str(resultater[0]['vegObjekter'][0]['lokasjon']['fylke']['nummer']) + ".bin", 'w')
num_nodes = 0
speeds = []

for i in resultater:
    for j in resultater[0]['vegObjekter']:
        coordstmp = re.sub("(MULTI)?LINESTRING ", "", j['lokasjon']['geometriWgs84'])
        coordstmp = re.sub("[\(\),]", "", coordstmp).split()
        coordstmp = map(float, coordstmp)

        coords += (coordstmp)

        for k in j['egenskaper']:
            if "enumVerdi" in k and k['navn'] == "Fartsgrense":
                speeds += [int(k['verdi']) for i in range(0, len(coordstmp)/2)]
print "speed"
for e in speeds:
    print e                
print "num_nodes: %d" % num_nodes
#outfile.write(pack("<I", num_nodes))
outfile.close()

print "totalt antall returnert: " + str(data1['totaltAntallReturnert'])


data1 = sok( [{'id': 775, 'antall': 1000000}], {'fylke': fylker} )
#data1 = json.loads(shit)

print json.dumps(data1, indent=4)
#exit(1)

resultater = data1['resultater']

coords2 = []
outfile = open("fylke_" + str(resultater[0]['vegObjekter'][0]['lokasjon']['fylke']['nummer']) + ".bin", 'w')
num_nodes = 0
for i in resultater:
    for j in resultater[0]['vegObjekter']:
        coordstmp = re.sub("(MULTI)?LINESTRING ", "", j['lokasjon']['geometriWgs84'])
        coordstmp = re.sub("[\(\),]", "", coordstmp).split()
        coordstmp = map(float, coordstmp)
        coords2 += coordstmp
        

        #print coords
        #print ""

        # skriv koordinater og fartsgrense til fil, paa foelgende format:
        # "XYF" X = x-koordinatet, Y = y-koordinatet, F = fartsgrensen
        # big endian fordi java bruker det fremfor little endian
        
newdata = [0 for i in range(0, len(coords)/2)]

itercount = 0
for count in xrange(0, len(coords2), 2):
    distance = 23423423423 # large number
    distanceindex = 0
    #print "%f, %f" %(coords[count+1],coords[count])
    for i in xrange(0, len(coords), 2):
        itercount += 1
        newdistance = ((coords[i]-coords2[count])**2)+((coords[i+1]-coords2[count+1])**2)
        if(newdistance < distance):
            distance = newdistance
            distanceindex = i
    newdata[distanceindex/2] = 1
    print float(count)/len(coords2)

print "len coords: %d" % (len(coords)) 
print "len newdata: %d" % (len(newdata)) 
print "len speeds: %d" % (len(speeds)) 
for e in newdata:
    print e
cunt = 0
for count in xrange(0, len(coords), 2):
    outfile.write(pack("<ddI", coords[count], coords[count + 1], ((speeds[count/2]/10)) | (newdata[count/2]<<4)))
    cunt += 1
print "cunt: %d" %(cunt)
print "num_nodes: %d" % num_nodes
outfile.write(pack("<I", len(coords)/2))
outfile.flush()
outfile.close()
print "totalt antall returnert: " + str(data1['totaltAntallReturnert'])

#for e in newdata:
#    print e

print "itercount: " + str(itercount)
print "len coords: " + str(len(coords))
print "len coords2: " + str(len(coords2))


#
#cunt: 340884
#num_nodes: 0
#totalt antall returnert: 10
#itercount: 686199492
#len coords: 681768
#len coords2: 402

