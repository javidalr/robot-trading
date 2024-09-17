# **Robot Trading**

## **Descripcion**

Software que busca los valores de las acciones de "BTC-USD" desde la libreria yfinance, y entrega los precios de las transacciones de los ultimos 7 dias, cada 5 minutos, esto permite al software, mediante los criterios entregados simular la accion de tomar decisiones referente a los datos que entrega el mercado, el cual informa sobre la variacion en los valores de apertura y cierre durante el periodo establecido del Bitcoin(BTC) sobre el dolar(USD).

Ademas, extrae el valor de bitcoin aproximadamente en tiempo real, para comparar la media del cierre de los registros de la ultima semana con el valor actual, y obtiene su tendencia para posteriormente orientar al usuario sobre la accion que debe tomar referente a la informacion obtenida.

Por ultimo, el proyecto genera un grafico con la decision del software, y esta automatizado para que cada 5 minutos, obtenga nuevamente la informacion y se actualice aproximadamente en tiempo real. 

## **Librerias utilizadas**

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
import timegit a