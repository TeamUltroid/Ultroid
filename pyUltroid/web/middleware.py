import logging
from aiohttp import web
from typing import Callable, Awaitable
import os, hmac, json, time, hashlib
from urllib.parse import parse_qs, unquote

logger = logging.getLogger(__name__)

PUBLIC_PATHS = ['/health', '/metrics', '/api/user']

def parse_init_data(init_data_raw: str) -> dict:
    try:
        parsed = parse_qs(init_data_raw)
        result = {}
        for key, value in parsed.items():
            if key == 'user' and value:
                result[key] = json.loads(unquote(value[0]))
            elif value:
                result[key] = value[0]
        return result
    except Exception as e:
        logger.error(f"Failed to parse init data: {e}", exc_info=True)
        return {}

def checkValidateInitData(hash_str: str, init_data_raw: str, token: str, c_str: str = "WebAppData") -> bool:
    if not all([hash_str, init_data_raw, token]):
        logger.error("Missing required validation arguments")
        return False
    try:
        data_pairs = []
        for chunk in unquote(init_data_raw).split("&"):
            if not chunk.startswith("hash="):
                kv = chunk.split("=", 1)
                if len(kv) == 2:
                    data_pairs.append(kv)
        data_pairs.sort(key=lambda x: x[0])
        data_check_string = "\n".join([f"{rec[0]}={rec[1]}" for rec in data_pairs])
        logger.debug(f"Data check string for HMAC:\n{data_check_string}")

        secret_key = hmac.new(c_str.encode(), token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        logger.debug(f"Expected hash: {hash_str}")
        logger.debug(f"Calculated hash: {calculated_hash}")
        return calculated_hash == hash_str
    except Exception as e:
        logger.error(f"Error in validation: {e}", exc_info=True)
        return False

@web.middleware
async def telegram_auth_middleware(request: web.Request, handler: Callable[[web.Request], Awaitable[web.Response]]) -> web.Response:
    # Always allow OPTIONS requests for CORS
    if request.method == "OPTIONS":
        return await handler(request)
        
    # Skip auth for public paths
    if request.path in PUBLIC_PATHS:
        return await handler(request)
        
    try:
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            logger.error("BOT_TOKEN not set for: %s", request.path)
            raise web.HTTPInternalServerError(text=json.dumps({"error": "Server configuration error"}))
            
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('tma '):
            logger.warning("Invalid auth header for: %s", request.path)
            raise web.HTTPUnauthorized(text=json.dumps({"error": "Authorization required"}))
            
        init_data_raw = auth_header[4:]
        parsed_data = parse_init_data(init_data_raw)

        if not parsed_data or not (hash_to_verify := parsed_data.get('hash')):
            logger.error("Invalid/missing init data for: %s", request.path)
            raise web.HTTPBadRequest(text=json.dumps({"error": "Invalid init data"}))

        if not checkValidateInitData(hash_str=hash_to_verify, init_data_raw=init_data_raw, token=bot_token):
            logger.warning("Signature validation failed: %s", request.path)
            raise web.HTTPUnauthorized(text=json.dumps({"error": "Invalid signature"}))
        
        if auth_date_str := parsed_data.get('auth_date'):
            try:
                auth_date = int(auth_date_str)
                if time.time() - auth_date > 3600:
                    raise web.HTTPUnauthorized(text=json.dumps({"error": "Authentication expired"}))
            except ValueError:
                raise web.HTTPBadRequest(text=json.dumps({"error": "Invalid auth_date"}))
            
        for key in ['user', 'start_param', 'auth_date', 'chat_type', 'chat_instance']:
            request[key] = parsed_data.get(key, {} if key == 'user' else None)
        
        logger.info("Auth success: %s, user: %s", request.path, parsed_data.get('user', {}).get('id', 'unknown'))
        return await handler(request)
        
    except web.HTTPException as e:
        if e.status_code not in [400,401,403]:
            logger.error("HTTP error in auth: %s", e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Unexpected auth error: %s", e, exc_info=True)
        raise web.HTTPInternalServerError(text=json.dumps({"error": "Internal server error"})) 