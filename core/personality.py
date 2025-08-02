import random

# You can define different personality profiles here.
PERSONALITY_PROFILES = [
    {
        "name": "PAI",
        "creator": "Dhruv Jadav",
        "traits": ["humorous", "helpful", "curious"],
    }
]

def get_personality(profile_name=None):
    if profile_name:
        for profile in PERSONALITY_PROFILES:
            if profile["name"].lower() == profile_name.lower():
                return profile
    # Default to random if not specified
    return random.choice(PERSONALITY_PROFILES)
