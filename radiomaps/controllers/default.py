# -*- coding: utf-8 -*-
import os, sys
import TileStache as ts
import time
import tools
from gluon.serializers import loads_json
import json
from gluon.dal import DAL, Field, geoPoint, geoLine, geoPolygon

def index():

    sys.stdout = open('output.logs', 'w') # Joga a saída dos prints para o arquivo output.logs >> tail -F output.logs

    # Se o cliente for Local ou o adaptador de rede
    if request.client=='127.0.0.1' or request.client=='192.168.56.1':
        print request.client

    ip = tools.ipv4_generator() #  ip = request.client
    desc , lat, lng = tools.get_pos(ip)   #  ip = request.client
    dbpg.ippos.insert(ip=ip, descricao=desc , pos=geoPoint(lng, lat))

########## Acionar a entrega de serviço WMS de Geoserver ao Leaflet - obsoleto
#     layer="radiomaps:ippos"#"tasmania"#"tiger-ny"
#     extent = tools.get_wms_extent(layer)
### Na View:
#//          var wmsurl = 'http://192.168.56.30:8080/geoserver/ows?'
#//          var wmsLayer = L.tileLayer.wms(wmsurl, { layers: '{{=layer}}',format: 'image/png',  transparent: true})
#//         map2.fitBounds({{=extent}},{padding:[100,100]});
#//         map2.addLayer(wmsLayer);

######### Acionar a entrega de GeoJSon ao Leaflet
    str_json = get_geojson2()
#     tools.pgis()

    sys.stdout = sys.__stdout__ # Reset to the standard output

    return locals()

# https://192.168.56.30/radiomaps/default/streamer/ready.mkv # 2GB Download...
# https://192.168.56.30/radiomaps/default/streamer/bludv.mp4 # 30MB Stream
# https://192.168.56.30/radiomaps/default/streamer/pna.MP3 # 13MB Stream
# https://192.168.56.30/radiomaps/default/streamer/pantera.mp4 # 2GB Stream
def streamer():
    filename=request.args[0]
    print filename
    path=os.path.join(request.folder,'static',filename)
#     response.stream(file, chunk_size, request=request, attachment=False, filename=None)
    return response.stream(open(path,'rb'),chunk_size=4096)

############################## REST API, função interna e API de retorno das posições como GeoJson #############################
# https://192.168.56.30/radiomaps/default/get_geojson
# https://192.168.56.30/get_geojson
# string = json.dumps(dicionario) , json = json.loads(string de json)
@request.restful()
def get_geojson():
    def GET(*args, **vars):
        rows=dbpg().select(dbpg.ippos.ip, dbpg.ippos.descricao, dbpg.ippos.pos.st_asgeojson(), orderby=dbpg.ippos.id)
        features= [{"type": "Feature",
                    "properties": { "popupContent": r[dbpg.ippos.ip]+"</br>"+r[dbpg.ippos.descricao] },
                    "geometry": loads_json(r[dbpg.ippos.pos.st_asgeojson()])} for r in rows]
        return response.json({"type": "FeatureCollection", 'features': features})
    return locals()

def get_geojson2():
    rows=dbpg().select(dbpg.ippos.ip, dbpg.ippos.descricao, dbpg.ippos.pos.st_asgeojson(), orderby=dbpg.ippos.id)
    features= [{"type": "Feature",
                "properties": { "popupContent": r[dbpg.ippos.ip]+"</br>"+r[dbpg.ippos.descricao] },
                "geometry": loads_json(r[dbpg.ippos.pos.st_asgeojson()])} for r in rows]
    return json.dumps(dict(type= "FeatureCollection", features= features))

def get_geojson3():
    rows=dbpg().select(dbpg.ippos.ip, dbpg.ippos.descricao, dbpg.ippos.pos.st_asgeojson(), orderby=dbpg.ippos.id)
    features= [{"type": "Feature",
                "properties": {
                "popupContent": r[dbpg.ippos.ip]
                },
                "geometry": loads_json(r[dbpg.ippos.pos.st_asgeojson()])} for r in rows]
    return response.json(dict(type= "FeatureCollection", features= features))

############################## REST API de retorno das partes do mapa servido por Tilestache #############################
# https://192.168.56.30/radiomaps/default/gettile
# https://192.168.56.30/gettile
def gettile():
    def GET(layer,zoom,x,y):
        ini = time.clock()
        path_configfile = os.path.join(request.folder,'static/tilestache.cfg')
        config2=ts.parseConfigfile(path_configfile)
        formato=request.extension
        token_version = "x234dffx"
        response.headers["Cache-Control"] = "public, max-age=100"
        if request.env.http_if_none_match==token_version:
            raise HTTP(304, "", **response.headers)
        else:
            try:
                layer2 = config2.layers[layer]
                coord = ts.Coordinate(int(y), int(x), int(zoom))
                mime_type, tile_content = ts.getTile(layer2, coord, formato)
            except:
                raise HTTP(404)
            response.headers["Content-Type"] = mime_type
            response.headers["Etag"] = token_version
            raise HTTP(200, tile_content, **response.headers)
        return locals()
    return locals()

# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)


# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def call():
    return service()
