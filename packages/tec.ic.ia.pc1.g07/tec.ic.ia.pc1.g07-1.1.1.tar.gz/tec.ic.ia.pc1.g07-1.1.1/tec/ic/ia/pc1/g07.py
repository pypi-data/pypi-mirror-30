import csv
import random

# Rutas de archivos csv por incluir
Indicadores_x_Canton = 'Indicadores_x_Canton.csv'
Juntas = 'Juntas.csv'
VotosxPartidoxJunta = 'VotosxPartidoxJunta.csv'
semilla = 0


# Setea la semilla para las generaciones aleatorias.
# Entradas: semilla.
# Salidas: n/a.

def set_semilla(seed):
    global semilla
    semilla = seed


# Genera muestras por pais.
# Entradas: num de muestras.
# Salidas: muestras creadas.

def generar_muestra_pais(n):
    muestra = []
    indice = 0
    data_indicadores = []
    data_juntas = []
    data_votos = []
    if not isinstance(n, int):
        print('El valor ingresado para generar una muestra debe ser un entero.')
        return
    with open(Indicadores_x_Canton, 'r') as csv_indicadores, open(Juntas, 'r') as csv_juntas, open(VotosxPartidoxJunta, 'r') as csv_votos:
        data_indicadores = list(csv.reader(csv_indicadores))
        data_juntas = list(csv.reader(csv_juntas))
        data_votos = list(csv.reader(csv_votos))
    while indice < n:
        # Generar junta
        aleatorio_juntas = generar_aleatorio_x_celdas(
            6, 0, 6542, data_juntas)
        if aleatorio_juntas == 'no encontrado':
            print('No se han encontrado los datos del CSV Juntas.')
            return
        muestra += [generar_muestra_aux(aleatorio_juntas,
                                        data_indicadores, data_votos)]
        indice += 1
    return muestra


# Genera muestras por provincia indicada.
# Entradas: num de muestras, provincia a la que pertenecera la muestra.
# Salidas: muestras creadas.

def generar_muestra_provincia(n, nombre_provincia):
    indice = 0
    muestra = []
    data_juntas = []
    data_indicadores = []
    data_votos = []
    with open(Indicadores_x_Canton, 'r') as csv_indicadores, open(VotosxPartidoxJunta, 'r') as csv_votos, open(Juntas, 'r') as csv_juntas:
        data_indicadores = list(csv.reader(csv_indicadores))
        data_votos = list(csv.reader(csv_votos))
        data_juntas = list(csv.reader(csv_juntas))
    # Lee indices de provincias en csv
    indices_provincias = obtener_indices_provincias(0, data_juntas)
    if indices_provincias == 'no encontrado':
        print('No se han obtenido los datos del CSV Juntas.')
        return
    # Valida parametros
    if not isinstance(
            n,
            int) or nombre_provincia not in indices_provincias:
        print(
            'El valor ingresado para generar una muestra debe ser un entero.',
            'La provincia indicada debe ingresarse en UPPERCASE, entre comillas y con los espacios apropiados. Ej: "SAN JOSE".')
        return
    # Genera junta dependiendo de su provincia
    index_provincia = indices_provincias[nombre_provincia]
    while indice < n:
        aleatorio_juntas = generar_aleatorio_x_celdas(
            6, index_provincia[0], index_provincia[1], data_juntas)
        if aleatorio_juntas == 'no encontrado':
            print('No se han encontrado los datos del CSV Juntas.')
            return
        muestra += [generar_muestra_aux(aleatorio_juntas,
                                        data_indicadores, data_votos)]
        indice += 1
    return muestra


# Genera valor aleatorio para seleccionar un rango especifico segun
# celdas recibidas del csv.
# Entradas: columna a analizar, num de fila de inicio, num fila final,
# lista de filas del csv.
# Salidas: fila elegida por aleatorio, resultado aleatorio.

def generar_aleatorio_x_celdas(col, rango_min, rango_max, lista_archivo):
    # Los rangos inician en 1. Cada uno representa la cantidad que abarca cada
    # atributo.
    rangos = []
    if semilla == 0:
        random.seed()
    else:
        random.seed(semilla)
    # Si es para juntas
    try:
        if col != 'n/a':
            for fila in lista_archivo[rango_min:rango_max]:
                if len(rangos) == 0:
                    rangos.append(int(fila[col]))
                else:
                    rangos.append(rangos[-1] + int(fila[col]))
            num_aleatorio = random.randint(1, rangos[-1])
            for i, rango in enumerate(rangos):
                if num_aleatorio <= rango:
                    # Devuelvo fila elegida, y resultado aleatorio
                    return([lista_archivo[rango_min + i], num_aleatorio])
        # Si es para indicadores
        else:
            for dato in lista_archivo[rango_min:rango_max]:
                if len(rangos) == 0:
                    rangos.append(float(dato))
                else:
                    rangos.append(rangos[-1] + float(dato))
            num_aleatorio = random.uniform(1, rangos[-1])
            for i, rango in enumerate(rangos):
                if num_aleatorio <= rango:
                    # Devuelvo celda elegida, y resultado aleatorio
                    return([i, num_aleatorio])
    except BaseException:
        return 'no encontrado'


# Genera los datos de canton especifico en filas de csv.
# Entradas: num de fila de inicio, num fila final, lista de filas del csv,
# canton por buscar.
# Salidas: fila de datos de canton, o 'no encontrado'.

def encontrar_datos_canton(rango_min, rango_max, lista_archivo, canton):
    # En caso de no encontrar datos en el csv.
    try:
        for fila in lista_archivo[rango_min:rango_max]:
            if fila[1] == canton:
                return fila
        return 'no encontrado'
    except BaseException:
        return 'no encontrado'


# Genera los datos de junta especifica en filas de csv.
# Entradas: lista de filas del csv, junta por buscar.
# Salidas: fila de datos de junta, o 'no encontrado'.

def encontrar_votos_junta(lista_archivo, junta):
    try:
        for fila in lista_archivo:
            if fila[0] == junta:
                return fila
        return 'no encontrado'
    except BaseException:
        return 'no encontrado'


# Obtiene indices de provincias de lista de filas de csv.
# Entradas: col por examinar, lista de filas del csv.
# Salidas: diccionario de indices, o 'no encontrado'.

def obtener_indices_provincias(col, lista_archivo):
    provincias = [
        'SAN JOSE',
        'ALAJUELA',
        'CARTAGO',
        'HEREDIA',
        'GUANACASTE',
        'PUNTARENAS',
        'LIMON']
    indice_prov = 0
    diccionario_rangos = {}
    ultimo_indice = 0
    try:
        for i, fila in enumerate(lista_archivo):
            if fila[col] not in diccionario_rangos:
                if len(diccionario_rangos) != 0:
                    diccionario_rangos[provincias[indice_prov]] = [
                        diccionario_rangos[provincias[indice_prov]], i - 1]
                    indice_prov += 1
                diccionario_rangos[provincias[indice_prov]] = i
            ultimo_indice = i
        diccionario_rangos[provincias[indice_prov]] = [
            diccionario_rangos[provincias[indice_prov]], ultimo_indice]
        return diccionario_rangos
    except BaseException:
        return 'no encontrado'


# Genera atributos aleatorios para cada muestra.
# Entradas: junta aleatoria, lista de filas del csv de indicadores, lista de
# filas del csv de votos.
# Salidas: muestra creada.

def generar_muestra_aux(aleatorio_juntas, data_indicadores, data_votos):
    edades = [
        '15 a 19',
        '20 a 24',
        '25 a 29',
        '30 a 34',
        '35 a 39',
        '40 a 44',
        '45 a 49',
        '50 a 54',
        '55 a 59',
        '60 a 64',
        '65 a 69',
        '70 a 74',
        '75 a 79',
        '80 a 84',
        '85 y más']
    escolaridad = [
        'ningun año',
        'primaria incompleta',
        'primaria completa',
        'secundaria incompleta',
        'secundaria completa',
        'superior']
    razon_desempleo = [
        'pensionado',
        'rentista',
        'estudia',
        'oficios domesticos',
        'otros']
    sectores = [
        'sector primario',
        'sector secundario',
        'sector terciario']
    partidos = [
        'ACCESIBILIDAD SIN EXCLUSION',
        'ACCION CIUDADANA',
        'ALIANZA DEMOCRATA CRISTIANA',
        'DE LOS TRABAJADORES',
        'FRENTE AMPLIO',
        'INTEGRACION NACIONAL',
        'LIBERACION NACIONAL',
        'MOVIMIENTO LIBERTARIO',
        'NUEVA GENERACION',
        'RENOVACION COSTARRICENSE',
        'REPUBLICANO SOCIAL CRISTIANO',
        'RESTAURACION NACIONAL',
        'UNIDAD SOCIAL CRISTIANA',
        'NULOS',
        'BLANCOS']
    #Pone semilla en el random.
    if semilla == 0:
        random.seed()
    else:
        random.seed(semilla)
    # Lee indices de provincias en csv
    indices_provincias = obtener_indices_provincias(0, data_indicadores)
    if indices_provincias == 'no encontrado':
        print('No se han obtenido los datos del CSV Indicadores_x_Canton.')
        return
    # Generar junta
    nueva_muestra = []
    # Agrega nueva muestra con datos de junta
    nueva_muestra += aleatorio_juntas[0]
    canton = aleatorio_juntas[0][1]
    indices_provincia = indices_provincias[aleatorio_juntas[0][0]]
    # Encuentra datos de canton correspondiente
    datos_canton = encontrar_datos_canton(
        indices_provincia[0],
        indices_provincia[1] + 1,
        data_indicadores,
        canton)
    if datos_canton == 'no encontrado':
        print('No se han encontrado los datos del canton ',
              canton, 'en el CSV Indicadores_x_Canton.')
        return
    # Agrega poblacion total, superficie, densidad (personasXkm2), porc.
    # Poblacion urbana
    nueva_muestra += datos_canton[2:6]
    # Genera si es pob urbana o no
    urbana = generar_aleatorio_x_celdas("n/a", 6, 8, datos_canton)
    if urbana[0] == 0:
        nueva_muestra += ['urbana']
    else:
        nueva_muestra += ['no urbana']
    # Agrega relacion hombres-mujeres
    nueva_muestra += [datos_canton[8]]
    # Genera si es hombre o mujes
    genero = generar_aleatorio_x_celdas('n/a', 9, 11, datos_canton)
    if genero[0] == 0:
        nueva_muestra += ['mujer']
    else:
        nueva_muestra += ['hombre']
    # Agrega relacion de dependencia demografica
    nueva_muestra += [datos_canton[11]]
    # Aenera edad segun genero
    edad = []
    if genero[0] == 0:
        edad = generar_aleatorio_x_celdas('n/a', 12, 27, datos_canton)
        nueva_muestra += [edades[edad[0]]]
    else:
        edad = generar_aleatorio_x_celdas('n/a', 27, 42, datos_canton)
        nueva_muestra += [edades[edad[0]]]
    # Agrega viviendas individuales ocupadas, promedio de ocupantes,
    # Porc. de viviendas en buen estado
    nueva_muestra += datos_canton[42:45]
    # Genera si tiene vivienda en buen estado o no
    vivienda = generar_aleatorio_x_celdas("n/a", 45, 47, datos_canton)
    if vivienda[0] == 0:
        nueva_muestra += ['vivienda en buen estado']
    else:
        nueva_muestra += ['vivienda en mal estado']
    # Agrega porc. de viviendas hacinadas
    nueva_muestra += [datos_canton[47]]
    # Genera si tiene vivienda hacinada o no
    hacinamiento = generar_aleatorio_x_celdas(
        "n/a", 48, 50, datos_canton)
    if hacinamiento[0] == 0:
        nueva_muestra += ['vivienda hacinada']
    else:
        nueva_muestra += ['vivienda no hacinada']
    # Genera grado de escolaridad
    escolar = generar_aleatorio_x_celdas("n/a", 61, 67, datos_canton)
    nueva_muestra += [escolaridad[escolar[0]]]
    # Agrega porc. de alfabetismo
    nueva_muestra += [datos_canton[50]]
    # Agrega porc. de alfabetismo de su edad
    alfabetismo = []
    if edad[0] == 0 or edad[0] == 1:  # pues es de 10-24 annos
        alfabetismo = datos_canton[51]
    else:  # De 25 en adelante
        alfabetismo = datos_canton[52]
    nueva_muestra += [alfabetismo]
    # Genera si es alfabeta o no. Solo se considera no alfabeta si no tuviera
    # Escolaridad o primaria incompleta.
    alfabeta = 'alfabeta'
    if escolar[0] == 0 or escolar[0] == 1:
        num_aleatorio = random.uniform(1, 100)
        if num_aleatorio > float(alfabetismo):
            alfabeta = 'no alfabeta'
    nueva_muestra += [alfabeta]
    # Agrega escolaridad promedio
    nueva_muestra += [datos_canton[53]]
    # Agrega escolaridad promedio de su edad
    escolaridad_edad = []
    if edad[0] >= 0 or edad[0] <= 6:  # Pues es de 18(25)-49 annos
        escolaridad_edad = datos_canton[54]
    else:  # De 49 en adelante
        escolaridad_edad = datos_canton[55]
    nueva_muestra += [escolaridad_edad]
    # Agrega porcentaje de asistencia a la educacion regular
    nueva_muestra += [datos_canton[56]]
    # Agrega p.a.e.r. de su edad
    paer = []
    if edad[0] == 0:  # Pues es de (5-17)15-19 annos
        paer = datos_canton[58]
    elif edad[0] == 1:  # Pues es de (18-24)20-24 annos
        paer = datos_canton[59]
    else:  # De 25 en adelante
        paer = datos_canton[60]
    nueva_muestra += [paer]
    # Agrega porc. personas fuera de la fuerza de trabajo
    fuera_trabajo = datos_canton[67]
    nueva_muestra += [fuera_trabajo]
    # Agrega porc. personas dentro de la fuerza de trabajo (tasa neta de
    # Participacion),porc. personas dentro de la fuerza de trabajo Hombres,
    # Porc. personas dentro de la fuerza de trabajo Mujeres
    nueva_muestra += datos_canton[73:76]
    # Genera si se encuentra fuera de la fuerza de trabajo
    num_aleatorio = random.uniform(1, 100)
    if num_aleatorio > float(fuera_trabajo):
        nueva_muestra += ['dentro de fuerza']
        sector = generar_aleatorio_x_celdas("n/a", 76, 79, datos_canton)
        nueva_muestra += [sectores[sector[0]]]
    else:
        nueva_muestra += ['fuera de fuerza']
        razon = generar_aleatorio_x_celdas('n/a', 68, 73, datos_canton)
        while (razon[0] == 0 and edad[0] <
               9):  # Solo puede estar pensionado si es mayor a 59 annos
            razon = generar_aleatorio_x_celdas(
                'n/a', 68, 73, datos_canton)
        nueva_muestra += [razon_desempleo[razon[0]]]
    # Agrega porc. poblacion ocupada no asegurada, porc. poblacion nacida en
    # El extranjero
    nueva_muestra += datos_canton[79:81]
    # Genera si nacio en el extranjero o no
    extranjero = generar_aleatorio_x_celdas("n/a", 81, 83, datos_canton)
    if extranjero[0] == 0:
        nueva_muestra += ['nacido en extranjero']
    else:
        nueva_muestra += ['no nacido en extranjero']
    # Agrega porc. poblacion con discapacidad
    nueva_muestra += [datos_canton[83]]
    # Genera discapacidad o no
    discapacidad = generar_aleatorio_x_celdas(
        "n/a", 84, 86, datos_canton)
    if discapacidad[0] == 0:
        nueva_muestra += ['discapacidad']
    else:
        nueva_muestra += ['sin discapacidad']
    # Agrega porc. poblacion no asegurada
    nueva_muestra += [datos_canton[86]]
    # Genera si esta asegurado o no
    asegurado = generar_aleatorio_x_celdas("n/a", 87, 89, datos_canton)
    if asegurado[0] == 0:
        nueva_muestra += ['no asegurado']
        nueva_muestra += ['n/a']  # No tiene forma de aseguramiento
    else:
        nueva_muestra += ['asegurado']
        # Genera forma de aseguramiento
        forma = generar_aleatorio_x_celdas("n/a", 89, 92, datos_canton)
        if forma[0] == 0:
            nueva_muestra += ['directo']
        elif asegurado[0] == 1:
            nueva_muestra += ['indirecto']
        else:
            nueva_muestra += ['otras formas']
    # Agrega porc. hogares con jefatura femenina, porc. hogares con
    # Jefatura compartida
    nueva_muestra += datos_canton[92:94]
    # Genera si el hogar tiene jefatura femenina, compartida, o
    # Masculina
    num_aleatorio = random.uniform(1, 100)
    if num_aleatorio <= float(datos_canton[92]):
        nueva_muestra += ['jefatura femenina']
    elif num_aleatorio <= float(datos_canton[93]):
        nueva_muestra += ['jefatura compartida']
    else:
        nueva_muestra += ['jefatura masculina']
    # Genera si posee telefono celular
    num_aleatorio = random.uniform(1, 100)
    if num_aleatorio > float(datos_canton[94]):
        nueva_muestra += ['no telefono celular']
    else:
        nueva_muestra += ['telefono celular']
    # Genera si posee telefono residencial
    num_aleatorio = random.uniform(1, 100)
    if num_aleatorio > float(datos_canton[95]):
        nueva_muestra += ['no telefono residencial']
    else:
        nueva_muestra += ['telefono residencial']
    # Genera si posee computadora
    num_aleatorio = random.uniform(1, 100)
    if num_aleatorio > float(datos_canton[96]):
        nueva_muestra += ['no computadora']
    else:
        nueva_muestra += ['computadora']
    # Genera si posee internet
    num_aleatorio = random.uniform(1, 100)
    if num_aleatorio > float(datos_canton[97]):
        nueva_muestra += ['no internet']
    else:
        nueva_muestra += ['internet']
    # Genera si posee electricidad
    num_aleatorio = random.uniform(1, 100)
    if num_aleatorio > float(datos_canton[98]):
        nueva_muestra += ['no electricidad']
    else:
        nueva_muestra += ['electricidad']
    # Genera si posee servicio sanitario
    num_aleatorio = random.uniform(1, 100)
    if num_aleatorio > float(datos_canton[99]):
        nueva_muestra += ['no servicio sanitario']
    else:
        nueva_muestra += ['servicio sanitario']
    # Genera si posee agua
    num_aleatorio = random.uniform(1, 100)
    if num_aleatorio > float(datos_canton[100]):
        nueva_muestra += ['no agua']
    else:
        nueva_muestra += ['agua']
    # Encuentra votos de junta
    junta = aleatorio_juntas[0][4]
    datos_votos = encontrar_votos_junta(data_votos, junta)
    if datos_votos == 'no encontrado':
        print('No se han encontrado los datos de la junta ',
              junta, 'en el CSV VotosxPartidoxJunta.')
        return
    # Genera voto
    voto = generar_aleatorio_x_celdas("n/a", 1, 16, datos_votos)
    nueva_muestra += [partidos[voto[0]]]
    return nueva_muestra
