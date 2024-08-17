#!/usr/bin/env python3
"""
DB module for managing the database interactions.
"""

from sqlalchemy import create_engine
from sqlalchemy.exc import InvalidRequestError, SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from typing import Optional

from user import Base, User


class DB:
    """DB class for managing the database interactions."""

    def __init__(self) -> None:
        """Initialize a new DB instance."""
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session: Optional[Session] = None

    @property
    def _session(self) -> Session:
        """Memoized session object."""
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Adds a new user to the database.

        Args:
            email (str): The user's email address.
            hashed_password (str): The user's hashed password.

        Returns:
            User: The newly created User object.
        """
        new_user = User(email=email, hashed_password=hashed_password)
        try:
            self._session.add(new_user)
            self._session.commit()
            return new_user
        except SQLAlchemyError:
            self._session.rollback()
            raise

    def find_user_by(self, **kwargs) -> User:
        """Finds a user by given attributes.

        Args:
            **kwargs: Arbitrary keyword arguments representing user attributes to filter by.

        Returns:
            User: The first User object that matches the given filters.

        Raises:
            InvalidRequestError: If any of the filter keys are invalid.
            NoResultFound: If no user matches the filters.
        """
        try:
            query = self._session.query(User)
            for key, value in kwargs.items():
                if not hasattr(User, key):
                    raise InvalidRequestError(f"Invalid attribute: {key}")
                query = query.filter(getattr(User, key) == value)
            result = query.first()
            if result is None:
                raise NoResultFound(
                    f"No user found with the given criteria: {kwargs}")
            return result
        except SQLAlchemyError:
            raise

    def update_user(self, user_id: int, **kwargs) -> None:
        """Updates a user's attributes based on the given user_id.

        Args:
            user_id (int): The ID of the user to update.
            **kwargs: Arbitrary keyword arguments representing attributes to update.

        Raises:
            ValueError: If any of the attributes are invalid.
        """
        try:
            user = self.find_user_by(id=user_id)
            for key, value in kwargs.items():
                if not hasattr(User, key):
                    raise ValueError(f"Invalid attribute: {key}")
                setattr(user, key, value)
            self._session.commit()
        except SQLAlchemyError:
            self._session.rollback()
            raise
