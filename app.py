from flask import Flask, redirect

import logging
import toml
import requests

from providers import s3Provider

app = Flask(__name__)
# load the config file from the TOML formatted file (not checked into repository)
app.config.from_file('config.toml', toml.load)



plausible_url = 'https://plausible.io/api/event'
domain = app.config['PLAUSIBLE_DOMAIN']


notebooks = {
    'bsi/2021/nonamer-peptides':{'url':'https://colab.research.google.com/'},
    'bsi/2021/antigen-binding-cleft':{'url':'https://colab.research.google.com/'}
}


mediatypes = {
    'posters': {
        'mediatype': 'posters',
        'plausible_name': 'PDFDownload'
    },
    'pymols': {
        'mediatype': 'pymols',
        'plausible_name': 'PyMolDownload'
    }
}

plausible_payload = {
    "name":"FileDownload",
    "url": None,
    "domain": domain}


# instantiate providers for the S3 bucket
s3 = s3Provider(app.config['AWS_ACCESS_KEY_ID'], app.config['AWS_SECRET_KEY'], app.config['AWS_DEFAULT_REGION'])


def log_activity(name, url):
    plausible_payload['name'] = name
    plausible_payload['url'] = url
    r = requests.post(plausible_url, data=plausible_payload)
    if r.status_code == 202:
        return True
    else:
        return False


@app.route('/')
def default_route_handler():
    return "Nothing to see. Move along please..."


@app.route('/<string:mediatype>/<path:path>')
def mediatype_handler(mediatype, path):
    path = mediatype + '/' + path
    if mediatype in mediatypes:
        try:
            data, success, errors = s3.get(app.config['MASTER_BUCKET'], path)
        except:
            data, success, errors = None, False, ['no_matching_file']
            path = '/' + path
        if success:
            url = 'https://data.' + domain + '/' + path
            log_activity(mediatypes[mediatype]['plausible_name'], url)
            return redirect('https://static.' + domain + '/' + path)
        else:
            return {'success': success, 'errors':errors, 'path':path}
    else:
        return {'success': False, 'errors':['no_matching_mediatype'], 'path': path}


@app.route('/notebooks/<path:path>')
def notebook_handler(path):
    if path in notebooks:
        success=True
    else:
        success=False
    if success:
        url = 'https://data.' + domain + '/' + path
        log_activity('NotebookView', url)
        return redirect(notebooks[path]['url'])
    else:
        return {'success': success, 'errors':['file_not_found'], 'path':path}


