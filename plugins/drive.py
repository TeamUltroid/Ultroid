from core.decorators._decorators import ultroid_cmd
from somewhere import GDrive

drive = GDrive()


@ultroid_cmd("gdul( (.*)|$)", fullsudo=True)
async def drive_upload_func(event):
    """`{}gdul <path to file/reply to document>` - Upload file from local/telegram to Google Drive."""
    ...


@ultroid_cmd("gddl( (.*)|$)", fullsudo=True)
async def drive_download_func(event):
    """`{}gddl <link>` - Download file from Google Drive using link."""
    ...


@ultroid_cmd("gdusage$")
async def drive_usage_func(event):
    """`{}gdusage` - Show total limit and usage of Google Drive storage."""
    ...


@ultroid_cmd("gdauth( (.*)|$)", fullsudo=True)
async def drive_auth_func(event):
    """`{}gdauth <code>` - To authorise with Google Drive API.
Args:
    `code` - Code which you get after visiting the link provided by `{}gdauth`"""
    ...


@ultroid_cmd("gdls( (.*)|$)", fullsudo=True)
async def drive_list_func(event):
    """`{}gdls <folder_id>` - List all files of Google Drive.
Args:
    `folder_id` - Folder ID or Folder link of Google Drive to list files from."""
    ...


@ultroid_cmd("gdmv( (.*)|$)", fullsudo=True)
async def drive_move_func(event):
    """`{}gdmv <file_id> <folder_id>` - Move file to another directory in Google Drive.
Args:
    `file_id` - File ID or File Link which you want to move.
    `folder_id` - Folder ID or Folder Link where you want to move."""
    ...


@ultroid_cmd("gdcp( (.*)|$)", fullsudo=True)
async def drive_copy_func(event):
    """`{}gdcp <file_id> <folder_id>` - Copy file to another directory in Google Drive.
Args:
    `file_id` - File ID or File Link which you want to copy.
    `folder_id` - Folder ID or Folder Link where you want to copy."""
    ...


@ultroid_cmd("gdsearch( (.*)|$)", fullsudo=True)
async def drive_search_func(event):
    """`{}gdmv <filename/file_id>` - Search for specific file in Google Drive.
Args:
    `filename` - Name of file (case-sensitive).
    `file_id` - File ID or File Link which you want to search."""
    ...


@ultroid_cmd("gddel( (.*)|$)", fullsudo=True)
async def drive_delete_func(event):
    """`{}gddel <file_id>` - Delete file from Google Drive.
Args:
    `file_id` - File ID or File Link which you want to move."""
    ...
