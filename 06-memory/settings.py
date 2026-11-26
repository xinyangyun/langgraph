"""Test-only connection settings for future model and database integration."""

# These are placeholders. The runnable demos use in-memory implementations and
# never connect to either address.
TEST_MODEL_BASE_URL = "http://127.0.0.1:9999/v1"
TEST_POSTGRES_URI = (
    "postgresql://demo:demo@127.0.0.1:5432/langgraph_memory_demo"
    "?sslmode=disable"
)
