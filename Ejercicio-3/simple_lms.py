import sys
import os
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import webbrowser
import time

# +----------------------+
# | -*- SCORM LOADER -*- |
# +----------------------+

class ScormLoader:

    SCORM_FOLDER = 'scorm_files'
    SCORM_COURSES = 'scorm_courses'
    SCORM_NAMESPACE = '{http://www.imsproject.org/xsd/imscp_rootv1p1p2}'

    def __init__(self):
        # We extract all the files in the scorm folder
        for file in os.listdir(self.SCORM_FOLDER):
            with ZipFile('%s/%s' % (self.SCORM_FOLDER, file), 'r') as zipObj:
                # Extract all the contents of zip file in current directory
                zipObj.extractall('%s/%s' % (self.SCORM_COURSES, file.split('.')[0]))

        self.validate_courses()

    def validate_courses(self):
        self.valid_units = []

        # We validate the courses
        for file in os.listdir(self.SCORM_COURSES):
            with open('%s/%s/imsmanifest.xml' % (self.SCORM_COURSES, file), 'rb') as manifest:
                    tree = ET.parse(manifest)

            root = tree.getroot()
            child = root.find(self.SCORM_NAMESPACE + 'resources').find(self.SCORM_NAMESPACE + 'resource')
            self.valid_units.append('%s/%s/%s' % (self.SCORM_COURSES, file, child.get('href')))

# +----------------+
# | -*- COURSE -*- |
# +----------------+

class Course:

    def __init__(self, units):
        self.units = units

    def complete(self, i):
        webbrowser.open('file://' + os.path.realpath(self.units[i]))
        time.sleep(5)

# +------------+
# | -*- UI -*- |
# +------------+

class UI:

    def __init__(self):
        self.scorm_loader = None
        self.course = None

        self.informationDialog()
        self.loop()
    
    def informationDialog(self):
        print('+----------------------------------------------------------------+')
        print('| Bienvenido a SimpleLMS un sencillo gestor de paquetes de SCORM |')
        print('|    --> Aceptamos cualquier formato multimedia.                 |')
        print('|    --> Sólo aceptamos documentos en formato HTML.              |')
        print('|    --> Sólo aceptamos un curso cada vez.                       |')
        print('+----------------------------------------------------------------+')
        print('                                Creado por Ángel Iglesias Préstamo\n')

    def optionDialog(self):
        print('\n        -*- Elija una de las 3 opciones para continuar -*-        \n')
        print('1. Cargar los paquetes (simulación de subida de ficheros)')
        print('2. Mostar los paquetes cargados')
        print('3. Crear curso')
        print('4. Realizar curso (simulación)\n')
        print('0. Salir\n')

        return input("  --> ")

    def showPackagesLoadedDialog(self):
        print('\n        -*- Estos son los paquetes cargados -*-        \n')

        for i, unit in enumerate(self.scorm_loader.valid_units):
            print('     %d. %s' % (i, unit))

    def chooseCourseDialog(self):
        print('\nElija el tema: \n')
        self.showPackagesLoadedDialog()
        return self.scorm_loader.valid_units[int(input("\n  --> "))]

    def courseCreationDialog(self):
        print('\n        -*- Vamos a crear un CURSO -*-        \n')
        
        number_of_units = int(input('   - Número de temas: '))
        units = []

        for i in range(0, number_of_units):
            units.append(self.chooseCourseDialog())

        self.course = Course(units)

    def completeCourse(self):
        print('\n        -*- Vamos a completar el curso -*-        \n')

        for i, unit in enumerate(self.course.units):
            print('     %d. %s' % (i, unit))
        
        print('\n\nEmpezamos:\n')

        for i, unit in enumerate(self.course.units):
            print('     Completando unidad %d. %s' % (i, unit))
            self.course.complete(i)

    def loop(self):
        option = self.optionDialog()

        while (option != '0'):
            if (option == '1'):
                # Load the SCORM packages
                self.scorm_loader = ScormLoader()
            elif (option == '2'):
                # Allow the user to create a simple course
                if (self.scorm_loader != None):
                    self.showPackagesLoadedDialog()
                else:
                    print('Debe cargar primero los paquetes!')
            elif (option == '3'):
                # Allow the user to create a simple course
                if (self.scorm_loader != None):
                    self.courseCreationDialog()
                else:
                    print('Debe cargar primero los paquetes!')
            elif (option == '4'):
                # Allow the user to complete a course
                if (self.course != None):
                    self.completeCourse()
                else:
                    print('Debe crear primero un curso!')
            else:
                print('Escoja una opción válida!')
            
            option = self.optionDialog()
        
        sys.exit(0)

# +----------------------+
# | -*- MAIN METHODS -*- |
# +----------------------+

def main():
    UI()
    
if __name__ == "__main__":
    main()