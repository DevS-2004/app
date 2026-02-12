from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Tuple
import uuid
from datetime import datetime, timezone
import random


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Game Models
class Position(BaseModel):
    x: int
    y: int

class GameEntity(BaseModel):
    type: str  # 'wumpus', 'pit', 'bat', 'gold'
    position: Position

class GameState(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_position: Position
    entities: List[GameEntity]
    arrows_remaining: int = 3
    moves_count: int = 0
    has_gold: bool = False
    game_status: str = "active"  # active, won, lost
    score: int = 0
    visited_cells: List[List[bool]]
    sensory_info: Dict[str, bool] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GameStateResponse(BaseModel):
    game_id: str
    player_position: Position
    arrows_remaining: int
    moves_count: int
    has_gold: bool
    game_status: str
    score: int
    visited_cells: List[List[bool]]
    sensory_info: Dict[str, bool]
    message: Optional[str] = None

class MoveRequest(BaseModel):
    game_id: str
    direction: str  # 'up', 'down', 'left', 'right'

class ShootRequest(BaseModel):
    game_id: str
    direction: str

class LeaderboardEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_name: str
    score: int
    moves: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LeaderboardSubmit(BaseModel):
    player_name: str
    score: int
    moves: int


# Game Logic Helper Functions
def initialize_game() -> GameState:
    """Initialize a new game with random entity placement"""
    grid_size = 8
    
    # Initialize visited cells (only starting position is visible)
    visited = [[False for _ in range(grid_size)] for _ in range(grid_size)]
    visited[0][0] = True
    
    # Player starts at (0, 0)
    player_pos = Position(x=0, y=0)
    
    # Generate random positions for entities
    occupied_positions = [(0, 0)]  # Player start position
    entities = []
    
    def get_random_position():
        while True:
            x = random.randint(0, grid_size - 1)
            y = random.randint(0, grid_size - 1)
            if (x, y) not in occupied_positions:
                occupied_positions.append((x, y))
                return Position(x=x, y=y)
    
    # Add Wumpus (1)
    entities.append(GameEntity(type="wumpus", position=get_random_position()))
    
    # Add Pits (3)
    for _ in range(3):
        entities.append(GameEntity(type="pit", position=get_random_position()))
    
    # Add Bats (2)
    for _ in range(2):
        entities.append(GameEntity(type="bat", position=get_random_position()))
    
    # Add Gold (1)
    entities.append(GameEntity(type="gold", position=get_random_position()))
    
    game_state = GameState(
        player_position=player_pos,
        entities=entities,
        visited_cells=visited
    )
    
    # Calculate initial sensory info
    game_state.sensory_info = calculate_sensory_info(game_state)
    
    return game_state

def calculate_sensory_info(game_state: GameState) -> Dict[str, bool]:
    """Calculate what the player can sense at current position"""
    pos = game_state.player_position
    adjacent_positions = [
        (pos.x - 1, pos.y), (pos.x + 1, pos.y),
        (pos.x, pos.y - 1), (pos.x, pos.y + 1)
    ]
    
    sensory = {
        "smell_wumpus": False,
        "feel_breeze": False,
        "hear_bats": False
    }
    
    for entity in game_state.entities:
        entity_pos = (entity.position.x, entity.position.y)
        if entity_pos in adjacent_positions:
            if entity.type == "wumpus":
                sensory["smell_wumpus"] = True
            elif entity.type == "pit":
                sensory["feel_breeze"] = True
            elif entity.type == "bat":
                sensory["hear_bats"] = True
    
    return sensory

def check_position_for_entity(game_state: GameState, entity_type: str) -> Optional[GameEntity]:
    """Check if there's an entity of given type at player's position"""
    pos = game_state.player_position
    for entity in game_state.entities:
        if entity.position.x == pos.x and entity.position.y == pos.y and entity.type == entity_type:
            return entity
    return None

def calculate_score(game_state: GameState) -> int:
    """Calculate final score"""
    base_score = 1000
    score = base_score - (game_state.moves_count * 5)
    score += (game_state.arrows_remaining * 50)
    if game_state.has_gold:
        score += 500
    return max(score, 0)


# API Routes
@api_router.get("/")
async def root():
    return {"message": "Wumpus Game API"}

@api_router.post("/game/start", response_model=GameStateResponse)
async def start_game():
    """Start a new game"""
    game_state = initialize_game()
    
    # Save to database
    game_dict = game_state.model_dump()
    game_dict['created_at'] = game_dict['created_at'].isoformat()
    await db.games.insert_one(game_dict)
    
    return GameStateResponse(
        game_id=game_state.game_id,
        player_position=game_state.player_position,
        arrows_remaining=game_state.arrows_remaining,
        moves_count=game_state.moves_count,
        has_gold=game_state.has_gold,
        game_status=game_state.game_status,
        score=game_state.score,
        visited_cells=game_state.visited_cells,
        sensory_info=game_state.sensory_info,
        message="Welcome to the cave! Find the gold and escape alive."
    )

@api_router.get("/game/{game_id}", response_model=GameStateResponse)
async def get_game(game_id: str):
    """Get current game state"""
    game_dict = await db.games.find_one({"game_id": game_id}, {"_id": 0})
    if not game_dict:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Convert ISO string back to datetime
    if isinstance(game_dict['created_at'], str):
        game_dict['created_at'] = datetime.fromisoformat(game_dict['created_at'])
    
    game_state = GameState(**game_dict)
    
    return GameStateResponse(
        game_id=game_state.game_id,
        player_position=game_state.player_position,
        arrows_remaining=game_state.arrows_remaining,
        moves_count=game_state.moves_count,
        has_gold=game_state.has_gold,
        game_status=game_state.game_status,
        score=game_state.score,
        visited_cells=game_state.visited_cells,
        sensory_info=game_state.sensory_info
    )

@api_router.post("/game/move", response_model=GameStateResponse)
async def move_player(move_request: MoveRequest):
    """Move player in a direction"""
    game_dict = await db.games.find_one({"game_id": move_request.game_id}, {"_id": 0})
    if not game_dict:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if isinstance(game_dict['created_at'], str):
        game_dict['created_at'] = datetime.fromisoformat(game_dict['created_at'])
    
    game_state = GameState(**game_dict)
    
    if game_state.game_status != "active":
        raise HTTPException(status_code=400, detail="Game is not active")
    
    # Calculate new position
    new_x, new_y = game_state.player_position.x, game_state.player_position.y
    
    if move_request.direction == "up":
        new_y -= 1
    elif move_request.direction == "down":
        new_y += 1
    elif move_request.direction == "left":
        new_x -= 1
    elif move_request.direction == "right":
        new_x += 1
    else:
        raise HTTPException(status_code=400, detail="Invalid direction")
    
    # Check boundaries
    if new_x < 0 or new_x >= 8 or new_y < 0 or new_y >= 8:
        return GameStateResponse(
            game_id=game_state.game_id,
            player_position=game_state.player_position,
            arrows_remaining=game_state.arrows_remaining,
            moves_count=game_state.moves_count,
            has_gold=game_state.has_gold,
            game_status=game_state.game_status,
            score=game_state.score,
            visited_cells=game_state.visited_cells,
            sensory_info=game_state.sensory_info,
            message="You can't go that way!"
        )
    
    # Update position
    game_state.player_position.x = new_x
    game_state.player_position.y = new_y
    game_state.moves_count += 1
    game_state.visited_cells[new_y][new_x] = True
    
    message = None
    
    # Check for Wumpus
    if check_position_for_entity(game_state, "wumpus"):
        game_state.game_status = "lost"
        game_state.score = calculate_score(game_state)
        message = "You were eaten by the Wumpus! Game Over."
    
    # Check for Pit
    elif check_position_for_entity(game_state, "pit"):
        game_state.game_status = "lost"
        game_state.score = calculate_score(game_state)
        message = "You fell into a pit! Game Over."
    
    # Check for Bat
    elif bat_entity := check_position_for_entity(game_state, "bat"):
        # Teleport to random position
        new_x = random.randint(0, 7)
        new_y = random.randint(0, 7)
        game_state.player_position.x = new_x
        game_state.player_position.y = new_y
        game_state.visited_cells[new_y][new_x] = True
        message = "A bat carried you to another location!"
    
    # Check for Gold
    elif gold_entity := check_position_for_entity(game_state, "gold"):
        if not game_state.has_gold:
            game_state.has_gold = True
            message = "You found the gold! Return to start (0,0) to win!"
    
    # Check win condition (has gold and at start)
    if game_state.has_gold and game_state.player_position.x == 0 and game_state.player_position.y == 0:
        game_state.game_status = "won"
        game_state.score = calculate_score(game_state)
        message = "You escaped with the gold! Victory!"
    
    # Update sensory info
    game_state.sensory_info = calculate_sensory_info(game_state)
    
    # Save updated game state
    game_dict = game_state.model_dump()
    game_dict['created_at'] = game_dict['created_at'].isoformat()
    await db.games.update_one(
        {"game_id": move_request.game_id},
        {"$set": game_dict}
    )
    
    return GameStateResponse(
        game_id=game_state.game_id,
        player_position=game_state.player_position,
        arrows_remaining=game_state.arrows_remaining,
        moves_count=game_state.moves_count,
        has_gold=game_state.has_gold,
        game_status=game_state.game_status,
        score=game_state.score,
        visited_cells=game_state.visited_cells,
        sensory_info=game_state.sensory_info,
        message=message
    )

@api_router.post("/game/shoot", response_model=GameStateResponse)
async def shoot_arrow(shoot_request: ShootRequest):
    """Shoot an arrow in a direction"""
    game_dict = await db.games.find_one({"game_id": shoot_request.game_id}, {"_id": 0})
    if not game_dict:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if isinstance(game_dict['created_at'], str):
        game_dict['created_at'] = datetime.fromisoformat(game_dict['created_at'])
    
    game_state = GameState(**game_dict)
    
    if game_state.game_status != "active":
        raise HTTPException(status_code=400, detail="Game is not active")
    
    if game_state.arrows_remaining <= 0:
        return GameStateResponse(
            game_id=game_state.game_id,
            player_position=game_state.player_position,
            arrows_remaining=game_state.arrows_remaining,
            moves_count=game_state.moves_count,
            has_gold=game_state.has_gold,
            game_status=game_state.game_status,
            score=game_state.score,
            visited_cells=game_state.visited_cells,
            sensory_info=game_state.sensory_info,
            message="No arrows left!"
        )
    
    game_state.arrows_remaining -= 1
    message = "You shot an arrow... but missed!"
    
    # Check if wumpus is in the direction
    wumpus_entity = None
    for entity in game_state.entities:
        if entity.type == "wumpus":
            wumpus_entity = entity
            break
    
    if wumpus_entity:
        player_pos = game_state.player_position
        wumpus_pos = wumpus_entity.position
        
        hit = False
        if shoot_request.direction == "up" and wumpus_pos.x == player_pos.x and wumpus_pos.y < player_pos.y:
            hit = True
        elif shoot_request.direction == "down" and wumpus_pos.x == player_pos.x and wumpus_pos.y > player_pos.y:
            hit = True
        elif shoot_request.direction == "left" and wumpus_pos.y == player_pos.y and wumpus_pos.x < player_pos.x:
            hit = True
        elif shoot_request.direction == "right" and wumpus_pos.y == player_pos.y and wumpus_pos.x > player_pos.x:
            hit = True
        
        if hit:
            game_state.entities = [e for e in game_state.entities if e.type != "wumpus"]
            game_state.game_status = "won"
            game_state.score = calculate_score(game_state)
            message = "You killed the Wumpus! Victory!"
    
    # Update sensory info
    game_state.sensory_info = calculate_sensory_info(game_state)
    
    # Save updated game state
    game_dict = game_state.model_dump()
    game_dict['created_at'] = game_dict['created_at'].isoformat()
    await db.games.update_one(
        {"game_id": shoot_request.game_id},
        {"$set": game_dict}
    )
    
    return GameStateResponse(
        game_id=game_state.game_id,
        player_position=game_state.player_position,
        arrows_remaining=game_state.arrows_remaining,
        moves_count=game_state.moves_count,
        has_gold=game_state.has_gold,
        game_status=game_state.game_status,
        score=game_state.score,
        visited_cells=game_state.visited_cells,
        sensory_info=game_state.sensory_info,
        message=message
    )

@api_router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard():
    """Get top 10 leaderboard entries"""
    entries = await db.leaderboard.find({}, {"_id": 0}).sort("score", -1).limit(10).to_list(10)
    
    for entry in entries:
        if isinstance(entry['timestamp'], str):
            entry['timestamp'] = datetime.fromisoformat(entry['timestamp'])
    
    return entries

@api_router.post("/leaderboard", response_model=LeaderboardEntry)
async def submit_leaderboard(entry: LeaderboardSubmit):
    """Submit a score to leaderboard"""
    leaderboard_entry = LeaderboardEntry(
        player_name=entry.player_name,
        score=entry.score,
        moves=entry.moves
    )
    
    entry_dict = leaderboard_entry.model_dump()
    entry_dict['timestamp'] = entry_dict['timestamp'].isoformat()
    await db.leaderboard.insert_one(entry_dict)
    
    return leaderboard_entry


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
