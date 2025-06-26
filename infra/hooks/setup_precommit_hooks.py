from pathlib import Path

main_cfg = Path(".pre-commit-config.yaml")
shared_cfg = Path("xo-precommit.shared.yaml")

if shared_cfg.exists():
    shared_content = shared_cfg.read_text()
    main_text = main_cfg.read_text() if main_cfg.exists() else ""
    if "xo-precommit-essentials" not in main_text:
        print("🪄 Appending shared pre-commit config...")
        main_cfg.write_text(main_text.strip() + "\n\n" + shared_content)
    else:
        print("✅ Already included.")
else:
    print("❌ xo-precommit.shared.yaml not found.")
