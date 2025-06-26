import os

from invoke import task


@task
def syntax(c):
    print("🔧 Starting syntax fix attempt...")

    print("\n🔍 Checking appagent_tasks.py at line 8...")
    try:
        with open("/home/sandbox/fab_tasks/appagent_tasks.py") as f:
            lines = f.readlines()
            start = max(8 - 3, 0)
            end = min(8 + 2, len(lines))
            for i in range(start, end):
                print(f"{i+1:>3}: {lines[i].rstrip()}")
    except Exception as e:
        print("❌ Failed to read appagent_tasks.py: ", e)

    print("\n🔍 Checking appagent_webhook.py at line 8...")
    try:
        with open("/home/sandbox/fab_tasks/appagent_webhook.py") as f:
            lines = f.readlines()
            start = max(8 - 3, 0)
            end = min(8 + 2, len(lines))
            for i in range(start, end):
                print(f"{i+1:>3}: {lines[i].rstrip()}")
    except Exception as e:
        print("❌ Failed to read appagent_webhook.py: ", e)

    print("\n🔍 Checking appagent_workflows.py at line 5...")
    try:
        with open("/home/sandbox/fab_tasks/appagent_workflows.py") as f:
            lines = f.readlines()
            start = max(5 - 3, 0)
            end = min(5 + 2, len(lines))
            for i in range(start, end):
                print(f"{i+1:>3}: {lines[i].rstrip()}")
    except Exception as e:
        print("❌ Failed to read appagent_workflows.py: ", e)

    print("\n🔍 Checking audit_tasks.py at line 9...")
    try:
        with open("/home/sandbox/fab_tasks/audit_tasks.py") as f:
            lines = f.readlines()
            start = max(9 - 3, 0)
            end = min(9 + 2, len(lines))
            for i in range(start, end):
                print(f"{i+1:>3}: {lines[i].rstrip()}")
    except Exception as e:
        print("❌ Failed to read audit_tasks.py: ", e)

    print("\n🔍 Checking audit_utils.py at line 9...")
    try:
        with open("/home/sandbox/fab_tasks/audit_utils.py") as f:
            lines = f.readlines()
            start = max(9 - 3, 0)
            end = min(9 + 2, len(lines))
            for i in range(start, end):
                print(f"{i+1:>3}: {lines[i].rstrip()}")
    except Exception as e:
        print("❌ Failed to read audit_utils.py: ", e)

    print("\n🔍 Checking cicd.py at line 5...")
    try:
        with open("/home/sandbox/fab_tasks/cicd.py") as f:
            lines = f.readlines()
            start = max(5 - 3, 0)
            end = min(5 + 2, len(lines))
            for i in range(start, end):
                print(f"{i+1:>3}: {lines[i].rstrip()}")
    except Exception as e:
        print("❌ Failed to read cicd.py: ", e)

    print("\n🔍 Checking cicd_tasks.py at line 8...")
    try:
        with open("/home/sandbox/fab_tasks/cicd_tasks.py") as f:
            lines = f.readlines()
            start = max(8 - 3, 0)
            end = min(8 + 2, len(lines))
            for i in range(start, end):
                print(f"{i+1:>3}: {lines[i].rstrip()}")
    except Exception as e:
        print("❌ Failed to read cicd_tasks.py: ", e)

    print("\n🔍 Checking dashboard.py at line 6...")
    try:
        with open("/home/sandbox/fab_tasks/dashboard.py") as f:
            lines = f.readlines()
            start = max(6 - 3, 0)
            end = min(6 + 2, len(lines))
            for i in range(start, end):
                print(f"{i+1:>3}: {lines[i].rstrip()}")
    except Exception as e:
        print("❌ Failed to read dashboard.py: ", e)

    print("\n🔍 Checking deploy_dashboard.py at line 5...")
    try:
        with open("/home/sandbox/fab_tasks/deploy_dashboard.py") as f:
            lines = f.readlines()
            start = max(5 - 3, 0)
            end = min(5 + 2, len(lines))
            for i in range(start, end):
                print(f"{i+1:>3}: {lines[i].rstrip()}")
    except Exception as e:
        print("❌ Failed to read deploy_dashboard.py: ", e)

    print("\n🔍 Checking deploy_tasks.py at line 32...")
    try:
        with open("/home/sandbox/fab_tasks/deploy_tasks.py") as f:
            lines = f.readlines()
            start = max(32 - 3, 0)
            end = min(32 + 2, len(lines))
            for i in range(start, end):
                print(f"{i+1:>3}: {lines[i].rstrip()}")
    except Exception as e:
        print("❌ Failed to read deploy_tasks.py: ", e)
