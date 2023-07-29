from pydantic import BaseSettings


class DatabaseSettings(BaseSettings):
    DATABASE_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_HOSTNAME: str

    class Config:
        env_file = './.env'


class RedisSettings(BaseSettings):
    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int

    class Config:
        env_file = './.env'


class EmailSettings(BaseSettings):
    EMAIL_HOST: str
    EMAIL_PORT: str
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str

    class Config:
        env_file = './.env'


class AppSettings(DatabaseSettings, RedisSettings, EmailSettings):
    JWT_PRIVATE_KEY: str
    JWT_PUBLIC_KEY: str
    JWT_ALGORITHM: str

    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    VERIFICATION_TOKEN_EXPIRES_IN: int

    VERIFICATION_ALGORITHM: str
    VERIFICATION_SECRET_KEY: str

    CLIENT_ORIGIN: str

    PASSWORD_REGEX: str

    RATE_LIMIT: int
    RATE_LIMIT_INTERVAL: int

    class Config:
        env_file = './.env'


class LogConfig(BaseSettings):
    LOGGER_NAME: str = "app"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }


config = AppSettings()
