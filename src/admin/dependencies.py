from fastapi import Depends
from typing import Annotated
from database.models import User
from .service import is_superuser_cooke


super_user_dependency = Annotated[User, Depends(is_superuser_cooke)]