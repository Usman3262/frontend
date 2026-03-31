"""Application constants."""

# Reaction types
VALID_REACTIONS = {"Relatable", "Inspired", "StayStrong", "Helpful"}

# Categories
VALID_CATEGORIES = {
    "Life Lessons",
    "Achievements",
    "Regrets",
    "Career",
    "Relationships",
    "Personal Growth",
}

# Moderation
MODERATION_PENDING = "pending"
MODERATION_APPROVED = "approved"
MODERATION_REJECTED = "rejected"

# Error messages
ERROR_USER_NOT_FOUND = "User not found. Please register."
ERROR_INVALID_CREDENTIALS = "Invalid anonymous number or password."
ERROR_STORY_NOT_FOUND = "Story not found."
ERROR_INVALID_REACTION = "Invalid reaction type."
ERROR_CONTENT_TOO_SHORT = "Story must be at least 10 characters."
ERROR_CONTENT_TOO_LONG = "Story must be at most 2000 characters."

# Success messages
SUCCESS_USER_CREATED = "User created successfully."
SUCCESS_STORY_CREATED = "Story created successfully."
SUCCESS_REACTION_ADDED = "Reaction added successfully."
