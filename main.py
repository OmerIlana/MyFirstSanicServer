from sanic import Sanic
from sanic import response
from aiocache import cached
from aiohttp import ClientSession, ClientConnectorError
from sanic_limiter import Limiter, get_remote_address

app = Sanic('cyesec')
limiter = Limiter(app)

async def fetch_data_from_remote_server(session, url):
    try:
        async with session.get(url) as result:
            return await result.json()
    except ClientConnectorError as e:
        return ('Connection Error', str(e))

@cached(ttl=3600)
async def expensive_request_should_use_cache(get_remote_address):
    url = "https://reqres.in/api/users"
    async with ClientSession() as session:
        result = await fetch_data_from_remote_server(session, url)
        return response.json(result)

@app.route("/")
@limiter.limit("1000 per day;10/minute", key_func=get_remote_address)
async def handle_request(request):
    return await expensive_request_should_use_cache(get_remote_address)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
