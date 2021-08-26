import asyncio
import configparser
import os
import platform
import sys
import os.path

ERROR = (
    "Something is wrong with your API {}, "
    "please double check and re-enter the same."
)

if platform.python_version_tuple() < ('3', '7', '3'):
    print(
        "Please run this script with Python 3.7.3 or above."
        "\nExiting the script."
    )
    sys.exit(1)

if sys.platform.startswith('win'):
    loop = asyncio.ProactorEventLoop()
else:
    loop = asyncio.get_event_loop()


async def install_pip_package(package: str) -> bool:
    args = ['-m', 'pip', 'install', '--upgrade', '--user', package]
    process = await asyncio.create_subprocess_exec(
        sys.executable.replace(' ', '\\ '), *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    return True if process.returncode == 0 else False


try:
    import telethon
    from telethon.errors import AuthKeyError, InvalidBufferError
except (ModuleNotFoundError, ImportError):
    print('Installing Telethon...')
    pip = loop.run_until_complete(install_pip_package('telethon'))
    if pip:
        print('Successfully installed Telethon. Run the script again.')
    else:
        print(
            'Failed to install Telethon. '
            'Run the script again after installing it manually using:'
        )
        print('"python3 -m pip install -U telethon --user"')
    sys.exit()


api_id = os.environ.get('api_id', None)
api_hash = os.environ.get('api_hash', None)
endpoint = os.environ.get('redis_endpoint', None)
password = os.environ.get('redis_password', None)
redis = False

if all((api_id, api_hash)):
    redis_ip = input("Would you like to generate a Redis session? (yes/no): ")
    if redis_ip.lower() in ('y', 'yes'):
        if ':' not in endpoint:
            print('Invalid Redis endpoint! Try again.')
            sys.exit(1)
        redis = True
elif os.path.exists('./config.ini'):
    config = configparser.ConfigParser()
    config.read('./config.ini')
    api_id = config['telethon'].getint('api_id', False)
    api_hash = config['telethon'].get('api_hash', False)
    if not (api_id or api_hash):
        print("Invalid config file! Fix it before generating a session.")
        sys.exit(1)
    redis_ip = input("Would you like to generate a Redis session? (yes/no): ")
    if redis_ip.lower() in ('y', 'yes'):
        endpoint = config['telethon'].get('redis_endpoint', False)
        password = config['telethon'].get('redis_password', False)
        if not (endpoint or password):
            print(
                "Make sure you have redis_endpoint and redis_password "
                "in your config.ini"
            )
            sys.exit(1)
        elif ':' not in endpoint:
            print("Invalid Redis endpoint.")
            sys.exit(1)
        redis = True
else:
    while True:
        api_id = input("Enter your API ID: ")
        if len(api_id) >= 2 and api_id.isnumeric():
            break
        else:
            print(ERROR.format('ID'))
    while True:
        api_hash = input("Enter your API hash: ")
        if len(api_hash) == 32 and api_hash.isalnum():
            break
        else:
            print(ERROR.format('hash'))
    redis_ip = input("Would you like to generate a Redis session? (yes/no): ")
    if redis_ip.lower() in ('y', 'yes'):
        while True:
            endpoint = input("Enter your Redis endpoint: ")
            if ':' in endpoint:
                break
            else:
                print('Invalid Redis endpoint! Try again.')
        password = input("Enter your Redis password: ")
        redis = True

if redis:
    try:
        import redis
    except (ModuleNotFoundError, ImportError):
        print('Installing Redis...')
        pip = loop.run_until_complete(install_pip_package('redis'))
        if pip:
            print('Successfully installed Redis. Run the script again.')
        else:
            print(
                'Failed to install Redis. '
                'Run the script again after installing it manually using:'
            )
            print('"python3 -m pip install -U redis --user"')
        sys.exit()

    from sessions.redis import RedisSession

    redis_connection = redis.Redis(
        host=endpoint.split(':')[0],
        port=endpoint.split(':')[1],
        password=password.strip()
    )
    try:
        redis_connection.ping()
    except Exception:
        print("Invalid Redis credentials! Exiting the script")
        sys.exit(1)
    session = RedisSession("userbot", redis_connection)
else:
    session = "userbot"

client = telethon.TelegramClient(session, api_id, api_hash)
try:
    with client:
        me = client.loop.run_until_complete(client.get_me())
        name = telethon.utils.get_display_name(me)
    print(f"Successfully generated a session for {name}")
except (AuthKeyError, InvalidBufferError):
    client.session.delete()
    print(
        "Your old session was invalid and has been automatically deleted! "
        "Run the script again to generate a new session."
    )
    sys.exit(1)
