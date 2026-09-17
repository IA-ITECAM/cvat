# SAM 3 proxy for CVAT

This folder is a starting scaffold for a CVAT serverless interactor that sends
inference requests to a private SAM 3 service running on a DGX Spark.

## Copy destination

Copy the `sam3` folder to the CVAT server at:

```text
<CVAT_REPOSITORY>/serverless/pytorch/facebookresearch/sam3
```

The resulting location must be:

```text
<CVAT_REPOSITORY>/serverless/pytorch/facebookresearch/sam3/nuclio/function.yaml
```

## Before deployment

1. Replace `REPLACE_WITH_SPARK_PRIVATE_IP` in `nuclio/function.yaml` with the
   private DNS name or IP address of the Spark service.
2. Keep the Spark service private: only the CVAT server should be able to call
   it.
3. Validate the request/response mapping in `main.py` against the exact CVAT
   release. Legacy Nuclio SAM interactors use a browser plugin and do not share
   the same response format as native interaction functions.

## Deployment

This proxy does not run inference locally, so deploy it from the CVAT repository
root with:

```bash
./serverless/deploy_cpu.sh serverless/pytorch/facebookresearch/sam3/nuclio
```

Then check:

```bash
nuctl get functions --platform local
```

## Important limitation

Registering the function as `type: interactor` is necessary for model discovery
in the magic-wand UI, but it is not sufficient to reproduce CVAT Online's SAM 3
experience in CVAT Community. A compatible response adapter and potentially a
custom CVAT UI plugin are required.
