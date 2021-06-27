import json,sqlite3


def test_mutant(app, client):
    res = client.post('/mutant',data='{"dna":["CCCC","CAGC","TTAC","AAAA"]}',content_type='application/json')
    assert res.status_code == 200
    
def test_human(app, client):
    res = client.post('/mutant',data='{"dna":["ATGC","CAGC","TTAC","AAAA"]}',content_type='application/json')
    assert res.status_code == 403

def test_stats(app, client):
    res = client.get('/stats')
    assert res.status_code == 200 
    assert b"count_human_dna" in res.data 
    assert b"count_mutant_dna" in res.data 
    assert b"ratio" in res.data 

def test_dbcache(app, client):
    con = sqlite3.connect('dna.db')
    cursor = con.cursor()
    assert len(list(cursor.execute('SELECT * FROM dna'))) >= 2 