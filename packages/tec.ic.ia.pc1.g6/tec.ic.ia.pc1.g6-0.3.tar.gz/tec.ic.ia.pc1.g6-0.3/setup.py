from setuptools import setup

setup(name='tec.ic.ia.pc1.g6',
      version='0.3',
      description='Modulo para la generación de muestras',
      url='https://github.com/Xbolanos/PC1-IA/',
      author='Grupo6-IA-ITCR',
      py_modules=['tec.ic.ia.pc1.g06'],
      package_data={
        'minutes': ['minutes.csv'],
        'properties': ['properties.csv']
      })
