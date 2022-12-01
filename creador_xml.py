import xml.etree.ElementTree as ET
import pandas as pd
import sys
import signal
import re
from operator import itemgetter


def handler_signal(signal, frame):  # funcion de salida controlada
    print("\n\n Interrupcion del programa, saliendo del prograam de manera controlada y ordenada")
    sys.exit(1)


# Ctrl + C, en caso de introducirlo por teclado saldremos del programa
signal.signal(signal.SIGINT, handler_signal)


def extract_rudimentario():
    # funcion impelmentada para realizar eñ informe de datos sobre NANS NULLS y tipologia de cada columna de cada dataset
    lista_csv = []
    ingredientes = pd.read_csv("pizza_types.csv", sep=",", encoding="LATIN-1")
    pizzas = pd.read_csv("pizzas.csv", sep=",", encoding="UTF-8")
    pedidos_detallados = pd.read_csv(
        "order_details.csv", sep=";", encoding="latin1")
    pedidos_detallados.fillna("NaN")
    pedidos = pd.read_csv(
        "orders.csv", sep=";", encoding="latin1")
    pedidos.fillna("NaN")
    lista_csv = [ingredientes, pizzas, pedidos_detallados, pedidos]
    return lista_csv


def extract_and_transform():  # extraccion y transformacion dataset de order details
    pedidos_detallados = pd.read_csv(
        "order_details.csv", sep=";", encoding="latin1")
    pedidos_detallados = pedidos_detallados.dropna()
    pedidos_detallados.reset_index(inplace=True)
    lista = []
    lista_mala = []
    for pizza in range(0, len(pedidos_detallados['pizza_id'])):
        lista_mala.append(pizza)
        a = re.sub('@', 'a', pedidos_detallados['pizza_id'][pizza])
        b = re.sub('0', 'o', a)
        c = re.sub('3', 'e', b)
        e = re.sub(' ', '_', c)
        f = re.sub('-', '_', e)
        lista.append(f)
    pedidos_detallados["pizza_id"] = lista
    return pedidos_detallados


def extract_transform_fechas():
    pedidos = pd.read_csv(
        "orders.csv", sep=";", encoding="latin1")
    for date in range(len(pedidos["date"])):
        try:
            pedidos["date"][date] = pd.to_datetime(
                pedidos["date"][date], erros="ignore").date()
        except:
            None
    return pedidos


def extract():
    # En nuestro caso no será necesario extraer la informacion del csv de las orders
    # puesto que nos basaremos en calcular todos las pizzas pedidas en un año y despues
    # dividiremos entre el numero de semanas
    ingredientes = pd.read_csv("pizza_types.csv", sep=",", encoding="LATIN-1")
    pizzas = pd.read_csv("pizzas.csv", sep=",", encoding="UTF-8")
    pedidos_detallados = extract_and_transform()
    pedidos = extract_transform_fechas()
    # En nuestro caso no será necesario extraer la informacion del csv de las orders
    # puesto que nos basaremos en calcular todos las pizzas pedidas en un año y despues
    # dividiremos entre el numero de semanas
    return ingredientes, pizzas, pedidos_detallados, pedidos


def cambias_one_1(pedidos_detallados):
    lista = []
    lista_mala = []
    for cantidad in range(0, len(pedidos_detallados["quantity"])):
        lista_mala.append(cantidad)
        a = re.sub('one', '1', pedidos_detallados['quantity'][cantidad])
        b = re.sub('0ne', '1', a)
        c = re.sub('One', '1', b)
        e = re.sub('two', "2", c)
        f = re.sub("-1", "1", e)
        lista.append(int(f))
    pedidos_detallados["quantity"] = lista
    return pedidos_detallados


def diccionario_ingredientes(ingredientes):
    diccionario_ingredientes = {}  # Creamos un diccionario vacio
    lista_uncia = []  # Tenemos una lista vacia
    # nos pasamos lo singredientes a una lista
    lista_ingredientes = ingredientes["ingredients"].tolist()
    for i in range(len(lista_ingredientes)):  # Recorremos dicha lista
        # Separamos los ingredientes asociados a cada una de las pizzas y las convertimos en llave de mi diccionario
        separaciones = lista_ingredientes[i].split(", ")
        for j in range(len(separaciones)):
            if separaciones[j] not in lista_uncia:
                a = separaciones[j]
                lista_uncia.append(a)
    for i in lista_uncia:
        # Inicializamos todo ingrediente(llave de mi diccioanrio) a valor 0
        diccionario_ingredientes[i] = 0
    # Devolvemos el diccioanrio que tiene por clave todo los ingredienets y como valores todo 0
    return diccionario_ingredientes


def ing_pizza(ingredientes):  # Funcion encargada de definir que ingredienets tiene cada pizza
    diccionario_ingredientes_por_pizza = {}  # Creamos un diccionario nuevo
    # extraemos nombre generico sin tamaño
    tipo_pizza_generico = ingredientes["pizza_type_id"].to_list()
    #  Sacamos todos los ingredienets asociados a cada pizza
    lista_ingredientes = ingredientes["ingredients"].tolist()
    lista_nueva = []  # inicializamos lista vacia
    for ing_p in lista_ingredientes:
        lista_nueva.append(ing_p.split(", "))

    for i in range(len(tipo_pizza_generico)):
        diccionario_ingredientes_por_pizza[tipo_pizza_generico[i]
                                           ] = lista_nueva[i]
    return diccionario_ingredientes_por_pizza


def ponderacion_semanal(ingredientes, pedidos_detallados):
    pizzas_numero_anual = {}
    tipos_pizza = pedidos_detallados["pizza_id"].unique().tolist()
    for pizza in tipos_pizza:
        pizzas_numero_anual[pizza] = pedidos_detallados[pedidos_detallados["pizza_id"]
                                                        == pizza]["quantity"].sum()
    # ahora tendria en el diccionario el numeor de pizzas anuales
    # paar saber las semanas dividire entre 51, a pesar de que un año tenga 52 semanas con el fin de prevenir una semana de mayor media
    pizzas_numero_semanal = {}
    for pizza in tipos_pizza:
        # el mas 1 lo sumaremos para tener en cuenta aquellas pizzas que no llegan siquiera a 1 por semana
        pizzas_numero_semanal[pizza] = pizzas_numero_anual[pizza] // 51 + 1
    # Ahora toca crear el respecticvo diccionario que contenga el nombre de la pizza y los ingredientes que requiere
    diccionario_ingredientes = {}
    # los tipos de pizza seran nuestras pizzas sin tener en cuenta tamaños
    tipo_pizza = ingredientes["pizza_type_id"].tolist()
    # Los valores de nuestro diccionario serán los ingredientes
    tamaños = ["m", "s", "l", "xl", "xxl"]
    diccionario_pizzas = {}
    nombres_pizzas_genericos = list(ingredientes["pizza_type_id"])
    for nombre in nombres_pizzas_genericos:
        diccionario_pizzas[nombre] = 0

    for pizza in tipos_pizza:  # Bucle realizado para eliminar el tamaño de pizzas para facilitarnos lectura posterior
        # Realizado una vez se ha tenido en cuenta la ponderaion por tamaños
        a = str(pizza)
        if "_s" in a:
            numero_pizzas = pizzas_numero_semanal[pizza]
            nm = a[:-2]
            diccionario_pizzas[nm] += numero_pizzas
        if "_m" in a:
            numero_pizzas = pizzas_numero_semanal[pizza] * 2
            nm = a[:-2]
            diccionario_pizzas[nm] += numero_pizzas

        if "_l" in a:
            numero_pizzas = pizzas_numero_semanal[pizza] * 3
            nm = a[:-2]
            diccionario_pizzas[nm] += numero_pizzas

        if "_xl" in a:
            numero_pizzas = pizzas_numero_semanal[pizza] * 4
            nm = a[:-3]
            diccionario_pizzas[nm] += numero_pizzas

        if "_xxl" in a:
            numero_pizzas = pizzas_numero_semanal[pizza] * 5
            nm = a[:-4]
            diccionario_pizzas[nm] += numero_pizzas
    return diccionario_pizzas


def transform(ingredientes, pizzas, pedidos_detallados):
    pedidos_detallados = cambias_one_1(pedidos_detallados)
    # contenido practica 1
    # diccionario inicializado a 0 con el numero de ingredientes de cada tipo
    diccionario_ingredientes_0 = diccionario_ingredientes(ingredientes)
    # diccionario con ingredientes por pizza
    ingredientes_cada_pizza = ing_pizza(ingredientes)
    # diccionario con numero pizzas semanales con ponderacion por tamaño
    pizzas_semana = ponderacion_semanal(ingredientes, pedidos_detallados)
    return pizzas_semana, ingredientes_cada_pizza, diccionario_ingredientes_0


def ingredientes_xml(diccionario_ingredientes):
    diccionario_ingredientes_ordenado = dict(sorted(diccionario_ingredientes.items(),
                                                    key=itemgetter(1), reverse=True))

    root = ET.Element("Ingredientes_semanales")
    root.text = "Cantidad estimada ingredientes semanales"

    # Para cada dataframe empleado en el programa
    lista_claves = list(diccionario_ingredientes_ordenado.keys())
    contador = 0
    for key in lista_claves:
        ingredient = ET.SubElement(root, "Ingredient")
        ET.SubElement(ingredient, "INDEX").text = str(contador)
        ET.SubElement(ingredient, "INGREDIENT", Name=str(key))
        ET.SubElement(ingredient, "QUANTITY", Units=str(
            diccionario_ingredientes_ordenado[key]))
        contador += 1

    ET.indent(root)
    # Escribimos todos los datos organizados en un fichero xml
    tree = ET.ElementTree(root)
    tree.write("ingredientes_per_week.xml",
               xml_declaration=True, encoding='UTF-8')


def pizzas_semnales(diccionario_pizzas):
    diccionario_pizzas_ordenado = dict(sorted(diccionario_pizzas.items(),
                                              key=itemgetter(1), reverse=True))
    root = ET.Element("XML_MAVEN_PIZZAS_INGREDIENTS_2016")
    root.text = "Pizzas per week"
    lista_claves = list(diccionario_pizzas_ordenado.keys())
    contador = 0
    for key in lista_claves:
        pizzas = ET.SubElement(root, "Pizza")
        ET.SubElement(pizzas, "INDEX").text = str(contador)
        ET.SubElement(pizzas, "PIZZA_ID", Name=str(key))
        ET.SubElement(pizzas, "QUANTITY", Units=str(
            diccionario_pizzas_ordenado[key]))
        contador += 1
    ET.indent(root)
    tree = ET.ElementTree(root)
    tree.write("Pizzas_week.xml",
               xml_declaration=True, encoding="UTF-8")


def informe_datasets(lista_datasets):
    # Cabe destacar que al igual que el resto de .xml creados me he basado en
    # informacion sacada tantos de videos tutoriales de yt como de distintos blogs de
    # data adquisition
    lista_nombres = ["Pizza_types", "Pizzas", "Order_details", "Orders"]
    root = ET.Element("XML_MAVEN_PIZZAS_2016")  # titulo generico del trabajo
    # vamos a crear un xml con el informe de mis datos
    root.text = "Informe de los datos"
    contador = 0
    for csv in lista_datasets:  # por cada uno de los csv haremos lo siguiente
        df = ET.SubElement(
            root, "DATASET", nombre_dataset=str(lista_nombres[contador]))
        ET.SubElement(df, "Null", total_of_Nulls=str(
            csv.isnull().sum().sum()))  # obtenemos los nulls totales
        ET.SubElement(df, "NaN", total_of_Nans=str(
            csv.isna().sum().sum()))  # obtenemos los nans totales
        # ahora averiguaremos la tipologia de cada columna
        column_names = list(csv.columns.values)
        for column in column_names:
            columna = ET.SubElement(df, "columna", column_name=column)
            ET.SubElement(columna, "Tipologia",
                          tipologia_columna=str(csv[column].dtype))
        contador += 1
    ET.indent(root)
    # Escribimos todos los datos organizados en un fichero xml
    tree = ET.ElementTree(root)
    tree.write("informe_dataframes_pizzas_maven_2016.xml",
               xml_declaration=True, encoding='UTF-8')


def load(diccionario_ingredientes_0, ingredientes_cada_pizza, pizzas_semana, tipo_pizza_generico):
    for pizza in tipo_pizza_generico:
        a = pizzas_semana[pizza]
        lista_ing = ingredientes_cada_pizza[pizza]
        for ing in lista_ing:
            diccionario_ingredientes_0[ing] += a
    return diccionario_ingredientes_0


if __name__ == "__main__":
    ingredientes, pizzas, pedidos_detallados, pedidos = extract()
    tipo_pizza_generico = ingredientes["pizza_type_id"].to_list()
    pizzas_semana, ingredientes_cada_pizza, diccionario_ingredientes_0 = transform(
        ingredientes, pizzas, pedidos_detallados)
    diccionario_ingredientes = load(
        diccionario_ingredientes_0, ingredientes_cada_pizza, pizzas_semana, tipo_pizza_generico)
    df = pd.DataFrame([[key, diccionario_ingredientes[key]]
                       for key in diccionario_ingredientes.keys()], columns=['Ingredients', 'Quantity'])
    ingredientes_xml(diccionario_ingredientes)
    pizzas_semnales(pizzas_semana)
    lista_datasets = extract_rudimentario()
    informe_datasets(lista_datasets)
