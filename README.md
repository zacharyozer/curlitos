curlitos
========

A small utility that downloads a file and then uploads it to S3.

The original intent was to save a publicly accessible file periodically via a cron without having 
to worry about storage space on the drive. 

## Configuration Options

curlitos can be configured via command line or configuration file, and accepts the following 
options:

 * -i, --input_file - The URL to be downloaded. (required)
 * -o, --output_key - The S3 key where the data will be stored. (required)
 * -b, --bucket - The S3 bucket where files will be stored. (required)
 * -k, --key - The key for accessing S3. (required)
 * -s, --secret - The secret for accessing S3. (required)
 * -a, --acl - The access control permissions for the file stored on S3. (required)
 * -m, --mime_type - The mimetype of the file stored on S3. (required)
 * -f, --force - Overwrite an existing key.
 * -z, --compress - gzip output before placing it on S3.
 * --jsonp_callback_function - If set, the contents of the downloaded file be passed to the named
     function via jsonp.
 * -c, --conf_file - The configuration file, which can specify any of the aforementioned options

## Requirements
 * Python 2.7+
 * boto
