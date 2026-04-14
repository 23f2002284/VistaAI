# logics/prompts.py
IMAGE_EDIT_PROMPT_GENERATION_PROMPT = """Analyze the room in the given image. DO NOT invent new architecture (walls, floors). Select a style that fits the existing room. Write a staging prompt describing the furniture to ADD.
Critical Rule: PRESERVE existing architecture — walls, floors, windows must stay exactly as they are. Only describe placing furniture.
Output Format: JSON:
{
  "room_type": "Living Room",
  "visual_style": "Modern Minimalist",
  "description": "...",
  "staging_prompt": "Furnish this room in a Modern Coastal style. Keep existing walls..."
}"""

TRANSFORMED_IMAGE_GENERATION_PROMPT = """{PROMPT_FROM_PREVIOUS_STEP}"""

VIDEO_TRANSITION_PROMPT = """Each piece of furniture pops up, rotates and falls into places one by one. The camera has super smooth forward motion. Cinematic, 2k, photorealistic, interior design."""

VIDEO_GENERATION_REINOVATION_PROMPT = """The room transforms and renovates itself piece by piece. Individual elements and furniture pop up, rotate, and fall into place one by one to complete the design. There is super smooth background camera motion. Cinematic, 2k, photorealistic, interior design."""

SCRIPT_AUDIO_PROMPT = """Given the property description, user preference, and basic run notes, create a scene-by-scene narration plan for the video tour.
Key constraint: Each narration is STRICTLY 10-15 words (fits in 4 seconds of audio).
Property: {property_description}
Preference: {preference}
Script notes: {script}

Output Format: JSON:
{
  "tour_plan": [
    {"sequence_id": 1, "scene_name": "Living Room", "visual_theme": "Modern and Cozy", "narration_text": "..."},
    {"sequence_id": 2, "scene_name": "Dining Area", "visual_theme": "...", "narration_text": "..."}
  ]
}"""

MASTER_SCRIPT_PROMPT = """Given a sequence of room names, rough notes, and a style preference, write a cohesive, flowing narrative for the entire property tour. One segment per room. Consistent tone.
Rooms: {room_sequence}
Notes: {rough_notes}
Preference: {preference}

Output Format: JSON:
{
  "tour_script": [
    {"sequence_id": 1, "room_name": "Living Room", "narration_text": "..."},
    {"sequence_id": 2, "room_name": "Kitchen", "narration_text": "..."}
  ]
}"""
