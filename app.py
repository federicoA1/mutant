import flask
from flask import request, jsonify
import json,hashlib,sqlite3,os

# This script might return false positives when the dna have long secuences of the same base, ie (longer than 4 rows/columns/diagonals with the same char): 
#                       
#[['C' 'C' 'C' 'G' 'C']
# ['C' 'A' 'A' 'G' 'A']
# ['A' 'A' 'A' 'A' 'A'] <-
# ['A' 'C' 'C' 'A' 'A']
# ['A' 'G' 'C' 'A' 'G']]
# We can simple store each secuence coordinates found, in a found list, and check if it's there before start checking or before


app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/installDB', methods=['GET'])
def Install():
    con = sqlite3.connect('dna.db')
    con.execute('''CREATE TABLE IF NOT EXISTS dna
               (id INTEGER PRIMARY KEY AUTOINCREMENT, type INT,hash TEXT UNIQUE, dna text)''')
    os.system("cp dna.db /tmp/dna.db")    
    return ('',200)              

def AddDNA(DNAtype,DNAseq):
    #Insert a DNA to the database.

    #Parameters:
    #    DNAtype (int):The type of the DNA
    #    DNAseq (str):The DNA sequence

    #Returns:
    #    None.   
    con = sqlite3.connect('/tmp/dna.db')
    hash_object = hashlib.md5(DNAseq.encode()).hexdigest()
    con.execute("INSERT OR IGNORE INTO dna (type,dna,hash) VALUES(?,?,?)",(DNAtype,DNAseq,hash_object))
    con.commit()

def DNAInDB(DNAseq):
    #Check if DNA is in the database.

    #Parameters:
    #    DNAseq (str):The DNA sequence

    #Returns:
    #    Type Of DNA(int):The type of the DNA.  
    con = sqlite3.connect('/tmp/dna.db')
    hash_object = hashlib.md5(DNAseq.encode()).hexdigest()
    cursor = con.cursor()
    cursor.execute("SELECT type FROM dna WHERE hash=?",(hash_object,))
    row = cursor.fetchone()
    if (row is None):
        return 0
    else:
        return row[0]

@app.route('/mutant', methods=['POST'])
def isMutant():
    #Check if DNA is Mutant.

    #Parameters:
    #    dna (str):The DNA sequence in JSON

    #Returns:
    #    HTTPResponse(int):200 for Mutant DNA, 403 for Human DNA.  

    requestData = request.get_json()
    
    if requestData is None:
        return ('',403)

    dna = requestData['dna']
    
    n = len(dna)
    n2 = len(dna[0])
    #if less than 4 then it's false (or we can return custom errors)
    if (n<4) or (n2<4) or (n != n2):
        AddDNA(0,json.dumps(dna))
        return ('',403)
    
    #if it's not a square, return false (or we can return custom errors)
    IsDNAInDB = DNAInDB(json.dumps(dna))
    
    
    #is a stored mutant dna
    if (IsDNAInDB == 2):
        return ('',200)
    #is a human dna    
    if (IsDNAInDB == 1):
        return ('',403)
        
    mutantGenes = 0
    i = 0
    j = 0
    
    while i< n:
        j=0
        while j< n:
            
            #diagonal match
            if (i<= n-4) and (j <= n-4):
                #print(dna[i][j],dna[i+1][j+1],dna[i+2][j+2],dna[i+3][j+3])
                if (dna[i][j] == dna[i+1][j+1]) and (dna[i][j] == dna[i+2][j+2]) and (dna[i][j] == dna[i+3][j+3]):
                    mutantGenes = mutantGenes+1

            #Linear matches
            if (j <= n-4):
                #print(dna[i][j],dna[i][j+1],dna[i][j+2],dna[i][j+3])
                if (dna[i][j] == dna[i][j+1]) and (dna[i][j] == dna[i][j+2]) and (dna[i][j] == dna[i][j+3]):
                    mutantGenes = mutantGenes+1    
              
            if (i <= n-4):
                #print(dna[i][j],dna[i+1][j],dna[i+2][j],dna[i+3][j])
                if (dna[i][j] == dna[i+1][j]) and (dna[i][j] == dna[i+2][j]) and (dna[i][j] == dna[i+3][j]):
                    mutantGenes = mutantGenes+1
            #print(mutantGenes)
            if (mutantGenes >= 2):
                 #Found mutant dna, 200
                 AddDNA(2,json.dumps(dna))
                 return ('',200)
            j = j+1
        i = i+1
    #did not found mutant dna, 403 Forbidden
    AddDNA(1,json.dumps(dna))
    return ('',403)

@app.route('/stats', methods=['GET'])
def stats():
    countMutantDNA = 0
    countHumanDNA = 0
    # We can implement cache here so we only do the queries when it's necesary
    con = sqlite3.connect('/tmp/dna.db')
    cursor = con.cursor()
    cursor.execute("SELECT COUNT(*) as CountHumanDNA FROM dna WHERE type=1")
    row = cursor.fetchone()
    if (row is not None):
        countHumanDNA = row[0]
    
    cursor.execute("SELECT COUNT(*) as CountMutantDNA FROM dna WHERE type=2")
    row = cursor.fetchone()
    if (row is not None):
        countMutantDNA = row[0]

    if (countHumanDNA == 0):
        #here we can return a custom error
        Ratio = 0
    else:
        Ratio = round(countMutantDNA / countHumanDNA,2)
    
    results = {"count_mutant_dna":countMutantDNA,"count_human_dna":countHumanDNA,"ratio":Ratio}
    
    return jsonify(results),200


if __name__ == '__main__':
    app.run(debug=True)   