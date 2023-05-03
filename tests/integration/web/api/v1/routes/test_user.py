from uuid import UUID, uuid4

import pytest
from fastapi import status
from httpx import AsyncClient, Response

from src.core.models.user import User


@pytest.mark.asyncio
async def test_create_user(
    client: AsyncClient,
    create_user_data: dict[str, str],
):
    response: Response = await client.post("/users/", json=create_user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"id": str(UUID(response.json()["id"]))}


@pytest.mark.asyncio
async def test_create_user_already_exists(
    client: AsyncClient,
    create_user_data: dict[str, str],
    user: User,
):
    response: Response = await client.post("/users/", json=create_user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "User with given email already exists"}


@pytest.mark.asyncio
async def test_get_users(
    client: AsyncClient,
    user: User,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get("/users/", headers=user_bearer_token_header)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body) == 1

    assert body[0]["id"] == str(user.id)
    assert body[0]["email"] == user.email
    assert body[0]["is_active"] == user.is_active


@pytest.mark.asyncio
async def test_get_user_by_id(
    client: AsyncClient,
    user: User,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get(
        f"/users/{user.id}/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["id"] == str(user.id)
    assert body["email"] == user.email
    assert body["is_active"] == user.is_active


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
    client: AsyncClient,
    user: User,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get(
        f"/users/{uuid4()}/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not found"}


@pytest.mark.asyncio
async def test_delete_user(
    client: AsyncClient,
    user: User,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.delete(
        f"/users/{user.id}/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_user_not_found(
    client: AsyncClient,
    user: User,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.delete(
        f"/users/{uuid4()}/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Permission denied"}


@pytest.mark.asyncio
async def test_delete_user_unauthorized(
    client: AsyncClient,
    user: User,
):
    response: Response = await client.delete(f"/users/{user.id}/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_delete_user_other_user(
    client: AsyncClient,
    user: User,
    other_user: User,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.delete(
        f"/users/{other_user.id}/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Permission denied"}


@pytest.mark.asyncio
async def test_update_user(
    client: AsyncClient,
    user: User,
    user_bearer_token_header: dict[str, str],
):
    update_user_data = {"first_name": "New Name", "last_name": "New Last Name"}
    response: Response = await client.patch(
        f"/users/{user.id}/",
        json=update_user_data,
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["id"] == str(user.id)


@pytest.mark.asyncio
async def test_update_user_other_user(
    client: AsyncClient,
    user: User,
    other_user: User,
    user_bearer_token_header: dict[str, str],
):
    update_user_data = {"first_name": "New Name", "last_name": "New Last Name"}
    response: Response = await client.patch(
        f"/users/{other_user.id}/",
        json=update_user_data,
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Permission denied"}


@pytest.mark.asyncio
async def test_get_user_profile(
    client: AsyncClient,
    user: User,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.get(
        "/users/profile/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["id"] == str(user.id)
    assert body["email"] == user.email
    assert body["is_active"] == user.is_active


@pytest.mark.asyncio
async def test_get_user_profile_unauthorized(
    client: AsyncClient,
):
    response: Response = await client.get("/users/profile/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_user_profile_invalid_token(
    client: AsyncClient,
    invalid_bearer_token_header: dict[str, str],
):
    response: Response = await client.get(
        "/users/profile/",
        headers=invalid_bearer_token_header,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials"}


@pytest.mark.asyncio
async def test_password_reset_unauthorized(
    user: User,
    client: AsyncClient,
):
    post_data = {"email": user.email}
    response: Response = await client.post(
        "/users/password-reset/send-email/",
        json=post_data,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_password_reset_unauthorized_invalid_email(
    user: User,
    client: AsyncClient,
):
    post_data = {"email": "invalid@example.com"}
    response: Response = await client.post(
        "/users/password-reset/send-email/",
        json=post_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not found"}


@pytest.mark.asyncio
async def test_send_password_reset_email(
    user: User,
    client: AsyncClient,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.post(
        f"/users/{user.id}/password-reset/send-email/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_send_password_reset_email_other_user(
    user: User,
    other_user: User,
    client: AsyncClient,
    user_bearer_token_header: dict[str, str],
):
    response: Response = await client.post(
        f"/users/{other_user.id}/password-reset/send-email/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Permission denied"}


@pytest.mark.asyncio
async def test_reset_password(
    user: User,
    client: AsyncClient,
):
    user.generate_password_reset_token()
    post_data = {"password": "new_password"}
    response: Response = await client.post(
        f"/users/{user.id}/password-reset/{user.password_reset_token}/",
        json=post_data,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_reset_password_invalid_token(
    user: User,
    client: AsyncClient,
):
    user.generate_password_reset_token()
    post_data = {"password": "new_password"}
    response: Response = await client.post(
        f"/users/{user.id}/password-reset/invalid-token/",
        json=post_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Bad request"}


@pytest.mark.asyncio
async def test_resend_activation_email(
    user: User,
    client: AsyncClient,
):
    user.deactivate()

    response: Response = await client.post(f"/users/{user.id}/activate/send-email/")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_resend_activation_email_already_active(
    user: User,
    client: AsyncClient,
):
    response: Response = await client.post(f"/users/{user.id}/activate/send-email/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Bad request"}


@pytest.mark.asyncio
async def test_confirm_email(
    user: User,
    client: AsyncClient,
):
    user.deactivate()
    user.generate_email_confirmation_token()

    response: Response = await client.post(
        f"/users/{user.id}/activate/{user.email_confirmation_token}/",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_confirm_email_invalid_token(
    user: User,
    client: AsyncClient,
):
    user.deactivate()
    user.generate_email_confirmation_token()

    response: Response = await client.post(
        f"/users/{user.id}/activate/invalid-token/",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Bad request"}


@pytest.mark.asyncio
async def test_confirm_email_already_active(
    user: User,
    client: AsyncClient,
):
    user.generate_email_confirmation_token()

    response: Response = await client.post(
        f"/users/{user.id}/activate/{user.email_confirmation_token}/",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Bad request"}
