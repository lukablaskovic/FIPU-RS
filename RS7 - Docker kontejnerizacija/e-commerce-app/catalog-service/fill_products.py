import argparse
import sqlite3
from pathlib import Path

from db import DEFAULT_DB_PATH, EXPECTED_PRODUCT_COLUMNS, init_db
from helpers.sqlite_utils import connect
from logging_setup import logging_setup

logger = logging_setup.get_logger()

PREDEFINED_PRODUCTS: list[dict[str, object]] = [
    {
        "id": "p001",
        "name": "Muška Hoodica NEMREM",
        "category": "Hoodice",
        "price": 36.90,
        "currency": "EUR",
        "description": "Muška Hoodica NEMREM. Recite im natpisom na duksi (hoodici) kaj mislite. Dođe s vremena na vrijeme dan kad jednostavno više niš nemrete. Ova Zagreb Facts muška duksa (hoodica) supač ide na trapke, hlače ili trenitku. Kak' god skombinirate, nemrete fulati.",
        "shipping_time": "3-10 radnih dana",
        "amount_available": 35,
        "public_image_url": "https://www.zgfshop.hr/112-medium_default/muska-hoodica-fkt-mi-se-ne-da.jpg",
    },
    {
        "id": "p002",
        "name": "BASE pamučna majica kratkih rukava",
        "category": "Majice",
        "price": 15.00,
        "currency": "EUR",
        "description": "Klasična pamučna majica - nema tu šta više za dodati.",
        "shipping_time": "2-4 radna dana",
        "amount_available": 120,
        "public_image_url": "https://jako.hr/images/thumbs/0007852_6165_09.jpeg",
    },
    {
        "id": "p003",
        "name": "Košulja dugih rukava Jeordie's",
        "category": "Košulje",
        "price": 51.99,
        "currency": "EUR",
        "description": "Prozračna Slim Fit košulja dugih rukava. 60% pamuk, 40% poliestersko vlakno. Idealna za toplije dane.",
        "shipping_time": "3-5 radnih dana",
        "amount_available": 40,
        "public_image_url": "https://www.jeordiesmen.com/uploads/product/big/2_JRT20SF05M003_C027.jpg",
    },
    {
        "id": "p004",
        "name": "Polo majica ženska Grand 269",
        "category": "Majice",
        "price": 17.50,
        "currency": "EUR",
        "description": "Lagano strukiran kroj s prorezima s bočnim šavovima, ovratnik s kontrastnom trakom od rebraste pletenine 1:1, uska poprečna traka s 5 gumba u boji materijala, prorezi u bočnim šavovima s kontrastnom trakom, unutarnji dio ovratnika zaštićen kontrastnom trakom, trakom ojačani šavovi na ramenima, pamuk oplemenjen mercerizacijom.",
        "shipping_time": "2-4 radna dana",
        "amount_available": 55,
        "public_image_url": "https://novival.hr/wp-content/uploads/2025/09/269_02_cw400.jpg",
    },
    {
        "id": "p005",
        "name": "Traperice LEVI'S Slimfit - plava boja",
        "category": "Hlače",
        "price": 59.00,
        "currency": "EUR",
        "description": "Traperice ravnog kroja s umjerenom elastičnošću za udobnost kroz cijeli dan.",
        "shipping_time": "3-5 radnih dana",
        "amount_available": 65,
        "public_image_url": "https://images.shopsycdn.com/products/17/50/175042d7c783f1ed87b38a65775990e9.webp",
    },
    {
        "id": "p006",
        "name": "G-STAR Tapered Chino hlače 'Kate' - Bež boja",
        "category": "Hlače",
        "price": 45.00,
        "currency": "EUR",
        "description": "Dizajn: 5-džepni stil, Bočni džepovi, Zatvaranje na gumbe; Vrsta zatvaranja: Zatvarač; Materijal: Pamuk; Uzorak: Jednobojno; Dodaci: Zakrpa marke, Narukvice/trake za remen; Dužina: 7/8 duljina; Kroj: Tapered; Struk: Srednje visoki struk",
        "shipping_time": "3-5 radnih dana",
        "amount_available": 50,
        "public_image_url": "https://cdn.aboutstatic.com/file/images/70ae399549e31eccf6c67285e6e6e59d.jpg?brightness=0.96&quality=75&trim=1&height=1280&width=960",
    },
    {
        "id": "p007",
        "name": "Adidas TECH APP S-PANT, muške hlače, crna)",
        "category": "Trenirke",
        "price": 29.90,
        "currency": "EUR",
        "description": "adidas Tech Apparel Trackpant su muške duge hlače koje su stvorene za brojne sportske aktivnosti. Izrađene su od blago rastezljivog recikliranog umjetnog materijala. Tehnologija Climacool osigurava brzo sušenje, prozračnost i uklanjanje vlage. Elastičan pojas nudi udobno prianjanje. Imaju dva bočna džepa s patentnim zatvaračima. Nogavice završavaju rubom. Dizajnirane su u...",
        "shipping_time": "2-4 radna dana",
        "amount_available": 80,
        "public_image_url": "https://www.intersport.hr/media/catalog/product/cache/7f6b40782d8703cf49e835b0be757464/J/M/JM8135_1_APPAREL_Photography_Front_Center_View_white_5.png",
    },
    {
        "id": "p008",
        "name": "Energetics OLAN II W, ženske fitnes hlače, crna",
        "category": "Trenirke",
        "price": 37.99,
        "currency": "EUR",
        "description": "Energetics Olan II W su ženske duge hlače koje su kao stvorene za brojne sportske aktivnosti i slobodno vrijeme. Izrađene su od ugodne mješavine prirodnog i umjetnog materijala koji nudi obilje udobnosti pri nošenju. Elastični pojas s vrpcom nudi udobno prilagođavanje. Imaju dva bočna džepa. Dizajnirane su u opuštenom kroju, bez patenta na donjem rubu nogavica.",
        "shipping_time": "2-4 radna dana",
        "amount_available": 70,
        "public_image_url": "https://www.intersport.hr/media/catalog/product/cache/5864b084779f11fa289096d3dce89f9c/e/n/energetics_432968_050_hero_5.png",
    },
    {
        "id": "p009",
        "name": "JXESME Pleteni pulover",
        "category": "Pletivo",
        "price": 49.99,
        "currency": "EUR",
        "description": "Ovo je vrsta opuštenog pletiva koje možete nositi vikendom uz traperice, kao i preko košulje i hlača u uredu. Ravno pletivo je pletena tkanina s udobnošću i fleksibilnošću.",
        "shipping_time": "3-6 radnih dana",
        "amount_available": 45,
        "public_image_url": "https://images.jackjones.com/12293724/5022081/002/jjxx-jxesmev-neckknit-brown.png?v=a070351656832477e45562b2010cbfc5&format=webp&width=2048&quality=90&key=22-0-3&bg-color=%23f5f5f5",
    },
    {
        "id": "p010",
        "name": "Falconeri: Kardigan s gumbima od kašmira",
        "category": "Pletivo",
        "price": 250.00,
        "currency": "EUR",
        "description": "Pozornost posvećena detaljima i profinjena pređa obilježja su ovog kardigana od mekog kašmirskog pletiva. S elegantnim ovratnikom V-izreza ovaj kardigan kopča se gumbima po sredini i ima našivene prednje džepove. Regularni kroj uravnotežuje liniju te je savršen za samostalno nošenje ili u kombinaciji s drugim odjevnim predmetima.",
        "shipping_time": "3-6 radnih dana",
        "amount_available": 30,
        "public_image_url": "https://www.falconeri.com/dw/image/v2/BKQL_PRD/on/demandware.static/-/Sites-FAL_EC_COM/default/dw336216b0/images/UML250S9400-F.jpg?sfrm=png&bgcolor=f4f4f4&sw=1536&q=80",
    },
    {
        "id": "p011",
        "name": "Faina Prijelazni kaput - Menta boja",
        "category": "Jakne",
        "price": 69.00,
        "currency": "EUR",
        "description": "Lagani baloner s pojasom. Štiti od vjetra i lagane kiše, elegantan i funkcionalan.",
        "shipping_time": "3-6 radnih dana",
        "amount_available": 22,
        "public_image_url": "https://cdn.aboutstatic.com/file/images/d8a99cf5a1383a653f909c1af7f0197a.jpg?brightness=0.96&quality=75&trim=1&height=1280&width=960",
    },
    {
        "id": "p012",
        "name": "PREITAN - Ljetna jakna - insignia blue",
        "category": "Jakne",
        "price": 89.99,
        "currency": "EUR",
        "description": "Topla zimska jakna s kapuljačom. Punjenje srednje gustoće, kroj prilagođen svakodnevnoj upotrebi.",
        "shipping_time": "4-7 radnih dana",
        "amount_available": 18,
        "public_image_url": "https://img01.ztat.net/article/spp-media-p1/58e3aabb9d7b4da7a73780a365fbd4a4/2726d65504e54b12bf5a8d37d4958d80.jpg?imwidth=1800&filter=packshot",
    },
    {
        "id": "p013",
        "name": "Karen by Simonsen: Dnevna haljina - ursula print simply taupe",
        "category": "Haljine",
        "price": 154.00,
        "currency": "EUR",
        "description": "Lepršava dnevna haljina izrađena od 100% viskoze. Plitki V-izrez, uzorak s prijelazom boje. Regularni kroj, dužina do koljena.",
        "shipping_time": "3-5 radnih dana",
        "amount_available": 25,
        "public_image_url": "https://img01.ztat.net/article/spp-media-p1/a748b2f4fce4483d8926e6ffa451c614/47389c9413a84fc49d5eea42ba8fac4d.jpg?imwidth=1800",
    },
    {
        "id": "p014",
        "name": "Suknja Versace Jeans Couture",
        "category": "Suknje",
        "price": 169.90,
        "currency": "EUR",
        "description": "Suknja iz kolekcije Versace Jeans Couture izrađena od pletiva s uzorkom. Visoko elastičan materijal jamči potpunu slobodu kretanja.",
        "shipping_time": "3-5 radnih dana",
        "amount_available": 28,
        "public_image_url": "https://images.shopsycdn.com/products/0a/63/0a63a4eddeb196f42a6caac60c3ac1d7.webp",
    },
    {
        "id": "p015",
        "name": "PRMattes - Majica - true black",
        "category": "Majice",
        "price": 41.90,
        "currency": "EUR",
        "description": "Predivna muška majica od 100% pamuka. Elegantan kroj, boja true black, okrugli izrez, preokrenuti ovratnik s gumbima. Džep na prsima.",
        "shipping_time": "2-4 radna dana",
        "amount_available": 90,
        "public_image_url": "https://img01.ztat.net/article/spp-media-p1/a50425cfaaec481a8b10244d5a9b4565/db9e6bafe9e54390abea677706c4f3f8.jpg?imwidth=1800&filter=packshot",
    },
    {
        "id": "p016",
        "name": "Adidas U BL SHORT, dječje kratke hlače, crna",
        "category": "Kratke hlače",
        "price": 20.00,
        "currency": "EUR",
        "description": "adidas Essentials Big Logo Cotton Shorts su dječje sportske kratke hlače za trening i slobodno vrijeme. Dizajnirane su u modernom kroju. Izrađene su od udobnog prirodnog materijala. Imaju elastični pojas s vrpcom i dva bočna džepa. Ukrašene su velikim zaštitnim znakom adidas.",
        "shipping_time": "2-4 radna dana",
        "amount_available": 60,
        "public_image_url": "https://www.intersport.hr/media/catalog/product/cache/382907d7f48ae2519bf16cd5f39b77f9/H/Y/HY4718_1_APPAREL_Photography_Front_View_white_5.jpg",
    },
    {
        "id": "p017",
        "name": "Next - SET - Pidžame - white",
        "category": "Pidžame",
        "price": 35.00,
        "currency": "EUR",
        "description": "Udoban pidžama set od mekanog pamuka. Gornji dio i hlače s opuštenim krojem.",
        "shipping_time": "2-5 radnih dana",
        "amount_available": 44,
        "public_image_url": "https://img01.ztat.net/article/spp-media-p1/6766526c18da495ba8a66ee7719823e5/de9b27308c9b4f238117137e61da42f5.jpg?imwidth=762&filter=packshot",
    },
    {
        "id": "p018",
        "name": "ZARA: UDOBAN SAKO OD ODIJELA",
        "category": "Sakoi",
        "price": 89.00,
        "currency": "EUR",
        "description": "Slim fit sako od tkanine s viskozom. Ovratnik s reverima. Dugi rukavi s manžetama i ukrasnim gumbima. Obrubljeni džep na prsima i džepovi s preklopima na bokovima. Unutarnji džep. Prorezi straga. Kopčanje gumbima sprijeda.",
        "shipping_time": "4-7 radnih dana",
        "amount_available": 16,
        "public_image_url": "https://static.zara.net/assets/public/46a6/0a74/3f25414db577/a56c50e3cc4b/01564300420-e1/01564300420-e1.jpg?ts=1753725354215&w=2240",
    },
    {
        "id": "p019",
        "name": "Nike U NK EVERYDAY CUSH ANKLE 3PR, muške čarape za fitnes, bijela",
        "category": "Čarape",
        "price": 19.90,
        "currency": "EUR",
        "description": "Nike U Nk Everyday Cush Ankle 3Pr su veoma udobne čarape savršene za sve sportske i rekreativne aktivnosti. Izrađene su od kvalitetnog materijala koji osigurava udobnost i ugodan osjećaj tokom cijelog dana.",
        "shipping_time": "2-4 radna dana",
        "amount_available": 110,
        "public_image_url": "https://www.intersport.hr/media/catalog/product/cache/5864b084779f11fa289096d3dce89f9c/s/x/sx7667-100-phcfh001-1000.jpeg",
    },
    {
        "id": "p020",
        "name": "Muški kaiš Replay",
        "category": "Kaiši",
        "price": 29.00,
        "currency": "EUR",
        "description": "Muški kožni kaiš REPLAY tamno smeđe boje. Obujam je od 105 do 135 cm. Kolekcija: Proljeće/ljeto 2022",
        "shipping_time": "4-7 radnih dana",
        "amount_available": 12,
        "public_image_url": "https://www.nsport.ba/UserFiles/products/big/10/12/muski-kais-replay-2417A3001-128.jpg",
    },
]


def _validate_products() -> None:
    if len(PREDEFINED_PRODUCTS) != 20:
        raise RuntimeError(
            f"Expected exactly 20 products, got: {len(PREDEFINED_PRODUCTS)}"
        )

    seen_ids: set[str] = set()
    for p in PREDEFINED_PRODUCTS:
        pid = str(p.get("id"))
        if pid in seen_ids:
            raise RuntimeError(f"Duplicate product id: {pid}")
        seen_ids.add(pid)

        for col in EXPECTED_PRODUCT_COLUMNS:
            if col not in p:
                raise RuntimeError(f"Product {pid} is missing required field: {col}")

        if str(p.get("currency")) != "EUR":
            raise RuntimeError(
                f"Product {pid} must have currency EUR, got: {p.get('currency')}"
            )

        if p.get("public_image_url") is None:
            raise RuntimeError(
                f"Product {pid} has public_image_url=None (must be a string)"
            )


def fill_db(db_path: Path, *, reset_schema: bool, append: bool) -> int:
    _validate_products()

    try:
        init_db(db_path, reset=bool(reset_schema))
    except RuntimeError:
        init_db(db_path, reset=True)

    with connect(db_path) as conn:
        try:
            conn.execute("BEGIN;")
            if not append:
                conn.execute("DELETE FROM products;")

            conn.executemany(
                """
                INSERT INTO products (
                  id, name, category, price, currency, description, shipping_time, amount_available, public_image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """.strip(),
                [
                    (
                        str(p["id"]),
                        str(p["name"]),
                        str(p["category"]),
                        float(p["price"]),
                        str(p["currency"]),
                        str(p["description"]),
                        str(p["shipping_time"]),
                        int(p["amount_available"]),
                        str(p["public_image_url"]),
                    )
                    for p in PREDEFINED_PRODUCTS
                ],
            )

            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            raise RuntimeError(
                "Unable to insert products (likely duplicate IDs). "
                "Run without --append or clear the table first."
            ) from e

        broj = conn.execute("SELECT COUNT(1) FROM products;").fetchone()[0]
        return int(broj)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fill the catalog-service SQLite database with 20 predefined clothing products (EUR). "
            "Public image URLs are intentionally empty."
        )
    )
    parser.add_argument(
        "--db",
        dest="db_path",
        default=str(DEFAULT_DB_PATH),
        help=f"Path to sqlite db file (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--reset-schema",
        action="store_true",
        help="Drop and recreate the `products` table if schema mismatch is detected",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Do not delete existing products before inserting (may fail on duplicates)",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path).expanduser().resolve()

    logger.info("Filling database: %s", db_path)
    logger.info("Mode: %s", "APPEND" if args.append else "RESET DATA")

    total = fill_db(
        db_path, reset_schema=bool(args.reset_schema), append=bool(args.append)
    )

    logger.info("Done. Total products in DB: %s", total)
    return 0


#   python3 fill_products.py (dodaje svih 20 gore definiranih proizvoda u sqlite)
#   python3 fill_products.py --db products.db
#   python3 fill_products.py --reset-schema

if __name__ == "__main__":
    raise SystemExit(main())
