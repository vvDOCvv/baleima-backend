from fastapi import Request


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: str | None = None
        self.password: str | None = None

    async def create_user(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")


class UpdateUser:
    def __init__(self, request: Request) -> None:
        self.request: Request = request


    async def update_user(self):
        form = await self.request.form()
        to_int = ["trade_quantity", "user_id"]
        to_float = [
            "trade_percent",
            "bif_percent_1",
            "bif_percent_2",
            "bif_percent_3",
            "bif_price_1",
            "bif_price_2",
            "bif_price_3",
        ]
        to_bool = [
            "bif_is_active",
            "auto_trade",
            "is_superuser",
            "is_staff",
            "for_free",
            "ban"
        ]
        user_data = {
            "bif_is_active": False,
            "auto_trade": False,
            "is_superuser": False,
            "is_staff": False,
            "for_free": False,
            "ban": False,
        }
        for key, val in form.multi_items():
            if key in to_bool and val == "on":
                user_data[key] = True
            elif key in to_int:
                user_data[key] = int(val)
            elif key in to_float:
                user_data[key] = float(val)
            elif key == "_save":
                continue
            elif val:
                user_data[key] = val
        return user_data
            


