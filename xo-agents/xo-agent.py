#!/usr/bin/env python3

import argparse
import subprocess

def list_tasks():
    print("Available tasks:")
    print("  pulse.sync        – Sync a pulse bundle")
    print("  vault.bundle      – Create a Vault bundle")
    print("  vault.pin         – Pin a Vault item")

def run_task(task, args):
    print(f"🚀 Running task: {task} with args: {args}")
    # Simulate execution (or call subprocess.run([...]) to trigger real commands)
    if task == "pulse.sync":
        print(f"[pulse.sync] Syncing bundle: {args[0] if args else 'default'}")
    elif task == "vault.bundle":
        print("[vault.bundle] Creating Vault bundle")
    elif task == "vault.pin":
        print("[vault.pin] Pinning to Vault")
    else:
        print("❌ Unknown task")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XO Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List available tasks")

    run_parser = subparsers.add_parser("run", help="Run a task")
    run_parser.add_argument("task", help="Task name")
    run_parser.add_argument("args", nargs="*", help="Task arguments")

    args = parser.parse_args()

    if args.command == "list":
        list_tasks()
    elif args.command == "run":
        run_task(args.task, args.args)
    else:
        parser.print_help()
