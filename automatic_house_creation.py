import xml.etree.ElementTree as ET
import random
import os
import json

from sprites import count_number_house_tmx_files
# Create the root element}


def create_house_interior():
    width = 10
    height = 10
    #root = ET.Element("?xml")
    #root.set('version', '1.0')
    # root.set('encoding', 'utf-8')

    mapa = ET.Element('map')
    mapa.set('version', '1.10')
    mapa.set('tiledversion', '1.10.2')
    mapa.set('orientation', 'orthogonal')
    mapa.set('renderorder', 'right-down')
    mapa.set('width', '50')
    mapa.set('height', '30')
    mapa.set('tilewidth', '64')
    mapa.set('tileheight', '64')
    mapa.set('infinite', '0')
    mapa.set('nextlayerid', '4')
    mapa.set('nextobjectid', '52')
    mapa.text = ''

    tileset = ET.SubElement(mapa, 'tileset')
    tileset.set('firstgid', '1')
    tileset.set('source', '../img/Kenney Topdown Pack.tsx')

    


    layer= ET.SubElement(mapa, 'layer')
    layer.set('id', '1')
    layer.set('name', 'ground')
    layer.set('width', f'{width}')
    layer.set('height', f'{height}')

    data = ET.SubElement(layer, 'data')

    data.set('encoding', 'csv')

    data_list = ''


    floor = random.choice([[x for x in range(42, 48)],
                        [x for x in range(69, 74)],
                        [x for x in range(96, 102)]]
                        )

    n_furniture = 3     
    possible_furniture = [450, 451, 477, 478]
    loc_chair = [(random.randrange(3, height - 3), random.randrange(3, width - 3))
                for _ in range(n_furniture)]

    n_possible_furniture = 0
    loc_chair = set()
    while n_possible_furniture < n_furniture:
        length_before = len(loc_chair)
        loc_chair.add((random.randrange(3, height - 3), random.randrange(3, width - 3)))
        length_after = len(loc_chair)

        if length_before < length_after:
            n_possible_furniture += 1

    loc_chair = sorted(list(loc_chair))

    

    for r in range(height):
        for c in range(width):
            
            if r == 0 and c == 0:
                data_list += f'{random.choice(floor)}'
            else:
                data_list += f',{random.choice(floor)}'
        data_list += '\n'

    data.text = data_list


    objectgroup = ET.SubElement(mapa, 'objectgroup')
    objectgroup.set('id', '3')
    objectgroup.set('name', 'obstacles')
    #<object id="1" name="player" x="656" y="272" width="32" height="30"/>

    for i, lc in enumerate(loc_chair):
        obj = ET.SubElement(objectgroup, 'object')
        obj.set('id', f'{i + 1}')
        obj.set('name', 'wall')
        obj.set('x', f'{lc[1] * 64 + 32 + 32*i}')
        obj.set('y', f'{lc[0] * 64 + 16}')
        obj.set('width', '32')
        obj.set('height', '30')
    
    idx = i + 2
    obj = ET.SubElement(objectgroup, 'object')
    obj.set('id', f'{idx}')
    obj.set('name', 'wall')
    obj.set('x', '0')
    obj.set('y', '0')
    obj.set('width', '16')
    obj.set('height', '640')

    idx += 1
    obj = ET.SubElement(objectgroup, 'object')
    obj.set('id', f'{idx}')
    obj.set('name', 'wall')
    obj.set('x', '624')
    obj.set('y', '0')
    obj.set('width', '16')
    obj.set('height', '640')

    idx += 1
    obj = ET.SubElement(objectgroup, 'object')
    obj.set('id', f'{idx}')
    obj.set('name', 'wall')
    obj.set('x', '16')
    obj.set('y', '0')
    obj.set('width', '608')
    obj.set('height', '16')

    idx += 1
    obj = ET.SubElement(objectgroup, 'object')
    obj.set('id', f'{idx}')
    obj.set('name', 'wall')
    obj.set('x', '16')
    obj.set('y', '624')
    obj.set('width', '608')
    obj.set('height', '16')

    idx += 1
    obj = ET.SubElement(objectgroup, 'object')
    obj.set('id', f'{idx}')
    obj.set('name', 'player')
    obj.set('x', '100')
    obj.set('y', '400')
    obj.set('width', '32')
    obj.set('height', '32')


    layer2 = ET.SubElement(mapa, 'layer')
    layer2.set('id', '2')
    layer2.set('name', 'trees')
    layer2.set('width', f'{width}')
    layer2.set('height', f'{height}')

    data2 = ET.SubElement(layer2, 'data')

    data2.set('encoding', 'csv')


    data_list = ''


    idx = 0
    for r in range(height):
        for c in range(width):
            
            if c == loc_chair[idx][1] and r == loc_chair[idx][0]:
                data_list += f',{random.choice(possible_furniture)}'
                if idx < n_furniture - 1:
                    idx += 1
            if r == 0 and c == 0:
                data_list += '0'
            else:
                data_list += f',0'

        data_list += '\n'
        


    data2.text = data_list
    



    tree = ET.ElementTree(mapa)

    n_house_interior_tmx_files = count_number_house_tmx_files('maps')

    print('n_house_interior_tmx_files')
    print(n_house_interior_tmx_files)

    path = 'maps'
    house_interior = f'house_interior{n_house_interior_tmx_files + 1}'
    fullpath = os.path.join(path, house_interior + '.tmx')
    add_scene(house_interior)
    # Write the XML to a file
    tree.write(fullpath, xml_declaration=True, encoding='UTF-8')

def add_scene(scene_name):
    file = open('locations.json', 'r', encoding='utf-8')
    locations = json.load(file)
    
    for obj in locations:
        locations[obj][scene_name] = []
        if obj == 'doors':
            locations[obj][scene_name].append([100, 500])
        if obj == 'chests':
            n_chests = random.randrange(0, 5)
            chest_coors = []
            
            for i in range(n_chests):
                coors = [
                    random.choice([200, 300, 400, 500]),
                    random.choice([100, 200, 300, 400, 500])
                    ]
                
                chest_coors.append(coors)
            if chest_coors:
                #print('chest_coors')
                #print(chest_coors)
                #chest_coors = list(set(chest_coors))
                for chest_coor in chest_coors:
                    locations[obj][scene_name].append(coors)
    file = open('locations.json', 'w', encoding='utf-8')
    json.dump(locations, file)

# if __name__ == '__main__':
#     create_house_interior()



