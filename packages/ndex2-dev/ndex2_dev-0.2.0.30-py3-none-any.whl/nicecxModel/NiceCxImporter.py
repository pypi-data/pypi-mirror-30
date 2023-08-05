__author__ = 'aarongary'

import argparse
from bottle import template, Bottle, request, response
import json
import os
import sys
import pandas as pd
import csv
import networkx as nx
import ndex2
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from ndex.networkn import NdexGraph
from copy import deepcopy
from nicecxModel.NiceCXNetwork import NiceCXNetwork

api = Bottle()

#log = logs.get_logger('api')

root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
ref_networks = {}

@api.get('/statuscheck')
def index():
    return "<b>Service is up and running</b>!"

@api.post('/upload/tsv')
def upload_tsv_post():
    uuid = None
    data = request.files.get('network_cx')
    query_string = dict(request.query)
    source = ''
    target = ''
    sourceattr = []
    targetattr = []
    edgeattr = []
    edgeinteraction = None
    if 'source' in query_string:
        source = query_string.get('source')
    if 'target' in query_string:
        target = query_string.get('target')
    if 'sourceattr' in query_string:
        sourceattr = query_string.get('sourceattr').split(',')
    if 'targetattr' in query_string:
        targetattr = query_string.get('targetattr').split(',')
    if 'edgeinteraction' in query_string:
        edgeinteraction = query_string.get('edgeinteraction')

    if data and data.file:
        try:
            tsvfile = data.file
            header = [h.strip() for h in tsvfile.readline().split('\t')]

            df = pd.read_csv(tsvfile, delimiter='\t', engine='python', names=header)

            niceCx = NiceCXNetwork()
            #niceCx = ndex2.create_nice_cx_from_pandas(df, source_field='GeneSymbol', target_field='PathwayName', source_node_attr=['GeneID'], target_node_attr=['Pathway Source'], edge_attr=[])

            niceCx = ndex2.create_nice_cx_from_pandas(df, source_field=source, target_field=target,
                                          source_node_attr=sourceattr, target_node_attr=targetattr,
                                          edge_attr=edgeattr, edge_interaction=edgeinteraction)
        except Exception as e:
            response.status = 400
            response.content_type = 'application/json'
            return json.dumps({'message': 'Network file is not valid CX/JSON. Error --> ' + e.message})

        return json.dumps(niceCx.to_cx())

# run the web server
def main():
    status = 0
    parser = argparse.ArgumentParser()
    parser.add_argument('port', nargs='?', type=int, help='HTTP port', default=5603)
    args = parser.parse_args()

    print 'starting web server on port %s' % args.port
    print 'press control-c to quit'
    try:
        server = WSGIServer(('0.0.0.0', args.port), api, handler_class=WebSocketHandler)
        #log.info('entering main loop')
        server.serve_forever()
    except KeyboardInterrupt:
        print('keyboard interrupt')
        #log.info('exiting main loop')
    except Exception as e:
        str = 'could not start web server: %s' % e
        #log.error(str)
        print str
        status = 1

    #log.info('exiting with status %d', status)
    return status

if __name__ == '__main__':
    sys.exit(main())