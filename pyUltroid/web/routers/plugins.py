import logging
import aiohttp
import base64
from aiohttp import web
from ...state_config import temp_config_store
from ...configs import CENTRAL_REPO_URL

logger = logging.getLogger(__name__)


async def get_auth_headers(request: web.Request):
    """Get authentication headers for central API requests"""
    from ... import ultroid_bot

    # Use bot ID for auth
    user_id = str(ultroid_bot.me.id)

    # Get stored central API auth data from temp config
    encoded_init_data = temp_config_store.get(f"X-TG-INIT-DATA-{user_id}")
    encoded_hash = temp_config_store.get(f"X-TG-HASH-{user_id}")

    if not encoded_init_data or not encoded_hash:
        raise web.HTTPUnauthorized(text="Central API authentication data not found.")

    # Decode the stored data for central API
    init_data = base64.b64decode(encoded_init_data.encode()).decode()
    hash_value = base64.b64decode(encoded_hash.encode()).decode()

    # Return headers
    return {
        "Content-Type": "application/json",
        "x-telegram-init-data": init_data,
        "x-telegram-hash": hash_value,
    }


async def proxy_request(
    request: web.Request, path: str, method: str = "GET", require_auth: bool = False
):
    """Generic proxy function to forward requests to central API"""
    try:
        # Get authentication headers if required
        if require_auth:
            headers = await get_auth_headers(request)
        else:
            headers = {"Content-Type": "application/json"}

        # Prepare the target URL
        target_url = f"{CENTRAL_REPO_URL}{path}"

        async with aiohttp.ClientSession() as session:
            # Forward the request with appropriate method
            if method == "GET":
                async with session.get(target_url, headers=headers) as response:
                    resp_json = await response.json()
                    return web.json_response(resp_json, status=response.status)

            elif method == "POST":
                # Handle multipart form data for file uploads
                if request.content_type.startswith("multipart/"):
                    data = await request.post()
                    form_data = aiohttp.FormData()

                    # Add auth data to form fields if this is a protected route
                    if require_auth:
                        try:
                            from ... import ultroid_bot

                            user_id = str(ultroid_bot.me.id)
                            encoded_init_data = temp_config_store.get(
                                f"X-TG-INIT-DATA-{user_id}"
                            )
                            encoded_hash = temp_config_store.get(f"X-TG-HASH-{user_id}")

                            if encoded_init_data and encoded_hash:
                                init_data = base64.b64decode(
                                    encoded_init_data.encode()
                                ).decode()
                                hash_value = base64.b64decode(
                                    encoded_hash.encode()
                                ).decode()

                                # Add auth data as form fields
                                form_data.add_field("x_telegram_init_data", init_data)
                                form_data.add_field("x_telegram_hash", hash_value)
                        except Exception as e:
                            logger.error(f"Error adding auth to form: {str(e)}")

                    # Add the regular form data fields
                    for key, value in data.items():
                        if hasattr(value, "file"):
                            form_data.add_field(
                                key,
                                value.file,
                                filename=value.filename,
                                content_type=value.content_type,
                            )
                        else:
                            form_data.add_field(key, value)

                    # For multipart, we need to remove content-type from headers
                    headers_without_content_type = headers.copy()
                    if "Content-Type" in headers_without_content_type:
                        headers_without_content_type.pop("Content-Type")

                    async with session.post(
                        target_url, headers=headers_without_content_type, data=form_data
                    ) as response:
                        try:
                            resp_json = await response.json()
                            return web.json_response(resp_json, status=response.status)
                        except:
                            # Return raw text if not JSON
                            resp_text = await response.text()
                            return web.Response(text=resp_text, status=response.status)
                else:
                    body = await request.json()
                    async with session.post(
                        target_url, headers=headers, json=body
                    ) as response:
                        resp_json = await response.json()
                        return web.json_response(resp_json, status=response.status)

            elif method == "PUT":
                if request.content_type.startswith("multipart/"):
                    data = await request.post()
                    form_data = aiohttp.FormData()

                    # Add auth data to form fields if this is a protected route
                    if require_auth:
                        try:
                            from ... import ultroid_bot

                            user_id = str(ultroid_bot.me.id)
                            encoded_init_data = temp_config_store.get(
                                f"X-TG-INIT-DATA-{user_id}"
                            )
                            encoded_hash = temp_config_store.get(f"X-TG-HASH-{user_id}")

                            if encoded_init_data and encoded_hash:
                                init_data = base64.b64decode(
                                    encoded_init_data.encode()
                                ).decode()
                                hash_value = base64.b64decode(
                                    encoded_hash.encode()
                                ).decode()

                                # Add auth data as form fields
                                form_data.add_field("x_telegram_init_data", init_data)
                                form_data.add_field("x_telegram_hash", hash_value)
                        except Exception as e:
                            logger.error(f"Error adding auth to form for PUT: {str(e)}")

                    # Add the regular form data fields
                    for key, value in data.items():
                        if hasattr(value, "file"):
                            form_data.add_field(
                                key,
                                value.file,
                                filename=value.filename,
                                content_type=value.content_type,
                            )
                        else:
                            form_data.add_field(key, value)

                    # For multipart, remove Content-Type from headers
                    headers_without_content_type = headers.copy()
                    if "Content-Type" in headers_without_content_type:
                        headers_without_content_type.pop("Content-Type")

                    async with session.put(
                        target_url, headers=headers_without_content_type, data=form_data
                    ) as response:
                        try:
                            resp_json = await response.json()
                            return web.json_response(resp_json, status=response.status)
                        except:
                            # Return raw text if not JSON
                            resp_text = await response.text()
                            return web.Response(text=resp_text, status=response.status)
                else:
                    body = await request.json()
                    async with session.put(
                        target_url, headers=headers, json=body
                    ) as response:
                        resp_json = await response.json()
                        return web.json_response(resp_json, status=response.status)

            elif method == "DELETE":
                async with session.delete(target_url, headers=headers) as response:
                    resp_json = await response.json()
                    return web.json_response(resp_json, status=response.status)

    except web.HTTPUnauthorized as e:
        return web.json_response({"error": str(e)}, status=401)
    except Exception as e:
        logger.error(f"Error in proxy request: {e}", exc_info=True)
        return web.json_response(
            {"error": f"Internal server error: {str(e)}"}, status=500
        )


# Plugin handlers
async def proxy_plugins_list(request: web.Request):
    """Proxy GET /api/v1/plugins"""
    return await proxy_request(request, "/api/v1/plugins", require_auth=True)


async def proxy_plugin_get(request: web.Request):
    """Proxy GET /api/v1/plugins/{plugin_id}"""
    plugin_id = request.match_info["plugin_id"]
    return await proxy_request(
        request, f"/api/v1/plugins/{plugin_id}", require_auth=True
    )


async def proxy_plugin_upload(request: web.Request):
    """Proxy POST /api/v1/plugins"""
    return await proxy_request(request, "/api/v1/plugins", "POST", require_auth=True)


async def proxy_plugin_update(request: web.Request):
    """Proxy PUT /api/v1/plugins/{plugin_id}"""
    plugin_id = request.match_info["plugin_id"]
    return await proxy_request(
        request, f"/api/v1/plugins/{plugin_id}", "PUT", require_auth=True
    )


async def proxy_plugin_delete(request: web.Request):
    """Proxy DELETE /api/v1/plugins/{plugin_id}"""
    plugin_id = request.match_info["plugin_id"]
    return await proxy_request(
        request, f"/api/v1/plugins/{plugin_id}", "DELETE", require_auth=True
    )


async def proxy_plugins_by_uploader(request: web.Request):
    """Proxy GET /api/v1/plugins/uploader/{uploader_id}"""
    uploader_id = request.match_info["uploader_id"]
    return await proxy_request(
        request, f"/api/v1/plugins/uploader/{uploader_id}", require_auth=True
    )


async def proxy_plugins_compute_diff(request: web.Request):
    """Proxy POST /api/v1/plugins/compute_diff"""
    return await proxy_request(
        request, "/api/v1/plugins/compute_diff", "POST", require_auth=True
    )


def setup_plugin_routes(app):
    """Setup routes for plugins API"""
    # Public routes - no auth required
    app.router.add_get("/api/v1/plugins", proxy_plugins_list)
    app.router.add_get(
        "/api/v1/plugins/uploader/{uploader_id}", proxy_plugins_by_uploader
    )
    app.router.add_get("/api/v1/plugins/{plugin_id}", proxy_plugin_get)

    # Protected routes - auth required
    app.router.add_post("/api/v1/plugins", proxy_plugin_upload)
    app.router.add_post("/api/v1/plugins/compute_diff", proxy_plugins_compute_diff)
    app.router.add_put("/api/v1/plugins/{plugin_id}", proxy_plugin_update)
    app.router.add_delete("/api/v1/plugins/{plugin_id}", proxy_plugin_delete)

    logger.info("Plugin proxy routes configured at /api/v1/plugins")
