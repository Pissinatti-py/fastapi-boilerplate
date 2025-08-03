from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import update, delete
from pydantic import BaseModel

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
        """
        Initialize the CRUD manager with a specific model class.

        Args:
            model: The SQLAlchemy model class to manage
        """
        self.model = model

    async def create(
        self,
        db: AsyncSession,
        obj_in: Union[CreateSchemaType, Dict[str, Any]]
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
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_field(
        self,
        db: AsyncSession,
        field_name: str,
        field_value: Any
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
        if not hasattr(self.model, field_name):
            raise AttributeError(
                f"Model {self.model.__name__} has no field '{field_name}'"
            )

        field = getattr(self.model, field_name)
        result = await db.execute(
            select(self.model).where(field == field_value)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
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
            if order_by.startswith('-'):
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
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None
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
        self,
        db: AsyncSession,
        id: Any,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
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
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
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

    async def delete_bulk(
        self,
        db: AsyncSession,
        filters: Dict[str, Any]
    ) -> int:
        """
        Delete multiple instances that match the filters.

        Args:
            db: Database session
            filters: Dictionary of field filters to identify records to delete

        Returns:
            Number of deleted records
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

        Args:
            db: Database session
            id: ID of the instance to check

        Returns:
            True if the instance exists, False otherwise
        """
        result = await db.execute(
            select(self.model.id).where(self.model.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def exists_by_field(
        self,
        db: AsyncSession,
        field_name: str,
        field_value: Any
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
        if not hasattr(self.model, field_name):
            raise AttributeError(
                f"Model {self.model.__name__} has no field '{field_name}'"
            )

        field = getattr(self.model, field_name)
        result = await db.execute(
            select(self.model.id).where(field == field_value)
        )
        return result.scalar_one_or_none() is not None

    async def get_by_id(
        self,
        db: AsyncSession,
        id: Any
    ) -> Optional[ModelType]:
        """
        Alias for get method to retrieve by ID.

        Args:
            db: Database session
            id: ID of the instance to retrieve

        Returns:
            The model instance if found, None otherwise
        """
        return await self.get(db, id)
