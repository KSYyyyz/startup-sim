# employee-motion-atlas-v0.2 Prompt

Use case: stylized-concept
Asset type: 2D top-down management game sprite atlas for Startup Sim employee motion

Primary request: Create a clean game-ready sprite sheet on a perfectly flat solid #00ff00 chroma-key background for background removal. The subject is 8 distinct SaaS office employees for a top-down / slight isometric office construction simulation game.

Scene/backdrop: perfectly flat #00ff00 background only, no shadows, no texture, no gradients, no floor plane.

Subject: 8 visibly different employee characters arranged as rows. Each row is one consistent character identity across 12 cells: front walk frame A, front walk frame B, back walk frame A, back walk frame B, left walk frame A, left walk frame B, right walk frame A, right walk frame B, idle, working-at-laptop/desk, tired/slumped, resting/coffee-break. Characters must differ clearly in age, face shape, hairstyle, clothing, accessories, expression, body shape, and color accents. Include roles such as young developer with hoodie, senior architect with glasses, energetic sales lead, operations coordinator, server engineer, HR recruiter, calm manager, finance/strategy analyst.

Style/medium: polished 2D indie management-game art with light pixel-art influence, readable at small sizes, crisp silhouettes, clean edges, no outlines bleeding into background.

Composition/framing: strict 12 columns x 8 rows sprite sheet, evenly spaced cells, each character centered in its cell with generous padding, full body small office worker sprites, top-down/slight isometric camera, no cropping. Use consistent scale across all cells.

Lighting/mood: neutral bright game asset lighting.

Color palette: varied clothing and accessories, avoid using #00ff00 anywhere in characters.

Text: none.

Constraints: background must be one uniform #00ff00 chroma key; no cast shadows, no contact shadows, no reflections, no text, no watermark. Do not make all faces similar. Do not make all characters face right. Maintain each character identity across the whole row.

## Production Notes

The generated sheet was reorganized into a stricter Godot-facing atlas:

- Final export uses the six rows with the most stable identity continuity.
- Final export is `12 columns x 6 rows`.
- Cell size is `192 x 192`.
- The generated pass missed one side-walk frame consistently, so column `right_walk_b` duplicates `right_walk_a` as a v0.2 placeholder.
- The raw generated source is preserved as `sources/employee-motion-atlas-v0.2-raw-generated.png`.
