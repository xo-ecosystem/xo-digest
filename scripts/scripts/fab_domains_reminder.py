from fabric import task
from invoke import run


@task
def setup_reminder(c):
    """Install cron job to check domain renewals daily."""
    cron_line = (
        "8 8 * * * /usr/bin/python3 /mnt/shield/domains/xo_domain_notifier.py "
        ">> /mnt/shield/domains/renewal.log 2>&1"
    )
    run(f'(crontab -l 2>/dev/null; echo "{cron_line}") | crontab -')
    print("✅ Domain renewal reminder cron job installed.")


@task
def check_renewals(c):
    """Run the renewal checker immediately."""
    run("python3 /mnt/shield/domains/xo_domain_notifier.py")
