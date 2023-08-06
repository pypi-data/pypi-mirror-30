import argparse
import sys
import xml.etree.ElementTree as etree

import triz2sce_func

print('triz2sce 1.0 180402 (c) 2018 Pedro Fernández.')

parser = argparse.ArgumentParser()
parser.add_argument("in_file", help='Fichero de entrada')
parser.add_argument("out_file", help='Fichero de salida')
parser.add_argument('-p1', help="Mensajes de sistema en primera persona", action="store_true")

args=parser.parse_args()

in_file=args.in_file
out_file=args.out_file

tree=etree.parse(in_file)
root=tree.getroot()
info=root[0]
map=root[1]

# Valores por defecto para título, autor, etc...

title='Aventura de prueba generada con triz2sce.'
author='Anónimo'
description='Aventura de prueba del script conversor triz2sce (mapas de trizbort a código fuente SCE del DAAD).'
history='Texto introductorio de la aventura.' 

# Los sustituye por los del elemento 'info' del mapa si los hubiera

for x in info:
	if x.tag=='title':
		title=x.text
	if x.tag=='author':
		author=x.text
	if x.tag=='description':
		description=x.text
	if x.tag=='history':
		history=x.text

rooms=map.findall('room')
lines=map.findall('line')

listRooms=[]
listObjects=[]
startRoom=1


print ('Creando lista de localidades y objetos.')
loc=1
for y in rooms:
	if y.get('isStartRoom')=='yes':
		startRoom=loc
	listRooms.append([y.get('description'),y.get('id'),loc])
	x=y.find('objects')
	if x!=None:
		a=x.text.strip('|')
		l=a.split('|')
		for p in l:
			genero=0
			numero=0
			propio=0
			if '[m]' in p:
				genero=1
				p=p.replace('[m]','')
			if '[f]' in p:
				genero=2
				p=p.replace('[f]','')
			if '[1]' in p:
				numero=1
				p=p.replace('[1]','')
			if '[2]' in p:
				numero=2
				p=p.replace('[2]','')
			if '[!]' in p:
				propio=1
				p=p.replace('[!]','')
			listObjects.append([triz2sce_func.acentos(p.split()[0]).upper(),loc,p.lower(), genero, numero, propio])
	loc=loc+1
	
print('Creando lista de conexiones.')	
for y in listRooms:
	a=[]
	for x in lines:
		w=x.findall('dock')
		if len(w)==2:
			for z in w:
				if y[1]==z.get('id'):
					if z.get('index')=='0':
						b=triz2sce_func.dirTransform2(x.get('startText'))
						if b!=None:
							a.append(b+' '+triz2sce_func.id2loc(w[1].get('id'),listRooms))
						else:	
							a.append(triz2sce_func.dirTransform(z.get('port'))+' '+triz2sce_func.id2loc(w[1].get('id'),listRooms))
					else:
						if x.get('flow')!='oneWay':
							b=triz2sce_func.dirTransform2(x.get('endText'))
							if b!=None:
								a.append(b+' '+triz2sce_func.id2loc(w[0].get('id'),listRooms))
							else:
								a.append(triz2sce_func.dirTransform(z.get('port'))+' '+triz2sce_func.id2loc(w[0].get('id'),listRooms))				
	y.append(a)	

# Si no hay objetos, crea una linterna como objeto dummy (como en la plantilla original)
if listObjects==[]:
	listObjects.append(['LINTERNA',0,'una linterna (encendida)'])
	
	
# Abre fichero
	
f=open(out_file,'w',encoding='850', newline='\r\n')

triz2sce_func.imprimeDEF(f)	# Imprime sección /DEF
triz2sce_func.imprimeCTL(f)	# Imprime sección /CTL
triz2sce_func.imprimeTOK(f)	# Imprime sección /TOK
triz2sce_func.imprimeVOC(f)	# Imprime sección /VOC (primera parte)

# Inserta objetos del usuario en sección /VOC

x=50
print('; Objetos definidos por el usuario en el mapa visual, si los hubiera', file=f)
for y in listObjects:
	print (y[0]+'      '+str(x)+'      noun',file=f)
	x=x+1

triz2sce_func.imprimeVOC2(f)			# Imprime sección /VOC (saegunda parte)

if args.p1:
	triz2sce_func.imprimeSTX1p(f)		# Imprime sección /STX en primera persona
else:
	triz2sce_func.imprimeSTX(f)		# Imprime sección /STX en segunda persona

triz2sce_func.imprimeMTX(f, history)			# Imprime sección /MTX

x=1
for y in rooms:
	print('/'+str(15+x), file=f)
	if y.get('subtitle')!='':
		print(y.get('subtitle')[:26], file=f)
	else:
		if y.get('name')!='Cave':
			print(y.get('name')[:26], file=f)
		else:
			print('Localidad '+str(x), file=f)
	x=x+1
	
helpMessage1=x + 15
helpMessage2=helpMessage1 + 1

print('/'+str(helpMessage1), file=f)
print(' PANTALLA DE AYUDA', file=f)
print('/'+str(helpMessage2), file=f)
print('Las aventuras conversacionales son juegos de texto basados en la exploración de localidades y la manipulación de objetos al alcance inmediato del protagonista.', file=f)
print('', file=f)
print('', file=f)
print('Las acciones se comunican al ordenador mediante frases sencillas del tipo "acción-objeto".', file=f)
print('', file=f)
print('', file=f)
print('El movimiento se efectua mediante puntos cardinales "IR NORTE", "SUR", "OESTE" o sus abreviaturas: N, S, E, O. Ocasionalmente órdenes como "SUBIR", o "ENTRAR" también funcionarán.', file=f)
print('', file=f)
print('', file=f)
print('Acciones comunes con los objetos son "COGER objeto", "DEJAR", "EXAMINAR" (o su abreviatura "EX". "INVENTARIO" (o "I") lista los objetos llevados. "MIRAR" o "M" redescribe la localidad.', file=f)
print('', file=f)
print(';', file=f)
print('OK.')


# Imprime sección /OTX

print('Imprimiendo sección /OTX',end=' -> ')
print('/OTX',file=f)
x=0
for y in listObjects:
	print('/'+str(x),file=f)
	a=''
	if y[3]==1:
		a='un '
		if y[4]==2:
			a='unos '
	if y[3]==2:
		a='una '
		if y[4]==2:
			a='unas '
	print(a+y[2],file=f)
	x=x+1
print(';', file=f)
print('OK.')

# Imprime sección /LTX	

print('Imprimiendo sección /LTX',end=' -> ')	
print('/LTX',file=f)
print('/0',file=f)
print(title.title(), file=f)
print('', file=f)
print('', file=f)
print('por: ',triz2sce_func.acentos(author).upper(), file=f)
print('', file=f)
print('', file=f)
print(description, file=f)
print('', file=f)
print('', file=f)
x=1
for y in listRooms:
	print('/'+str(x),file=f)
	if (y[0]!=''):
		print(y[0],file=f)
	else:
		print('Descripción localidad '+str(x), file=f)
	x=x+1
print(';', file=f)
print('OK.')	
	
# Imprime sección /CON

print('Imprimiendo sección /CON',end=' -> ')
print('/CON',file=f)
print('/0',file=f)
x=1
for y in listRooms:
	print('/'+str(x),file=f)
	if y[3]!=[]:
		for z in y[3]:
			print(z,file=f)
	x=x+1
print(';', file=f)
print('OK.')

# Imprime sección /OBJ

print('Imprimiendo sección /OBJ',end=' -> ')
print ('/OBJ',file=f)
print(';obj  starts  weight    c w  5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0    noun   adjective', file=f)
print(';num    at', file=f)
x=0
for y in listObjects:
	print('/'+str(x)+' '+str(y[1])+' '+'1'+' '+'_ _   _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _  '+y[0]+' _',file=f)
	x=x+1
print(';', file=f)
print('OK.')

triz2sce_func.imprimePRO0(f)								# Imprime sección /PRO 0
triz2sce_func.imprimePRO1(f)								# Imprime sección /PRO 1
triz2sce_func.imprimePRO2(f)								# Imprime sección /PRO 2
triz2sce_func.imprimePRO3(f)								# Imprime sección /PRO 3
triz2sce_func.imprimePRO4(f)								# Imprime sección /PRO 4
triz2sce_func.imprimePRO5(f, helpMessage1, helpMessage2)			# Imprime sección /PRO 5
triz2sce_func.imprimePRO6(f,startRoom)						# Imprime sección /PRO 6
triz2sce_func.imprimeOtrosPros(f)							# Imprime otros PROs

# Imprime la parte de PRO 11 que pone el atributo subtitle en la barra de estado

x=1
for y in listRooms:
	print('_	_	AT '+str(x), file=f)
	print('		MES '+str(x+15), file=f)
	print('', file=f)
	x=x+1

triz2sce_func.imprimeOtrosPros2(f)		# Imprime otros PROs

# Cierra fichero

f.close()

	





