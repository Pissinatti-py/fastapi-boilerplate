# D&D 5e Service

Este serviço fornece uma interface para interagir com a [D&D 5e SRD API](https://www.dnd5eapi.co/), permitindo buscar informações sobre ability scores, spells e monsters do universo de Dungeons & Dragons 5ª edição.

## Funcionalidades

O serviço oferece métodos para acessar os seguintes recursos:

### 1. Ability Scores (Atributos)

- `get_ability_score(index)` - Busca um atributo específico
- `get_all_ability_scores()` - Lista todos os atributos

### 2. Spells (Magias)

- `get_spell(index)` - Busca uma magia específica
- `get_all_spells()` - Lista todas as magias
- `get_spells_by_level(level)` - Filtra magias por nível (0-9)
- `search_spells_by_school(school)` - Filtra magias por escola de magia

### 3. Monsters (Monstros)

- `get_monster(index)` - Busca um monstro específico
- `get_all_monsters()` - Lista todos os monstros
- `get_monsters_by_challenge_rating(cr)` - Filtra monstros por CR

## Como Usar

### Usando como Context Manager (Recomendado)

```python
from src.services.dnd5 import DnD5eService, DnD5eAPIError

async def exemplo_uso():
    try:
        async with DnD5eService() as service:
            # Buscar um atributo
            strength = await service.get_ability_score("str")
            print(f"Força: {strength['name']}")

            # Buscar uma magia
            fireball = await service.get_spell("fireball")
            print(f"Magia: {fireball['name']} - Nível {fireball['level']}")

            # Buscar um monstro
            goblin = await service.get_monster("goblin")
            print(f"Monstro: {goblin['name']} - CR {goblin['challenge_rating']}")

    except DnD5eAPIError as e:
        print(f"Erro na API: {e}")
```

### Usando o Método Quick Request

```python
# Para requests rápidas sem gerenciar o context
strength = await DnD5eService.quick_request("get_ability_score", "str")
spells = await DnD5eService.quick_request("get_spells_by_level", 3)
```

### Exemplos de Filtros

```python
async with DnD5eService() as service:
    # Magias de nível 3
    level_3_spells = await service.get_spells_by_level(3)

    # Magias de evocação
    evocation_spells = await service.search_spells_by_school("evocation")

    # Monstros com CR 1/2
    cr_half_monsters = await service.get_monsters_by_challenge_rating("1/2")
```

## Endpoints da API

Os seguintes endpoints estão disponíveis na aplicação:

### Ability Scores

- `GET /api/v1/dnd5/ability-scores` - Lista todos os atributos
- `GET /api/v1/dnd5/ability-scores/{index}` - Busca atributo específico

### Spells

- `GET /api/v1/dnd5/spells` - Lista todas as magias
- `GET /api/v1/dnd5/spells?level={level}` - Filtra magias por nível
- `GET /api/v1/dnd5/spells?school={school}` - Filtra magias por escola
- `GET /api/v1/dnd5/spells/{index}` - Busca magia específica

### Monsters

- `GET /api/v1/dnd5/monsters` - Lista todos os monstros
- `GET /api/v1/dnd5/monsters?challenge_rating={cr}` - Filtra por CR
- `GET /api/v1/dnd5/monsters/{index}` - Busca monstro específico

## Exemplos de Índices

### Ability Scores

- `cha` - Charisma (Carisma)
- `con` - Constitution (Constituição)
- `dex` - Dexterity (Destreza)
- `int` - Intelligence (Inteligência)
- `str` - Strength (Força)
- `wis` - Wisdom (Sabedoria)

### Spells (exemplos)

- `fireball` - Bola de Fogo
- `magic-missile` - Míssil Mágico
- `cure-wounds` - Curar Ferimentos
- `shield` - Escudo

### Monsters (exemplos)

- `goblin` - Goblin
- `ancient-black-dragon` - Dragão Negro Ancião
- `owlbear` - Urso-coruja
- `troll` - Troll

## Tratamento de Erros

O serviço define uma exceção personalizada `DnD5eAPIError` que é lançada em caso de:

- Erros de conexão
- Timeouts
- Responses inválidos
- Parâmetros inválidos

```python
try:
    async with DnD5eService() as service:
        result = await service.get_ability_score("invalid")
except DnD5eAPIError as e:
    print(f"Erro: {e}")
    if e.status_code:
        print(f"Status Code: {e.status_code}")
```

## Configuração

O serviço usa as seguintes configurações padrão:

- **Base URL**: `https://www.dnd5eapi.co/api`
- **Timeout**: 30 segundos

Você pode personalizar o timeout ao instanciar o serviço:

```python
async with DnD5eService(timeout=60.0) as service:
    # Requests com timeout de 60 segundos
    pass
```

## Testes

Execute os testes do serviço com:

```bash
pytest src/tests/services/test_dnd5_service.py -v
```

## Dependências

- `requests` - Cliente HTTP
- `fastapi` - Framework web (para os endpoints)

As dependências já estão incluídas no `requirements.txt` do projeto.
