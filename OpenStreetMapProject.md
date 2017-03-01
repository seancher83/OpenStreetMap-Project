# OpenStreetMap Udacity Project

## Map Area

Seattle, WA, United States

* https://mapzen.com/data/metro-extracts/metro/seattle_washington/


I was going to choose my how area, but it appears as though the file would be much too small to satisfy the requirements of this project. As a result, I chose Seattle, a city that I am comfortable with.  I am interested in seeing what queries can reveal.

## Problems with Data

After downloading the sample data I began to run the sample .osm file through my python code to begin to parse the tags appropriately. Here are the problems that I noticed:

* Keyerror: ID 
 
## Keyerror: Id 
My code was giving me a keyerror: 'ID'.  I realized that this was because there were certain data points entered without proper id codes.  In order to remediate that problem, I chose to input the code of '9999999' rather than omit the code entirely.  I would rather omit this id code, than realize I omitted records in error. 

```Python
for item in node_attr_fields:
                try:
                    node_attribs[item] = element.attrib[item]
                except:
                    node_attribs[item] = '9999999'
```

After doing so, my sample osm file processed without error.
