import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { User, ArrowUp, Coins, Skull, AlertTriangle, Ghost, Wind, Crosshair, Trophy, HelpCircle, Play } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [gameState, setGameState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showTutorial, setShowTutorial] = useState(false);
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [showGameOver, setShowGameOver] = useState(false);
  const [leaderboard, setLeaderboard] = useState([]);
  const [playerName, setPlayerName] = useState("");

  // Start new game
  const startGame = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/game/start`);
      setGameState(response.data);
      setShowGameOver(false);
      if (response.data.message) {
        toast.success(response.data.message);
      }
    } catch (error) {
      console.error("Error starting game:", error);
      toast.error("Failed to start game");
    } finally {
      setLoading(false);
    }
  };

  // Move player
  const movePlayer = useCallback(async (direction) => {
    if (!gameState || gameState.game_status !== "active" || loading) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API}/game/move`, {
        game_id: gameState.game_id,
        direction
      });
      setGameState(response.data);
      
      if (response.data.message) {
        if (response.data.game_status === "won") {
          toast.success(response.data.message);
          setShowGameOver(true);
        } else if (response.data.game_status === "lost") {
          toast.error(response.data.message);
          setShowGameOver(true);
        } else {
          toast.info(response.data.message);
        }
      }
    } catch (error) {
      console.error("Error moving:", error);
      toast.error("Failed to move");
    } finally {
      setLoading(false);
    }
  }, [gameState, loading]);

  // Shoot arrow
  const shootArrow = async (direction) => {
    if (!gameState || gameState.game_status !== "active" || loading) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API}/game/shoot`, {
        game_id: gameState.game_id,
        direction
      });
      setGameState(response.data);
      
      if (response.data.message) {
        if (response.data.game_status === "won") {
          toast.success(response.data.message);
          setShowGameOver(true);
        } else {
          toast.info(response.data.message);
        }
      }
    } catch (error) {
      console.error("Error shooting:", error);
      toast.error("Failed to shoot");
    } finally {
      setLoading(false);
    }
  };

  // Keyboard controls
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (!gameState || gameState.game_status !== "active") return;
      
      const key = e.key.toLowerCase();
      if (key === 'w') movePlayer('up');
      else if (key === 's') movePlayer('down');
      else if (key === 'a') movePlayer('left');
      else if (key === 'd') movePlayer('right');
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [gameState, movePlayer]);

  // Fetch leaderboard
  const fetchLeaderboard = async () => {
    try {
      const response = await axios.get(`${API}/leaderboard`);
      setLeaderboard(response.data);
    } catch (error) {
      console.error("Error fetching leaderboard:", error);
    }
  };

  // Submit score
  const submitScore = async () => {
    if (!playerName.trim()) {
      toast.error("Please enter your name");
      return;
    }

    try {
      await axios.post(`${API}/leaderboard`, {
        player_name: playerName,
        score: gameState.score,
        moves: gameState.moves_count
      });
      toast.success("Score submitted!");
      setShowGameOver(false);
      setPlayerName("");
      fetchLeaderboard();
      setShowLeaderboard(true);
    } catch (error) {
      console.error("Error submitting score:", error);
      toast.error("Failed to submit score");
    }
  };

  // Render grid cell
  const renderCell = (x, y) => {
    if (!gameState) return null;

    const isVisited = gameState.visited_cells[y][x];
    const isPlayer = gameState.player_position.x === x && gameState.player_position.y === y;
    const isStart = x === 0 && y === 0;

    let cellClass = "grid-cell aspect-square border border-white/5 flex items-center justify-center text-3xl relative ";
    
    if (!isVisited) {
      cellClass += "bg-black/80";
    } else if (isPlayer) {
      cellClass += "bg-white/10 ring-1 ring-white/20";
    } else {
      cellClass += "bg-white/5";
    }

    return (
      <div key={`${x}-${y}`} className={cellClass} data-testid={`cell-${x}-${y}`}>
        {isPlayer && <User className="text-white glow-player" data-testid="player-icon" />}
        {isStart && !isPlayer && isVisited && (
          <div className="text-green-400 text-sm font-mono">START</div>
        )}
      </div>
    );
  };

  // Landing page
  if (!gameState) {
    return (
      <div className="min-h-screen cave-background flex items-center justify-center p-4">
        <Toaster position="top-center" richColors />
        <Card className="bg-card/50 backdrop-blur-xl border border-white/10 p-8 md:p-12 max-w-2xl w-full text-center">
          <h1 className="font-heading text-5xl md:text-7xl font-black tracking-tighter text-primary mb-4" data-testid="game-title">
            WUMPUS CAVE
          </h1>
          <p className="font-heading text-xl md:text-2xl text-muted-foreground mb-8">Echoes of the Deep</p>
          <p className="font-body text-base text-muted-foreground leading-relaxed mb-8">
            Navigate the treacherous cave, find the gold, and escape alive. Beware of the deadly Wumpus, bottomless pits, and mysterious bats.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              onClick={startGame}
              disabled={loading}
              className="game-button bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_15px_rgba(225,29,72,0.3)] font-heading tracking-widest uppercase px-8 py-6 text-lg"
              data-testid="start-game-button"
            >
              <Play className="mr-2" /> {loading ? "Starting..." : "Start Game"}
            </Button>
            <Button
              onClick={() => setShowTutorial(true)}
              variant="outline"
              className="game-button bg-secondary/20 text-secondary-foreground hover:bg-secondary/30 border border-secondary/50 backdrop-blur-md font-heading tracking-widest uppercase px-8 py-6 text-lg"
              data-testid="tutorial-button"
            >
              <HelpCircle className="mr-2" /> Tutorial
            </Button>
            <Button
              onClick={() => {
                fetchLeaderboard();
                setShowLeaderboard(true);
              }}
              variant="outline"
              className="game-button bg-secondary/20 text-secondary-foreground hover:bg-secondary/30 border border-secondary/50 backdrop-blur-md font-heading tracking-widest uppercase px-8 py-6 text-lg"
              data-testid="leaderboard-button"
            >
              <Trophy className="mr-2" /> Leaderboard
            </Button>
          </div>
        </Card>

        {/* Tutorial Dialog */}
        <Dialog open={showTutorial} onOpenChange={setShowTutorial}>
          <DialogContent className="bg-card border-border max-w-2xl" data-testid="tutorial-dialog">
            <DialogHeader>
              <DialogTitle className="font-heading text-3xl text-primary">How to Play</DialogTitle>
              <DialogDescription className="sr-only">Game instructions and tutorial</DialogDescription>
            </DialogHeader>
            <div className="font-body text-muted-foreground space-y-4">
              <div>
                <h3 className="font-heading text-xl text-foreground mb-2">Objective</h3>
                <p>Find the gold and return to the start (0,0) to win. Or kill the Wumpus with your arrows!</p>
              </div>
              <div>
                <h3 className="font-heading text-xl text-foreground mb-2">Controls</h3>
                <p><strong>W/A/S/D</strong> - Move Up/Left/Down/Right</p>
                <p><strong>Arrow Buttons</strong> - Shoot in direction</p>
              </div>
              <div>
                <h3 className="font-heading text-xl text-foreground mb-2">Hazards</h3>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2"><Skull className="text-red-500" /> <strong>Wumpus:</strong> Deadly creature. You'll smell it nearby.</li>
                  <li className="flex items-center gap-2"><AlertTriangle className="text-cyan-500" /> <strong>Pits:</strong> Fall in and die. You'll feel a breeze nearby.</li>
                  <li className="flex items-center gap-2"><Ghost className="text-purple-500" /> <strong>Bats:</strong> Teleport you randomly. You'll hear them nearby.</li>
                </ul>
              </div>
              <div>
                <h3 className="font-heading text-xl text-foreground mb-2">Tips</h3>
                <p>• You have 3 arrows. Use them wisely!</p>
                <p>• Listen to sensory clues to avoid hazards.</p>
                <p>• Plan your route carefully.</p>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Leaderboard Dialog */}
        <Dialog open={showLeaderboard} onOpenChange={setShowLeaderboard}>
          <DialogContent className="bg-card border-border max-w-2xl" data-testid="leaderboard-dialog">
            <DialogHeader>
              <DialogTitle className="font-heading text-3xl text-primary">Leaderboard</DialogTitle>
              <DialogDescription className="sr-only">Top player scores and rankings</DialogDescription>
            </DialogHeader>
            <div className="font-body">
              {leaderboard.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">No scores yet. Be the first!</p>
              ) : (
                <div className="space-y-2">
                  {leaderboard.map((entry, index) => (
                    <div
                      key={entry.entry_id}
                      className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10"
                      data-testid={`leaderboard-entry-${index}`}
                    >
                      <div className="flex items-center gap-4">
                        <span className="font-heading text-2xl text-primary font-bold w-8">#{index + 1}</span>
                        <span className="font-body text-foreground">{entry.player_name}</span>
                      </div>
                      <div className="flex items-center gap-6">
                        <span className="font-mono text-sm text-muted-foreground">{entry.moves} moves</span>
                        <span className="font-mono text-lg text-accent font-bold">{entry.score} pts</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>
    );
  }

  // Game board
  return (
    <div className="min-h-screen cave-background p-4 md:p-8">
      <Toaster position="top-center" richColors />
      
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Game Board */}
          <div className="lg:col-span-8">
            <Card className="bg-card/50 backdrop-blur-xl border border-white/10 p-4 md:p-6">
              <div className="aspect-square w-full" data-testid="game-board">
                <div className="grid grid-cols-8 gap-1 h-full">
                  {Array.from({ length: 8 }, (_, y) =>
                    Array.from({ length: 8 }, (_, x) => renderCell(x, y))
                  )}
                </div>
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-4 space-y-6">
            {/* Stats */}
            <Card className="bg-card/50 backdrop-blur-xl border border-white/10 p-6" data-testid="stats-panel">
              <h2 className="font-heading text-2xl font-bold text-foreground mb-4">Stats</h2>
              <div className="space-y-3 font-mono text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">ARROWS</span>
                  <span className="text-accent font-bold text-lg" data-testid="arrows-count">{gameState.arrows_remaining}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">MOVES</span>
                  <span className="text-foreground font-bold text-lg" data-testid="moves-count">{gameState.moves_count}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">SCORE</span>
                  <span className="text-primary font-bold text-lg" data-testid="score-count">{gameState.score}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">GOLD</span>
                  <span className="text-yellow-400 font-bold text-lg" data-testid="gold-status">
                    {gameState.has_gold ? "✓" : "✗"}
                  </span>
                </div>
              </div>
            </Card>

            {/* Sensory Info */}
            <Card className="bg-card/50 backdrop-blur-xl border border-white/10 p-6" data-testid="sensory-panel">
              <h2 className="font-heading text-2xl font-bold text-foreground mb-4">Senses</h2>
              <div className="space-y-3">
                {gameState.sensory_info.smell_wumpus && (
                  <div className="flex items-center gap-3 text-red-500 animate-pulse-glow" data-testid="smell-warning">
                    <Skull className="glow-wumpus" />
                    <span className="font-body">You smell the Wumpus nearby!</span>
                  </div>
                )}
                {gameState.sensory_info.feel_breeze && (
                  <div className="flex items-center gap-3 text-cyan-500 animate-pulse-glow" data-testid="breeze-warning">
                    <Wind className="glow-pit" />
                    <span className="font-body">You feel a breeze...</span>
                  </div>
                )}
                {gameState.sensory_info.hear_bats && (
                  <div className="flex items-center gap-3 text-purple-500 animate-pulse-glow" data-testid="bats-warning">
                    <Ghost className="glow-bat" />
                    <span className="font-body">You hear bats nearby...</span>
                  </div>
                )}
                {!gameState.sensory_info.smell_wumpus && !gameState.sensory_info.feel_breeze && !gameState.sensory_info.hear_bats && (
                  <p className="text-muted-foreground font-body">All is quiet...</p>
                )}
              </div>
            </Card>

            {/* Movement Controls */}
            <Card className="bg-card/50 backdrop-blur-xl border border-white/10 p-6" data-testid="controls-panel">
              <h2 className="font-heading text-2xl font-bold text-foreground mb-4">Move (WASD)</h2>
              <div className="grid grid-cols-3 gap-2">
                <div></div>
                <Button
                  onClick={() => movePlayer('up')}
                  disabled={loading || gameState.game_status !== 'active'}
                  className="game-button bg-white/10 hover:bg-white/20"
                  data-testid="move-up-button"
                >
                  <ArrowUp />
                </Button>
                <div></div>
                <Button
                  onClick={() => movePlayer('left')}
                  disabled={loading || gameState.game_status !== 'active'}
                  className="game-button bg-white/10 hover:bg-white/20"
                  data-testid="move-left-button"
                >
                  <ArrowUp className="rotate-[-90deg]" />
                </Button>
                <Button
                  onClick={() => movePlayer('down')}
                  disabled={loading || gameState.game_status !== 'active'}
                  className="game-button bg-white/10 hover:bg-white/20"
                  data-testid="move-down-button"
                >
                  <ArrowUp className="rotate-180" />
                </Button>
                <Button
                  onClick={() => movePlayer('right')}
                  disabled={loading || gameState.game_status !== 'active'}
                  className="game-button bg-white/10 hover:bg-white/20"
                  data-testid="move-right-button"
                >
                  <ArrowUp className="rotate-90" />
                </Button>
              </div>
            </Card>

            {/* Shoot Controls */}
            <Card className="bg-card/50 backdrop-blur-xl border border-white/10 p-6" data-testid="shoot-panel">
              <h2 className="font-heading text-2xl font-bold text-foreground mb-4">Shoot Arrow</h2>
              <div className="grid grid-cols-3 gap-2">
                <div></div>
                <Button
                  onClick={() => shootArrow('up')}
                  disabled={loading || gameState.game_status !== 'active' || gameState.arrows_remaining === 0}
                  className="game-button bg-primary/20 hover:bg-primary/30 border border-primary/50"
                  data-testid="shoot-up-button"
                >
                  <Crosshair />
                </Button>
                <div></div>
                <Button
                  onClick={() => shootArrow('left')}
                  disabled={loading || gameState.game_status !== 'active' || gameState.arrows_remaining === 0}
                  className="game-button bg-primary/20 hover:bg-primary/30 border border-primary/50"
                  data-testid="shoot-left-button"
                >
                  <Crosshair />
                </Button>
                <Button
                  onClick={() => shootArrow('down')}
                  disabled={loading || gameState.game_status !== 'active' || gameState.arrows_remaining === 0}
                  className="game-button bg-primary/20 hover:bg-primary/30 border border-primary/50"
                  data-testid="shoot-down-button"
                >
                  <Crosshair />
                </Button>
                <Button
                  onClick={() => shootArrow('right')}
                  disabled={loading || gameState.game_status !== 'active' || gameState.arrows_remaining === 0}
                  className="game-button bg-primary/20 hover:bg-primary/30 border border-primary/50"
                  data-testid="shoot-right-button"
                >
                  <Crosshair />
                </Button>
              </div>
            </Card>

            {/* Action Buttons */}
            <div className="flex flex-col gap-3">
              <Button
                onClick={startGame}
                className="game-button bg-secondary/20 hover:bg-secondary/30 border border-secondary/50 font-heading tracking-widest uppercase"
                data-testid="new-game-button"
              >
                New Game
              </Button>
              <Button
                onClick={() => setShowTutorial(true)}
                variant="outline"
                className="game-button font-heading tracking-widest uppercase"
                data-testid="help-button"
              >
                <HelpCircle className="mr-2" /> Help
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Game Over Dialog */}
      <Dialog open={showGameOver} onOpenChange={setShowGameOver}>
        <DialogContent className="bg-card border-border" data-testid="game-over-dialog">
          <DialogHeader>
            <DialogTitle className="font-heading text-4xl text-center mb-4">
              {gameState?.game_status === 'won' ? (
                <span className="text-green-400">Victory!</span>
              ) : (
                <span className="text-red-400">Game Over</span>
              )}
            </DialogTitle>
            <DialogDescription className="text-center space-y-4">
              <div className="font-mono text-2xl text-accent font-bold" data-testid="final-score">
                Score: {gameState?.score}
              </div>
              <div className="font-body text-muted-foreground">
                Moves: {gameState?.moves_count} | Arrows Left: {gameState?.arrows_remaining}
              </div>
              <div className="space-y-3 pt-4">
                <Input
                  placeholder="Enter your name"
                  value={playerName}
                  onChange={(e) => setPlayerName(e.target.value)}
                  className="bg-white/5 border-white/10"
                  data-testid="player-name-input"
                />
                <Button
                  onClick={submitScore}
                  className="w-full game-button bg-primary text-primary-foreground hover:bg-primary/90 font-heading tracking-widest uppercase"
                  data-testid="submit-score-button"
                >
                  Submit to Leaderboard
                </Button>
                <Button
                  onClick={() => {
                    setShowGameOver(false);
                    startGame();
                  }}
                  variant="outline"
                  className="w-full game-button font-heading tracking-widest uppercase"
                  data-testid="play-again-button"
                >
                  Play Again
                </Button>
              </div>
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>

      {/* Tutorial Dialog */}
      <Dialog open={showTutorial} onOpenChange={setShowTutorial}>
        <DialogContent className="bg-card border-border max-w-2xl" data-testid="tutorial-dialog-ingame">
          <DialogHeader>
            <DialogTitle className="font-heading text-3xl text-primary">How to Play</DialogTitle>
            <DialogDescription className="sr-only">Game instructions and tutorial</DialogDescription>
          </DialogHeader>
          <div className="font-body text-muted-foreground space-y-4">
            <div>
              <h3 className="font-heading text-xl text-foreground mb-2">Objective</h3>
              <p>Find the gold and return to the start (0,0) to win. Or kill the Wumpus with your arrows!</p>
            </div>
            <div>
              <h3 className="font-heading text-xl text-foreground mb-2">Controls</h3>
              <p><strong>W/A/S/D</strong> - Move Up/Left/Down/Right</p>
              <p><strong>Arrow Buttons</strong> - Shoot in direction</p>
            </div>
            <div>
              <h3 className="font-heading text-xl text-foreground mb-2">Hazards</h3>
              <ul className="space-y-2">
                <li className="flex items-center gap-2"><Skull className="text-red-500" /> <strong>Wumpus:</strong> Deadly creature. You'll smell it nearby.</li>
                <li className="flex items-center gap-2"><AlertTriangle className="text-cyan-500" /> <strong>Pits:</strong> Fall in and die. You'll feel a breeze nearby.</li>
                <li className="flex items-center gap-2"><Ghost className="text-purple-500" /> <strong>Bats:</strong> Teleport you randomly. You'll hear them nearby.</li>
              </ul>
            </div>
            <div>
              <h3 className="font-heading text-xl text-foreground mb-2">Tips</h3>
              <p>• You have 3 arrows. Use them wisely!</p>
              <p>• Listen to sensory clues to avoid hazards.</p>
              <p>• Plan your route carefully.</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default App;
