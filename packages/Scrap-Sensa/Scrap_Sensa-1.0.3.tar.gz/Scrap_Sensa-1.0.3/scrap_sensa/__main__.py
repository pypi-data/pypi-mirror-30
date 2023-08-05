#!/usr/bin/env python
# -*- coding: utf-8  -*-

import requests
import unicodecsv
from bs4 import BeautifulSoup
import json
import re

inputurl = input("Url de la ficha")

def scrappingpelicula():
		url = inputurl + '/reparto/'
		page = requests.get(url)
		statusCode = page.status_code

		pagescrap = BeautifulSoup(page.content, "html.parser")

		pelicula = pagescrap.find('div', {'class': 'titlebar titlebar-page'}).getText()

		return pelicula

def scrappingreparto():
		url = inputurl + '/reparto/'
		page = requests.get(url)
		statusCode = page.status_code
		
		directors = {}
		actors = {}

		pagescrap = BeautifulSoup(page.content, "html.parser")

		directores = pagescrap.find_all('section',{'class':'section casting-director'})
		modact = pagescrap.find('section',{'class':'section casting-actor'})
		actores = modact.find_all('div',{'class':'card card-person col-xs-6'})

		for director in directores:
				nombre = director.find('span',{'itemprop':'name'}).getText()[1:-2]
				nombre = {}
				nombre['url_foto'] = director.find('img', {'class':'thumbnail-img'})['src']
				nombre['nombre'] = director.find('a',{'class':'meta-title-link'}).getText()[1:-2]
				nombre['page'] = 'http://www.sensacine.com' + director.find('a',{'class':'meta-title-link'})['href']
				directors[nombre['nombre']] = nombre	

		for actor in actores:
				nombre = actor.find('span',{'itemprop':'name'}).getText()
				nombre = {}
				nombre['url_foto'] = actor.find('img', {'class':'thumbnail-img'})['data-src']
				nombre['nombre'] = actor.find('span',{'itemprop':'name'}).getText()
				nombre['personaje'] = actor.find('div',{'class':'meta-sub light'}).getText()[22:-9]
				nombre['page'] = 'http://www.sensacine.com' + actor.find('a',{'class':'meta-title-link'})['href']
				actors[nombre['nombre']] = nombre
			
		objeto = {}

		objeto['directors'] = directors
		objeto['actors'] = actors		

		return objeto
		
def scrappingcritica():
		url = inputurl + '/criticas-prensa/'
		page = requests.get(url)
		statusCode = page.status_code
		
		critics = {}

		pagescrap = BeautifulSoup(page.content, "html.parser")

		criticas = pagescrap.find_all('div',{'class':'item hred'})
		hola = pagescrap.find_all('a')

		for i, critica in enumerate(criticas):
				numero = {}
				numero['nombre_medio'] = critica.find('h2',{'class':'title'}).getText()[1:-1]
				#numero['url_medio'] = 'http://www.sensacine.com' + critica.find('h2',{'class':'title'})['href']
				numero['autor'] = critica.find('span',{'class':'author'}).getText()[21:-14]
				numero['critica'] = critica.find('p',{'class':'text'}).getText()[14:-10]
				contenedor = critica.find('div',{'class':'stareval stareval-medium '})
				punt = contenedor.find_all('div')[0]['class'][1][1:]
				estrellas = punt[0:-1]
				dic = {'5':'1','0':'0'}
				mediaestrella = dic[punt[1:]]
				puntuacion = []

				for estrella in range(int(estrellas)):
					puntuacion.append(2)

				if int(estrellas) == 5:
					ok = 1

				else:
					puntuacion.append(int(mediaestrella))

					for estrella in range(4-int(estrellas)):
						puntuacion.append(0)					

				numero['puntuacion'] = puntuacion
				critics[i+1] = numero

		return critics

def scrappingfotos():
		url = inputurl + '/fotos/'
		page = requests.get(url)
		statusCode = page.status_code
		
		fot = []

		pagescrap = BeautifulSoup(page.content, "html.parser")

		fotos = pagescrap.find_all('a',{'class':'shot-item'})

		for foto in fotos:
			dominio = 'http://www.sensacine.com'
			path = foto['href']
			url = dominio + path
			page = requests.get(url)
		
			pagescrap = BeautifulSoup(page.content, "html.parser")

			foto = pagescrap.find('img',{'class':'gallery-media photo'})['src']
			fot.append(foto)

		return fot	

def scrappingcuriosidades():
		url = inputurl + '/secretos/'
		page = requests.get(url)
		statusCode = page.status_code
		
		curiosidades = {}

		pagescrap = BeautifulSoup(page.content, "html.parser")

		secrets = pagescrap.find_all('div',{'class':'trivia hred'})

		for secret in secrets:
			titulo = secret.find('h2', {'class':'trivia-title'}).getText()[2:-2]
			curiosidad = secret.find('div', {'class':'trivia-news'}).getText()[1:-1]
			curiosidades[titulo] = curiosidad

		return curiosidades

def createjson():
		pelicula = scrappingpelicula()
		f

		objeto = scrappingreparto()
		criticas = scrappingcritica()
		fotos = scrappingfotos()
		curiosidades = scrappingcuriosidades()

		objeto['criticas'] = criticas
		objeto['fotos'] = fotos
		objeto['curiosidades'] = curiosidades

		jsonstr = json.dumps(objeto, indent=4, ensure_ascii=False)

		f = open('data.json','w')
		f.write(jsonstr)
		f.close()
		print('hecho')

createjson()

