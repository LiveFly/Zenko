Out-of-Band Updates
===================

|product| depends on object storage metadata for its operation. When a new |product|
location is configured, |product| encounters a new object storage system. If |product|
does not understand the location's namespace, |product| creates a new |product|
namespace and uses it to perform all of its data management tasks (metadata
search, replication, lifecycle transition and expiration). If |product| recognizes
the existing namespace, it can ingest the existing namespace metadata, in a
process called an out-of-band update.

Out-of-band updates are available for Scality's RING object storage
system via S3 Connector. |product| communicates directly with the S3 Connector
namespace and replicates it natively. |product| can also interoperate with RINGs
using the Scale-Out File System (SOFS) via the NFS protocol and with buckets
hosted by Amazon Web Services. For NFS and AWS data stores, |product| downloads and
extrapolates metadata from the stores to create its own namespace, updates the
namespace in scheduled cron jobs, then acts on changes registered in this
virtual namespace.

When establishing a |product| location for out-of-band updates, versioning must be
enabled. Out-of-band updates for S3C provide metrics; for NFS and AWS services,
metrics remain under development. This feature is not yet implemented for Azure
Blob frontends.

.. note::

   This feature is not yet implemented for Azure Blob frontends. 

