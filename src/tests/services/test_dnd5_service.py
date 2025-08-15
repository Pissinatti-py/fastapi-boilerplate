"""Tests for D&D 5e service."""

import pytest
from unittest.mock import patch, MagicMock

from src.services.dnd5 import DnD5eAPIError, DnD5eService


class TestDnD5eService:
    """Test cases for DnD5eService."""

    @pytest.mark.asyncio
    async def test_get_ability_score_success(self):
        """Test successful ability score retrieval."""
        mock_response = {
            "index": "str",
            "name": "Strength",
            "full_name": "Strength",
            "desc": ["Strength measures bodily power..."],
            "skills": [{"index": "athletics", "name": "Athletics"}],
        }

        # Mock asyncio.to_thread to return our mock response directly
        with patch("asyncio.to_thread") as mock_to_thread:
            # Create a mock response object
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_response
            mock_resp.raise_for_status.return_value = None
            mock_to_thread.return_value = mock_resp

            async with DnD5eService() as service:
                result = await service.get_ability_score("str")
                assert result == mock_response

    @pytest.mark.asyncio
    async def test_get_ability_score_invalid_index(self):
        """Test invalid ability score index."""
        async with DnD5eService() as service:
            with pytest.raises(DnD5eAPIError) as exc_info:
                await service.get_ability_score("invalid")

            assert "Invalid ability score index" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_spell_success(self):
        """Test successful spell retrieval."""
        mock_response = {
            "index": "fireball",
            "name": "Fireball",
            "level": 3,
            "school": {"index": "evocation", "name": "Evocation"},
            "components": ["V", "S", "M"],
            "range": "150 feet",
        }

        with patch.object(DnD5eService, "_make_request", return_value=mock_response):
            async with DnD5eService() as service:
                result = await service.get_spell("fireball")
                assert result == mock_response

    @pytest.mark.asyncio
    async def test_get_monster_success(self):
        """Test successful monster retrieval."""
        mock_response = {
            "index": "goblin",
            "name": "Goblin",
            "type": "humanoid",
            "challenge_rating": 0.25,
            "hit_points": 7,
            "armor_class": 15,
        }

        with patch.object(DnD5eService, "_make_request", return_value=mock_response):
            async with DnD5eService() as service:
                result = await service.get_monster("goblin")
                assert result == mock_response

    @pytest.mark.asyncio
    async def test_get_spells_by_level(self):
        """Test filtering spells by level."""
        mock_all_spells = {
            "results": [
                {"index": "fireball", "name": "Fireball"},
                {"index": "magic-missile", "name": "Magic Missile"},
            ]
        }

        mock_fireball = {"index": "fireball", "name": "Fireball", "level": 3}
        mock_magic_missile = {
            "index": "magic-missile",
            "name": "Magic Missile",
            "level": 1
        }

        with patch.object(
            DnD5eService, "get_all_spells", return_value=mock_all_spells
        ), patch.object(
            DnD5eService,
            "get_spell",
            side_effect=[mock_fireball, mock_magic_missile]
        ):

            async with DnD5eService() as service:
                result = await service.get_spells_by_level(3)
                assert len(result) == 1
                assert result[0]["name"] == "Fireball"

    @pytest.mark.asyncio
    async def test_spell_level_validation(self):
        """Test spell level validation."""
        async with DnD5eService() as service:
            with pytest.raises(DnD5eAPIError) as exc_info:
                await service.get_spells_by_level(10)

            assert "Spell level must be between 0 and 9" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_service_not_initialized_error(self):
        """Test error when service is not initialized."""
        service = DnD5eService()
        with pytest.raises(DnD5eAPIError) as exc_info:
            await service._make_request("/test")

        assert "Service not initialized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_quick_request_method(self):
        """Test the quick_request convenience method."""
        mock_response = {"index": "cha", "name": "Charisma"}

        with patch.object(DnD5eService, "_make_request", return_value=mock_response):
            result = await DnD5eService.quick_request("get_ability_score", "cha")
            assert result == mock_response
