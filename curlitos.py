import argparse
import ConfigParser
import cStringIO
import gzip
import logging
import json
import os
import sys
import traceback
import urllib

from boto.s3.connection import S3Connection
from boto.s3.key import Key

def _init_config():
  conf_parser = argparse.ArgumentParser(
    description="Downloads a file from a URL and uploads it to Amazon S3",
    # Turn off help, so we print all options in response to -h
    add_help=False
  )
  conf_parser.add_argument("-c", "--conf_file", help="Specify a config file", action="store", 
    metavar="FILE")
  args, remaining_argv = conf_parser.parse_known_args()

  defaults = {}
  
  if args.conf_file:
    config = ConfigParser.SafeConfigParser()
    config.read([os.path.dirname(sys.argv[0]) + "/" + args.conf_file])
    defaults = dict(config.items("Defaults"))

  # Don't surpress add_help here so it will handle -h
  parser = argparse.ArgumentParser(
    # Inherit options from config_parser
    parents=[conf_parser],
    # print script description with -h/--help
    description=__doc__,
    # Don't mess with format of description
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )
  parser.set_defaults(**defaults)
  parser.add_argument("-i", "--input_file", help="The URL to be downloaded.", required=True)
  parser.add_argument("-o", "--output_key", help="The S3 key where the data will be stored.",
    required=True)
  parser.add_argument("-b", "--bucket", help="The S3 bucket where files will be stored.",
    required=True)
  parser.add_argument("-k", "--key", help="The key for accessing S3.", required=True)
  parser.add_argument("-s", "--secret", help="The secret for accessing S3.", required=True)
  parser.add_argument("-m", "--mime_type", help="The mimetype of the file stored on S3.",
    required=True)
  parser.add_argument("-a", "--acl",
    help="The access control permissions for the file stored on S3.", required=True)
  parser.add_argument("-f", "--force", help="Overwrite an existing key.", action="store_true")
  parser.add_argument("-z", "--compress", help="Compress the output before placing it on S3.",
    action='store_true')
  parser.add_argument("--jsonp_callback_function", 
    help="If set, the contents of the downloaded file be passed to the named function via jsonp.")

  return parser.parse_args(remaining_argv)

def _init_logging(log_level="INFO"):
  """Initialize logging so that it is pretty and compact."""
  DATE_FMT = "%Y%m%d %H:%M:%S"
  FORMAT = "%(levelname).1s%(asctime)s %(threadName)s %(filename)s:%(lineno)d %(message)s"
  old_logging_handlers = logging.root.handlers
  # Drop all and any logging handlers, otherwise basicConfig will do nothing.
  logging.root.handlers = []
  logging.basicConfig(
    format=FORMAT,
    datefmt=DATE_FMT,
    level=log_level,
  )
  if old_logging_handlers:
    logging.error("Logging handlers initialized prior to _init_logging were dropped.")

def s3_progress(complete, total):
  if (complete > 0 and total > 0):
    percentComplete = float(complete)/float(total)
    logging.info("Upload %d%% complete" % (round((percentComplete*1000), 0) / 10))

def compress_string(s):
  """Gzip a given string."""
  zbuf = cStringIO.StringIO()
  zfile = gzip.GzipFile(mode="wb", compresslevel=6, fileobj=zbuf)
  zfile.write(s)
  zfile.close()
  return zbuf.getvalue()

def put(source_url, bucket, dest_key, mime_type, acl, compress, jsonp, overwrite=False):
  k = Key(bucket)
  k.key = dest_key
  headers = {
    "Content-Type": mime_type
  }
  if k.exists() and not overwrite:
    logging.info("Skipping %s - already exists")
    return False
  try:
    logging.info("Downloading from %s" % source_url)
    stream = urllib.urlopen(source_url)
    contents = stream.read()
    logging.info("Uploading to %s" % dest_key)
    string_to_store = "%s(%s);" % (prefix, contents) if jsonp else contents
    if compress:
      headers["Content-Encoding"] = "gzip"
      string_to_store = compress_string(string_to_store)
    k.set_contents_from_string(string_to_store, headers=headers, cb=s3_progress, num_cb=1000)
    k.set_acl(acl)
  except:
    logging.info("There was an error uploading to %s" % dest_key)
  logging.info("Finished uploading to %s" % dest_key)

if __name__ == "__main__":
  _init_logging()
  args = _init_config()
  conn = S3Connection(args.key, args.secret)
  bucket = conn.get_bucket(args.bucket)
  put(args.input_file, bucket, args.output_key, args.mime_type, args.acl, args.compress, 
    args.jsonp_callback_function, args.force)