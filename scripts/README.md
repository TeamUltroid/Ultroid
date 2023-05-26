
## Scripts

This directory contains the various shellscripts for Ultroid.<br>Do not run them directly, instead, use the ```ultroid``` file with arguments.

## Shell scripts
* `installer.sh` - Script to install Ultroid
* `install-termux` - Script to install Ultroid in termux
* `session` - Script to generator String Session
* `startup` - Script to start Ultroid

## `installer.sh`
Installs Ultroid in machine. Use custom flags to define installation configs or don't provide any flags to use default configs

```bash
./ultroid install [Options]
```
### Options
```
    --help: Show message containing usage of the script
    --dir: Install Ultroid in a custom or specified directory, Default is current directory/Ultroid
    --branch: Clone custom or specificed Ultroid repo branch like main or dev, Default is main
    --env-file: Path to .env file, required only if using any env file other than .env
    --no-root: Install Ultroid without root access
```

## `install-termux`
```bash
./ultroid termux
```
Installs Ultroid in termux.

## `session`
Generates string session of telethon or pyrogram.
```bash
./ultroid session
```

## `start`
Starts the bot.
```bash
./ultroid start [Options]
```

### Options
```
    --help: Show the help message
    --http-server: Start a http server serving files over http, default port: 8000
```
