# Sample task factory for Gather

This is a simple task generator. It pulls from Overpass and stores in S3. 

## Use it

* Make sure your AWS credentials `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set.
* Edit the variables in the configuration section of the script
* Install python modules `shapely` and `boto`.
* And then:

```
$ python overpass-factory.py
Connecting to your S3 bucket gather-files
retrieving data from Overpass...
252 results retrieved from Overpass. Generating output.
Writing to your S3 bucket...
The data is now available at https://gather-files.s3.amazonaws.com/restaurants-no-cuisine
```