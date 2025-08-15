"""D&D 5e API Service for interacting with the 5e SRD API."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import requests
from requests import RequestException, Timeout

logger = logging.getLogger(__name__)


class DnD5eAPIError(Exception):
    """Custom exception for D&D 5e API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            status_code: HTTP status code if available
        """
        super().__init__(message)
        self.status_code = status_code


class DnD5eService:
    """Service for interacting with the D&D 5e SRD API."""

    BASE_URL = "https://www.dnd5eapi.co/api"
    TIMEOUT = 30.0

    def __init__(self, timeout: float = TIMEOUT) -> None:
        """Initialize the D&D 5e service.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self._session: Optional[requests.Session] = None

    async def __aenter__(self) -> "DnD5eService":
        """Async context manager entry."""
        self._session = requests.Session()
        self._session.timeout = self.timeout
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._session:
            self._session.close()
            self._session = None

    async def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make a request to the D&D 5e API.

        Args:
            endpoint: API endpoint path

        Returns:
            JSON response data

        Raises:
            DnD5eAPIError: If the request fails
        """
        if not self._session:
            error_msg = "Service not initialized. Use as async context manager."
            raise DnD5eAPIError(error_msg)

        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        try:
            logger.info(f"Making request to D&D 5e API: {url}")

            # Run the request in a thread to avoid blocking the event loop
            response = await asyncio.to_thread(
                self._session.get, url, timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Received response from {url}: {len(str(data))} characters")
            return data

        except requests.HTTPError as e:
            response_text = e.response.text if e.response else 'No response'
            status_code = e.response.status_code if e.response else None
            error_msg = f"HTTP error occurred: {status_code} - {response_text}"
            logger.error(error_msg)
            raise DnD5eAPIError(error_msg, status_code)

        except (RequestException, Timeout) as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise DnD5eAPIError(error_msg)

        except ValueError as e:
            error_msg = f"Failed to parse JSON response: {str(e)}"
            logger.error(error_msg)
            raise DnD5eAPIError(error_msg)

    async def get_ability_score(self, index: str) -> Dict[str, Any]:
        """Get an ability score by index.

        Args:
            index: The ability score index (cha, con, dex, int, str, wis)

        Returns:
            Ability score data

        Raises:
            DnD5eAPIError: If the request fails or ability score not found
        """
        valid_indexes = ["cha", "con", "dex", "int", "str", "wis"]
        if index.lower() not in valid_indexes:
            error_msg = f"Invalid ability score index. Valid values: {valid_indexes}"
            raise DnD5eAPIError(error_msg)

        endpoint = f"/ability-scores/{index.lower()}"
        return await self._make_request(endpoint)

    async def get_all_ability_scores(self) -> Dict[str, Any]:
        """Get list of all ability scores.

        Returns:
            List of all ability scores
        """
        endpoint = "/ability-scores"
        return await self._make_request(endpoint)

    async def get_spell(self, index: str) -> Dict[str, Any]:
        """Get a spell by index.

        Args:
            index: The spell index (e.g., 'fireball', 'magic-missile')

        Returns:
            Spell data

        Raises:
            DnD5eAPIError: If the request fails or spell not found
        """
        endpoint = f"/spells/{index.lower()}"
        return await self._make_request(endpoint)

    async def get_all_spells(self) -> Dict[str, Any]:
        """Get list of all spells.

        Returns:
            List of all spells
        """
        endpoint = "/spells"
        return await self._make_request(endpoint)

    async def get_spells_by_level(self, level: int) -> List[Dict[str, Any]]:
        """Get spells filtered by level.

        Args:
            level: Spell level (0-9)

        Returns:
            List of spells for the specified level

        Raises:
            DnD5eAPIError: If the request fails or invalid level
        """
        if not 0 <= level <= 9:
            raise DnD5eAPIError("Spell level must be between 0 and 9")

        # Get all spells and filter by level
        all_spells = await self.get_all_spells()
        filtered_spells = []

        for spell_ref in all_spells.get("results", []):
            spell_data = await self.get_spell(spell_ref["index"])
            if spell_data.get("level") == level:
                filtered_spells.append(spell_data)

        return filtered_spells

    async def get_monster(self, index: str) -> Dict[str, Any]:
        """Get a monster by index.

        Args:
            index: The monster index (e.g., 'ancient-black-dragon', 'goblin')

        Returns:
            Monster data

        Raises:
            DnD5eAPIError: If the request fails or monster not found
        """
        endpoint = f"/monsters/{index.lower()}"
        return await self._make_request(endpoint)

    async def get_all_monsters(self) -> Dict[str, Any]:
        """Get list of all monsters.

        Returns:
            List of all monsters
        """
        endpoint = "/monsters"
        return await self._make_request(endpoint)

    async def get_monsters_by_challenge_rating(
        self, challenge_rating: str
    ) -> List[Dict[str, Any]]:
        """Get monsters filtered by challenge rating.

        Args:
            challenge_rating: Challenge rating (e.g., '1', '1/2', '1/4')

        Returns:
            List of monsters for the specified challenge rating
        """
        # Get all monsters and filter by challenge rating
        all_monsters = await self.get_all_monsters()
        filtered_monsters = []

        for monster_ref in all_monsters.get("results", []):
            monster_data = await self.get_monster(monster_ref["index"])
            if str(monster_data.get("challenge_rating")) == str(challenge_rating):
                filtered_monsters.append(monster_data)

        return filtered_monsters

    async def search_spells_by_school(self, school: str) -> List[Dict[str, Any]]:
        """Search spells by magic school.

        Args:
            school: Magic school name (e.g., 'evocation', 'enchantment')

        Returns:
            List of spells from the specified school
        """
        all_spells = await self.get_all_spells()
        filtered_spells = []

        for spell_ref in all_spells.get("results", []):
            spell_data = await self.get_spell(spell_ref["index"])
            spell_school = spell_data.get("school", {}).get("name", "").lower()
            if school.lower() in spell_school:
                filtered_spells.append(spell_data)

        return filtered_spells

    # Método de conveniência para uso direto sem context manager
    @classmethod
    async def quick_request(cls, method_name: str, *args, **kwargs) -> Any:
        """Make a quick request without managing the context manually.

        Args:
            method_name: Name of the method to call
            *args: Arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method

        Returns:
            Result from the method call
        """
        async with cls() as service:
            method = getattr(service, method_name)
            return await method(*args, **kwargs)
