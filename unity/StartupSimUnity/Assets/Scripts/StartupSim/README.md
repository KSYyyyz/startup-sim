# StartupSim Unity Components

These scripts are adapter-only components for the future Unity vertical slice.

They may:

- bind office room hotspots to prepared commands
- present a prepared action
- submit a turn through an API bridge

They must not:

- settle cash, users, product score, valuation, equity, endings, board state, or competitor state
- duplicate Python or `StartupSim.Core` TurnEngine rules; this Unity layer does not settle outcomes
- invent game facts that were not returned by the core/API

`StartupSim.Core` is the intended long-term deterministic rules layer. Unity is the presentation and input layer.
