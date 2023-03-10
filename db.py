import logging

from gino import Gino
from sqlalchemy import (Column, Integer, BigInteger, Boolean)

from config import db_user, db_password, host, db_name, port


db = Gino()

logging.basicConfig()
logging.getLogger('gino.engine._SAEngine').setLevel(logging.ERROR)


class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    subscription_days = Column(Integer)
    is_active = Column(Boolean)

    def __repr__(self):
        return f'<Id={self.id}, user_id={self.user_id}>'


class UserCommands:
    async def add_user(self, user_id, sub_time):
        new_user = User()
        new_user.user_id = user_id
        new_user.subscription_days = sub_time
        new_user.is_active = True
        await new_user.create()

    async def delete_user(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        await user.delete()

    async def user_exists(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return bool(user)

    async def get_sub_days(self, user_id):
        info = await User.select('subscription_days').where(User.user_id == user_id).gino.first()
        return int(info[0])

    async def update_sub_days(self, user_id, seconds):
        user = await User.query.where(User.user_id == user_id).gino.first()
        await user.update(subscription_days=seconds).apply()

    async def update_user_status(self, user_id, status):
        user = await User.query.where(User.user_id == user_id).gino.first()
        await user.update(is_active=status).apply()

    async def is_active(self, user_id):
        info = await User.select('is_active').where(User.user_id == user_id).gino.first()
        return bool(info[0])


async def create_db():
    print('Connecting to db')
    await db.set_bind(f'postgresql://{db_user}:{db_password}@{host}:{port}/{db_name}')

    await db.gino.create_all()
