# IMPORTAR BIBLIOTECAS

from parser import cargar_datos

#====================================================== FUNCIONES AUXILIARES ======================================================

def formatear_as_path(as_path):
    """Convierte una lista de AS en una cadena legible: 100 -> 200 -> 300"""

    return " -> ".join(str(as_num) for as_num in as_path)

def pausar():
    """Detiene la ejecucion hasta que el usuario presione ENTER."""

    input("\nPresiona ENTER para volver al menu...")

#====================================================== FUNCIONES DE CONSULTA ======================================================

def consultar_funcionalidad_1(datos_func_1):
    """Muestra todos los prefijos que tienen 2 o mas AS de origen distintos."""

    print("\n--- Prefijos con 2 o mas AS de origen ---")

    prefijos_multiorigen = {
        prefijo: origenes
        for prefijo, origenes in datos_func_1.items()
        if len(origenes) >= 2
    }

    if not prefijos_multiorigen:
        print("  No se encontraron prefijos con 2 o mas AS de origen.")
        return

    for indice, prefijo in enumerate(sorted(prefijos_multiorigen), start=1):
        origenes = sorted(prefijos_multiorigen[prefijo])
        print(f"  {indice}. {prefijo} | AS de origen que reportan el perfijo: {origenes}")


def consultar_funcionalidad_1_2(datos_func_1):
    """
    Pide un prefijo y muestra los AS de origen que lo reportaron.
    Esto es lo que originalmente hacia la funcionalidad 1; se deja
    como funcion aparte para que mas adelante la reutilicen las
    funcionalidades 2 y 3.

    Devuelve el prefijo ingresado, para que quien la llame pueda
    seguir usandolo.
    """

    prefijo = input("Prefijo (ej 1.2.3.0/24): ").strip()

    origenes = datos_func_1.get(prefijo)

    print(f"\n--- AS de origen para el prefijo {prefijo} ---")

    if not origenes:
        print("  No hay datos para ese prefijo.")
    else:
        for indice, as_origen in enumerate(sorted(origenes), start=1):
            print(f"  {indice}. AS {as_origen}")

    return prefijo

def consultar_funcionalidad_2(datos_func_2):
    """
    Solicita un numero de AS y muestra:
    - La cantidad total de aristas del AS.
    - Las aristas encontradas (Peer IP).
    - Para cada arista, los prefijos conocidos.
    - El AS Path asociado a cada prefijo.
    """

    # Solicitar el numero de AS al usuario
    entrada = input("Numero de AS: ").strip()

    # Validar que el AS ingresado sea numerico
    try:
        peer_as = int(entrada)

    except ValueError:
        print("El numero de AS debe ser un valor numerico.")
        return

    # Buscar el AS en la estructura de datos
    peer_ips = datos_func_2.get(peer_as)

    # Verificar si existen datos para ese AS
    if not peer_ips:
        print(f"\nNo hay datos para el AS {peer_as}.")
        return

    # Encabezado
    print("\n================ FUNCIONALIDAD 2 ================")

    # Mostrar el AS consultado
    print(f"\nAS consultado: {peer_as}")

    # Mostrar la cantidad de aristas
    print(f"Total de aristas: {len(peer_ips)}")

    # Mostrar todas las aristas encontradas
    print("\nAristas encontradas:")

    for indice, peer_ip in enumerate(sorted(peer_ips.keys()), start=1):
        print(f"  {indice}. {peer_ip}")

    # Pausa antes de mostrar todas las rutas
    input("\nPresiona ENTER para mostrar los prefijos y AS Paths...")

    # Recorrer cada arista
    for peer_ip, rutas in sorted(peer_ips.items()):

        print("\n" + "-" * 80)
        print(f"ARISTA (Peer IP): {peer_ip}")
        print("-" * 80)

        # Encabezados de la tabla
        print(f"{'PREFIJO':<25} AS PATH")
        print("-" * 80)

        # Recorrer las rutas conocidas a traves de esta arista
        for ruta in rutas:

            # Obtener el prefijo
            prefijo = ruta["prefijo"]

            # Obtener el AS Path
            as_path = ruta["as_path"]

            # Convertir la lista del AS Path a un formato legible
            as_path_formateado = formatear_as_path(as_path)

            # Mostrar el prefijo y su AS Path
            print(f"{prefijo:<25} {as_path_formateado}")

        # Mostrar la cantidad de rutas de esta arista
        print(f"\nTotal de rutas por esta arista: {len(rutas)}")

    print("\n=================================================")

def consultar_funcionalidad_3(datos_func_1, datos_func_3):
    """
    Dados dos prefijos A y B, muestra todas las rutas disponibles
    entre ellos utilizando los AS Paths almacenados durante el parseo.

    datos_func_1:
        Permite obtener los AS de origen asociados a cada prefijo.

    datos_func_3:
        Permite acceder directamente a los AS Paths conocidos para
        un prefijo, agrupados por Peer AS.
    """

    print("\n================ FUNCIONALIDAD 3 ================")

    # 1. Solicitar los dos prefijos

    prefijo_a = input("Prefijo A (ej 1.2.3.0/24): ").strip()
    prefijo_b = input("Prefijo B (ej 1.2.3.0/24): ").strip()

    # 2. Obtener AS de origen usando funcionalidad 1

    origenes_a = datos_func_1.get(prefijo_a)
    origenes_b = datos_func_1.get(prefijo_b)

    if not origenes_a:
        print(f"\nNo hay datos para el prefijo A: {prefijo_a}")
        return

    if not origenes_b:
        print(f"\nNo hay datos para el prefijo B: {prefijo_b}")
        return

    print(f"\nPrefijo A: {prefijo_a}")
    print(f"AS de origen: {sorted(origenes_a)}")

    print(f"\nPrefijo B: {prefijo_b}")
    print(f"AS de origen: {sorted(origenes_b)}")

    # 3. Buscar directamente las rutas hacia B

    rutas_hacia_b = datos_func_3.get(prefijo_b)

    if not rutas_hacia_b:
        print(f"\nNo existen rutas conocidas hacia {prefijo_b}.")
        return

    rutas_encontradas = []

    # 4. Revisar los AS Paths de B

    for peer_as, as_paths in rutas_hacia_b.items():

        for as_path in as_paths:

            # Verificar que alguno de los AS de origen del prefijo A
            # aparezca en cualquier posicion del AS Path
            contiene_origen_a = any(
                as_origen in as_path
                for as_origen in origenes_a
            )

            # Verificar que el AS Path termine en uno de los
            # AS de origen del prefijo B
            termina_en_origen_b = (
                as_path[-1] in origenes_b
            )

            # Si cumple ambas condiciones, se conserva
            # el AS Path COMPLETO
            if contiene_origen_a and termina_en_origen_b:

                if as_path not in rutas_encontradas:
                    rutas_encontradas.append(as_path)

    # 5. Mostrar resultados

    print("\n" + "-" * 80)
    print("RUTAS DISPONIBLES")
    print("-" * 80)

    if not rutas_encontradas:

        print(
            f"No se encontraron rutas entre "
            f"{prefijo_a} y {prefijo_b}."
        )

        return

    for indice, ruta in enumerate(rutas_encontradas, start=1):

        print(
            f"{indice}. "
            f"{prefijo_a} -> "
            f"{formatear_as_path(ruta)} -> "
            f"{prefijo_b}"
        )

    print(f"\nTotal de rutas encontradas: {len(rutas_encontradas)}")

    print("\n=================================================")    


#====================================================== MENU PRINCIPAL ======================================================

def mostrar_submenu_funcionalidad_1():
    print("\n------------- FUNCIONALIDAD 1 -------------")
    print("1. Consultar el AS de origen de un prefijo")
    print("2. Mostrar los prefijos con 2 o mas AS de origen")
    print("0. Volver al menu principal")
    print("--------------------------------------------")


def submenu_funcionalidad_1(datos_func_1):
    """Submenu de la funcionalidad 1: consulta puntual o vista general."""

    while True:

        mostrar_submenu_funcionalidad_1()

        opcion = input("Elige una opcion: ").strip()

        if opcion == "1":
            consultar_funcionalidad_1_2(datos_func_1)
            pausar()

        elif opcion == "2":
            consultar_funcionalidad_1(datos_func_1)
            pausar()

        elif opcion == "0":
            break

        else:
            print("Opcion invalida, intenta de nuevo.")


def mostrar_menu():
    print("\n==================== MENU ====================")
    print("1. Funcionalidad 1")
    print("2. Funcionalidad 2")
    print("3. Funcionalidad 3")
    print("0. Salir")
    print("===============================================")


def main():
    print("Cargando y procesando los chunks, esto puede tardar...")

    datos_func_1, datos_func_2, datos_func_3 = cargar_datos()

    print("\nDatos cargados con exito.")

    while True:

        mostrar_menu()

        opcion = input("Elige una opcion: ").strip()

        if opcion == "1":
            submenu_funcionalidad_1(datos_func_1)

        elif opcion == "2":
            consultar_funcionalidad_2(datos_func_2)
            pausar()

        elif opcion == "3":
            consultar_funcionalidad_3(datos_func_1, datos_func_3)
            pausar()

        elif opcion == "0":
            print("Saliendo...")
            break

        else:
            print("Opcion invalida, intenta de nuevo.")


if __name__ == "__main__":
    main()
