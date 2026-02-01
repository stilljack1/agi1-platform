import os, time, subprocess

def clear():
    os.system('clear')

def deploy_cluster(path_pattern, name):
    os.makedirs('logs', exist_ok=True)
    print(f'\n