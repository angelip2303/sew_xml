import xml.etree.ElementTree as ET

# +--------------------+
# | -*- XML PARSER -*- |
# +--------------------+

class XMLParser:

    NAMESPACE = '{https://www.uniovi.es}'

    def __init__(self, path_to_file):
        with open(path_to_file, 'rb') as xml_file:
            tree = ET.parse(xml_file)
        self.root = tree.getroot()
        child = self.root.find(self.NAMESPACE + 'persona')
        self.root_node = self.parse_person(child)
        self.create_person(self.root_node, child)

    class Persona:

        def __init__(self, name, surname, date_of_birth, date_of_death, comments):
            self.name = name
            self.surname = surname
            self.date_of_birth = date_of_birth
            self.date_of_death = date_of_death
            self.comments = comments

            self.parent_left = None
            self.parent_right = None

            self.coordinates = []
            self.photos = []
            self.videos = []

        def add_parent(self, parent):
            if not self.parent_left:
                self.parent_left = parent
            elif not self.parent_right:
                self.parent_right = parent

    class Coordinate:

        def __init__(self, place, type, length, latitude, heigth):
            self.place = place
            self.type = type
            self.length = float(length)
            self.latitude = float(latitude)
            self.heigth = int(heigth)

    class Photo:

        def __init__(self, url):
            self.url = url

    class Video:

        def __init__(self, url):
            self.url = url

    def parse_person(self, child):
        name = child.get('nombre')
        surname = child.get('apellidos')
        date_of_birth = child.get('fechaNacimiento')
        date_of_death = child.get('fechaFallecimiento')
        comments = child.get('comentarios')

        return self.Persona(name, surname, date_of_birth, date_of_death, comments)

    def parse_coordinate(self, child):
        place = child.get('lugar')
        type = child.get('tipo')
        length = child.get('longitud')
        latitude = child.get('latitud')
        heigth = child.get('altitud')

        return self.Coordinate(place, type, length, latitude, heigth)

    def parse_photo(self, child):
        return self.Photo(child.get('url'))

    def parse_video(self, child):
        return self.Video(child.get('url'))

    def create_person(self, p, node):
        if not node:
            return # STOP rec
        else:
            # We add the parents...
            for e in node.findall(self.NAMESPACE + 'persona'):
                person = self.parse_person(e)
                p.add_parent(person)
                self.create_person(person, e)

            # We add the coordinates...
            for e in node.findall(self.NAMESPACE + 'coordenada'):
                p.coordinates.append(self.parse_coordinate(e))

            # We add the photos...
            for e in node.findall(self.NAMESPACE + 'fotografia'):
                p.photos.append(self.parse_photo(e))

            # We add the videos...
            for e in node.findall(self.NAMESPACE + 'video'):
                p.videos.append(self.parse_video(e))

# +-------------------+
# | -*- XML 2 KML -*- |
# +-------------------+

class Xml2Kml:

    kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<name> Árbol Genealógico - Lugares de nacimento y defunción </name>
<open>1</open>
%s
</Document>
</kml>
    '''

    def __init__(self, xml_file, kml_file):
        self.xml_parser = XMLParser(xml_file)
        self.kml = self.kml % self.rec(self.xml_parser.root_node)
        open(kml_file, 'w', encoding='utf-8').write(self.kml)

    def person_2_kml(self, p, aux=''):
        for e in p.coordinates:
            aux += '<Placemark>'
            aux += '\n<name> Lugar de %s de %s %s </name>' % (e.type.lower(), p.name, p.surname)
            
            if (e.type.lower() == 'nacimiento'):
                aux += '\n<description> Nació el día: %s </description>' % (p.date_of_birth)
            elif (e.type.lower() == 'fallecimiento'):
                aux += '\n<description> Falleció el día: %s </description>' % (p.date_of_death)
            
            aux += '\n<Point>'
            aux += '\n<coordinates>%.6f,%.6f,%d</coordinates>' % (e.length, e.latitude, e.heigth)
            aux += '\n</Point>'
            aux += '\n</Placemark>' + 2*'\n'

        return aux

    def rec(self, p, ans=''):
        if (not p):
            return ans

        ans += self.person_2_kml(p)

        return ans + self.rec(p.parent_left) + self.rec(p.parent_right)

# +----------------------+
# | -*- MAIN METHODS -*- |
# +----------------------+

def main():
    xml_file = input('Seleccione el archivo XML: ')
    kml_file = input('Indique el nombre del archivo KML generado: ')

    try:
        Xml2Kml(xml_file, kml_file)
    except FileNotFoundError:
        print('No se ha podido encontrar el archivo... Vamos a volver a intentarlo!')
        main()
    

if __name__ == "__main__":
    main()