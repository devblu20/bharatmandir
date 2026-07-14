"""
BharatMandir — Reset & Reimport Pipeline
=========================================
Steps:
  1. DELETE all data from temples + related tables (cascade)
  2. Read all 4 CSV files from /data/
  3. Assign hero_image_url as a real Wikimedia Commons URL per temple
     (no local file paths — pure https:// URLs)
  4. Clean + insert every temple row using the full v2 schema

Usage (from backend/):
    python pipeline/reset_and_reimport.py

Environment:
    Needs DATABASE_URL in .env  (already present)
"""

import sys
import os

# ── Path setup ─────────────────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from pipeline.cleaner  import clean_temple_row
from pipeline.inserter import bulk_insert_temples

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# ── Data directory ─────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

CSV_FILES = [
    "temples.csv",
  
]

# ══════════════════════════════════════════════════════════════════════════
# HERO IMAGE URL MAP
# Key   = temple slug  (from CSV — used as unique identifier)
# Value = direct Wikimedia Commons / Wikipedia image URL  (https, no auth)
#
# All URLs point to actual public-domain / CC-licensed images.
# Slugs not listed here get a category-based fallback URL.
# ══════════════════════════════════════════════════════════════════════════

HERO_IMAGE_URLS: dict[str, str] = {
    # ── Madhya Pradesh ──────────────────────────────────────────────────
    "omkareshwar-jyotirlinga-khandwa":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Omkareshwar_temple.jpg/1200px-Omkareshwar_temple.jpg",
    "mamleshwar-temple-omkareshwar":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Omkareshwar_temple.jpg/1200px-Omkareshwar_temple.jpg",
    "pashupatinath-mandsaur":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Pashupatinath_temple_mandsaur.jpg/1200px-Pashupatinath_temple_mandsaur.jpg",
    "pitambara-peeth-datia":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Pitambara_Peeth.jpg/1200px-Pitambara_Peeth.jpg",
    "mahakaleshwar-ujjain":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Mahakaleshwar_Temple_Ujjain.jpg/1200px-Mahakaleshwar_Temple_Ujjain.jpg",
    "kal-bhairav-temple-ujjain":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Kal_Bhairav_Temple%2C_Ujjain.jpg/1200px-Kal_Bhairav_Temple%2C_Ujjain.jpg",
    "harsiddhi-temple-ujjain":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Harsiddhi_Temple_Ujjain.jpg/1200px-Harsiddhi_Temple_Ujjain.jpg",
    "mangalnath-temple-ujjain":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Mangalnath_Temple_Ujjain.jpg/1200px-Mangalnath_Temple_Ujjain.jpg",
    "gadkalika-temple-ujjain":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Gadkalika_temple_Ujjain.jpg/1200px-Gadkalika_temple_Ujjain.jpg",
    "chintaman-ganesh-ujjain":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Chintaman_Ganesh_temple_Ujjain.jpg/1200px-Chintaman_Ganesh_temple_Ujjain.jpg",
    "sandipani-ashram-ujjain":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Sandipani_Ashram_Ujjain.jpg/1200px-Sandipani_Ashram_Ujjain.jpg",
    "bhartrihari-caves-ujjain":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Bhartrihari_Caves_Ujjain.jpg/1200px-Bhartrihari_Caves_Ujjain.jpg",
    "triveni-sangam-ujjain":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Triveni_Sangam_Ujjain.jpg/1200px-Triveni_Sangam_Ujjain.jpg",
    "siddhavat-temple-ujjain":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Ram_Ghat_Ujjain.jpg/1200px-Ram_Ghat_Ujjain.jpg",

    # ── South India ─────────────────────────────────────────────────────
    "tirupati-balaji-tirumala":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Tirumala_temple.jpg/1200px-Tirumala_temple.jpg",
    "meenakshi-amman-madurai":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Meenakshi_Amman_Temple.jpg/1200px-Meenakshi_Amman_Temple.jpg",
    "rameshwaram-jyotirlinga":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Ramanathaswamy_Temple.jpg/1200px-Ramanathaswamy_Temple.jpg",
    "brihadeeswarar-temple-thanjavur":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Brihadeswarar_Temple.jpg/1200px-Brihadeswarar_Temple.jpg",
    "padmanabhaswamy-temple-thiruvananthapuram":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Sree_Padmanabhaswamy_Temple.jpg/1200px-Sree_Padmanabhaswamy_Temple.jpg",
    "guruvayur-temple-kerala":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Guruvayur_Temple.jpg/1200px-Guruvayur_Temple.jpg",
    "sabarimala-ayyappa-temple":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Sabarimala_temple.jpg/1200px-Sabarimala_temple.jpg",
    "chamundeshwari-mysore":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Chamundeshwari_temple_mysore.jpg/1200px-Chamundeshwari_temple_mysore.jpg",
    "sringeri-sharada-temple":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Sringeri_Sharada_Temple.jpg/1200px-Sringeri_Sharada_Temple.jpg",
    "udupi-krishna-temple":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Udupi_Krishna_temple.jpg/1200px-Udupi_Krishna_temple.jpg",
    "murudeshwar-temple":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Murudeshwar_Temple.jpg/1200px-Murudeshwar_Temple.jpg",
    "kollur-mookambika-temple":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Kollur_Mookambika_Temple.jpg/1200px-Kollur_Mookambika_Temple.jpg",
    "subramanya-temple-kukke":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Kukke_Subramanya_Temple.jpg/1200px-Kukke_Subramanya_Temple.jpg",
    "nataraja-temple-chidambaram":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Chidambaram_Nataraja_temple.jpg/1200px-Chidambaram_Nataraja_temple.jpg",
    "arunachaleswarar-temple-tiruvannamalai":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Tiruvannamalai_temple.jpg/1200px-Tiruvannamalai_temple.jpg",
    "kapaleeshwarar-temple-chennai":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Kapaleeshwarar_temple.jpg/1200px-Kapaleeshwarar_temple.jpg",
    "ekambareshwarar-temple-kanchipuram":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Ekambareswarar_Temple.jpg/1200px-Ekambareswarar_Temple.jpg",

    # ── UP / Rajasthan / Maharashtra ────────────────────────────────────
    "kashi-vishwanath-varanasi":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Kashi_Vishwanath_Temple.jpg/1200px-Kashi_Vishwanath_Temple.jpg",
    "sankat-mochan-varanasi":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Sankat_Mochan_Temple_Varanasi.jpg/1200px-Sankat_Mochan_Temple_Varanasi.jpg",
    "mrityunjaya-mahadev-varanasi":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Varanasi_Ghats.jpg/1200px-Varanasi_Ghats.jpg",
    "vrindavan-banke-bihari":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Banke_Bihari_Temple_Vrindavan.jpg/1200px-Banke_Bihari_Temple_Vrindavan.jpg",
    "krishna-janmabhoomi-mathura":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Krishna_Janmabhoomi.jpg/1200px-Krishna_Janmabhoomi.jpg",
    "dwarkadhish-mathura":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Dwarkadhish_Temple.jpg/1200px-Dwarkadhish_Temple.jpg",
    "ram-mandir-ayodhya":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Ram_Mandir_Ayodhya_2024.jpg/1200px-Ram_Mandir_Ayodhya_2024.jpg",
    "hanuman-garhi-ayodhya":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Hanuman_Garhi_Ayodhya.jpg/1200px-Hanuman_Garhi_Ayodhya.jpg",
    "naimisharanya-chakrateertha":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Naimisharanya.jpg/1200px-Naimisharanya.jpg",
    "vindyavasini-vindhyachal":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Vindhyavasini_Temple.jpg/1200px-Vindhyavasini_Temple.jpg",
    "shirdi-sai-baba":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Shirdi_Sai_Baba_Temple.jpg/1200px-Shirdi_Sai_Baba_Temple.jpg",
    "trimbakeshwar-jyotirlinga":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Trimbakeshwar_Temple.jpg/1200px-Trimbakeshwar_Temple.jpg",
    "bhimashankar-jyotirlinga":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Bhimashankar_Temple.jpg/1200px-Bhimashankar_Temple.jpg",
    "grishneshwar-jyotirlinga":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Grishneshwar_Temple.jpg/1200px-Grishneshwar_Temple.jpg",
    "kolhapur-mahalakshmi":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Mahalakshmi_Temple_Kolhapur.jpg/1200px-Mahalakshmi_Temple_Kolhapur.jpg",
    "pandharpur-vitthal":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Pandarpur_temple.jpg/1200px-Pandarpur_temple.jpg",
    "tulja-bhavani-tuljapur":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Tulja_Bhavani_Temple.jpg/1200px-Tulja_Bhavani_Temple.jpg",
    "akkalkot-swami-samarth":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Akkalkot_Swami_Samarth_Temple.jpg/1200px-Akkalkot_Swami_Samarth_Temple.jpg",
    "pushkar-brahma-temple":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Brahma_Temple_Pushkar.jpg/1200px-Brahma_Temple_Pushkar.jpg",
    "eklingji-temple-udaipur":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Eklingji_Temple.jpg/1200px-Eklingji_Temple.jpg",
    "ranakpur-jain-temple":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Ranakpur_jain_temple.jpg/1200px-Ranakpur_jain_temple.jpg",
    "khatu-shyam-sikar":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Khatu_Shyam_Temple.jpg/1200px-Khatu_Shyam_Temple.jpg",
    "salasar-balaji":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Salasar_Balaji_Temple.jpg/1200px-Salasar_Balaji_Temple.jpg",
    "govind-devji-jaipur":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Govind_Devji_Temple_Jaipur.jpg/1200px-Govind_Devji_Temple_Jaipur.jpg",
    "birla-mandir-jaipur":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Birla_Temple_Jaipur.jpg/1200px-Birla_Temple_Jaipur.jpg",
    "tanot-mata-jaisalmer":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Tanot_Mata_Temple.jpg/1200px-Tanot_Mata_Temple.jpg",
}

# ── Fallback images by deity / sect ────────────────────────────────────────
DEITY_FALLBACK_URLS: dict[str, str] = {
    "Lord Shiva":      "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Shiva_the_Great.jpg/800px-Shiva_the_Great.jpg",
    "Goddess Durga":   "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Durga_Mata.jpg/800px-Durga_Mata.jpg",
    "Lord Vishnu":     "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Lord_Vishnu.jpg/800px-Lord_Vishnu.jpg",
    "Lord Ganesha":    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Ganesha_Basohli_miniature_circa_1730_Dubost_p73.jpg/800px-Ganesha_Basohli_miniature_circa_1730_Dubost_p73.jpg",
    "Lord Hanuman":    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Hanuman_Chalisa_p1.jpg/800px-Hanuman_Chalisa_p1.jpg",
    "Lord Krishna":    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Krishna_Arjuna_Gita.jpg/800px-Krishna_Arjuna_Gita.jpg",
    "Lord Rama":       "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Ram_Darbar.jpg/800px-Ram_Darbar.jpg",
    "Goddess Lakshmi": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Lakshmi_Puja.jpg/800px-Lakshmi_Puja.jpg",
    "Goddess Saraswati":"https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Goddess_Saraswati.jpg/800px-Goddess_Saraswati.jpg",
    "Lord Ayyappa":    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Sabarimala_temple.jpg/800px-Sabarimala_temple.jpg",
    "Lord Murugan":    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Murugan_swami.jpg/800px-Murugan_swami.jpg",
    "Lord Venkateswara":"https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Tirumala_temple.jpg/800px-Tirumala_temple.jpg",
    "Lord Nataraja":   "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Chidambaram_Nataraja_temple.jpg/800px-Chidambaram_Nataraja_temple.jpg",
}

DEFAULT_IMAGE_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/"
    "Hindu_temple_Gopuram.jpg/800px-Hindu_temple_Gopuram.jpg"
)


def resolve_hero_image(slug: str, primary_deity: str | None) -> str:
    """Return a real https:// URL for a temple's hero image."""
    # 1. Exact slug match
    if slug in HERO_IMAGE_URLS:
        return HERO_IMAGE_URLS[slug]
    # 2. Deity fallback
    if primary_deity:
        for deity_key, url in DEITY_FALLBACK_URLS.items():
            if deity_key.lower() in (primary_deity or "").lower():
                return url
    # 3. Generic temple image
    return DEFAULT_IMAGE_URL


# ══════════════════════════════════════════════════════════════════════════
# STEP 1 — Delete all temple data from Neon
# ══════════════════════════════════════════════════════════════════════════

RELATED_TABLES = [
    "temple_puja_schedule",
    "temple_priests",
    "temple_committees",
    "temple_registrations",
    "festivals",
    "sevas",
    "mantras",
]


def delete_all_temple_data():
    print("\n🗑️  STEP 1: Deleting all temple data from Neon...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()
    try:
        # Delete related tables first (foreign keys point to temples.id)
        for table in RELATED_TABLES:
            cur.execute(f"DELETE FROM {table}")
            count = cur.rowcount
            print(f"   ✅ Deleted {count:>5} rows from {table}")

        # Finally delete temples
        cur.execute("DELETE FROM temples")
        count = cur.rowcount
        print(f"   ✅ Deleted {count:>5} rows from temples")

        # Reset sequences so IDs restart from 1
        cur.execute("""
            SELECT sequence_name FROM information_schema.sequences
            WHERE sequence_schema = 'public'
        """)
        seqs = [r[0] for r in cur.fetchall()]
        for seq in seqs:
            cur.execute(f"ALTER SEQUENCE {seq} RESTART WITH 1")
        print(f"   🔄 Reset {len(seqs)} sequences")

        conn.commit()
        print("   ✅ All temple data deleted & committed.\n")
    except Exception as e:
        conn.rollback()
        print(f"   ❌ Delete failed, rolled back: {e}")
        raise
    finally:
        cur.close()
        conn.close()


# ══════════════════════════════════════════════════════════════════════════
# STEP 2 — Load CSVs
# ══════════════════════════════════════════════════════════════════════════

def load_all_csvs() -> pd.DataFrame:
    print("📂 STEP 2: Loading CSV files...")
    frames = []
    for csv_file in CSV_FILES:
        path = os.path.join(DATA_DIR, csv_file)
        if not os.path.exists(path):
            print(f"   ⚠️  File not found, skipping: {path}")
            continue
        df = pd.read_csv(path, dtype=str, encoding="utf-8")
        df.columns = df.columns.str.strip()
        df["_source_file"] = csv_file
        frames.append(df)
        print(f"   📄 {csv_file}: {len(df)} rows")
    if not frames:
        raise FileNotFoundError("No CSV files found in data/")
    combined = pd.concat(frames, ignore_index=True)
    print(f"   📊 Total rows loaded: {len(combined)}\n")
    return combined


# ══════════════════════════════════════════════════════════════════════════
# STEP 3 — Patch image URLs and clean rows
# ══════════════════════════════════════════════════════════════════════════

def prepare_rows(df: pd.DataFrame) -> list[dict]:
    print("🔧 STEP 3: Patching image URLs & cleaning rows...")
    raw_rows = df.to_dict(orient="records")
    cleaned_rows = []
    url_stats = {"slug_match": 0, "deity_fallback": 0, "default": 0}

    for raw in raw_rows:
        slug = str(raw.get("slug", "") or "").strip()
        deity = str(raw.get("primary_deity", "") or "").strip()

        # Resolve a proper https:// URL — never use local file paths
        hero_url = resolve_hero_image(slug, deity)
        raw["hero_image_url"] = hero_url

        # Track match type for stats
        if slug in HERO_IMAGE_URLS:
            url_stats["slug_match"] += 1
        elif any(d.lower() in deity.lower() for d in DEITY_FALLBACK_URLS):
            url_stats["deity_fallback"] += 1
        else:
            url_stats["default"] += 1

        # Override source with the CSV filename
        raw["source"] = raw.pop("_source_file", "csv_import")

        cleaned = clean_temple_row(raw)
        cleaned_rows.append(cleaned)

    print(f"   🖼️  Image URL assignment:")
    print(f"       Exact slug match : {url_stats['slug_match']}")
    print(f"       Deity fallback   : {url_stats['deity_fallback']}")
    print(f"       Default image    : {url_stats['default']}")
    print(f"   ✅ {len(cleaned_rows)} rows cleaned.\n")
    return cleaned_rows


# ══════════════════════════════════════════════════════════════════════════
# STEP 4 — Insert into Neon
# ══════════════════════════════════════════════════════════════════════════

def insert_rows(cleaned_rows: list[dict]):
    print(f"💾 STEP 4: Inserting {len(cleaned_rows)} temples into Neon...")
    results = bulk_insert_temples(cleaned_rows)
    print(f"\n{'='*55}")
    print(f"  🏁  PIPELINE COMPLETE")
    print(f"{'='*55}")
    print(f"  ✅ Inserted  : {len(results['inserted'])} temples")
    print(f"  ⏭️  Skipped   : {len(results['skipped'])} (duplicate slugs)")
    print(f"  ❌ Failed    : {len(results['failed'])} temples")
    if results["failed"]:
        print("\n  Failed rows:")
        for f in results["failed"]:
            print(f"    → {f['name']}: {f['error']}")
    print()


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  🛕  BharatMandir — Full Reset & Reimport")
    print("=" * 55)

    if not DATABASE_URL:
        print("❌ DATABASE_URL not set in .env — aborting.")
        sys.exit(1)

    # Confirm before wiping
    print("\n⚠️  This will DELETE all temple data and reimport from CSVs.")
    confirm = input("   Type 'yes' to continue: ").strip().lower()
    if confirm != "yes":
        print("Aborted.")
        sys.exit(0)

    delete_all_temple_data()
    df = load_all_csvs()
    cleaned = prepare_rows(df)
    insert_rows(cleaned)