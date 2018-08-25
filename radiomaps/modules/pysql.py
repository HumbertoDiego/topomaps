# -*- coding: utf-8 -*-
import psycopg2
import time
import pandas
ini = time.time()
try:
    conn = psycopg2.connect("dbname='pgis' user='postgres' host='localhost' password='postgres'")
except:
    print "N deu pra conectar com a database"
cur = conn.cursor()
#################### Lição 1 - Verificar a base de dados ###############################################################
# cur.execute("SELECT datname from pg_database") # mostra todas as databases
# cur.execute("SELECT * FROM INFORMATION_SCHEMA.Tables") # mostra as tabelas do db conectado
# cur.execute("SELECT * FROM INFORMATION_SCHEMA.columns where TABLE_NAME='area';") # mostra as colunas da tabela 'area'

################### Lição 2 - Criar a tabela e Inserir dados geoespaciais ##############################################
# cur.execute("DROP TABLE IF EXISTS area;") # exclui a tabela 'area' se ela existir
# cur.execute("CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS postgis_topology;")
# cur.execute("CREATE TABLE IF NOT EXISTS area ( " +
#             "id serial PRIMARY KEY, " +
#             "nome varchar(80)," +
#             "geometria geometry('POINT', 4326));") # Cria a tabela com extensão pgis se ela não existir
#
# cur.execute("INSERT INTO area (nome, geometria) VALUES ('p1', ST_geomfromtext('POINT(-22 -44.1)',4326));")
# cur.execute("INSERT INTO area (nome, geometria) VALUES ('p2', ST_geomfromtext('POINT(-22 -44)',4326));")
# cur.execute("INSERT INTO area (nome, geometria) VALUES ('p3', ST_geomfromtext('POINT(-22.1 -44.1)',4326));")
# cur.execute("INSERT INTO area (nome, geometria) VALUES ('p4', ST_geomfromtext('POINT(-22.1 -44)',4326));")
# cur.execute("INSERT INTO area (nome, geometria) VALUES ('p5', ST_geomfromtext('POINT(-22.1 -44.2)',4326));")


################## Lição 3 - Selecionar as geometrias em formato texto ################################################
# cur.execute("SELECT nome,ST_AsEWKT(geometria),ST_AsText(geometria) FROM area;") # mostra as geometrias com/sem SRID
# cur.execute("SELECT ST_AsEWKT('POINT(-22.1 -44.1)::geometry');") # definir geometria sem SRID
# cur.execute("SELECT ST_AsGeoJSON(geometria) from area") # mostra o ponto no formato GeoJson (perde o SRID)

################## Lição 4 - Distância entre dois pontos: ST_Distance(geom1,geom2) #####################################
# cur.execute("SELECT ST_Distance((select geometria from area where id=1)," +
#             "(select geometria from area where id=2));") # dist entre dois pontos ::geometry da mesma tabela (º)
# cur.execute("SELECT ST_Distance_Sphere((select geometria from area where id=1)," +
#             "(select geometria from area where id=2));") # dist entre dois pontos ::geometry da mesma tabela (m)
# cur.execute("SELECT st_distance(ST_GeomFromText('POINT(-22 -44.1)',4326)," +
#             "ST_GeomFromText('POINT(-22 -44)',4326));") # dist entre dois pontos ::geometry sem tabela (º)

# cur.execute("SELECT ST_Distance(ST_GeographyFromText('SRID=4326;POINT(-0.1 -44)')," +
#             "ST_GeographyFromText('SRID=4326;POINT(0 -44)'));") # dist entre dois pontos ::geography sem tabela (m)
# cur.execute("SELECT ST_Distance(ST_GeographyFromText('SRID=4326;POINT(-160 -44)')," +
#             "ST_GeographyFromText('SRID=4326;POINT(-160.1 -44)'));") # dist entre dois pontos ::geography sem tabela (m)
# Conclusão: distancias constantes dentro do mesmo paralelo (mesmo y)

# cur.execute("SELECT ST_Distance(ST_GeographyFromText('SRID=4326;POINT(2 4.1)')," +
#             "ST_GeographyFromText('SRID=4326;POINT(2 4)'));") # dist entre (x=2º,y=4.1º)-(x=2º,y=4º) em (m)
# cur.execute("SELECT ST_Distance(ST_GeographyFromText('SRID=4326;POINT(2 70.1)')," +
#             "ST_GeographyFromText('SRID=4326;POINT(2 70)'));") # dist entre (x=2º,y=70.1º)-(x=2º,y=70º) em (m)
# Conclusão: distâncias variam dentro do mesmo meridiano (mesmo x)

#################### Lição 5 - Menor distância entre ponto e reta: ST_Distance(geom1,geom2) ############################
# cur.execute("SELECT ST_Distance(ST_GeomFromText('POINT(0 0)',4326)," +
#             "ST_GeomFromText('LINESTRING(0 0.1, 0 -0.1)',4326));") # dist=0º pq a linha cruza o ponto
# cur.execute("SELECT ST_Distance(ST_GeomFromText('POINT(0 0)',4326)," +
#             "ST_GeomFromText('LINESTRING(0 0.1,0 0.2)',4326));") # dist=0.1º
# cur.execute("SELECT ST_Distance_Sphere(geometria," +
#             "ST_GeomFromText('LINESTRING(-22 -45,-22 -43)',4326))" +
#             "FROM area;") # distancia (m) entre toda a coluna 'geometria' da tabela 'area' e a linha
# cur.execute("SELECT CONCAT(nome,'-LINHA'),ST_Distance_Sphere(geometria," +
#             "ST_GeomFromText('LINESTRING(-22 -45,-22 -43)',4326))" +
#             "FROM area;") # coluna 'nome'"-LINHA" + distância(m) entre a coluna 'geometria' da tabela 'area' e a linha

#################### Lição 6 - Menor distância entre ponto e poligono: ST_Distance(geom1,geom2) ########################
# cur.execute("SELECT CONCAT('Dist(', nome, '-POLIGONO)'), ST_Distance_Sphere(geometria," +
#             "ST_GeomFromText('POLYGON((-22 -44.4, -23 -43, -22.1 -44, -22 -44.4))',4326))" +
#             "FROM area;") # se dist=0 => ponto dentro do poligono

#################### Lição 7 - Menor distância entre linha e poligono: ST_Distance(geom1,geom2) ########################
# cur.execute("SELECT ST_Distance_Sphere(ST_GeomFromText('LINESTRING(23 44,23 40)',4326), " +
#             "ST_GeomFromText('POLYGON((22 44,22 43,22.1 44,22 44))',4326))")# se dist=0 => linha corta o poligono

#################### Lição 8 - Menor distância entre dois poligonos: ST_Distance(geom1,geom2) ##########################
# cur.execute("SELECT ST_Distance_Sphere(ST_GeomFromText('POLYGON((-22 -44,-22 -43,-22.1 -44,-22 -44))',4326), " +
#             "ST_GeomFromText('POLYGON((22 44,22 43,22.1 44,22 44))',4326))")# se dist=0 => poligonos se cortam

############### Lição 9 - Find all objects within a radius of another object: ST_DWithin(geom1, geom2, distance) #######
# cur.execute("SELECT ST_DWithin(ST_GeomFromText('POINT(-22 -44)',4326)," +
#             "ST_GeomFromText('POINT(-22 -44.2)',4326), 0.1) ") # distância na unidade da geometria=º
# cur.execute("SELECT ST_DWithin(geometria," +
#             "ST_GeomFromText('POINT(-22 -44)',4326), 0.1)" +
#             "FROM area;  ") # array de booleanos, distância na unidade da geometria=º

# cur.execute("SELECT ST_DWithin(ST_GeographyFromText('SRID=4326;POINT(-22 -44)')," +
#             "ST_GeographyFromText('SRID=4326;POINT(-22 -44.1)'), 11111.33)") # distância na unidade da geografia=m
# cur.execute("SELECT ST_DWithin(geometria," +
#             "ST_GeographyFromText('SRID=4326;POINT(-22 -44)'), 11120)" +
#             "FROM area;  ") # array de booleanos, distância na unidade da geografia=m

# cur.execute("SELECT ST_dwithin(ST_GeographyFromText('SRID=4326;POINT(-22 -44)'), " +
#             "ST_GeographyFromText('SRID=4326;LINESTRING(-22 -45,-22 -43)'), " +
#             "11120)") # distância ponto-Linha < 11120m ?

#################### Lição 10 - Verificar interseção: ST_Insersects(geo1, geo2) #########################################
# cur.execute("SELECT ST_Intersects('LINESTRING ( 2 0, 0 2 )'::geometry," +
#             " 'LINESTRING ( 2 1, 1 2 )'::geometry)" )

#################### Lição 11 - Comprimento de um linestring #########################################
# cur.execute("SELECT ST_Length('LINESTRING(22 44,22 44.1)'::geometry)") # unidades da referencia espacial de geometry=º
cur.execute("SELECT ST_Length('LINESTRING(22 44,22 44.1)'::geography)") # unidades da referencia espacial de geography=m

try:
    rows = cur.fetchall()
    pandas.set_option('display.width', 700)
    print pandas.DataFrame(rows)
    print "FIM :", time.time()-ini, "seg"
    # Make the changes to the database persistent
    conn.commit()
    # Close communication with the database
    cur.close()
    conn.close()
except:
    print "ñ houve seleção alguma"
    conn.commit()
    cur.close()
    conn.close()
