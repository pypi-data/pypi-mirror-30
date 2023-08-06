from setuptools import setup, find_packages

f=open('README.txt', encoding='UTF-8')
a=f.read()

setup(name="triz2sce",
	author="Pedro Fernández",
	author_email="rockersuke@gmail.com",
	version="1.0",
	license="MIT",
	url="http://www.zonafi.rockersuke.com/triz2sce/index.html",
	description="Convierte mapas de aventuras de texto generados por Trizbort en código fuente para el DAAD.",
	long_description=a,
	python_requires=">=3.5",
	scripts=['triz2sce.py', 'triz2sce_func.py'],
)