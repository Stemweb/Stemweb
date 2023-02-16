from flask import Flask, request
from datetime import date
import json
import requests as req

app = Flask(__name__)
STEMWEB_BASE = 'http://stemweb:8000/algorithms'
ALGO_MAP = {'01_rhm': 'RHM', '02_nj': 'Neighbour Joining', '03_nnet': 'Neighbour Net'}

# Check that we are up
@app.get('/')
def index():
    return '<h1>Hello World!</h1>'


# Implement the return path
@app.post('/result')
def receive_result():
    '''Just write the result we get to a file'''
    res = request.get_json()  # will return 400 if it isn't JSON
    runid = res['jobid']
    try:
        with open('received/result-%d-%s.json' % (runid, date.today()), 'w') as f:
            f.write(json.dumps(res, ensure_ascii=False))
    except IOError as e:
        return('File write error: %s' % e.message, 500)
    return('', 200)


@app.get('/query/<jobid>')
def query_job(jobid):
    '''Query a given job ID to see if it finished'''
    r = req.get('%s/jobstatus/%s/' % (STEMWEB_BASE, jobid))
    return _r2flask(r)


# Make one of the test requests
@app.post('/request/<fixid>')
def make_fixture_request(fixid):
    '''Send the content of the appropriate request to the Stemweb server'''
    fixfile = 'requests/%s.json' % fixid
    app.logger.debug('Got fixture file %s' % fixfile)
    algo = [x for x in _get_available() 
            if x['model'] == 'algorithms.algorithm' and x['fields']['name'] == ALGO_MAP[fixid]]
    if len(algo) != 1:
        return('ERROR: algorithm for %s not singled out!' % fixid, 400)
    thisalg = algo[0]
    app.logger.debug('Got algorithm %s' % json.dumps(thisalg))
    with open(fixfile, encoding='utf-8') as f:
        fixdata = json.load(f)
    app.logger.debug('Loaded the fixture data')
    r = req.post('%s/process/%d/' % (STEMWEB_BASE, thisalg['pk']), json=fixdata)
    app.logger.debug("Made the request")
    return _r2flask(r)

    

def _get_available():
    r = req.get('%s/available/' % STEMWEB_BASE)
    r.raise_for_status()
    return r.json()


def _r2flask(r):
    '''Return a Flask response object from a Requests one'''
    app.logger.debug("Got requests response object with status %d" % r.status_code)
    if r.status_code == 200:
        return r.json()
    else:
        return r.text, r.status_code


if __name__ == '__main__':
    app.run()