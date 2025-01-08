"""
Utils for handling Open Graph protocol operations
"""

from urllib.error import HTTPError, URLError

import opengraph_py3

from flask import json, redirect, Response, url_for


def handle_og_data(cert_id: int, url: str) -> Response:
    """
    Uses the Open Graph protocol to attempt to 
    populate the resource data fields in the 
    ResourceForm

    Args:
        cert_id (int): Cert object ID
        url (str): URL to parse

    Returns:
        Response: Flask Response object
    """
    try:
        og_data = opengraph_py3.OpenGraph(url)
        # just return if OG search is empty
        og_list = list(og_data.items())
        base_og_data = "scrape" in og_list[0] and "_url" in og_list[1]
        if len(og_list) == 2 and base_og_data:
            return Response(status=204)
        # get OG data as dict to send back to template
        og_dict = {}
        for key, value in og_data.items():
            og_dict[key] = value
        return redirect(
            url_for(
                'data.cert_data',
                cert_id=cert_id,
                og_data=json.dumps([og_dict]),
                has_og_data=True),
            307
        )
    except HTTPError:
        return Response(status=204)
    except ValueError:
        return Response(status=204)
    except URLError:
        return Response(status=204)
