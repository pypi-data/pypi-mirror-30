import os


def start(host=None):
    if host is None:
        host = os.environ.get('HOSTNAME', '')
    if '-' not in host:
        print('seems not a kube', host)
        return
    import requests
    try:
        import arrow
        r = requests.post('http://es.qbtrade.org/kube-start/doc',
                          json={'host': host, 'category': 'deploy', '@timestamp': arrow.now().isoformat()},
                          timeout=3)
        print(r)
        print(r.text)
    except:
        import logging
        logging.exception('failed')


if __name__ == '__main__':
    start('pytest-argv-xx')
