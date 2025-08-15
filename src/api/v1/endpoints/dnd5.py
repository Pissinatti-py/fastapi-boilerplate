"""D&D 5e API endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from src.services.dnd5 import DnD5eAPIError, DnD5eService

router = APIRouter()


@router.get("/ability-scores/{index}")
async def get_ability_score(index: str) -> Dict[str, Any]:
    """Get an ability score by index.

    Args:
        index: The ability score index (cha, con, dex, int, str, wis)

    Returns:
        Ability score data

    Raises:
        HTTPException: If the ability score is not found or API request fails
    """
    try:
        async with DnD5eService() as service:
            return await service.get_ability_score(index)
    except DnD5eAPIError as e:
        status_code = e.status_code or 500
        raise HTTPException(status_code=status_code, detail=str(e))


@router.get("/ability-scores/")
async def get_all_ability_scores() -> Dict[str, Any]:
    """Get list of all ability scores.

    Returns:
        List of all ability scores

    Raises:
        HTTPException: If API request fails
    """
    try:
        async with DnD5eService() as service:
            return await service.get_all_ability_scores()
    except DnD5eAPIError as e:
        status_code = e.status_code or 500
        raise HTTPException(status_code=status_code, detail=str(e))


@router.get("/spells/{index}")
async def get_spell(index: str) -> Dict[str, Any]:
    """Get a spell by index.

    Args:
        index: The spell index (e.g., 'fireball', 'magic-missile')

    Returns:
        Spell data

    Raises:
        HTTPException: If the spell is not found or API request fails
    """
    try:
        async with DnD5eService() as service:
            return await service.get_spell(index)
    except DnD5eAPIError as e:
        status_code = e.status_code or 500
        raise HTTPException(status_code=status_code, detail=str(e))


@router.get("/spells")
async def get_spells(
    level: int = Query(None, description="Filter spells by level (0-9)"),
    school: str = Query(None, description="Filter spells by magic school"),
) -> Dict[str, Any]:
    """Get spells with optional filters.

    Args:
        level: Optional spell level filter (0-9)
        school: Optional magic school filter

    Returns:
        Spells data (filtered if parameters provided)

    Raises:
        HTTPException: If API request fails
    """
    try:
        async with DnD5eService() as service:
            if level is not None:
                spells = await service.get_spells_by_level(level)
                return {"count": len(spells), "results": spells}
            elif school is not None:
                spells = await service.search_spells_by_school(school)
                return {"count": len(spells), "results": spells}
            else:
                return await service.get_all_spells()
    except DnD5eAPIError as e:
        status_code = e.status_code or 500
        raise HTTPException(status_code=status_code, detail=str(e))


@router.get("/monsters/{index}")
async def get_monster(index: str) -> Dict[str, Any]:
    """Get a monster by index.

    Args:
        index: The monster index (e.g., 'ancient-black-dragon', 'goblin')

    Returns:
        Monster data

    Raises:
        HTTPException: If the monster is not found or API request fails
    """
    try:
        async with DnD5eService() as service:
            return await service.get_monster(index)
    except DnD5eAPIError as e:
        status_code = e.status_code or 500
        raise HTTPException(status_code=status_code, detail=str(e))


@router.get("/monsters")
async def get_monsters(
    challenge_rating: str = Query(
        None, description="Filter monsters by challenge rating"
    ),
) -> Dict[str, Any]:
    """Get monsters with optional challenge rating filter.

    Args:
        challenge_rating: Optional challenge rating filter

    Returns:
        Monsters data (filtered if challenge_rating provided)

    Raises:
        HTTPException: If API request fails
    """
    try:
        async with DnD5eService() as service:
            if challenge_rating is not None:
                monsters = await service.get_monsters_by_challenge_rating(
                    challenge_rating
                )
                return {"count": len(monsters), "results": monsters}
            else:
                return await service.get_all_monsters()
    except DnD5eAPIError as e:
        status_code = e.status_code or 500
        raise HTTPException(status_code=status_code, detail=str(e))

