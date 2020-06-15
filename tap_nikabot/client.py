import requests


def make_session(access_token):
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {access_token}"})
    return session


def fetch_users(base_url, session, page_size, page):
    params = {"limit": page_size, "page": page}
    response = session.get(f"{base_url}/api/v1/users", params=params)
    response.raise_for_status()
    return response.json()


def fetch_swagger_definition(base_url):
    response = requests.get(f"{base_url}/v2/api-docs?group=public")
    response.raise_for_status()
    swagger = response.json()
    return swagger
