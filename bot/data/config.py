import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
PGUSER = str(os.getenv("POSTGRES_USER"))
PGPASSWORD = str(os.getenv("POSTGRES_PASSWORD"))
DATABASE = str(os.getenv("DB_NAME"))

admins = [  # В списке указываем Telegram ID администраторов бота
    1955750981
]

ip = os.getenv("ip")

POSTGRES_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{ip}/{DATABASE}"
