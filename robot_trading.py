# Importando librerias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import yfinance as yf
import datetime
import warnings
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from IPython.display import clear_output
import time

# Declaracion de variables globales
global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision

# Definiendo funcion para importar base de datos Bitcoins

def importar_base_bitcoin():
  # Declarando las variables globales del proyecto
  global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision
  
  # Variable con transaccion a buscar
  symbol = 'BTC-USD'
  
  # Variable con la fecha actual, que es donde finaliza el periodo
  end_date = datetime.datetime.now()
  
  # Variable con la fecha inicial de periodo, que esta dado por la fecha actual menos el periodo a analizar, en este caso 7 dias
  start_date = end_date - datetime.timedelta(days = 7)
  
  # Variable con el intervalo de cada cuanto se extrae la informacion  
  interval = '5m'
  
  # Variable df_bitcoin con el dataset obtenido desde la libreria yfinance
  df_bitcoin  = yf.download(symbol,start = start_date, end = end_date, interval = interval)
  
  # Reasignando el indice al DataFrame
  df_bitcoin.reset_index(inplace = True)
  
  # Retorno de la funcion
  return df_bitcoin 

# Funcion que gestiona el nombre de las columnas para tener un mismo formato (snake_case)

def nombre_columnas():
  # Asignando una lista vacia a la variable
  df_columns = []
  
  # Bucle for para ingresar cada nombre de columna 
  for name in df_bitcoin.columns:
    # Modificando el  nombre, a formato snake_case
    df_columns.append(name.lower().replace(' ','_').strip())
  
  # Asignando los nuevos nombres de columnas
  df_bitcoin.columns = df_columns  
  
  # Retorno de la funcion
  return df_bitcoin

# Funcion para mejorar el codigo obtenido desde la pagina, reemplazando caracteres y elimimnando espacios

def trata_html(input):
  return ' '.join(input.split()).replace('> <', '><')

# Funcion que extrae las tendencias del mercado desde la pagina coinmarketcap.com

def extraer_tendencias():
  # Declarando las variables globales del proyecto
  global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision
  
  # Utilizando funcion que modifica los nombres de las columnas
  nombre_columnas()
  
  # Asignando a variable url el nombre de la pagina web
  url = 'https://coinmarketcap.com/'
  
  # Asignando los encaebezados de la pagina a la variable headers
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}
  
  # Metodo try-except que en caso de error, indica que tipo de error
  try:
    req = Request(url, headers = headers)
    response = urlopen(req)
    html = response.read().decode('utf-8')
  # Indica estado y razon de error HTTP 
  except HTTPError as e:
    print(e.status, e.reason)
  # Indica razon de error URL
  except URLError as e:
    print(e.reason)
  
  # Aplicando funcion trata_html
  trata_html(html)
  
  # Asignando codigo de pagina a la variable soup
  soup = BeautifulSoup(html,'lxml')
  
  # Bucle for para encontrar 'BTC' en la lista de transacciones de la pagina
  for p in soup.find_all('p',{'class':'sc-71024e3e-0 OqPKt coin-item-symbol'}):
    
    # Verificando si el parrafo tiene la digla 'BTC'
    if p.get_text() == 'BTC':

      # Guardando variable con el precio actual del bitcoin que entrega la pagina
      precio_actual = soup.find('div', {'class':['sc-b3fc6b7-0 dzgUIj','sc-b3fc6b7-0 dzgUIj fall','sc-b3fc6b7-0 dzgUIj rise']})
      precio_actual = float(precio_actual.get_text().replace('$','').replace(',', ''))
  
      # Guardando el valor de la tendencia que entrega la pagina
      tendencia_porcentaje = float(soup.find('span', {'class':'sc-a59753b0-0 ivvJzO'}).get_text().replace('%',''))

      # Sentencia condicional if-elif-else para asignar los criterios de tendencia segun el procentaje obtenido
      if tendencia_porcentaje > 0:
        tendencia = 'alta'
      elif tendencia_porcentaje == 0:
        tendencia = 'neutro'
      else:
        tendencia = 'baja'
      break
    
    else:
      # Mensaje en caso de no estar la transaccion en el listado principal de la pagina
      print('La transaccion no se encuentra en la tabla principal')
      break      
  
  # Retorno de la funcion
  return precio_actual, tendencia

# Funcion para limpiar DF obtenido por la libreria yfinance 

def limpieza_datos():
  
  # Declarando las variables globales del proyecto
  global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision

  # Asignanado copia del df a variable df_bitcoin_limpio
  df_bitcoin_limpio = df_bitcoin.copy()
  
  # Creando variable 'filas_eliminar' como lista vacia
  filas_eliminar = []
  
  # Sentencia condicional if, para verificar que no existen duplicados en la columa datetime
  if df_bitcoin_limpio.datetime.duplicated().sum() == 0:
    # Bucle FOR para iterar el DF, obteniendo la posicion y el valor del registro
    for index, row in df_bitcoin_limpio.iterrows():
      # Sentencia condicional if, para revisar mediante operador logico or, que los registros de la columna close o la columna volume son iguales a 0
      if row['close'] == 0 or row['volume'] == 0:
        # Guardando indices de los registros que cumplen las condiciones en la variales 'filas_eliminar'
        filas_eliminar.append(index)
  # Condicional else, aplica cuando existen duplicados en la columna datetime
  else:
    # Eliminacion de duplicados de la columna datetime
    df_bitcoin_limpio.drop_duplicates(subset = 'datetime', inplace = True)
    # Bucle FOR para iterar el DF, obteniendo la posicion y el valor del registro
    for index, row in df_bitcoin_limpio.iterrows():
      # Sentencia condicional if, para revisar mediante operador logico or, que los registros de la columna close o la columna volume son iguales a 0
      if row['close'] == 0 or row['volume'] == 0:
        # Guardando indices de los registros que cumplen las condiciones en la variales 'filas_eliminar'
        filas_eliminar.append(index)
  
  # Eliminacion de los registros, donde la columna close o la columna volume eran iguales a 0, a traves del indice del registro
  df_bitcoin_limpio.drop(filas_eliminar, inplace = True)
  
  
  # Obteniendo valores de Q1 y Q3, para realizar filtrado y elimianr outliers del DF
  q1 = df_bitcoin_limpio['close'].quantile(0.25)
  q3 = df_bitcoin_limpio['close'].quantile(0.75)

  # Eliminando Outliers del dataset, mediante filtrado segun los valores de Q1 y Q3 
  df_bitcoin = df_bitcoin_limpio[(df_bitcoin['close'] >= q1) & (df_bitcoin['close'] <= q3)]
  df_bitcoin_limpio.reset_index(inplace = True)
  
  # Retorna el DF original
  return df_bitcoin

# Funcion para indicar que accion realizar segun los datos de mercado obtenidos en el proyecto

def tomar_decisiones():
  # Declarando las variables globales del proyecto
  global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision
  
  # Obteniendo el promedio de la columna close y asignandolo a varialble media_bitcoin
  media_bitcoin = df_bitcoin['close'].mean()
  
  # Sentencia condicional if, verifica si el precio_actual sea mayor o igual que media_bitcoin y que la tendencia este a la baja
  if precio_actual >= media_bitcoin and tendencia == 'baja':
      # Asignando la accion a realizar a la variable 'algoritmo decision'
      algoritmo_decision = 'Vender'
  
  # Sentencia condicional elif, verifica si el precio_actual es menor que media_bitcoin y que la tendencia este al alza
  elif precio_actual < media_bitcoin and tendencia == 'alta':
    # Asignando la accion a realizar a la variable 'algoritmo decision'
    algoritmo_decision = 'Comprar'
  
  # Sentencia condicional else, aplica si las 2 condiones anteriores no se cumplen
  else:
    # Asignando la accion a realizar a la variable 'algoritmo decision'
    algoritmo_decision = 'Esperar'
    
# Funcion que genera grafico del DF e indica cual es la decision a ejecutar

def visualizacion():
  # Declarando las variables globales del proyecto
  global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision
  
  # Agragando columna 'promedio' al dataframe 
  df_bitcoin['promedio'] = media_bitcoin
  
  # Define el tamano del grafico, en pixeles
  plt.figure(figsize=(20,5))
  
  # Inserta un titulo al grafico
  plt.title('Robot Trading')
  
  # Traza la linea de la columna close en el grafico 
  plt.plot(df_bitcoin['close'])  
  
  # Traza la linea de la columna promedio en el grafico
  plt.plot(df_bitcoin['promedio'])
  
  # Inserta en el grafico la decision a ejecutar
  plt.annotate(f'Decision: {algoritmo_decision}',(2000, media_bitcoin + 25))
  
  # Muestra el grafico final   
  plt.show()
  
# Automatizacion del proyecto

while(True):
  
  # Funcion que elimina los resultados anteriores para poder emitir uno nuevo
  clear_output()
  
  importar_base_bitcoin()
  extraer_tendencias()
  limpieza_datos()
  tomar_decisiones()
  visualizacion()
   
  # Funcion que permite automatizar el software, ya que mide tiempo para que se ejecute el software nuevamente
  time.sleep(300)