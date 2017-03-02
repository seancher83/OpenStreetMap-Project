# OpenStreetMap Udacity Project

## Map Area

Seattle, WA, United States

* https://mapzen.com/data/metro-extracts/metro/seattle_washington/


I was going to choose my how area, but it appears as though the file would be much too small to satisfy the requirements of this project. As a result, I chose Seattle, a city that I am comfortable with.  The selection from Mapzen appears to include the towns surrounding Seattle as well as Seattle. I am interested in seeing what queries can reveal.

## Problems with Data

After downloading the sample data I began to run the sample .osm file through my python code to begin to parse the tags appropriately.  Then I began to import those .csv files into SQL in order to analyze the data. Here are the problems that I noticed:

* Keyerror: ID - Python code gave error messages
* datatype mismatch -  SQL import gave error messages
 
### Keyerror: Id 
My code was giving me a keyerror: 'ID'.  I realized that this was because there were certain data points entered without proper id codes.  In order to remediate that problem, I chose to input the code of '9999999' rather than omit the code entirely.  I would rather omit this id code, than realize I omitted records in error. 

```Python
for item in node_attr_fields:
                try:
                    node_attribs[item] = element.attrib[item]
                except:
                    node_attribs[item] = '9999999'
```

After doing so, my sample osm file processed without error.

### Datatype mismatch
When I first tried to load my .csv file into the nodes table, I received an error: INSERT failed: datatype mismatch. Once I did some research I realized that this was because my .csv files had header rows.  In order to import this file, I first created a temporary table:
```SQL
 CREATE Table TEMP{
 "id" TEXT,
 "lat" TEXT,
 "lon" TEXT,
 "user" TEXT,
 "uid" TEXT,
 "version" TEXT,
 "timestamp" TEXT);
```
Then I inserted my node records into the temporary table:
```SQL
import nodes.csv TEMP
```
Then I deleted the first row which had string data from the header of the .csv file:
```SQL
DELETE FROM temp WHERE id = "id";
```
Then finally, I could insert the TEMP records into Nodes:
```SQL
INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) SELECT id, lat, lon, user, uid, version, changeset, timestamp FROM TEMP;
```
## Findings
### City Count
I wanted to confirm, that the map was including other towns outside of Seattle, as I suspected by looking at the shaded region.
In order to figure this out, I needed to look at both ways_tags and node_tags that had the value of "city":
```SQL
SELECT tags.value, count(*) as count
FROM (SELECT * from nodes_tags UNION ALL
		SELECT * from ways_tags) tags
WHERE tags.key = 'city'
GROUP BY tags.value
ORDER BY count DESC
;
```

