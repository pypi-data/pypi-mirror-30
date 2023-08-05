from setuptools import setup, find_packages

setup(name='tec.ic.ia.pc1.g06',
      version='0.3.2',
      description='Modulo para la generación de muestras',
      url='https://github.com/Xbolanos/PC1-IA/',
      author='Grupo6-IA-ITCR',
      py_modules=['tec.ic.ia.pc1.g06'],
      packages=find_packages(),
      package_data={
        'pc1': ['minutes.csv'],
        'pc1': ['properties.csv']
      })
