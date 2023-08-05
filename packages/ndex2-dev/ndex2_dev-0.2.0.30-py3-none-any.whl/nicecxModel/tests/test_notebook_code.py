import ndex2
import json
import requests
import ndex2.client as nc

my_username = "drh"
my_password = "drh"
my_server = 'public.ndexbio.org'

# TODO: get UUIDs from a network set

# network set --> 71cde621-deb7-11e7-adc1-0ac135e8bacf
# 26e3478c-deb7-11e7-adc1-0ac135e8bacf

username = 'scratch'
password = 'scratch'
server = 'http://public.ndexbio.org'
my_network_set = '71cde621-deb7-11e7-adc1-0ac135e8bacf'

ndex2_client = nc.Ndex2(host=server, username=username, password=password, debug=True)
set_response = ndex2_client.get_network_set(my_network_set)
uuids = set_response.get('networks')  # for one or more individually specified networks


def query_mygene_x(q, tax_id='9606', entrezonly=True):
    if entrezonly:
        r = requests.get('http://mygene.info/v3/query?q=' + q + '&species=' + tax_id + '&entrezonly=true')
    else:
        r = requests.get('http://mygene.info/v3/query?q=' + q + '&species=' + tax_id)
    result = r.json()
    hits = result.get("hits")
    if hits and len(hits) > 0:
        return hits[0]
    return False


def query_batch(query_string, tax_id='9606', scopes="symbol, entrezgene, alias, uniprot", fields="symbol, entrezgene"):
    data = {'species': tax_id,
            'scopes': scopes,
            'fields': fields,
            'q': query_string}
    r = requests.post('http://mygene.info/v3/query', data)
    json = r.json()
    return json


def query_mygene(q):
    hits = query_batch(q)
    for hit in hits:
        symbol = hit.get('symbol')
        id = hit.get('entrezgene')
        if symbol and id:
            return (symbol, id)
    return None

# per node update method
def update_node(node, nicecx):
    print("\nnode %s" % node.get_name())
    aliases = nicecx.get_node_attribute(node, "alias")
    print("aliases: %s" % aliases)
    #if aliases:
    #    aliases.push(name)
    #else:
    #    aliases = [name]

    hit = query_mygene(node.get_name())
    if hit:
        if hit:
            print("hit: %s" % json.dumps(hit, indent=4))
            succeed = True
            if (len(hit) > 0):
                node.set_node_name(hit[0])
            if (len(hit) > 1):
                node.set_node_represents(hit[1])
        print("hit: %s" % json.dumps(hit, indent=4))
    else:
        succeed = False
        for alias in aliases:
            # assume uniprot
            id = alias.split(':')[-1]
            hit = query_mygene(id)
            if hit:
                print("hit: %s" % json.dumps(hit, indent=4))
                succeed = True
                if(len(hit) > 0):
                    node.set_node_name(hit[0])
                if(len(hit) > 1):
                    node.set_node_represents(hit[1])

                break
        if not succeed:
            print("no gene hit for node %s " % node.get_name())

# TBD: create output network set
# HUGO example: hgnc.symbol:tp53 --> non-prefixed hugo symbol
# Entrez NCBI example: ncbigene:7157 --> represents
# Aliases with prefixes
# iteration over networks
count = 1
for network_uuid in uuids:
    # load network in NiceCX
    ncx = ndex2.create_nice_cx_from_server(server=my_server, uuid=network_uuid)
    for id, node in ncx.get_nodes():
        update_node(node, ncx)

    ncx.set_name('Normalized Nodes ' + str(count))
    count += 1
    # output network (TBD: in output set)
    #print("writing %s " % ncx.get_name())
    #ncx.upload_to(my_server, my_username, my_password)

    upload_message = ncx.upload_to(server, username, password)

print(ncx.to_cx())
