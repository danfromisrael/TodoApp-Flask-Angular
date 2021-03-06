import datetime
import json
from urllib.parse import urlparse

from bson import ObjectId
from pymongo import MongoClient
from Server.Domain.Entities import User
from Server.Domain.Interfaces import IUserRepository
from Server.Domain.Core import pre_condition_arg, Maybe
from Server.Infrastructure.Data.InMemoryUserRepository import UserDoesntExistsError


class MongoDbUserRepository(IUserRepository):
    def __init__(self, connection_string):

        pre_condition_arg(self, connection_string, of_type=str)

        # self.connection_details = DBConnectionDetails(connection_string)
        self._db_client = MongoClient(connection_string, _connect=False)
        self._users_db = None

    def get_by_email(self, email):
        users_collection = self._get_users_collection()
        result = users_collection.find_one({"email": email})
        user = self._from_json(result)
        self._db_client.close()
        return Maybe(value=user)

    def get_by_facebook_id(self, facebook_id):
        users_collection = self._get_users_collection()
        result = users_collection.find_one({"facebook": facebook_id})
        user = self._from_json(result)
        self._db_client.close()
        return Maybe(value=user)

    def get_by_google_id(self, google_id):
        users_collection = self._get_users_collection()
        result = users_collection.find_one({"google": google_id})
        user = self._from_json(result)
        self._db_client.close()
        return Maybe(value=user)

    def _get_users_collection(self):
        if not self._users_db:
            db = self._db_client.get_default_database()
            self._users_db = db['users']
        return self._users_db

    def _from_json(self, user):
        if user is None:
            return None

        # user = dict(user)
        u = User()
        if user.get("user_id", None):
            u.id = user["user_id"]

        if user.get("email", None):
            u.email = user["email"]

        if user.get("display_name", None):
            u.display_name = user["display_name"]

        if user.get("hashed_password", None):
            u.hashed_password = user["hashed_password"]

        if user.get("facebook", None):
            u.facebook = user["facebook"]

        if user.get("google", None):
            u.google = user["google"]

        if user.get("twitter", None):
            u.twitter = user["twitter"]

        if user.get("github", None):
            u.github = user["github"]

        if user.get("pic_link", None):
            u.pic_link = user["pic_link"]

        if user.get("linkedin", None):
            u.linkedin = user["linkedin"]

        return u

    def _to_json(self, user):
        json_user = dict()

        if getattr(user, 'id', None):
            json_user["user_id"] = user.id

        if getattr(user, 'email', None):
            json_user["email"] = user.email

        if getattr(user, 'display_name', None):
            json_user["display_name"] = user.display_name

        if getattr(user, 'hashed_password', None):
            json_user["hashed_password"] = user.hashed_password

        if getattr(user, 'facebook', None):
            json_user["facebook"] = user.facebook

        if getattr(user, 'google', None):
            json_user["google"] = user.google

        if getattr(user, 'twitter', None):
            json_user["twitter"] = user.twitter

        if getattr(user, 'github', None):
            json_user["github"] = user.github

        if getattr(user, 'pic_link', None):
            json_user["pic_link"] = user.pic_link

        if getattr(user, 'linkedin', None):
            json_user["linkedin"] = user.linkedin

        return json_user


    def get_all(self):
        users_collection = self._get_users_collection()
        db_users_list = list(users_collection.find())
        users = [self._from_json(user) for user in db_users_list]
        self._db_client.close()
        return users

    def add(self, user):
        users_collection = self._get_users_collection()
        json_user = self._to_json(user)
        users_collection.insert(json_user)
        self._db_client.close()

    def get_by_id(self, user_id):
        users_collection = self._get_users_collection()
        result = users_collection.find_one({"user_id": user_id})
        user = self._from_json(result)
        self._db_client.close()
        return Maybe(value=user)

    def update(self, user_id, user):
        users_collection = self._get_users_collection()
        maybe_db_user = users_collection.find_one({"user_id": user_id})
        if maybe_db_user is not None:
            db_user = maybe_db_user
        else:
            raise UserDoesntExistsError("invalid user_id")

        if db_user.get("hashed_password", None) != user.hashed_password:
            db_user["hashed_password"] = user.hashed_password

        if db_user.get("facebook", None) != user.facebook:
            db_user["facebook"] = user.facebook

        if db_user.get("email", None) != user.email:
            db_user["email"] = user.email

        if db_user.get("twitter", None) != user.twitter:
            db_user["twitter"] = user.twitter

        if db_user.get("google", None) != user.google:
            db_user["google"] = user.google

        if db_user.get("github", None) != user.github:
            db_user["github"] = user.github

        if db_user.get("display_name", None) != user.display_name:
            db_user["display_name"] = user.display_name

        if db_user.get("pic_link", None) != user.pic_link:
            db_user["pic_link"] = user.pic_link

        if db_user.get("linkedin", None) != user.linkedin:
            db_user["linkedin"] = user.linkedin

        users_collection.update({"user_id": user_id}, db_user)

    def delete(self, user_id):
        users_collection = self._get_users_collection()
        users_collection.remove({"user_id": user_id})
        self._db_client.close()