import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import schema

import cerberus

OSM_PATH = "/Users/Sean/Desktop/OpenStreetMaps/seattle_washington.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
ZIP_CODE_START = re.compile('[0-9]{5}')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular', lower_colon = LOWER_COLON):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    #first task is to check of tag is 'node'
    if element.tag == 'node':
        for item in element:
            element_dict = {}
            #Amended following code in order to deal with instances of blank required fields that was causing errors
            for item in node_attr_fields:
                try:
                    node_attribs[item] = element.attrib[item]
                except:
                    node_attribs[item] = '9999999'
            #Now cycle thorugh each child of the element
            for child in element:
                child_dict = {}
                #Check to make sure element attribute does not have problematic characters
                if not problem_chars.search(child.attrib['k']):
                    key_attrib = child.attrib['k']
                    child_dict['id'] = element.attrib['id']
                    #process_zip processes postalcode keys in order to fix problematic zip codes
                    child_dict['value'] = process_zip(key_attrib, child.attrib['v'])
                    #Splits the attribute if a colon is found
                    if lower_colon.search(child.attrib['k']):
                        split_array = child.attrib['k'].split(':', 1)
                        child_dict['type'] = split_array[0]
                        child_dict['key'] = split_array[1]
                    else:
                        child_dict['type'] = 'regular'
                        child_dict['key'] = child.attrib['k']
                    tags.append(child_dict)
            return {'node': node_attribs, 'node_tags': tags}
    # next check if the tag is a 'way'
    elif element.tag == 'way':
        tag_counter = 0
        for item in element.attrib:
            if item in way_attr_fields:
                way_attribs[item] = element.attrib[item]
        for child in element:
            child_dict = {}
            if child.tag == 'tag':
                if not problem_chars.search(child.attrib['k']):
                    key_attrib = child.attrib['k']
                    child_dict['id'] = element.attrib['id']
                    child_dict['value'] = process_zip(key_attrib, child.attrib['v'])
                    if lower_colon.search(child.attrib['k']):
                        split_array = child.attrib['k'].split(':', 1)
                        child_dict['type'] = split_array[0]
                        child_dict['key'] = split_array[1]
                    else:
                        child_dict['type'] = 'regular'
                        child_dict['key'] = child.attrib['k']
                    tags.append(child_dict)
            elif child.tag =='nd':
                child_dict['id'] = element.attrib['id']
                child_dict['node_id'] = child.attrib['ref']
                child_dict['position'] = tag_counter
                tag_counter +=1
                way_nodes.append(child_dict)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #

# Function grabs 5 digit zip codes starting with two digits if the key is 'postcode'
def process_zip(key, key_value, zip_re = ZIP_CODE_START):
    if 'postcode' in key:
        if re.search(zip_re, key_value):
            return str(re.findall(zip_re, key_value)[0])
    return key_value


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
