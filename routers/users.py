from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/")
def get_users():
    return {"message": "Тут буде список користувачів для нашого менеджера підписок"}

@router.get("/{user_id}")
def get_user_profile(user_id: int):
    return {"message": f"Профіль користувача з ID: {user_id}"}
