from fastapi import FastAPI

app = FastAPI()

country_dict = {
    'Russia': ['Moscow', 'St. Petersburg', 'Novosibirsk', 'Ekaterinburg', 'Kazan'],
    'USA': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Philadelphia'],
}

@app.get('/')
def welcome() -> dict:
    return {"message": 'My first project in FastAPI'}

@app.get('/users/admin')
async def admin() -> dict:
    return {'message': f'Hello admin'}

@app.get('/users')
async def users(name: str = 'Undefined', age: int = 18) -> dict:
    return {'user_name': name, 'user_age': age}

@app.get('/product')
async def detail_view(item_id: int) -> dict:
    return {'product_id': f'Stock number {item_id}'}


@app.get('/country/{country}')
async def list_cities(country: str, limit: int) ->dict:
    return {'country': country, 'cities': country_dict[country][:limit]}









