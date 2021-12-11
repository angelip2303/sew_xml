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

# +--------------------+
# | -*- XML 2 HTML -*- |
# +--------------------+

class Xml2Html:

    STARTING_TAB = 3
    sep = lambda self, x: '\n' + x * '\t'

    html = '''<!DOCTYPE HTML>
<html lang="es">
    <head>
        <meta charset="UTF-8" />
        <meta name="author" content="Ángel Iglesias Préstamo" />
        <meta name="description" content="Ejemplo de árbol genealógico convertido a HTML desde un XML." />
        <meta name="keywords" content="html,xml,árbol,genealógico" />
        <meta name="viewport" content ="width=device-width, initial scale=1.0" />
        <title>Arbol Genealógico - Ángel</title>
        <base href="media/" />
        <link rel="stylesheet" type="text/css" href="../estilos.css" />
    </head>

    <body>
        <h1> Árbol Genealógico </h1>
        <ul>%s
        </ul>
    </body>
</html>    
    '''

    def __init__(self, xml_file, html_file):
        self.xml_parser = XMLParser(xml_file)
        self.html = self.html % self.rec(self.xml_parser.root_node, self.STARTING_TAB)
        open(html_file, 'w', encoding='utf-8').write(self.html)

    def person_2_html(self, p, i, aux=''):
        for img in p.photos:
            aux += self.sep(i) + '<img src="%s" alt="%s"/>' % (img.url, p.comments)

        aux += self.sep(i) + '<p> Nombre: %s </p>' % p.name
        aux += self.sep(i) + '<p> Apellidos: %s </p>' % p.surname
        aux += self.sep(i) + '<p lang="en"> Fecha de nacimiento: %s </p>' % p.date_of_birth
        aux += self.sep(i) + '<p lang="en"> Fecha de fallecimiento: %s </p>' % p.date_of_death if p.date_of_death else ''
    
        for e in p.coordinates:
            aux += self.sep(i) + '<p> %s </p>' % e.type.upper()
            aux += self.sep(i) + '<p> Lugar: %s </p>' % e.place
            aux += self.sep(i) + '<p> Coordenadas: %.5f / %.5f / %d </p>' % (e.length, e.latitude, e.heigth)

        for video in p.videos:
            aux += self.sep(i) + '<video src="%s" controls> </video>' % video.url

        return aux

    def rec(self, p, i, ans=''):
        if (not p):
            return ans

        start_li = self.sep(i) + '<li>'
        end_li = self.sep(i) + '</li>'

        i += 1

        start_ul = self.sep(i) + '<ul>'
        end_ul = self.sep(i) + '</ul>'

        ans += start_li + self.person_2_html(p, i)

        if (p.parent_left and p.parent_right):
            ans += start_ul
            ans += self.rec(p.parent_left, i)
            ans += self.rec(p.parent_right, i)
            ans += end_ul

        elif (p.parent_left):
            ans += start_ul
            ans += self.rec(p.parent_left, i)
            ans += end_ul

        elif (p.parent_right):
            ans += start_ul
            ans += self.rec(p.parent_right, i)
            ans += end_ul

        ans += end_li

        return ans

# +----------------------+
# | -*- MAIN METHODS -*- |
# +----------------------+

def main():
    xml_file = input('Seleccione el archivo XML: ')
    html_file = input('Indique el nombre del archivo HTML generado: ')

    try:
        Xml2Html(xml_file, html_file)
    except FileNotFoundError:
        print('No se ha podido encontrar el archivo... Vamos a volver a intentarlo!')
        main()
    

if __name__ == "__main__":
    main()