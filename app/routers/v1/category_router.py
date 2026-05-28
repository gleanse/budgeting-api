from fastapi import APIRouter, HTTPException, status
from app.core.dependencies import UserAuthenticationDep, CategoryServiceDep
from app.schemas.v1.category_schema import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
    CategoryCreateResponse,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryResponse])
async def get_categories(
    current_user: UserAuthenticationDep, category_service: CategoryServiceDep
) -> list[CategoryResponse]:
    categories = category_service.list_by_user(current_user.id)
    return [
        CategoryResponse(
            id=category.id,
            user_id=category.user_id,
            name=category.name,
            type=category.type,
        )
        for category in categories
    ]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    current_user: UserAuthenticationDep,
    category_service: CategoryServiceDep,
    category_id: int,
) -> CategoryResponse:
    try:
        category = category_service.get_by_id_and_user(category_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return CategoryResponse(
        id=category.id,
        user_id=category.user_id,
        name=category.name,
        type=category.type,
    )


@router.post(
    "/", response_model=CategoryCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_category(
    current_user: UserAuthenticationDep,
    category_service: CategoryServiceDep,
    category_data: CategoryCreateRequest,
) -> CategoryCreateResponse:

    try:
        created_category = category_service.create(
            name=category_data.name,
            type=category_data.type,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return CategoryCreateResponse(
        created_item=CategoryResponse(
            id=created_category.id,
            name=created_category.name,
            type=created_category.type,
            user_id=created_category.user_id,
        )
    )


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    current_user: UserAuthenticationDep,
    category_service: CategoryServiceDep,
    category_id: int,
    category_data: CategoryUpdateRequest,
) -> CategoryResponse:
    try:
        updated_category = category_service.update(
            category_id=category_id,
            user_id=current_user.id,
            name=category_data.name,
            type=category_data.type,
        )
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return CategoryResponse(
        id=updated_category.id,
        user_id=updated_category.user_id,
        name=updated_category.name,
        type=updated_category.type,
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    current_user: UserAuthenticationDep,
    category_service: CategoryServiceDep,
    category_id: int,
) -> None:

    try:
        category_service.delete(category_id=category_id, user_id=current_user.id)
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
