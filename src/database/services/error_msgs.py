from database.utils.unitofwork import IUnitOfWork


class ErrorInfoMsgsService:
    async def add_error_msg(self, uow: IUnitOfWork, msg: str):
        async with uow:
            await uow.error_msgs.create(data={"error_msg": msg})


    async def get_error(self, uow: IUnitOfWork, error_id: int):
        async with uow:
            error = await uow.error_msgs.find_one(pk=error_id)
            return error.to_dict()


    async def get_all_errors(self, uow: IUnitOfWork):
        async with uow:
            error_msgs: list = await uow.error_msgs.find_all()
            return [err_msg.to_dict() for err_msg in error_msgs]


    async def delete_error_msg(self, uow: IUnitOfWork, error_id: int):
        async with uow:
            await uow.error_msgs.delete(pk=error_id)
