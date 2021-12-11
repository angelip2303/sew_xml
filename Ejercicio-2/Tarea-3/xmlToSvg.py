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
# | -*- XML 2 SVG -*- |
# +-------------------+

class Xml2Svg:

    WIDTH = 2400
    HEIGHT = 2400
    Y_INC = 400

    FONT_SIZE = 20

    svg = '''<svg version="1.1" xmlns="http://www.w3.org/2000/svg"
    width="%dpx" height="%dpx" viewBox="0 0 %d %d">%s

    <style><![CDATA[
    text{
        dominant-baseline: middle;
        text-anchor: middle;
        font: %s Verdana, Helvetica, Arial, sans-serif;
    }

    line {
        stroke:rgb(0,0,0);
        stroke-width:2;
    }
    ]]></style>
</svg>
    '''

    def __init__(self, xml_file, svg_file):
        self.xml_parser = XMLParser(xml_file)
        generated_svg = self.rec(self.xml_parser.root_node, self.WIDTH/2, self.FONT_SIZE, 1)
        self.svg = self.svg % (self.WIDTH, self.HEIGHT, self.WIDTH, self.HEIGHT, generated_svg, self.FONT_SIZE)
        open(svg_file, 'w', encoding='utf-8').write(self.svg)

    def person_2_svg(self, p, x, y, aux=''):
        text = lambda x,y,z,a: '\n\t\t<text x="%d" y="%d" %s> %s </text>' % (x,y,z,a)
        y_calc = lambda x: y + x * self.FONT_SIZE + 1

        aux += '\n\t<g>'

        aux += text(x,y_calc(1),'font-weight="bold"',(p.name + ' ' + p.surname))
        aux += text(x,y_calc(2),'',('Nacimiento: ' + p.date_of_birth))
        aux += text(x,y_calc(3),'',('Defunción: ' + p.date_of_death)) if p.date_of_death else ''
        aux += text(x,y_calc(4),'font-style="italic"',(p.comments))

        i = -3
        for e in p.coordinates:
            i += 3
            aux += text(x,y_calc(5 + i),'font-weight="bold"',e.type.capitalize())
            aux += text(x,y_calc(6 + i),'',('Lugar: ' + e.place))
            aux += text(x,y_calc(7 + i),'',('%.5f / %.5f / %d' % (e.length, e.latitude, e.heigth)))
        
        for img in p.photos:
            aux += text(x,y_calc(8 + i),'',(img.url))
            i+=1

        for video in p.videos:
            aux += text(x,y_calc(8 + i),'',(video.url))
            i+=1

        aux += '\n\t</g>'

        return aux, i

    def line_generator(self, x1, y1, x2, y2, aux=''):
        aux += '\n\t<line x1="%d" y1="%d" x2="%d" y2="%d" />' % (x1, y1, x2, y2-self.FONT_SIZE)
        return aux

    def rec(self, p, x, y, i, ans=''):
        if (not p):
            return ans

        person = self.person_2_svg(p, x, y)
        ans += person[0]

        i += 1

        x_l = x - self.HEIGHT/(2**i)
        x_r = x + self.HEIGHT/(2**i)
        y_2 = y + self.Y_INC
        y = y + (person[1] + 7) * self.FONT_SIZE + 10

        if (p.parent_left):
            ans += self.line_generator(x, y, x_l, y_2)
            ans += self.rec(p.parent_left, x_l, y_2, i)

        if (p.parent_right):
            ans += self.line_generator(x, y, x_r, y_2)
            ans += self.rec(p.parent_right, x_r, y_2, i)

        return ans

# +----------------------+
# | -*- MAIN METHODS -*- |
# +----------------------+

def main():
    xml_file = input('Seleccione el archivo XML: ')
    svg_file = input('Indique el nombre del archivo SVG generado: ')

    try:
        Xml2Svg(xml_file, svg_file)
    except FileNotFoundError:
        print('No se ha podido encontrar el archivo... Vamos a volver a intentarlo!')
        main()

if __name__ == "__main__":
    main()