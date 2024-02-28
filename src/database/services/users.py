from database.utils.unitofwork import IUnitOfWork
from database.models import User


class UsersService:
    async def add_user(self, uow: IUnitOfWork, user_data: dict):
        async with uow:
            user_exists: User | None = await uow.users.find_by_username(username=user_data["username"])

            if user_exists:
                return False

            user: User = await uow.users.create(user_data)
            await uow.commit()
            return user.to_dict()


    async def get_user(self, uow: IUnitOfWork, username: str):
        async with uow:
            user: User | None = await uow.users.find_by_username(username=username)
            return user.to_dict()


    async def update_user(self, uow: IUnitOfWork, user_id: int, data: dict):
        async with uow:
            user: User = await uow.users.update(pk=user_id, data=data)
            await uow.commit()
            return user.to_dict()

