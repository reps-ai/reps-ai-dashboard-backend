from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str

    @property
    def database_url_with_ssl(self) -> str:
        """Add SSL requirements for Neon database connection."""
        if 'neon.tech' in self.DATABASE_URL:
            if '?' not in self.DATABASE_URL:
                return f"{self.DATABASE_URL}?sslmode=require"
            elif 'sslmode=' not in self.DATABASE_URL:
                return f"{self.DATABASE_URL}&sslmode=require"
        return self.DATABASE_URL

    class Config:
        env_file = ".env"


settings = Settings()