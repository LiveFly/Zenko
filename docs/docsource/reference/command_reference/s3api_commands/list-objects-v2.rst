.. _list-objects-v2:

list-objects-v2
===============

Returns some or all (up to 1,000) of the objects in a bucket. You can use the
request parameters as selection criteria to return a subset of the objects in a
bucket.

.. Note::

   ListObjectsV2 is the revised List Objects API and we recommend you use this
   revised API for new application development.

See also: `AWS API Documentation
<https://docs.aws.amazon.com/goto/WebAPI/s3-2006-03-01/ListObjectsV2>`_.

``list-objects-v2`` is a paginated operation. Multiple API calls may be issued
in order to retrieve the entire data set of results. You can disable pagination
by providing the ``--no-paginate`` argument.  When using ``--output text`` and
the ``--query`` argument on a paginated response, the ``--query`` argument must
extract data from the results of the following query expressions: ``Contents``,
``CommonPrefixes``.

Synopsis
--------

::

  list-objects-v2
    --bucket <value>
    [--delimiter <value>]
    [--encoding-type <value>]
    [--prefix <value>]
    [--fetch-owner | --no-fetch-owner]
    [--start-after <value>]
    [--cli-input-json <value>]
    [--starting-token <value>]
    [--page-size <value>]
    [--max-items <value>]

Options
-------

``--bucket`` (string)

  Name of the bucket to list.

``--delimiter`` (string)

  A delimiter is a character you use to group keys.

``--encoding-type`` (string)

  Encoding type used by |product| to encode object keys in the response.

  Possible values:
  
  *   ``url``

``--prefix`` (string)

  Limits the response to keys that begin with the specified prefix.

``--fetch-owner`` | ``--no-fetch-owner`` (boolean)

  The owner field is not present in listV2 by default, if you want to return
  owner field with each key in the result then set the fetch owner field to true

``--start-after`` (string)

  StartAfter is where you want |product| to start listing from. |product|  starts
  listing after this specified key. StartAfter can be any key in the bucket

  Possible values:
  
  *   ``requester``

``--cli-input-json`` (string)

  .. include:: ../../../include/cli-input-json.txt

``--starting-token`` (string)

  A token to specify where to start paginating. This is the ``NextToken`` from a
  previously truncated response.

  |aws_cli_guide|

``--page-size`` (integer)

  The size of each page to get in the AWS service call. This does not affect the
  number of items returned in the command's output. Setting a smaller page size
  results in more calls to the AWS service, retrieving fewer items in each
  call. This can help prevent the AWS service calls from timing out.

  |aws_cli_guide|

``--max-items`` (integer)

  The total number of items to return in the command's output. If the total
  number of items available is more than the value specified, a ``NextToken`` is
  provided in the command's output. To resume pagination, provide the
  ``NextToken`` value in the ``starting-token`` argument of a subsequent
  command. **Do not** use the ``NextToken`` response element directly outside of
  the AWS CLI.

  |aws_cli_guide|

Output
------

IsTruncated -> (Boolean)

  A flag that indicates whether |product| returned all of the results
  that satisfied the search criteria.

Contents -> (list)

  Metadata about each object returned.

  (structure)

    Key -> (string)

    LastModified -> (timestamp)

    ETag -> (string)

    Size -> (integer)

    StorageClass -> (string)

      The class of storage used to store the object.
      
    Owner -> (structure)

      DisplayName -> (string)

      ID -> (string)

Name -> (string)

  Name of the bucket to list.

Prefix -> (string)

  Limits the response to keys that begin with the specified prefix.

Delimiter -> (string)

  A delimiter is a character you use to group keys.

MaxKeys -> (integer)

  Sets the maximum number of keys returned in the response. The response might
  contain fewer keys but will never contain more.

CommonPrefixes -> (list)

  CommonPrefixes contains all (if there are any) keys between Prefix and the
  next occurrence of the string specified by delimiter.

  (structure)

    Prefix -> (string)
    
EncodingType -> (string)

  Encoding type used by |product| to encode object keys in the response.

KeyCount -> (integer)

  KeyCount is the number of keys returned with this request. KeyCount is
  always less than or equal to the MaxKeys field. If you request 50 keys, your
  result will include 50 or fewer keys.

ContinuationToken -> (string)

  ContinuationToken indicates to |product| that the list is being continued
  on this bucket with a token. ContinuationToken is obfuscated and is not a real
  key.

NextContinuationToken -> (string)

  NextContinuationToken is sent when isTruncated is true which means there are
  more keys in the bucket that can be listed. The next list requests to S3
  Connector can be continued with this
  NextContinuationToken. NextContinuationToken is obfuscated and is not a real
  key.

StartAfter -> (string)

  StartAfter is where you want |product| to start listing from. |product| 
  starts listing after this specified key. StartAfter can be any key in the
  bucket.
