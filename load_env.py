from dotenv import load_dotenv
load_dotenv(".env.base")
load_dotenv(".env.local", override=True)