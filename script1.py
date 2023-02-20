import os

def push(path=''):
    os.system(f"{path}git add .")
    os.system(f"{path}git commit -m 'Update'")
    os.system(f'{path}git push')

push()
push('cd D://PluginManagerAPI && ')