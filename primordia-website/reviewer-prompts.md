# AI Reviewer Prompts for Visual Comparison

## Prompt for Claude (Anthropic API)

You are a precise visual design reviewer. Compare these two images pixel-by-pixel:

**Reference (Figma design):** `/Users/z/Desktop/PersonalProjects/ClaudeProjects/primordia-website/tests/og-figma-main.jpg`

**Current implementation:** `/Users/z/Desktop/PersonalProjects/ClaudeProjects/primordia-website/tests/current-home.png`

Focus on these specific areas and provide exact measurements:

1. **Hero Section (top)** - Are the "Apply" and "Fund Experiments" buttons positioned to fill the width under the "Funding Early Biology..." subtitle? Or are they grouped together to the right? Describe exact positioning.

2. **How it Works Section** - For each of the 5 step cards:
   - Are the icons positioned HALF IN / HALF OUT of the green rounded background boxes (top 20% overlapping)?
   - Is the descriptive text positioned INSIDE the green boxes below the icons?
   - Provide exact positioning for icons and text.

3. **Definition Section ("In biology...")** - Is the white text box positioned in the UPPER LEFT of the blue blob background? Or is it centered? Provide exact coordinates.

4. **FAQ Section** - Does the purple/blue gradient background fully contain ALL 7 FAQ items? Can you see the last FAQ row clearly within the purple background, or does it extend outside?

5. **Fund Page** - Are there any text overlaps in the "For Donors & Partners" section?

Provide specific measurements and coordinates for each issue found.

---

## Prompt for GPT-4 Vision (OpenAI API)

Analyze these two web design screenshots for pixel-perfect accuracy:

- **Target design:** `og-figma-main.jpg`
- **Current build:** `current-home.png`

Report ALL discrepancies in:

1. **Button positioning in hero section** - Measure horizontal spread and centering under subtitle
2. **Icon placement in "How it Works"** - Are icons half-overlapping the green card backgrounds?
3. **Text positioning in step cards** - Is text inside or outside green backgrounds?
4. **Definition section layout** - Upper-left vs centered positioning of white box on blue blob
5. **FAQ background coverage** - Does purple background extend to bottom FAQ item?
6. **Expanded FAQ state** - Does expanded content stay within purple boundary?

Be extremely specific with pixel measurements and positioning.

---

## Prompt for Gemini Vision (Google API)

You are a detail-oriented QA engineer comparing a Figma design to its implementation.

**Files to compare:**
- Design: `tests/og-figma-main.jpg`
- Implementation: `tests/current-home.png`

**Critical areas to check:**

### Hero Buttons
- In the reference, do the buttons span the full width under the subtitle text?
- In the implementation, are they clustered to one side?
- Exact width and positioning differences?

### How it Works Cards
- Icon positioning: Should be 50% inside green box, 50% outside (top portion overlapping)
- Text positioning: Should be fully inside green boxes
- Current implementation: Where are icons and text actually positioned?

### Primordium Definition
- Reference: Is white box in upper-left quadrant of blue blob?
- Implementation: Is it centered or upper-left?
- Exact coordinate differences?

### FAQ Section
- Reference: All FAQ items within purple background?
- Implementation: Does purple background height contain all items when collapsed AND expanded?
- Last item visibility: Fully inside purple area?

### Fund Page Issues
- Any text overlapping in donor section header?
- FAQ background coverage issues similar to home page?

Provide a numbered list of ALL issues with exact measurements.

---

## How to Use These Prompts

### For Claude (via API):
```bash
# Using anthropic CLI or curl
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4096,
    "messages": [{
      "role": "user",
      "content": [
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "<base64_encoded_og_image>"
          }
        },
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": "<base64_encoded_current_image>"
          }
        },
        {
          "type": "text",
          "text": "<paste Claude prompt from above>"
        }
      ]
    }]
  }'
```

### For GPT-4 Vision:
```bash
# Using openai CLI
openai api chat.completions.create \
  -m gpt-4-vision-preview \
  --messages '[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "<paste GPT-4 prompt>"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,<og_image_base64>"}},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,<current_image_base64>"}}
      ]
    }
  ]'
```

### For Gemini Vision:
```bash
# Using google-generativeai Python library
python3 << 'EOF'
import google.generativeai as genai
import base64

genai.configure(api_key='YOUR_API_KEY')
model = genai.GenerativeModel('gemini-1.5-pro')

with open('tests/og-figma-main.jpg', 'rb') as f:
    og_image = base64.b64encode(f.read()).decode()

with open('tests/current-home.png', 'rb') as f:
    current_image = base64.b64encode(f.read()).decode()

prompt = """<paste Gemini prompt from above>"""

response = model.generate_content([
    prompt,
    {'mime_type': 'image/jpeg', 'data': og_image},
    {'mime_type': 'image/png', 'data': current_image}
])

print(response.text)
EOF
```
