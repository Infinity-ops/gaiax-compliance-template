# Application Inventory

List what your application does, in business language. One row per
distinct capability — not per API route.

| Capability | Plain description | Internal module(s) it lives in |
|---|---|---|
| e.g. Image ingestion | Accepts drone imagery uploads from field operators | `api/routes.py::upload_*`, `services/storage.py` |
|  |  |  |
|  |  |  |

Notes:
- Group tightly-coupled internal steps under one capability row if a
  consumer would never interact with them separately.
- If you're not sure whether something belongs here or in the service
  inventory, put it here first — service_inventory.md is where you decide
  what gets *published*.
