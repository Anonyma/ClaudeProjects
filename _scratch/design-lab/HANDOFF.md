# Design Lab Handoff - Tab Memory Dashboard

## Status: IN PROGRESS - Awaiting Refinement

## What We're Designing
Redesigning the Comet Tab Memory Dashboard (`/Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch/comet-tab-dashboard.html`)

## User Requirements (from interview)

### Goal
- **Primary action**: Identify tabs to close quickly

### Pain Points with Original
- Looks generic/boring
- Wants it pleasant, modern, with personality
- Must still contain all the info needed

### Style Direction
- **Rich & Immersive** (gradients, depth, glass effects)
- **Live updates** (auto-refresh)
- **Some data visualization** (not crazy)
- **"Sand dissolving in the air"** particle effect - signifying resources being freed when tabs close
- **LIGHT color scheme** (user explicitly requested this - NOT dark mode)

## Variants Created

All variants at: `http://localhost:8877/design-lab/` (server may need restart: `cd /Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch && python3 -m http.server 8877 &`)

| File | Style | Notes |
|------|-------|-------|
| `variant-1-gradient-flow.html` | Glassmorphism, sidebar | User liked the **sidebar categories** |
| `variant-2-neon-glow.html` | Dark + neon pink/cyan | **USER'S FAVORITE** - preferred overall vibe |
| `variant-3-bento.html` | Apple-style bento grid | - |
| `variant-4-radial.html` | Circular progress rings | User liked the **radial chart** |
| `variant-5-command-center.html` | HUD/terminal aesthetic | - |
| `variant-refined.html` | Light mode attempt | User said it looks "ugly and generic, very cheap" |

## What User Wants in Final Design

Combine these elements:
1. **Neon Glow's overall vibe** (the color palette, glow effects, visual style) - BUT adapted to LIGHT mode
2. **Sidebar categories** from Gradient Flow (with progress bars)
3. **Radial circular chart** from variant 4
4. **Sand dissolving particle effect** when closing tabs (particles drift away like sand, signifying freed memory)
5. **Light color scheme** - NOT dark mode

## Key Insight
The user found the light mode attempt (variant-refined.html) too generic. The challenge is to bring Neon Glow's vibrant, punchy aesthetic into a light color scheme without making it feel cheap or generic.

Consider:
- Vibrant accent colors on light backgrounds
- Neon-style glows that work on light (colored shadows, vibrant borders)
- Glass/frosted effects on light backgrounds
- Bold typography and strong visual hierarchy
- The particle dissolve effect should feel magical/satisfying

## Files to Reference

- Original dashboard: `/Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch/comet-tab-dashboard.html`
- Neon Glow (favorite): `/Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch/design-lab/variant-2-neon-glow.html`
- Radial chart reference: `/Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch/design-lab/variant-4-radial.html`
- Sidebar reference: `/Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch/design-lab/variant-1-gradient-flow.html`

## Next Steps for Future Agent

1. Study `variant-2-neon-glow.html` - understand what makes it feel premium/vibrant
2. Create a new refined variant that:
   - Uses a LIGHT background
   - Keeps Neon Glow's vibrant, punchy feel (adapt the colors/glows for light mode)
   - Includes sidebar categories with progress bars
   - Includes radial chart visualization
   - Implements the sand dissolving particle effect on tab close
3. Show user and iterate based on feedback
4. When approved, clean up design-lab folder and create final implementation

## Command to Resume

```
Continue the Design Lab session for the Tab Memory Dashboard. Read the handoff at /Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch/design-lab/HANDOFF.md for context.
```
