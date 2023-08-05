# Generator for Calcudoku puzzles in Python

## Installation
Installation requires `numpy` and `matplotlib` with `Python>=3.5` 
```
pip install calcudoku
```

## Example


```python
from calcudoku.game import Calcudoku
from calcudoku.visualize import save_figure

game = Calcudoku.generate(6)

save_figure(game, 'puzzle.png', solution=False)
save_figure(game, 'puzzle_solution.png', solution=True)
```
### Puzzle
![](readme_examples/puzzle.png)

### Solution
![](readme_examples/puzzle_solution.png)

## TODO
Continue adding/fine tuning of various options to control the 
difficulty/originality of the puzzle generation.

Perhaps modify the code to allow for some variants to be generated as well