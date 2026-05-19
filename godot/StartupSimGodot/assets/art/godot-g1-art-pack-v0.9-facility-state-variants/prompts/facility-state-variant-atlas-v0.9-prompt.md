# Prompt - facility-state-variant-atlas-v0.9

Use case: stylized-concept

Asset type: transparent-ready facility state variant sprite atlas for Godot top-down office construction simulation

Primary request: Create a clean 8 columns x 3 rows sprite atlas of facility state variants for Startup Sim. Each cell is one centered top-down / slightly isometric facility sprite with clear status treatment. The atlas must be usable for slicing into equal cells.

Canvas/layout: single atlas, exactly 8 columns and 3 rows, equal cells, consistent margins, each facility centered with generous padding, no overlapping between cells. No labels, captions, letters, numbers, words, UI panels, or decorative text anywhere.

Scene/backdrop: Create all sprites on a perfectly flat solid #ff00ff chroma-key background for background removal. The background must be one uniform color with no shadows, gradients, texture, reflections, floor plane, or lighting variation. Do not use #ff00ff anywhere in the sprites.

Rows / facility types from top to bottom:
row 1 basic_desk: compact early startup office desk/workstation with chair and monitor, one-grid footprint visual
row 2 product_whiteboard: product planning whiteboard / collaboration wall on small stand, two-grid feeling, no writing or text on the board
row 3 starter_server_rack: small server rack cabinet with lights and cables, vertical infrastructure object, no symbols or letters

Columns / state variants from left to right:
1 idle: clean neutral state
2 active: subtle blue/green activity glow, monitor/light active
3 upgrading: small tool/gear sparkle and construction highlight, no text
4 blocked: red warning pulse or blocked aura, no exclamation mark if it looks like text
5 inefficient: muted gray/yellow low-efficiency haze, slightly tired but still readable
6 high_efficiency: bright clean performance glow, gold/blue success energy
7 placement_valid: translucent green placement ghost/outline, icon-like preview state
8 placement_invalid: translucent red placement ghost/outline with blocked tint, no X glyph or text

Style/medium: polished 2D stylized game art, crisp silhouettes, readable at small size, compatible with top-down office atlas art, soft antialiasing, no photorealism.

Color palette: neutral office objects with varied blue, green, gold, red status accents. Avoid dominant purple-only, beige-only, brown-only, or dark-blue-only palette.

Constraints: no readable text, no numbers, no watermark, no people, no UI cards, no cast shadows onto the background, no contact shadows, no reflections. Keep each sprite separated from the chroma-key background with crisp edges for clean alpha removal.
