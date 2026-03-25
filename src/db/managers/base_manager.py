from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeBase

# Type variables for generic typing
ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseManager(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD manager class for SQLAlchemy models.

    This class provides generic CRUD operations for any SQLAlchemy model.
    It handles Create, Read, Update, and Delete operations with proper
    async/await patterns and type safety.

    Args:
        model: The SQLAlchemy model class

    Example:
        ```python
        from src.models.user import User
        from src.schemas.user import UserCreate, UserUpdate

        user_manager = CRUDManager[User, UserCreate, UserUpdate](User)

        # Create a user
        user = await user_manager.create(db, user_create_data)

        # Get user by ID
        user = await user_manager.get(db, user_id)

        # Update user
        updated_user = await user_manager.update(db, user_id, user_update_data)

        # Delete user
        await user_manager.delete(db, user_id)
        ```
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(
        self, db: AsyncSession, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """


        :param db: Database session.
        :type db: AsyncSession
        :param obj_in: Data for creating the instance (Pydantic model or dict).
        :type obj_in: Union[CreateSchemaType, Dict[str, Any]]
        :return: The created model instance.
        :rtype: ModelType
        """
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump(exclude_unset=True)

        db_obj = self.model(**obj_data)

        db.add(db_obj)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Get a single instance by ID.

        :param db: Database session.
        :type db: AsyncSession
        :param id: ID of the instance to retrieve.
        :type id: Any
        :return: The model instance if found, None otherwise.
        :rtype: Optional[ModelType]
        """
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_by_field(
        self, db: AsyncSession, field_name: str, field_value: Any
    ) -> Optional[ModelType]:
        """
        Get a single instance by a specific field value.

        :param db: Database session.
        :type db: AsyncSession
        :param field_name: Name of the field to filter by.
        :type field_name: str
        :param field_value: Value of the field to filter by.
        :type field_value: Any
        :raises AttributeError: If the specified field does not exist on the model.
        :return: The model instance if found, None otherwise.
        :rtype: Optional[ModelType]
        """
        if not hasattr(self.model, field_name):
            raise AttributeError(
                f"Model {self.model.__name__} has no field '{field_name}'"
            )

        field = getattr(self.model, field_name)
        result = await db.execute(select(self.model).where(field == field_value))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        """
        Transform a list of model instances with optional filtering, ordering, and pagination.

        :param db: Database session
        :type db: AsyncSession
        :param skip: Number of records to skip for pagination, defaults to 0
        :type skip: int, optional
        :param limit: Maximum number of records to return, defaults to 100
        :type limit: int, optional
        :param filters: Dictionary of field filters {field_name: value}, defaults to None
        :type filters: Optional[Dict[str, Any]], optional
        :param order_by: Field name to order by, prefix with '-' for descending, defaults to None
        :type order_by: Optional[str], optional
        :return: List of model instances matching the criteria
        :rtype: List[ModelType]
        """
        query = select(self.model)

        # Apply filters
        if filters:
            for field_name, field_value in filters.items():
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    if isinstance(field_value, list):
                        query = query.where(field.in_(field_value))
                    else:
                        query = query.where(field == field_value)

        # Apply ordering
        if order_by:
            if order_by.startswith("-"):
                # Descending order
                field_name = order_by[1:]
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    query = query.order_by(field.desc())
            else:
                # Ascending order
                if hasattr(self.model, order_by):
                    field = getattr(self.model, order_by)
                    query = query.order_by(field.asc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def count(
        self, db: AsyncSession, filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count the number of instances that match the optional filters.

        :param db: Database session
        :type db: AsyncSession
        :param filters: Dictionary of field filters {field_name: value} to count matching records, defaults to None
        :type filters: Optional[Dict[str, Any]], optional
        :return: Number of records matching the criteria
        :rtype: int
        """
        from sqlalchemy import func

        query = select(func.count(self.model.id))

        # Apply filters
        if filters:
            for field_name, field_value in filters.items():
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    if isinstance(field_value, list):
                        query = query.where(field.in_(field_value))
                    else:
                        query = query.where(field == field_value)

        result = await db.execute(query)
        return result.scalar()

    async def update(
        self, db: AsyncSession, id: Any, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """
        Update an instance by ID.

        :param db: Database session
        :type db: AsyncSession
        :param id: ID of the instance to update
        :type id: Any
        :param obj_in: Data for updating the instance (Pydantic model or dict)
        :type obj_in: Union[UpdateSchemaType, Dict[str, Any]]
        :return: The updated model instance if found, None otherwise.
        :rtype: Optional[ModelType]
        """
        # Get the existing object
        db_obj = await self.get(db, id)
        if not db_obj:
            return None

        # Prepare update data
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Update fields
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_bulk(
        self,
        db: AsyncSession,
        filters: Dict[str, Any],
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> int:
        """
        Update multiple instances that match the filters.

        :param db: Database session.
        :type db: AsyncSession
        :param filters: Dictionary of field filters {field_name: value} to identify records to update.
        :type filters: Dict[str, Any]
        :param obj_in: Data for updating the instances (Pydantic model or dict).
        :type obj_in: Union[UpdateSchemaType, Dict[str, Any]]
        :return: Number of records updated.
        :rtype: int
        """
        # Prepare update data
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Build update query
        query = update(self.model)

        # Apply filters
        for field_name, field_value in filters.items():
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                query = query.where(field == field_value)

        # Apply updates
        query = query.values(**update_data)

        result = await db.execute(query)
        await db.commit()
        return result.rowcount

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """
        Delete an instance by ID.

        :param db: Database session.
        :type db: AsyncSession
        :param id: ID of the instance to delete.
        :type id: Any
        :return: True if the instance was found and deleted, False otherwise.
        :rtype: bool
        """
        db_obj = await self.get(db, id)
        if not db_obj:
            return False

        await db.delete(db_obj)
        await db.commit()
        return True

    async def delete_bulk(self, db: AsyncSession, filters: Dict[str, Any]) -> int:
        """
        Delete multiple instances that match the filters.

        :param db: Database session.
        :type db: AsyncSession
        :param filters: Dictionary of field filters {field_name: value} to identify records to delete.
        :type filters: Dict[str, Any]
        :return: Number of records deleted.
        :rtype: int
        """
        query = delete(self.model)

        # Apply filters
        for field_name, field_value in filters.items():
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                query = query.where(field == field_value)

        result = await db.execute(query)
        await db.commit()
        return result.rowcount

    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """
        Check if an instance exists by ID.

        :param db: Database session.
        :type db: AsyncSession
        :param id: ID of the instance to check for existence.
        :type id: Any
        :return: True if an instance with the specified ID exists, False otherwise.
        :rtype: bool
        """
        result = await db.execute(select(self.model.id).where(self.model.id == id))
        return result.scalar_one_or_none() is not None

    async def exists_by_field(
        self, db: AsyncSession, field_name: str, field_value: Any
    ) -> bool:
        """
        Check if an instance exists by a specific field value.

        :param db: Database session
        :type db: AsyncSession
        :param field_name: Name of the field to check for existence.
        :type field_name: str
        :param field_value: Value to check for existence in the specified field.
        :type field_value: Any
        :raises AttributeError: If the specified field does not exist on the model.
        :return: True if an instance with the specified field value exists, False otherwise.
        :rtype: bool
        """
        if not hasattr(self.model, field_name):
            raise AttributeError(
                f"Model {self.model.__name__} has no field '{field_name}'"
            )

        field = getattr(self.model, field_name)
        result = await db.execute(select(self.model.id).where(field == field_value))
        return result.scalar_one_or_none() is not None

    async def get_by_id(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Get a single instance by ID.

        :param db: Database session.
        :type db: AsyncSession
        :param id: ID of the instance to retrieve
        :type id: Any
        :return: The model instance if found, None otherwise.
        :rtype: Optional[ModelType]
        """
        return await self.get(db, id)
