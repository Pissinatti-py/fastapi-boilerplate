from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.selectable import Select
from sqlalchemy import update, delete
from pydantic import BaseModel


# Helper functions to reduce complexity and duplication
def _get_field_attr(
    model: Type[DeclarativeBase], field_name: str
):
    """
    Return attribute for field_name or raise AttributeError with clear message.

    :raises AttributeError: If the field does not exist on the model.
    :return: attribute for the field
    :rtype: Any
    """
    if not hasattr(model, field_name):
        raise AttributeError(
            "Model {} has no field '{}'".format(model.__name__, field_name)
        )

    return getattr(model, field_name)


def _apply_filters_to_query(
    query: Select,
    model: Type[DeclarativeBase],
    filters: Optional[Dict[str, Any]],
):
    """
    Method for applying filters to a SQLAlchemy query.

    :param query: SQLAlchemy query object to apply filters to
    :type query: Select
    :param model: SQLAlchemy model class to use for field access
    :type model: Type[DeclarativeBase]
    :param filters: Dictionary of field filters {field_name: value}
    :type filters: Optional[Dict[str, Any]]
    :return: Filtered SQLAlchemy query object
    :rtype: Any
    """
    if not filters:
        return query

    for fname, fvalue in filters.items():
        if hasattr(model, fname):
            field_attr = getattr(model, fname)
            if isinstance(fvalue, list):
                query = query.where(field_attr.in_(fvalue))
            else:
                query = query.where(field_attr == fvalue)

    return query


def _apply_ordering(
    query: Select, model: Type[DeclarativeBase], order_by: Optional[str]
):
    """
    Method for applying ordering to a SQLAlchemy query.

    :param query: SQLAlchemy query object to apply ordering to
    :type query: Select
    :param model: SQLAlchemy model class to use for field access
    :type model: Type[DeclarativeBase]
    :param order_by: Field name to order by
    :type order_by: Optional[str]
    :return: Ordered SQLAlchemy query object
    :rtype: Any
    """    """Apply ordering to query if provided."""
    if not order_by:
        return query

    if order_by.startswith("-"):
        fname = order_by[1:]
        if hasattr(model, fname):
            field_attr = getattr(model, fname)
            return query.order_by(field_attr.desc())

    if hasattr(model, order_by):
        field_attr = getattr(model, order_by)
        return query.order_by(field_attr.asc())

    return query


def _apply_update_fields(db_obj, update_data: Dict[str, Any]):
    """
    Apply update_data to db_obj attributes when present.

    :param db_obj: DeclarativeBase instance to update
    :type db_obj: DeclarativeBase
    :param update_data: Data to update the instance with
    :type update_data: Dict[str, Any]
    """
    for field_name, field_value in update_data.items():
        if hasattr(db_obj, field_name):
            setattr(db_obj, field_name, field_value)


# Type variables for generic typing
ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseManager(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType]
):  # noqa: WPS214
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
        """
        Initialize the CRUD manager with a specific model class.

        Args:
            model: The SQLAlchemy model class to manage
        """
        self.model = model

    async def create(
        self, db: AsyncSession, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Create a new instance of the model.

        Args:
            db: Database session
            obj_in: Data for creating the new instance (Pydantic model or dict)

        Returns:
            The created model instance

        Raises:
            SQLAlchemyError: If database operation fails
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

        Args:
            db: Database session
            id: The ID of the instance to retrieve

        Returns:
            The model instance if found, None otherwise
        """
        exec_result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return exec_result.scalar_one_or_none()

    async def get_by_field(
        self, db: AsyncSession, field_name: str, field_value: Any
    ) -> Optional[ModelType]:
        """
        Get a single instance by a specific field.

        Args:
            db: Database session
            field_name: Name of the field to search by
            field_value: Value to search for

        Returns:
            The model instance if found, None otherwise

        Raises:
            AttributeError: If the field doesn't exist on the model
        """
        # Validate and get field attribute
        field = _get_field_attr(self.model, field_name)
        exec_result = await db.execute(
            select(self.model).where(field == field_value)
        )
        return exec_result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        """
        Get multiple instances with pagination and filtering.

        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            filters: Dictionary of field filters {field_name: value}
            order_by: Field name to order by (prefix with '-' for desc)

        Returns:
            List of model instances
        """
        query = select(self.model)
        query = _apply_filters_to_query(query, self.model, filters)
        query = _apply_ordering(query, self.model, order_by)
        query = query.offset(skip).limit(limit)

        exec_result = await db.execute(query)
        return exec_result.scalars().all()

    async def count(
        self, db: AsyncSession, filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count instances with optional filtering.

        Args:
            db: Database session
            filters: Dictionary of field filters {field_name: value}

        Returns:
            Total count of matching instances
        """
        from sqlalchemy import func

        query = select(func.count(self.model.id))
        query = _apply_filters_to_query(query, self.model, filters)

        exec_result = await db.execute(query)
        return exec_result.scalar()

    async def update(
        self, db: AsyncSession, id: Any, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """
        Update an existing instance.

        Args:
            db: Database session
            id: ID of the instance to update
            obj_in: Data for updating the instance (Pydantic model or dict)

        Returns:
            The updated model instance if found, None otherwise
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
        _apply_update_fields(db_obj, update_data)

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

        Args:
            db: Database session
            filters: Dictionary of field filters to identify records to update
            obj_in: Data for updating the instances

        Returns:
            Number of updated records
        """
        # Prepare update data
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Build update query and apply filters
        query = update(self.model)
        query = _apply_filters_to_query(query, self.model, filters)

        # Apply updates
        query = query.values(**update_data)

        exec_result = await db.execute(query)
        await db.commit()
        return exec_result.rowcount

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """
        Delete an instance by ID.

        Args:
            db: Database session
            id: ID of the instance to delete

        Returns:
            True if the instance was deleted, False if not found
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

        Args:
            db: Database session
            filters: Dictionary of field filters to identify records to delete

        Returns:
            Number of deleted records
        """
        query = delete(self.model)
        query = _apply_filters_to_query(query, self.model, filters)

        exec_result = await db.execute(query)
        await db.commit()
        return exec_result.rowcount

    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """
        Check if an instance exists by ID.

        Args:
            db: Database session
            id: ID of the instance to check

        Returns:
            True if the instance exists, False otherwise
        """
        exec_result = await db.execute(
            select(self.model.id).where(self.model.id == id)
        )
        return exec_result.scalar_one_or_none() is not None

    async def exists_by_field(
        self, db: AsyncSession, field_name: str, field_value: Any
    ) -> bool:
        """
        Check if an instance exists by a specific field.

        Args:
            db: Database session
            field_name: Name of the field to check
            field_value: Value to check for

        Returns:
            True if an instance with the field value exists, False otherwise

        Raises:
            AttributeError: If the field doesn't exist on the model
        """
        # Validate field existence
        field = _get_field_attr(self.model, field_name)
        exec_result = await db.execute(
            select(self.model.id).where(field == field_value)
        )
        return exec_result.scalar_one_or_none() is not None

    async def get_by_id(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Alias for get method to retrieve by ID.

        Args:
            db: Database session
            id: ID of the instance to retrieve

        Returns:
            The model instance if found, None otherwise
        """
        return await self.get(db, id)
