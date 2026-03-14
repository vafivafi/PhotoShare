import pytest

class TestUserEndpoints:

    async def test_register_user(self, client):
        response = await client.post(
            "/users",
            json={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["username"] == "testuser"
        assert "user_id" in data
        assert "token" in data

    async def test_register_user_already_exists(self, client):
        await client.post(
            "/users",
            json={
                "username": "existinguser",
                "password": "testpass123"
            }
        )
        
        response = await client.post(
            "/users",
            json={
                "username": "existinguser",
                "password": "testpass123"
            }
        )
        assert response.status_code == 409
        assert response.json()["detail"] == "User already exists"

    async def test_login(self, client):
        await client.post(
            "/users",
            json={
                "username": "loginuser",
                "password": "testpass123"
            }
        )
        
        response = await client.post(
            "/users/login",
            json={
                "username": "loginuser",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert data["username"] == "loginuser"
        assert "token" in data

    async def test_login_wrong_password(self, client):
        await client.post(
            "/users",
            json={
                "username": "user123",
                "password": "testpass123"
            }
        )
        
        response = await client.post(
            "/users/login",
            json={
                "username": "user123",
                "password": "wrongpass"
            }
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

    async def test_login_user_not_found(self, client):
        response = await client.post(
            "/users/login",
            json={
                "username": "nonexistent",
                "password": "testpass123"
            }
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

    async def test_get_user(self, client):
        await client.post(
            "/users",
            json={
                "username": "findme",
                "password": "testpass123"
            }
        )
        
        response = await client.get("/users/findme")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User found"
        assert data["username"] == "findme"
        assert "user_id" in data
    
    async def test_get_user_not_found(self, client):
        response = await client.get("/users/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "User does not exist"
    
    async def test_get_user_with_images(self, client):
        await client.post(
            "/users",
            json={
                "username": "withimages",
                "password": "testpass123"
            }
        )
        
        response = await client.get("/users/withimages/images")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User found"
        assert data["username"] == "withimages"
        assert "images" in data
        assert isinstance(data["images"], list)
    
    async def test_get_user_with_images_not_found(self, client):
        response = await client.get("/users/nonexistent/images")
        assert response.status_code == 404
        assert response.json()["detail"] == "User does not exist"
