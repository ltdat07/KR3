from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")
    kafka_bootstrap_servers: str = Field(..., env="KAFKA_BOOTSTRAP_SERVERS")
    orders_topic: str = Field(..., env="ORDERS_TOPIC")
    payment_results_topic: str = Field(..., env="PAYMENT_RESULTS_TOPIC")
    kafka_consumer_group: str = Field("payments-service-group", env="KAFKA_CONSUMER_GROUP")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
