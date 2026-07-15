# Resource (Data Resource) Inventory

Gaia-X separates the *service that processes data* (`gx:ServiceOffering`)
from *data assets the service produces or holds* (`gx:DataResource`). Most
templates skip this — don't. If your service hands a customer a dataset,
report, or generated artifact that has its own lifecycle (its own
retention, its own access rules, its own format), it deserves its own
Data Resource credential, linked from the Service Offering rather than
buried inside it.

| Resource | Produced by which Service Offering | Format | Who owns it | Retention / deletion rule | Exported how |
|---|---|---|---|---|---|
| e.g. Orthophoto | Drone image processing | GeoTIFF | Customer | 30 days, then deleted by cleanup job | Download link, WebDAV |
|  |  |  |  |  |  |

If your service doesn't produce any standalone data asset a customer would
reference independently (e.g. a pure compute/API service with no lasting
output), leave this empty — `gaiax.config.yaml`'s `data_resources:` list can
stay empty and no Data Resource credential will be generated.
