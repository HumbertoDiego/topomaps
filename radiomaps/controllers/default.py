# -*- coding: utf-8 -*-
import os, sys
import TileStache as ts
import time
import tools

def index():
    sys.stdout = open('output.logs', 'w') # Joga a saída dos prints para o arquivo output.logs >> tail -F output.logs

    pos = tools.get_pos(request.client)

    layer="tasmania"#"tiger-ny"
    extent = tools.get_extent(layer)
    print extent

    sys.stdout = sys.__stdout__ # Reset to the standard output

    #  {ip: 191.189.19.105, subdivisions: frozenset([AM]), location: (-3.1133, -60.0253), country: BR,timezone: America/Manaus, continent:SA}
    return locals()

@request.restful()
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
