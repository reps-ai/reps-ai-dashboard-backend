from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    retell_api_key: str
    retell_from_number: str
    retell_agent_id: str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"  # Allow extra fields to be present
    )

settings = Settings()
