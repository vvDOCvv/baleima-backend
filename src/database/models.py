from datetime import datetime
from sqlalchemy import Integer,String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True, autoincrement=True)

    # @declared_attr.directive
    # def __tablename__(cls) -> str:
        # return cls.__name__.lower()


class User(Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    password: Mapped[str]
    mexc_api_key: Mapped[str] = mapped_column(String, nullable=True)
    mexc_secret_key: Mapped[str] = mapped_column(String, nullable=True)
    trade_quantity: Mapped[int] = mapped_column(Integer, default=6,)
    trade_percent: Mapped[float] = mapped_column(Float, default=0.3)
    symbol_to_trade: Mapped[str] = mapped_column(String, default="KASUSDT")
    auto_trade: Mapped[bool] = mapped_column(Boolean, default=False)
    for_free: Mapped[bool] = mapped_column(Boolean, default=False)
    last_paid: Mapped[datetime] = mapped_column(Boolean, nullable=True)
    ban: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())
    date_joined: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())

    trade: Mapped[list['TradeInfo']] = relationship()


class TradeInfo(Base):
    __tablename__ = "trade"

    symbol: Mapped[str] = mapped_column(String(15))
    buy_quantity: Mapped[float] = mapped_column(Float, nullable=True)
    cummulative_qoute_qty: Mapped[float] = mapped_column(Float, nullable=True)
    buy_order_id: Mapped[str] = mapped_column(String(50), nullable=True)
    buy_price: Mapped[float] = mapped_column(Float, nullable=True)
    sell_order_id: Mapped[str] = mapped_column(String(50), nullable=True)
    sell_price: Mapped[float] = mapped_column(Float, nullable=True)
    profit: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(15), nullable=True)
    date_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())
    user: Mapped[int] = mapped_column(ForeignKey("user.id"))


class ErrorInfoMsgs(Base):
    __tablename__ = "trade_error_msgs"

    error_msg: Mapped[str]
    date_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())
