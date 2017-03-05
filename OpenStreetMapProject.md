# OpenStreetMap Udacity Project
## Purpose
The purpose of this project is to write a Python code in order to process xml data of an OpenStreetMap area of our choice in order to find errors in the data and to use SQL in order to find information regarding the processed data.


## Map Area

Seattle, WA, United States

* https://mapzen.com/data/metro-extracts/metro/seattle_washington/


I was going to choose my how area, but it appears as though the file would be much too small to satisfy the requirements of this project. As a result, I chose Seattle, a city that I am comfortable with.  The selection from Mapzen appears to include the towns surrounding Seattle as well as Seattle. I am interested in seeing what queries can reveal.

## Problems with Data

After downloading the sample data I began to run the sample .osm file through my python code to begin to parse the tags appropriately.  Then I began to import those .csv files into SQL in order to analyze the data. Here are the problems that I noticed:

* Keyerror: ID - Python code gave error messages
* datatype mismatch -  SQL import gave error messages
* postcode standardization - SQL search shows errors in input
 
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

for nodes:
```SQL
 CREATE Table TEMP(
 "id" TEXT,
 "lat" TEXT,
 "lon" TEXT,
 "user" TEXT,
 "uid" TEXT,
 "version" TEXT,
 "changeset" TEXT,
 "timestamp" TEXT);
```

Then I inserted my node records into the temporary table:
```SQL
.import nodes.csv TEMP
```
Then I deleted the first row which had string data from the header of the .csv file:
```SQL
DELETE FROM TEMP Where ROWID = 1;
```
Then finally, I could insert the TEMP records into Nodes:
```SQL
INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) SELECT id, lat, lon, user, uid, version, changeset, timestamp FROM TEMP;
```


The same occurred for ways:
```SQL
 CREATE Table TEMP(
 "id" TEXT,
 "user" TEXT,
 "uid" TEXT,
 "version" TEXT,
 "changeset" TEXT,
 "timestamp" TEXT);
 
 .import ways.csv TEMP
 
 DELETE FROM TEMP Where ROWID = 1;
```
```SQL
INSERT INTO ways(id, user, uid, version, changeset, timestamp) SELECT id, user, uid, version, changeset, timestamp FROM TEMP;
```
### Postcode Errors
I wanted to find out if the postalcode field was standardized so I performed a query to pull all postal codes from node_tags and way_tags: 
```sql
SELECT tags.value, count(*) as count
FROM (SELECT * from nodes_tags UNION ALL
		SELECT * from ways_tags) tags
WHERE tags.key = 'postcode'
GROUP BY tags.value
ORDER BY count DESC
;
```
This produced a list of postal codes that are pretty clean, but not perfect.  I noticed a few instances like the following:
```
"Lacey, WA 98503"
```
I also see some instances of the postal code including the +4 like:
```
"98444-1858
```
I will fix this in my python code with the following function:
```SQL
# Regular expression to find zip code like numbers
ZIP_CODE_START = re.compile('[0-9]{5}')

# Function grabs 5 digit zip codes starting with two digits.
def process_zip(key, key_value, zip_re = ZIP_CODE_START):
    if 'postcode' in key:
        if re.search(zip_re, key_value):
            return str(re.findall(zip_re, key_value)[0])
    return key_value
```

This appeared to resolve the issue for most all cases that can be easily deciphered.  

## Findings
### Overview Statistics
* Size of the file: 1.68GB
* Number of unique users

* number of nodes and ways
To find nodes:
```SQL
SELECT count(*) 
FROM nodes;
```
397821 Nodes

To find ways:
To find nodes:
```SQL
SELECT count(*) 
FROM ways;
```
744335 ways

* Number of type of nodes
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
Here are the resulting nodes_tags and ways_tags combined:
```
Seattle,203377
Kirkland,42285
Mount Vernon,11729
Saanich,11547
Langford,2806
Oak Bay,2298
Colwood,1985
Sooke,1600
Esquimalt,1495
View Royal,998
```
This data, although listed as "Seattle" does indeed actually include the greater metropolitan area.

## Zip Codes
I also want to check and see what the most commonly entered zip code is:
```SQL
SELECT tags.value, count(*) as count
FROM (SELECT * from nodes_tags UNION ALL
		SELECT * from ways_tags) tags
WHERE tags.key = 'postcode'
GROUP BY tags.value
ORDER BY count DESC
;
```
Here are the resulting zip codes, along with the count of entries of each zip code:
```
98034,22954
98033,19369
98115,18127
98103,16844
98118,14384
98117,13559
98125,12133
98105,9928
98144,9289
98108,9255
```
