# Aporte Brandon

# Recordar que, la funcionlidad 1 tiene que validar si un presijo esta siendo reportado por un solo as number de origen.
# Con esto en cuennta, se creara un diccionario que use como llave el prefijo y guarde los as de origen que los reporta.
# de esta manera podemos validar si hay un prefijo siendo reportado por varios as de origen 

# CREAR DICCIONARIO 


#aqui se van a guardar los datos
funcionalidad_1 = {}

# PREFIJO Y AS PATH

# Se le pide al parser que devuelva los datos que neceistamos para validar la funcion 1

def p_ruta_bgp(p):
    'linea : TABLE_DUMP2 PIPE TIMESTAMP PIPE STATE PIPE IP PIPE AS_NUMBER PIPE PREFIX PIPE as_path'
    p[0]= {'prefijo': p[11], 
           'as_path': p[13]}

## Una vez con los datos, cunado el parser esta analizando la linea se le piden los datos y se guarda la informacion

 resultado = parser.parse(linea, lexer=lexer)

# EXTRAR DATOS PARA LA FUNCIONALIDAD 1

prefijo = resultado.get('prefijo') # informacion del prefijo
as_path = resultado.get('as_path') # informacion del as path

if prefijo not in funcionalidad_1: # si el prefijo no esta registrado se crea una llave para este
    funcionalidad_1[prefijo] = [as_path[-1]]
else:
    if as_path[-1] not in funcionalidad_1[prefijo]: # si el prefijo ya existe, se revisa si el as number ya existe y si no se agrega
        funcionalidad_1[prefijo].append(as_path[-1])
    else:                   
        continue 