"""
Скрипт для генерации тестовых данных в базу данных ByteJournal.

Генерирует:
- Пользователей (100+)
- Статьи (500-1000)
- Категории (10-20)
- Связи статей и категорий
- Лайки (3000+)
- Комментарии (2000+)
"""

import asyncio
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Попытка импортировать faker, если доступен
try:
    from faker import Faker

    fake = Faker("ru_RU")
    USE_FAKER = True
except ImportError:
    USE_FAKER = False
    # Простые заглушки для текста
    fake = None


# Простые генераторы текста без faker
SAMPLE_TITLES = [
    "Введение в Python",
    "Основы баз данных",
    "Современный веб-разработка",
    "Алгоритмы и структуры данных",
    "Машинное обучение для начинающих",
    "Разработка REST API",
    "Контейнеризация с Docker",
    "Системы контроля версий",
    "Тестирование программного обеспечения",
    "Архитектура микросервисов",
    "Основы кибербезопасности",
    "Работа с большими данными",
    "Облачные вычисления",
    "Мобильная разработка",
    "DevOps практики",
]

SAMPLE_BODIES = [
    "В этой статье мы рассмотрим основные концепции и принципы работы.",
    "Данная тема является одной из самых важных в современной разработке.",
    "Мы изучим практические примеры и лучшие практики.",
    "Эта статья поможет вам понять ключевые аспекты предметной области.",
    "Рассмотрим различные подходы и их преимущества.",
]

SAMPLE_CATEGORIES = [
    ("Программирование", "Статьи о программировании и разработке"),
    ("Базы данных", "Материалы по работе с базами данных"),
    ("Веб-разработка", "Создание веб-приложений и сайтов"),
    ("DevOps", "Автоматизация и развертывание"),
    ("Машинное обучение", "Искусственный интеллект и ML"),
    ("Безопасность", "Кибербезопасность и защита данных"),
    ("Мобильная разработка", "Создание мобильных приложений"),
    ("Облачные технологии", "Работа с облачными платформами"),
    ("Тестирование", "QA и тестирование ПО"),
    ("Архитектура", "Проектирование и архитектура систем"),
]


def generate_text(length: int = 100) -> str:
    """Генерирует случайный текст заданной длины."""
    if USE_FAKER:
        return fake.text(max_nb_chars=length)
    words = [
        "статья",
        "пример",
        "код",
        "данные",
        "система",
        "приложение",
        "разработка",
        "проект",
        "технология",
        "инструмент",
    ]
    return " ".join(random.choices(words, k=length // 10))


def generate_title() -> str:
    """Генерирует заголовок статьи."""
    if USE_FAKER:
        return fake.sentence(nb_words=random.randint(3, 8))[:300]
    return random.choice(SAMPLE_TITLES) + f" - часть {random.randint(1, 10)}"


def generate_body() -> str:
    """Генерирует тело статьи."""
    if USE_FAKER:
        return fake.text(max_nb_chars=random.randint(500, 2000))
    paragraphs = random.randint(3, 8)
    return "\n\n".join(
        [
            random.choice(SAMPLE_BODIES) + " " + generate_text(200)
            for _ in range(paragraphs)
        ]
    )


def generate_username(index: int) -> str:
    """Генерирует имя пользователя."""
    if USE_FAKER:
        return fake.user_name()[:50]
    return f"user_{index:04d}"


def generate_category_name(index: int) -> tuple[str, str]:
    """Генерирует название и описание категории."""
    if index < len(SAMPLE_CATEGORIES):
        return SAMPLE_CATEGORIES[index]
    if USE_FAKER:
        name = fake.word().capitalize()
        desc = fake.sentence()
        return (name, desc)
    return (f"Категория {index}", f"Описание категории {index}")


async def generate_users(db: AsyncSession, count: int = 150) -> list[str]:
    """Генерирует пользователей и возвращает список их ID."""
    print(f"Генерация {count} пользователей...")
    user_ids = []

    # Получаем роли
    role_query = text("SELECT id, name FROM roles")
    result = await db.execute(role_query)
    roles = {row.name: str(row.id) for row in result.fetchall()}
    reader_role_id = roles.get("reader", "")
    author_role_id = roles.get("author", "")

    # Генерируем пользователей батчами
    batch_size = 50
    for batch_start in range(0, count, batch_size):
        batch_end = min(batch_start + batch_size, count)
        values = []
        params = {}

        for i in range(batch_start, batch_end):
            username = generate_username(i)
            # Первые 50 - авторы, остальные - читатели
            role_id = author_role_id if i < 50 else reader_role_id
            password_hash = (
                "$2b$12$dummyhash" + "x" * 50
            )  # Упрощенный хеш для тестовых данных

            values.append(f"(:username_{i}, :password_{i}, :role_{i})")
            params[f"username_{i}"] = username
            params[f"password_{i}"] = password_hash
            params[f"role_{i}"] = role_id

        insert_query = text(f"""
            INSERT INTO users (username, password_hash, role_id)
            VALUES {", ".join(values)}
            ON CONFLICT (username) DO NOTHING
            RETURNING id
        """)

        result = await db.execute(insert_query, params)
        batch_ids = [str(row.id) for row in result.fetchall()]
        user_ids.extend(batch_ids)

    # Если новых пользователей не создано (они уже есть), загружаем существующих
    if not user_ids:
        print("  Новых пользователей не создано, загружаем существующих...")
        select_query = text("SELECT id FROM users LIMIT :count")
        result = await db.execute(select_query, {"count": count})
        user_ids = [str(row.id) for row in result.fetchall()]

    await db.commit()
    print(f"Всего доступно {len(user_ids)} пользователей")
    return user_ids


async def generate_categories(db: AsyncSession, count: int = 15) -> list[str]:
    """Генерирует категории и возвращает список их ID."""
    print(f"Генерация {count} категорий...")
    category_ids = []

    colors = [
        "#FF5733",
        "#33FF57",
        "#3357FF",
        "#FF33F5",
        "#F5FF33",
        "#33FFF5",
        "#FF8C33",
    ]

    for i in range(count):
        name, description = generate_category_name(i)
        color = random.choice(colors) if random.random() > 0.3 else None

        insert_query = text("""
            INSERT INTO categories (name, description, color)
            VALUES (:name, :description, :color)
            ON CONFLICT (name) DO NOTHING
            RETURNING id
        """)

        result = await db.execute(
            insert_query, {"name": name, "description": description, "color": color}
        )
        row = result.fetchone()
        if row:
            category_ids.append(str(row.id))

    # Если категории не созданы (уже есть), загружаем существующие
    if not category_ids:
        print("  Новых категорий не создано, загружаем существующие...")
        select_query = text("SELECT id FROM categories LIMIT :count")
        result = await db.execute(select_query, {"count": count})
        category_ids = [str(row.id) for row in result.fetchall()]

    await db.commit()
    print(f"Всего доступно {len(category_ids)} категорий")
    return category_ids


async def generate_articles(
    db: AsyncSession, author_ids: list[str], count: int = 800
) -> list[str]:
    """Генерирует статьи и возвращает список их ID."""
    print(f"Генерация {count} статей...")
    article_ids = []

    # Генерируем даты за последние 2 года
    now = datetime.now()
    start_date = now - timedelta(days=730)

    batch_size = 100
    for batch_start in range(0, count, batch_size):
        batch_end = min(batch_start + batch_size, count)
        values = []
        params = {}

        for i in range(batch_start, batch_end):
            author_id = random.choice(author_ids)
            title = generate_title()
            body = generate_body()
            # Случайная дата создания
            days_ago = random.randint(0, 730)
            created_at = start_date + timedelta(
                days=days_ago, hours=random.randint(0, 23)
            )

            values.append(f"(:author_{i}, :title_{i}, :body_{i}, :created_{i})")
            params[f"author_{i}"] = author_id
            params[f"title_{i}"] = title
            params[f"body_{i}"] = body
            params[f"created_{i}"] = created_at

        insert_query = text(f"""
            INSERT INTO articles (author_id, title, body, created_at)
            VALUES {", ".join(values)}
            RETURNING id
        """)

        result = await db.execute(insert_query, params)
        batch_ids = [str(row.id) for row in result.fetchall()]
        article_ids.extend(batch_ids)

        if (batch_start + batch_size) % 200 == 0:
            await db.commit()
            print(f"  Создано {len(article_ids)} статей...")

    await db.commit()
    print(f"Создано {len(article_ids)} статей")
    return article_ids


async def generate_article_categories(
    db: AsyncSession, article_ids: list[str], category_ids: list[str]
):
    """Связывает статьи с категориями."""
    print("Связывание статей с категориями...")
    count = 0

    for article_id in article_ids:
        # Каждая статья имеет 1-3 категории
        num_categories = random.randint(1, 3)
        selected_categories = random.sample(
            category_ids, min(num_categories, len(category_ids))
        )

        for category_id in selected_categories:
            insert_query = text("""
                INSERT INTO article_categories (article_id, category_id, weight)
                VALUES (:article_id, :category_id, :weight)
                ON CONFLICT (article_id, category_id) DO NOTHING
            """)

            await db.execute(
                insert_query,
                {
                    "article_id": article_id,
                    "category_id": category_id,
                    "weight": random.randint(1, 10),
                },
            )
            count += 1

        if count % 500 == 0:
            await db.commit()

    await db.commit()
    print(f"Создано {count} связей статей и категорий")


async def generate_likes(
    db: AsyncSession, article_ids: list[str], user_ids: list[str], count: int = 3500
):
    """Генерирует лайки."""
    print(f"Генерация {count} лайков...")
    created = 0

    # Создаем множество для отслеживания уникальных пар (user_id, article_id)
    used_pairs = set()

    batch_size = 200
    batch_values = []
    batch_params = {}
    param_index = 0

    while created < count:
        article_id = random.choice(article_ids)
        user_id = random.choice(user_ids)
        pair = (user_id, article_id)

        if pair in used_pairs:
            continue

        used_pairs.add(pair)
        days_ago = random.randint(0, 365)
        created_at = datetime.now() - timedelta(
            days=days_ago, hours=random.randint(0, 23)
        )

        batch_values.append(
            f"(:article_{param_index}, :user_{param_index}, :created_{param_index})"
        )
        batch_params[f"article_{param_index}"] = article_id
        batch_params[f"user_{param_index}"] = user_id
        batch_params[f"created_{param_index}"] = created_at
        param_index += 1
        created += 1

        if len(batch_values) >= batch_size:
            insert_query = text(f"""
                INSERT INTO likes (article_id, user_id, created_at)
                VALUES {", ".join(batch_values)}
                ON CONFLICT (article_id, user_id) DO NOTHING
            """)
            await db.execute(insert_query, batch_params)
            await db.commit()
            batch_values = []
            batch_params = {}
            param_index = 0
            print(f"  Создано {created} лайков...")

    if batch_values:
        insert_query = text(f"""
            INSERT INTO likes (article_id, user_id, created_at)
            VALUES {", ".join(batch_values)}
            ON CONFLICT (article_id, user_id) DO NOTHING
        """)
        await db.execute(insert_query, batch_params)
        await db.commit()

    print(f"Создано {created} лайков")


async def generate_comments(
    db: AsyncSession, article_ids: list[str], user_ids: list[str], count: int = 2500
):
    """Генерирует комментарии."""
    print(f"Генерация {count} комментариев...")
    created = 0

    batch_size = 200
    batch_values = []
    batch_params = {}
    param_index = 0

    while created < count:
        article_id = random.choice(article_ids)
        user_id = random.choice(user_ids)
        content = generate_text(random.randint(50, 500))
        days_ago = random.randint(0, 365)
        created_at = datetime.now() - timedelta(
            days=days_ago, hours=random.randint(0, 23)
        )
        is_edited = random.random() < 0.1  # 10% комментариев отредактированы

        batch_values.append(
            f"(:article_{param_index}, :user_{param_index}, :content_{param_index}, :is_edited_{param_index}, :created_{param_index})"
        )
        batch_params[f"article_{param_index}"] = article_id
        batch_params[f"user_{param_index}"] = user_id
        batch_params[f"content_{param_index}"] = content
        batch_params[f"is_edited_{param_index}"] = is_edited
        batch_params[f"created_{param_index}"] = created_at
        param_index += 1
        created += 1

        if len(batch_values) >= batch_size:
            insert_query = text(f"""
                INSERT INTO comments (article_id, user_id, content, is_edited, created_at)
                VALUES {", ".join(batch_values)}
            """)
            await db.execute(insert_query, batch_params)
            await db.commit()
            batch_values = []
            batch_params = {}
            param_index = 0
            print(f"  Создано {created} комментариев...")

    if batch_values:
        insert_query = text(f"""
            INSERT INTO comments (article_id, user_id, content, is_edited, created_at)
            VALUES {", ".join(batch_values)}
        """)
        await db.execute(insert_query, batch_params)
        await db.commit()

    print(f"Создано {created} комментариев")


async def main():
    """Основная функция генерации данных."""
    import os

    from dotenv import load_dotenv

    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Ошибка: DATABASE_URL не установлен в переменных окружения")
        sys.exit(1)

    print("Подключение к базе данных...")
    engine = create_async_engine(database_url, echo=False)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as db:
        try:
            print("\n=== Начало генерации данных ===\n")

            # Генерируем пользователей
            user_ids = await generate_users(db, count=150)
            if not user_ids:
                print("Ошибка: не удалось создать пользователей")
                return

            # Берем только авторов для создания статей
            author_query = text("""
                SELECT u.id FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE r.name = 'author'
                LIMIT 50
            """)
            result = await db.execute(author_query)
            author_ids = [str(row.id) for row in result.fetchall()]

            if not author_ids:
                print("Ошибка: не найдено авторов")
                return

            # Генерируем категории
            category_ids = await generate_categories(db, count=15)

            # Генерируем статьи
            article_ids = await generate_articles(db, author_ids, count=800)

            # Связываем статьи с категориями
            if category_ids:
                await generate_article_categories(db, article_ids, category_ids)

            # Генерируем лайки
            await generate_likes(db, article_ids, user_ids, count=3500)

            # Генерируем комментарии
            await generate_comments(db, article_ids, user_ids, count=2500)

            print("\n=== Генерация данных завершена ===\n")

            # Выводим статистику
            stats_query = text("""
                SELECT 
                    (SELECT COUNT(*) FROM users) as users,
                    (SELECT COUNT(*) FROM articles) as articles,
                    (SELECT COUNT(*) FROM categories) as categories,
                    (SELECT COUNT(*) FROM likes) as likes,
                    (SELECT COUNT(*) FROM comments) as comments,
                    (SELECT COUNT(*) FROM article_categories) as article_categories
            """)
            result = await db.execute(stats_query)
            stats = result.fetchone()

            print("Статистика базы данных:")
            print(f"  Пользователей: {stats.users}")
            print(f"  Статей: {stats.articles}")
            print(f"  Категорий: {stats.categories}")
            print(f"  Лайков: {stats.likes}")
            print(f"  Комментариев: {stats.comments}")
            print(f"  Связей статей-категорий: {stats.article_categories}")

        except Exception as e:
            await db.rollback()
            print(f"\nОшибка при генерации данных: {e}")
            import traceback

            traceback.print_exc()
            raise

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
