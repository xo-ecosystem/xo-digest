from dotenv import dotenv_values


def check_env(template_path=".env.template", prod_path=".env.production"):
    template = dotenv_values(template_path)
    prod = dotenv_values(prod_path)

    missing = [k for k in template if k not in prod]
    extra = [k for k in prod if k not in template]

    print("🔍 Missing keys:", missing)
    print("⚠️ Extra keys:", extra)
