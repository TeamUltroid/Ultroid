version: "3.9"
services:
  worker:
    build: .
    environment:
      REDIS_URI: $REDIS_URI
      REDIS_PASSWORD: $REDIS_PASSWORD
      SESSION: $SESSION
      API_ID: $API_ID  # defaults to None
      API_HASH: $API_HASH  # defaults to None
      MONGO_URI: $MONGO_URI  # defaults to None
      DATABASE_URL: $DATABASE_URL  # defaults to None
