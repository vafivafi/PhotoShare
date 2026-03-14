import io
import pytest

class TestImageEndpoints:

    async def test_get_images_empty(self, client):
        response = await client.get("/images")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "images not found"

    async def test_register_and_create_image(self, client):
        reg_response = await client.post(
            "/users",
            json={
                "username": "imageuser",
                "password": "testpass123"
            }
        )
        token = reg_response.json()["token"]
        
        file_data = io.BytesIO(b"fake image data")
        files = {"file": ("test.png", file_data, "image/png")}
        data = {"name": "Test Image", "description": "Test description"}
        
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/images", files=files, data=data, headers=headers)
        assert response.status_code == 201
        result = response.json()
        assert result["message"] == "Image successfully added"
        assert result["image_name"] == "Test Image"

    async def test_get_images_after_upload(self, client):
        reg_response = await client.post(
            "/users",
            json={
                "username": "imageuser2",
                "password": "testpass123"
            }
        )
        token = reg_response.json()["token"]
        
        file_data = io.BytesIO(b"fake image data")
        files = {"file": ("test.png", file_data, "image/png")}
        data = {"name": "Test Image", "description": "Test description"}
        
        headers = {"Authorization": f"Bearer {token}"}
        await client.post("/images", files=files, data=data, headers=headers)
        
        response = await client.get("/images")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "images found"
        assert len(data["images"]) == 1

    async def test_update_image_name(self, client):
        reg_response = await client.post(
            "/users",
            json={
                "username": "imageuser3",
                "password": "testpass123"
            }
        )
        token = reg_response.json()["token"]
        
        file_data = io.BytesIO(b"fake image data")
        files = {"file": ("test.png", file_data, "image/png")}
        data = {"name": "Original Name", "description": "Test description"}
        
        headers = {"Authorization": f"Bearer {token}"}
        upload_response = await client.post("/images", files=files, data=data, headers=headers)
        image_id = upload_response.json()["image_id"]
        
        update_response = await client.put(
            f"/images/{image_id}/name",
            json={"new_name": "Updated Name"},
            headers=headers
        )
        assert update_response.status_code == 200
        result = update_response.json()
        assert result["message"] == "Name updated"
        assert result["image_name"] == "Updated Name"

    async def test_update_image_description(self, client):
        reg_response = await client.post(
            "/users",
            json={
                "username": "imageuser4",
                "password": "testpass123"
            }
        )
        token = reg_response.json()["token"]
        
        file_data = io.BytesIO(b"fake image data")
        files = {"file": ("test.png", file_data, "image/png")}
        data = {"name": "Test Image", "description": "Original description"}
        
        headers = {"Authorization": f"Bearer {token}"}
        upload_response = await client.post("/images", files=files, data=data, headers=headers)
        image_id = upload_response.json()["image_id"]
        
        update_response = await client.put(
            f"/images/{image_id}/description",
            json={"new_description": "Updated description"},
            headers=headers
        )
        assert update_response.status_code == 200
        result = update_response.json()
        assert result["message"] == "Description updated"
        assert result["image_description"] == "Updated description"

    async def test_create_image_unauthorized(self, client):
        file_data = io.BytesIO(b"fake image data")
        files = {"file": ("test.png", file_data, "image/png")}
        data = {"name": "Test Image", "description": "Test description"}
        
        response = await client.post("/images", files=files, data=data)
        assert response.status_code == 401

    async def test_update_image_unauthorized(self, client):
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.put(
            f"/images/{fake_id}/name",
            json={"new_name": "Updated Name"}
        )
        assert response.status_code == 401

    async def test_update_image_not_found(self, client):
        reg_response = await client.post(
            "/users",
            json={
                "username": "imageuser5",
                "password": "testpass123"
            }
        )
        token = reg_response.json()["token"]
        
        import uuid
        fake_id = str(uuid.uuid4())
        
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.put(
            f"/images/{fake_id}/name",
            json={"new_name": "Updated Name"},
            headers=headers
        )
        assert response.status_code == 404
