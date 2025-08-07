from invoke import task
from scripts.env_check import check_env

@task
def check(c):
    """✅ Validate .env.production against .env.template"""
    check_env()
