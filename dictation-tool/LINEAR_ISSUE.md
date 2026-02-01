# Linear Issue - Create Manually or via MCP

**Workspace:** https://linear.app/z-z-z
**Team:** Z

## Issue to Create

**Title:** Dictation Tool - MVP Testing & Polish

**Description:**
Built a system-wide dictation app as a Willow/Wispr Flow alternative.

### Current State (MVP Complete)
- Menu bar app with press-to-toggle hotkey (Right Option)
- Groq Whisper API integration (fast, cheap)
- Auto-pastes to any focused text field
- Works system-wide

### Needs Testing
- [ ] User to test with Spanish-accented English
- [ ] Verify permissions flow works smoothly
- [ ] Check latency is acceptable

### Future Improvements
- [ ] Visual overlay during recording
- [ ] Language selection in menu
- [ ] Customizable hotkey via menu
- [ ] Package as standalone .app (py2app)
- [ ] Auto-start on login option
- [ ] Deepgram streaming backend

**Priority:** Medium
**Labels:** personal-tools, in-progress

---

## For Next Agent

If you have `mcp__linear-server__create_issue` available, create this issue:

```
mcp__linear-server__create_issue
  title: "Dictation Tool - MVP Testing & Polish"
  team: "Z"
  description: [above description]
  priority: 3
```
