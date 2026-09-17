"""SAM 3 proxy for CVAT Nuclio.

This is a scaffold, not a finished CVAT Community SAM 3 UI integration.
It forwards the image and visual prompts received by CVAT to a private SAM 3
service running on a DGX Spark. Adapt `parse_cvat_request` and
`to_cvat_response` to the exact interaction protocol of the CVAT release used
on the server before deployment.
"""

import base64
import json
import os

import requests


SAM3_URL = os.environ["SAM3_URL"]


def parse_cvat_request(body: dict) -> dict:
    """Map the CVAT interactor request to the Spark API request.

    Different CVAT releases use different payload shapes for legacy Nuclio
    interactors. Inspect the received body in the Nuclio logs and update this
    mapping; do not assume these placeholder field names are final.
    """
    return {
        "image": body["image"],
        "positive_points": body.get("positive_points", []),
        "negative_points": body.get("negative_points", []),
        "bounding_box": body.get("bounding_box"),
        "prompt": body.get("prompt"),
    }


def to_cvat_response(sam3_result: dict) -> dict:
    """Convert Spark output to the response expected by the CVAT UI.

    The Spark service should return a selected mask in CVAT's internal mask
    representation, not ordinary COCO RLE. Use cvat_sdk.masks.encode_mask in a
    native-function implementation, or adapt this function to the legacy
    Nuclio/UI protocol used by the installed CVAT version.
    """
    return sam3_result


def handler(context, event):
    body = event.body
    context.logger.info("Received SAM 3 interaction request")

    payload = parse_cvat_request(body)
    image_bytes = base64.b64decode(payload.pop("image"))

    try:
        response = requests.post(
            SAM3_URL,
            files={"image": ("frame.jpg", image_bytes, "image/jpeg")},
            data={key: json.dumps(value) for key, value in payload.items() if value is not None},
            timeout=110,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        context.logger.error(f"SAM 3 Spark request failed: {error}")
        return context.Response(
            body=json.dumps({"error": "SAM 3 service unavailable"}),
            content_type="application/json",
            status_code=502,
        )

    return context.Response(
        body=json.dumps(to_cvat_response(response.json())),
        content_type="application/json",
        status_code=200,
    )
