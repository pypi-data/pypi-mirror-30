import requests

BASE_API_URL = 'https://discordbots.fr/api/v1'

HTTP_401 = 'HTTP 401: You must provide a valid API key'
HTTP_404 = 'HTTP 404: The page could not be found'
HTTP_500 = 'HTTP 500: Internal server error'
HTTP_502 = 'HTTP 502: The server is not responding because of an error'

def update_counter(api_key, bot_id, servers_count, shards_count = None):
    request_body = {
        "count": servers_count,
        "shard": shards_count
    }

    headers = {
        "Authorization": api_key,
        "Content-Type": 'application/json'
    }

    response = requests.post(BASE_API_URL + '/bot/' + bot_id, json=request_body, headers=headers)

    # TODO: Handle more status codes if the API spits them

    if response.status_code == 401:
        raise RuntimeError(HTTP_401)
    elif response.status_code == 502:
        raise RuntimeError(HTTP_502)
    elif response.status_code == 500:
        raise RuntimeError(HTTP_500)
    elif response.status_code == 404:
        raise RuntimeError(HTTP_404)
    else:
        return response
