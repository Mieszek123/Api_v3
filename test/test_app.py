import pytest

EMAIL = "mieszko@gmail.com"
PASSWORD = "password"

#helper functions
async def register(client, email, password):
    return await client.post("/auth/register", json={"email": email, "password": password})

async def login(client, email, password):      #data not json 
    return await client.post("/auth/jwt/login", data={"username": email, "password": password})


#################
# /auth/register
#################

#register test
@pytest.mark.asyncio
async def test_register_user(client):
    response = await register(client, EMAIL, PASSWORD)
    assert response.status_code == 201

#duplicate register test
@pytest.mark.asyncio
async def test_duplicate_register_user(client):
    await register(client, EMAIL, PASSWORD)
    response = await register(client, EMAIL, PASSWORD)
    assert response.status_code == 400


#################
# /auth/jwt/login
#################

#login test
@pytest.mark.asyncio
async def test_login_user(client):
    await register(client, EMAIL, PASSWORD)
    response = await login(client, EMAIL, PASSWORD)
    assert response.status_code == 200

#token test
@pytest.mark.asyncio
async def test_login_token_user(client):
    await register(client, EMAIL, PASSWORD)
    response = await login(client, EMAIL, PASSWORD)
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

#fake password login
@pytest.mark.asyncio
async def test_fake_password_login_user(client):
    await register(client, EMAIL, PASSWORD)
    response = await login(client, EMAIL, "fakepassword")
    assert response.status_code == 400

#fake email login
@pytest.mark.asyncio
async def test_fake_email_login_user(client):
    await register(client, EMAIL, PASSWORD)
    response = await login(client, "mieszekkkk@gmail.com", PASSWORD)
    assert response.status_code == 400

