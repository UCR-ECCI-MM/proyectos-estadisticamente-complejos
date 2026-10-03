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
    print("0. Salir")
    print("===============================================")


def main():
    print("Cargando y procesando los chunks, esto puede tardar...")

    # Las funcionalidades 2 y 3 todavia no se colocan en este menu.
    datos_func_1, _, _ = cargar_datos()

    print("\nDatos cargados con exito.")

    while True:

        mostrar_menu()

        opcion = input("Elige una opcion: ").strip()

        if opcion == "1":
            submenu_funcionalidad_1(datos_func_1)

        elif opcion == "0":
            print("Saliendo...")
            break

        else:
            print("Opcion invalida, intenta de nuevo.")


if __name__ == "__main__":
    main()
