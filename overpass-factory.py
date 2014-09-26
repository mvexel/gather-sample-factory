from overpass import Overpass
import boto
import uuid
from shapely.geometry import Point
import re
import sys

# ----------------------------
# Configuration section
# ----------------------------

# S3 Configuration
#
# Make sure your AWS keys are available as environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
# See http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html for help
# Then, create your bucket using the command line tools or the manager interface.
# Configure the name of your bucket here:
s3_bucket_name = 'gather-files'
s3_file_key = 'restaurants-no-cuisine'

# Query Configuration
#
# Set the Overpass QL query to retrieve the nodes you want to include.
# See http://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL for the Overpass QL reference.
overpass_query = 'node["amenity"="restaurant"]["cuisine"!~"."](area:3600161993);'  # restaurants with no cuisine in Utah

# Task Text Configuration
#
# Set the text associated with each task here. You can use standard Python string formatting placeholders.
# Each placeholder will be substituted with the value of the tag with that key. So for example, if you
# have a placeholder {name}, it will be substituted with the name=* value for that OSM element.
task_text = 'You are very close to a restaurant called "{name}". Wht kind of restaurant is it?'

# ----------------------------
# End of Configuration section
# ----------------------------

# connect to s3
s3_bucket = None
s3_key = None

print "Connecting to your S3 bucket {name}".format(name=s3_bucket_name)
try:
    s3 = boto.connect_s3()
    s3_bucket = s3.get_bucket(s3_bucket_name)
    s3_key = boto.s3.key.Key(s3_bucket)
    s3_key.key = s3_file_key
except Exception as e:
    print "Something went wrong connecting to your S3 bucket. Please check your parameters. Below is the full error message."
    print e.message
    sys.exit(1)

# get the string format keys
string_replacement_keys = re.findall('\{([^\}]+)\}', task_text)

# retrieve the nodes
api = Overpass.API()
print 'retrieving data from Overpass...'
result = api.Get(overpass_query)
print '{l} results retrieved from Overpass. Generating output.'.format(l=len(result['elements']))

records = []

for elem in result['elements']:
    record = []
    substitutions = dict(zip(string_replacement_keys, [elem['tags'].get(k, "").encode('utf-8') for k in string_replacement_keys]))
    record.append(str(uuid.uuid4()))  # UUID as unique identifier
    record.append(Point(elem['lon'], elem['lat']).wkb.encode('hex'))  # OSM point geometry as WKB
    record.append(str(elem.get('id', 0)))  # OSM ID
    record.append(task_text.format(**substitutions))
    records.append('^'.join(record))

# write to bucket and set the file to public-readable
print "Writing to your S3 bucket..."
s3_key.set_contents_from_string('\n'.join(records))
s3_key.set_acl('public-read')

print "The data is now publicly available at {url}".format(url=s3_key.generate_url(expires_in=0, query_auth=False))
print "Done."
