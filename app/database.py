from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from .config import settings


def _ensure_db_dir_exists() -> None:
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)


def _get_connection() -> sqlite3.Connection:
    _ensure_db_dir_exists()
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def db_cursor() -> Generator[sqlite3.Cursor, None, None]:
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    schema_sql = """
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        description TEXT,
        image_url TEXT
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        subcategory TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        unit TEXT,
        price REAL NOT NULL DEFAULT 0,
        image_url TEXT,
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'received',
        verification_code TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id)
    );
    """
    with db_cursor() as cursor:
        cursor.executescript(schema_sql)
        _apply_migrations(cursor)


def _apply_migrations(cursor: sqlite3.Cursor) -> None:
    category_columns = {
        row["name"] for row in cursor.execute("PRAGMA table_info(categories);").fetchall()
    }
    if "image_url" not in category_columns:
        cursor.execute("ALTER TABLE categories ADD COLUMN image_url TEXT;")

    cursor.execute("UPDATE products SET price = COALESCE(price, 0);")
    cursor.execute(
        "UPDATE orders SET status = 'received' WHERE status = 'pending_verification';"
    )


def seed_data() -> None:
    catalog_seed: List[Dict[str, Any]] = [
        {
            "slug": "detergent-cleaning",
            "name": "Detergent & Cleaning Liquids",
            "description": (
                "Bulk chlorine, antiseptic solutions, floor detergents, dishwashing liquids and "
                "hand soaps for kitchen hygiene protocols."
            ),
            "image_url": "/static/images/category-detergent.svg",
            "items": [
                # Chlorine
                {
                    "subcategory": "Chlorine",
                    "name": "Chlorine 4L",
                    "unit": "Jerrycan 4L",
                    "price": 0.0,
                    "description": "Concentrated chlorine for dishwashing stations.",
                    "image_url": "/static/images/product-chlorine.svg",
                },
                {
                    "subcategory": "Chlorine",
                    "name": "Chlorine 10L",
                    "unit": "Jerrycan 10L",
                    "price": 0.0,
                    "description": "Medium volume chlorine for daily cleaning.",
                    "image_url": "/static/images/product-chlorine.svg",
                },
                {
                    "subcategory": "Chlorine",
                    "name": "Chlorine 22L",
                    "unit": "Jerrycan 22L",
                    "price": 0.0,
                    "description": "High capacity chlorine stock.",
                    "image_url": "/static/images/product-chlorine.svg",
                },
                {
                    "subcategory": "Chlorine",
                    "name": "Chlorine 30L",
                    "unit": "Jerrycan 30L",
                    "price": 0.0,
                    "description": "Bulk chlorine for central kitchens.",
                    "image_url": "/static/images/product-chlorine.svg",
                },
                # Antiseptic
                {
                    "subcategory": "Antiseptic",
                    "name": "Antiseptic 4L",
                    "unit": "Jerrycan 4L",
                    "price": 0.0,
                    "description": "Ready-to-use antiseptic for food-prep surfaces.",
                    "image_url": "/static/images/product-antiseptic.svg",
                },
                {
                    "subcategory": "Antiseptic",
                    "name": "Antiseptic 10L",
                    "unit": "Jerrycan 10L",
                    "price": 0.0,
                    "description": "Bulk supply for high-frequency sanitation.",
                    "image_url": "/static/images/product-antiseptic.svg",
                },
                # Floor detergent
                {
                    "subcategory": "Floor Detergent",
                    "name": "Floor Detergent 4L",
                    "unit": "Jerrycan 4L",
                    "price": 0.0,
                    "description": "Neutral floor cleaner for daily maintenance.",
                    "image_url": "/static/images/product-floor.svg",
                },
                {
                    "subcategory": "Floor Detergent",
                    "name": "Floor Detergent 10L",
                    "unit": "Jerrycan 10L",
                    "price": 0.0,
                    "description": "High coverage floor detergent.",
                    "image_url": "/static/images/product-floor.svg",
                },
                {
                    "subcategory": "Floor Detergent",
                    "name": "Floor Detergent 22L",
                    "unit": "Jerrycan 22L",
                    "price": 0.0,
                    "description": "Bulk floor detergent for large venues.",
                    "image_url": "/static/images/product-floor.svg",
                },
                {
                    "subcategory": "Floor Detergent",
                    "name": "Floor Detergent 30L",
                    "unit": "Jerrycan 30L",
                    "price": 0.0,
                    "description": "Heavy-duty stock for facilities teams.",
                    "image_url": "/static/images/product-floor.svg",
                },
                # Dishwashing
                {
                    "subcategory": "Dishwashing",
                    "name": "Dishwashing 4L",
                    "unit": "Jerrycan 4L",
                    "price": 0.0,
                    "description": "Concentrated dishwashing liquid.",
                    "image_url": "/static/images/product-dish.svg",
                },
                {
                    "subcategory": "Dishwashing",
                    "name": "Dishwashing 10L",
                    "unit": "Jerrycan 10L",
                    "price": 0.0,
                    "description": "Economical pack for dishwashing lines.",
                    "image_url": "/static/images/product-dish.svg",
                },
                {
                    "subcategory": "Dishwashing",
                    "name": "Dishwashing 22L",
                    "unit": "Jerrycan 22L",
                    "price": 0.0,
                    "description": "Bulk supply for central dish rooms.",
                    "image_url": "/static/images/product-dish.svg",
                },
                {
                    "subcategory": "Dishwashing",
                    "name": "Dishwashing 30L",
                    "unit": "Jerrycan 30L",
                    "price": 0.0,
                    "description": "Maximum volume dishwashing liquid.",
                    "image_url": "/static/images/product-dish.svg",
                },
                # Hand soap
                {
                    "subcategory": "Hand Soap",
                    "name": "Hand Soap 4L",
                    "unit": "Jerrycan 4L",
                    "price": 0.0,
                    "description": "Fragrance-free formula suitable for kitchen teams.",
                    "image_url": "/static/images/product-hand-soap.svg",
                },
                {
                    "subcategory": "Hand Soap",
                    "name": "Hand Soap 10L",
                    "unit": "Jerrycan 10L",
                    "price": 0.0,
                    "description": "High-volume refill for dispenser systems.",
                    "image_url": "/static/images/product-hand-soap.svg",
                },
            ],
        },
        {
            "slug": "food-packaging",
            "name": "Food & Packaging Containers",
            "description": (
                "Pizza boxes, plastic takeaway containers, salad bowls and kraft packaging for "
                "delivery and dine-out programs."
            ),
            "image_url": "/static/images/category-packaging.svg",
            "items": [
                # Pizza boxes
                {
                    "subcategory": "Pizza Boxes",
                    "name": "Pizza Box 20cm",
                    "unit": "Bundle",
                    "price": 0.0,
                    "description": "Corrugated pizza box 20cm, vented.",
                    "image_url": "/static/images/product-pizza-box.svg",
                },
                {
                    "subcategory": "Pizza Boxes",
                    "name": "Pizza Box 30cm",
                    "unit": "Bundle",
                    "price": 0.0,
                    "description": "Corrugated pizza box 30cm, vented.",
                    "image_url": "/static/images/product-pizza-box.svg",
                },
                {
                    "subcategory": "Pizza Boxes",
                    "name": "Pizza Box 35cm",
                    "unit": "Bundle",
                    "price": 0.0,
                    "description": "Wide format pizza box 35cm.",
                    "image_url": "/static/images/product-pizza-box.svg",
                },
                {
                    "subcategory": "Pizza Boxes",
                    "name": "Pizza Box 40cm",
                    "unit": "Bundle",
                    "price": 0.0,
                    "description": "XL pizza box 40cm for family portions.",
                    "image_url": "/static/images/product-pizza-box.svg",
                },
                # Plastic boxes
                {
                    "subcategory": "Plastic Boxes",
                    "name": "Plastic Box 100cc",
                    "unit": "Carton",
                    "price": 0.0,
                    "description": "Microwave-safe PP box 100cc.",
                    "image_url": "/static/images/product-plastic-box.svg",
                },
                {
                    "subcategory": "Plastic Boxes",
                    "name": "Plastic Box 150cc",
                    "unit": "Carton",
                    "price": 0.0,
                    "description": "Microwave-safe PP box 150cc.",
                    "image_url": "/static/images/product-plastic-box.svg",
                },
                {
                    "subcategory": "Plastic Boxes",
                    "name": "Plastic Box 375cc",
                    "unit": "Carton",
                    "price": 0.0,
                    "description": "Microwave-safe PP box 375cc.",
                    "image_url": "/static/images/product-plastic-box.svg",
                },
                {
                    "subcategory": "Plastic Boxes",
                    "name": "Plastic Box 750cc",
                    "unit": "Carton",
                    "price": 0.0,
                    "description": "Microwave-safe PP box 750cc.",
                    "image_url": "/static/images/product-plastic-box.svg",
                },
                {
                    "subcategory": "Plastic Boxes",
                    "name": "Plastic Box 1000cc",
                    "unit": "Carton",
                    "price": 0.0,
                    "description": "Microwave-safe PP box 1000cc.",
                    "image_url": "/static/images/product-plastic-box.svg",
                },
                {
                    "subcategory": "Plastic Boxes",
                    "name": "Plastic Box 1500cc",
                    "unit": "Carton",
                    "price": 0.0,
                    "description": "Microwave-safe PP box 1500cc.",
                    "image_url": "/static/images/product-plastic-box.svg",
                },
                # Other packaging
                {
                    "subcategory": "Sandwich Wrappers",
                    "name": "Sandwich Wrappers",
                    "unit": "Bundle",
                    "price": 0.0,
                    "description": "Grease-resistant sandwich wrap sheets.",
                    "image_url": "/static/images/product-wrapper.svg",
                },
                {
                    "subcategory": "Salad Bowls",
                    "name": "Salad Bowls",
                    "unit": "Carton",
                    "price": 0.0,
                    "description": "Clear salad bowls with lid.",
                    "image_url": "/static/images/product-salad-bowl.svg",
                },
                {
                    "subcategory": "Kraft Bags",
                    "name": "Kraft Bags",
                    "unit": "Bundle",
                    "price": 0.0,
                    "description": "Sturdy kraft takeaway bags.",
                    "image_url": "/static/images/product-kraft-bag.svg",
                },
                {
                    "subcategory": "Carton Plates",
                    "name": "Carton Plates",
                    "unit": "Bundle",
                    "price": 0.0,
                    "description": "Rigid carton plates for catering service.",
                    "image_url": "/static/images/product-carton-plate.svg",
                },
            ],
        },
        {
            "slug": "hygiene-safety",
            "name": "Hygiene & Safety",
            "description": (
                "Protective gloves, hair nets, sleeves and trash bags for front and back of house teams."
            ),
            "image_url": "/static/images/category-hygiene.svg",
            "items": [
                # Gloves (Blue)
                {
                    "subcategory": "Gloves",
                    "name": "Latex Gloves - Small (Blue)",
                    "unit": "Box",
                    "price": 0.0,
                    "description": "Powder-free latex gloves, blue, size small.",
                    "image_url": "/static/images/product-gloves.svg",
                },
                {
                    "subcategory": "Gloves",
                    "name": "Latex Gloves - Medium (Blue)",
                    "unit": "Box",
                    "price": 0.0,
                    "description": "Powder-free latex gloves, blue, size medium.",
                    "image_url": "/static/images/product-gloves.svg",
                },
                {
                    "subcategory": "Gloves",
                    "name": "Latex Gloves - Large (Blue)",
                    "unit": "Box",
                    "price": 0.0,
                    "description": "Powder-free latex gloves, blue, size large.",
                    "image_url": "/static/images/product-gloves.svg",
                },
                # Gloves (Black)
                {
                    "subcategory": "Gloves",
                    "name": "Latex Gloves - Small (Black)",
                    "unit": "Box",
                    "price": 0.0,
                    "description": "Powder-free latex gloves, black, size small.",
                    "image_url": "/static/images/product-gloves.svg",
                },
                {
                    "subcategory": "Gloves",
                    "name": "Latex Gloves - Medium (Black)",
                    "unit": "Box",
                    "price": 0.0,
                    "description": "Powder-free latex gloves, black, size medium.",
                    "image_url": "/static/images/product-gloves.svg",
                },
                {
                    "subcategory": "Gloves",
                    "name": "Latex Gloves - Large (Black)",
                    "unit": "Box",
                    "price": 0.0,
                    "description": "Powder-free latex gloves, black, size large.",
                    "image_url": "/static/images/product-gloves.svg",
                },
                # Hair nets
                {
                    "subcategory": "Hair Nets",
                    "name": "Hair Nets (White)",
                    "unit": "Pack",
                    "price": 0.0,
                    "description": "Breathable disposable hair nets, white.",
                    "image_url": "/static/images/product-hairnet.svg",
                },
                {
                    "subcategory": "Hair Nets",
                    "name": "Hair Nets (Black)",
                    "unit": "Pack",
                    "price": 0.0,
                    "description": "Breathable disposable hair nets, black.",
                    "image_url": "/static/images/product-hairnet.svg",
                },
                # Hand sleeves
                {
                    "subcategory": "Hand Sleeves",
                    "name": "Hand Sleeves (White)",
                    "unit": "Pack",
                    "price": 0.0,
                    "description": "Disposable hand sleeves, white.",
                    "image_url": "/static/images/product-sleeve.svg",
                },
                {
                    "subcategory": "Hand Sleeves",
                    "name": "Hand Sleeves (Black)",
                    "unit": "Pack",
                    "price": 0.0,
                    "description": "Disposable hand sleeves, black.",
                    "image_url": "/static/images/product-sleeve.svg",
                },
                # Trash bags
                {
                    "subcategory": "Trash Bags",
                    "name": "Trash Bags - Small",
                    "unit": "Roll",
                    "price": 0.0,
                    "description": "High-density small trash bags.",
                    "image_url": "/static/images/product-trash-bag.svg",
                },
                {
                    "subcategory": "Trash Bags",
                    "name": "Trash Bags - Medium",
                    "unit": "Roll",
                    "price": 0.0,
                    "description": "High-density medium trash bags.",
                    "image_url": "/static/images/product-trash-bag.svg",
                },
                {
                    "subcategory": "Trash Bags",
                    "name": "Trash Bags - Large",
                    "unit": "Roll",
                    "price": 0.0,
                    "description": "High-density large trash bags.",
                    "image_url": "/static/images/product-trash-bag.svg",
                },
                {
                    "subcategory": "Trash Bags",
                    "name": "Trash Bags - 85cm",
                    "unit": "Roll",
                    "price": 0.0,
                    "description": "Extra-strong trash bags 85cm.",
                    "image_url": "/static/images/product-trash-bag.svg",
                },
                {
                    "subcategory": "Trash Bags",
                    "name": "Trash Bags - 110cm",
                    "unit": "Roll",
                    "price": 0.0,
                    "description": "Extra-strong trash bags 110cm.",
                    "image_url": "/static/images/product-trash-bag.svg",
                },
                {
                    "subcategory": "Trash Bags",
                    "name": "Trash Bags - 125cm",
                    "unit": "Roll",
                    "price": 0.0,
                    "description": "Extra-strong trash bags 125cm.",
                    "image_url": "/static/images/product-trash-bag.svg",
                },
            ],
        },
        {
            "slug": "cloths-wipes",
            "name": "Microfiber Cloths & Wipes",
            "description": "Reusable microfiber cloths and disposable wipes for service stations.",
            "image_url": "/static/images/category-cloths.svg",
            "items": [
                {
                    "subcategory": "Microfiber Cloths",
                    "name": "Microfiber Color-Coded Cloths",
                    "unit": "Pack of 20",
                    "price": 0.0,
                    "description": "Color-coded cloths for HACCP separation.",
                    "image_url": "/static/images/product-microfiber.svg",
                },
                {
                    "subcategory": "Wipes",
                    "name": "Service Wipes",
                    "unit": "Tub of 200",
                    "price": 0.0,
                    "description": "Disposable wipes for food contact surfaces.",
                    "image_url": "/static/images/product-wipes.svg",
                },
            ],
        },
        {
            "slug": "tissues-napkins",
            "name": "Tissues & Napkins",
            "description": "Interfold napkins, toilet napkins and kitchen rolls stocked for dining rooms.",
            "image_url": "/static/images/category-tissues.svg",
            "items": [
                {
                    "subcategory": "Interfold Napkins",
                    "name": "Interfold Napkins 2kg",
                    "unit": "Pack",
                    "price": 0.0,
                    "description": "Food-service interfold napkins 2kg.",
                    "image_url": "/static/images/product-interfold.svg",
                },
                {
                    "subcategory": "Interfold Napkins",
                    "name": "Interfold Napkins 3kg",
                    "unit": "Pack",
                    "price": 0.0,
                    "description": "Food-service interfold napkins 3kg.",
                    "image_url": "/static/images/product-interfold.svg",
                },
                {
                    "subcategory": "Interfold Napkins",
                    "name": "Interfold Napkins 4kg",
                    "unit": "Pack",
                    "price": 0.0,
                    "description": "Food-service interfold napkins 4kg.",
                    "image_url": "/static/images/product-interfold.svg",
                },
                {
                    "subcategory": "Toilet Napkins",
                    "name": "Toilet Napkins (6 rolls)",
                    "unit": "Pack",
                    "price": 0.0,
                    "description": "Soft-touch toilet napkins pack of 6 rolls.",
                    "image_url": "/static/images/product-toilet.svg",
                },
                {
                    "subcategory": "Kitchen Napkins",
                    "name": "Kitchen Napkins (6 rolls)",
                    "unit": "Pack",
                    "price": 0.0,
                    "description": "Highly absorbent kitchen napkins pack of 6.",
                    "image_url": "/static/images/product-kitchen.svg",
                },
            ],
        },
    ]

    with db_cursor() as cursor:
        target_slugs = {category["slug"] for category in catalog_seed}
        existing_categories = cursor.execute(
            "SELECT id, slug FROM categories;"
        ).fetchall()

        for existing in existing_categories:
            if existing["slug"] in target_slugs:
                continue

            referencing = cursor.execute(
                """
                SELECT COUNT(*) AS c
                FROM order_items
                WHERE product_id IN (
                    SELECT id FROM products WHERE category_id = ?
                );
                """,
                (existing["id"],),
            ).fetchone()["c"]

            if referencing == 0:
                cursor.execute(
                    "DELETE FROM order_items WHERE product_id IN (SELECT id FROM products WHERE category_id = ?);",
                    (existing["id"],),
                )
                cursor.execute("DELETE FROM products WHERE category_id = ?;", (existing["id"],))
                cursor.execute("DELETE FROM categories WHERE id = ?;", (existing["id"],))

        for category in catalog_seed:
            existing_category = cursor.execute(
                "SELECT id FROM categories WHERE slug = ?;",
                (category["slug"],),
            ).fetchone()

            if existing_category:
                category_id = existing_category["id"]
                cursor.execute(
                    """
                    UPDATE categories
                    SET name = ?, description = ?, image_url = ?
                    WHERE id = ?;
                    """,
                    (
                        category["name"],
                        category["description"],
                        category.get("image_url"),
                        category_id,
                    ),
                )
            else:
                cursor.execute(
                    "INSERT INTO categories (slug, name, description, image_url) VALUES (?, ?, ?, ?);",
                    (
                        category["slug"],
                        category["name"],
                        category["description"],
                        category.get("image_url"),
                    ),
                )
                category_id = cursor.lastrowid

            for item in category["items"]:
                existing_product = cursor.execute(
                    """
                    SELECT id FROM products
                    WHERE category_id = ? AND name = ?;
                    """,
                    (category_id, item["name"]),
                ).fetchone()

                if existing_product:
                    cursor.execute(
                        """
                        UPDATE products
                        SET subcategory = ?, description = ?, unit = ?, price = ?, image_url = ?
                        WHERE id = ?;
                        """,
                        (
                            item["subcategory"],
                            item.get("description"),
                            item.get("unit"),
                            item.get("price", 0.0),
                            item.get("image_url"),
                            existing_product["id"],
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO products (
                            category_id, subcategory, name, description, unit, price, image_url
                        ) VALUES (?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            category_id,
                            item["subcategory"],
                            item["name"],
                            item.get("description"),
                            item.get("unit"),
                            item.get("price", 0.0),
                            item.get("image_url"),
                        ),
                    )


def get_catalog() -> List[Dict[str, Any]]:
    with db_cursor() as cursor:
        categories = cursor.execute(
            "SELECT id, slug, name, description, image_url FROM categories ORDER BY name;"
        ).fetchall()

        catalog: List[Dict[str, Any]] = []
        for category in categories:
            products = cursor.execute(
                """
                SELECT id, subcategory, name, description, unit, price, image_url
                FROM products
                WHERE category_id = ?
                ORDER BY subcategory, name;
                """,
                (category["id"],),
            ).fetchall()

            subcategory_map: Dict[str, Dict[str, Any]] = {}
            for product in products:
                entry = subcategory_map.setdefault(
                    product["subcategory"],
                    {"subcategory": product["subcategory"], "items": []},
                )
                entry["items"].append(
                    {
                        "id": product["id"],
                        "name": product["name"],
                        "description": product["description"],
                        "unit": product["unit"],
                        "price": product["price"],
                        "imageUrl": product["image_url"],
                    }
                )

            catalog.append(
                {
                    "id": category["id"],
                    "slug": category["slug"],
                    "name": category["name"],
                    "description": category["description"],
                    "imageUrl": category["image_url"],
                    "subcategories": list(subcategory_map.values()),
                }
            )

        return catalog


def _get_products_by_ids(cursor: sqlite3.Cursor, product_ids: List[int]) -> Dict[int, sqlite3.Row]:
    placeholders = ",".join("?" for _ in product_ids)
    rows = cursor.execute(
        f"SELECT id, name, price FROM products WHERE id IN ({placeholders});",
        product_ids,
    ).fetchall()
    return {row["id"]: row for row in rows}


def create_order(
    customer_name: str,
    email: str,
    phone: str,
    address: str,
    items: List[Dict[str, Any]],
) -> int:
    if not items:
        raise ValueError("Cart is empty.")

    with db_cursor() as cursor:
        product_ids = [int(item["productId"]) for item in items]
        products = _get_products_by_ids(cursor, product_ids)
        if len(products) != len(product_ids):
            raise ValueError("One or more products do not exist.")

        for item in items:
            quantity = int(item.get("quantity", 0))
            if quantity <= 0:
                raise ValueError("Quantities must be greater than zero.")

        timestamp = datetime.utcnow().isoformat(timespec="seconds")
        cursor.execute(
            """
            INSERT INTO orders (
                customer_name, email, phone, address, status, verification_code, created_at
            ) VALUES (?, ?, ?, ?, 'received', '', ?);
            """,
            (customer_name, email, phone, address, timestamp),
        )
        order_id = cursor.lastrowid

        for item in items:
            product_id = int(item["productId"])
            quantity = int(item["quantity"])
            cursor.execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity)
                VALUES (?, ?, ?);
                """,
                (order_id, product_id, quantity),
            )

    return order_id


def get_order_summary(order_id: int) -> Optional[Dict[str, Any]]:
    with db_cursor() as cursor:
        order = cursor.execute(
            """
            SELECT id, customer_name, email, phone, address, status, created_at
            FROM orders
            WHERE id = ?;
            """,
            (order_id,),
        ).fetchone()

        if not order:
            return None

        items = cursor.execute(
            """
            SELECT
                products.name,
                products.price,
                order_items.quantity
            FROM order_items
            JOIN products ON order_items.product_id = products.id
            WHERE order_items.order_id = ?;
            """,
            (order_id,),
        ).fetchall()

        total = sum(row["price"] * row["quantity"] for row in items)
        return {
            "id": order["id"],
            "customerName": order["customer_name"],
            "email": order["email"],
            "phone": order["phone"],
            "address": order["address"],
            "status": order["status"],
            "createdAt": order["created_at"],
            "items": [
                {
                    "name": row["name"],
                    "price": row["price"],
                    "quantity": row["quantity"],
                    "lineTotal": row["price"] * row["quantity"],
                }
                for row in items
            ],
            "total": total,
        }


def verify_order(order_id: int, verification_code: str) -> tuple[bool, str]:
    """
    Legacy helper retained for compatibility. Orders are auto-confirmed,
    so verification simply reports the current status.
    """
    summary = get_order_summary(order_id)
    if not summary:
        return False, "Order not found."
    return True, "Order already received and queued for dispatch."
