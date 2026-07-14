"""
BharatMandir — Temple Patcher
==============================
Fixes temples that were inserted with NULL fields (due to the csv_import enum bug).
This script UPDATES existing records rather than inserting new ones.

Run from your backend directory:
    cd bharatmandir/backend
    python patch_temples.py

What it does:
  1. Loads the same CSV (temples_batch1_10.csv)
  2. Cleans each row exactly like the pipeline
  3. For each slug, runs UPDATE instead of INSERT
  4. Prints a full summary
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.cleaner import clean_temple_row
from db.connection import get_db_cursor


def patch_temple(cleaned_row: dict) -> str:
    """
    UPDATE all fields of an existing temple identified by slug.
    Returns 'updated', 'not_found', or 'error:<msg>'
    """
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE temples SET
                -- Identity
                name                    = %(name)s,
                name_hindi              = %(name_hindi)s,
                name_local              = %(name_local)s,
                temple_type             = %(temple_type)s,
                architecture_style      = %(architecture_style)s,
                managing_authority      = %(managing_authority)s,
                trust_name              = %(trust_name)s,
                trust_registration_no   = %(trust_registration_no)s,

                -- Location
                latitude                = %(latitude)s,
                longitude               = %(longitude)s,
                location                = ST_GeogFromText('POINT(' || %(longitude)s || ' ' || %(latitude)s || ')'),
                address                 = %(address)s,
                city                    = %(city)s,
                district                = %(district)s,
                state                   = %(state)s,
                pincode                 = %(pincode)s,
                setting_environment     = %(setting_environment)s,
                google_maps_link        = %(google_maps_link)s,
                nearest_bus_stand       = %(nearest_bus_stand)s,
                local_landmark          = %(local_landmark)s,
                nearest_railway         = %(nearest_railway)s,
                nearest_airport         = %(nearest_airport)s,

                -- Deity
                primary_deity           = %(primary_deity)s,
                secondary_deities       = %(secondary_deities)s,
                sect                    = %(sect)s,

                -- History
                history                 = %(history)s,
                history_hindi           = %(history_hindi)s,
                sthala_purana           = %(sthala_purana)s,
                significance            = %(significance)s,
                estimated_year_built    = %(estimated_year_built)s,
                founded_by              = %(founded_by)s,
                last_renovation_year    = %(last_renovation_year)s,
                building_condition      = %(building_condition)s,
                puranic_stories         = %(puranic_stories)s,

                -- Heritage flags
                is_jyotirlinga          = %(is_jyotirlinga)s,
                is_shaktipeeth          = %(is_shaktipeeth)s,
                is_divya_desam          = %(is_divya_desam)s,
                is_ashtavinayak         = %(is_ashtavinayak)s,
                is_char_dham            = %(is_char_dham)s,
                is_heritage_site        = %(is_heritage_site)s,
                is_asi_protected        = %(is_asi_protected)s,
                is_pancha_bhuta         = %(is_pancha_bhuta)s,
                is_51_shakti_peeths     = %(is_51_shakti_peeths)s,
                is_unesco_heritage      = %(is_unesco_heritage)s,
                is_state_heritage       = %(is_state_heritage)s,

                -- Schedule
                opening_time            = %(opening_time)s,
                closing_time            = %(closing_time)s,
                afternoon_closure_start = %(afternoon_closure_start)s,
                afternoon_closure_end   = %(afternoon_closure_end)s,
                weekly_special_day      = %(weekly_special_day)s,
                online_puja_available   = %(online_puja_available)s,
                live_darshan_available  = %(live_darshan_available)s,
                live_stream_url         = %(live_stream_url)s,
                prasad_type             = %(prasad_type)s,

                -- Puja flags
                puja_rudrabhishek       = %(puja_rudrabhishek)s,
                puja_satyanarayan       = %(puja_satyanarayan)s,
                puja_havan_homa         = %(puja_havan_homa)s,
                puja_laghu_rudra        = %(puja_laghu_rudra)s,
                puja_mahamrityunjaya    = %(puja_mahamrityunjaya)s,
                puja_griha_pravesh      = %(puja_griha_pravesh)s,
                puja_naamkaran          = %(puja_naamkaran)s,
                puja_vivah              = %(puja_vivah)s,
                puja_annaprashan        = %(puja_annaprashan)s,
                puja_mundan             = %(puja_mundan)s,
                puja_pitru_tarpan       = %(puja_pitru_tarpan)s,
                puja_sahasranamarchana  = %(puja_sahasranamarchana)s,

                -- Media
                hero_image_url          = %(hero_image_url)s,
                video_aarti_url         = %(video_aarti_url)s,
                video_intro_url         = %(video_intro_url)s,
                video_360_url           = %(video_360_url)s,

                -- Finance
                bank_account_name       = %(bank_account_name)s,
                bank_name_branch        = %(bank_name_branch)s,
                bank_account_number     = %(bank_account_number)s,
                bank_ifsc               = %(bank_ifsc)s,
                upi_id                  = %(upi_id)s,
                certificate_80g_no      = %(certificate_80g_no)s,
                accept_online_donations = %(accept_online_donations)s,

                -- Donation flags
                donation_temple_renovation = %(donation_temple_renovation)s,
                donation_annadanam      = %(donation_annadanam)s,
                donation_priest_salary  = %(donation_priest_salary)s,
                donation_vedic_education = %(donation_vedic_education)s,
                donation_festival       = %(donation_festival)s,
                donation_medical_camps  = %(donation_medical_camps)s,
                donation_general        = %(donation_general)s,

                -- Facility flags
                facility_electricity    = %(facility_electricity)s,
                facility_water_supply   = %(facility_water_supply)s,
                facility_clean_toilets  = %(facility_clean_toilets)s,
                facility_wheelchair     = %(facility_wheelchair)s,
                facility_dharamshala    = %(facility_dharamshala)s,
                facility_prasad_dining  = %(facility_prasad_dining)s,
                facility_parking        = %(facility_parking)s,
                facility_security       = %(facility_security)s,
                facility_cctv           = %(facility_cctv)s,
                facility_pa_system      = %(facility_pa_system)s,
                facility_internet_wifi  = %(facility_internet_wifi)s,
                facility_library_pathshala = %(facility_library_pathshala)s,
                facility_gaushaala      = %(facility_gaushaala)s,
                facility_medical_support = %(facility_medical_support)s,

                -- Community programs
                prog_free_food          = %(prog_free_food)s,
                prog_medical_camps      = %(prog_medical_camps)s,
                prog_scholarship_edu    = %(prog_scholarship_edu)s,
                prog_womens_selfhelp    = %(prog_womens_selfhelp)s,
                prog_bhajan_kirtan      = %(prog_bhajan_kirtan)s,
                prog_disaster_relief    = %(prog_disaster_relief)s,

                -- Contact
                phone                   = %(phone)s,
                whatsapp_number         = %(whatsapp_number)s,
                official_email          = %(official_email)s,
                website_url             = %(website_url)s,
                facebook_page           = %(facebook_page)s,
                youtube_channel         = %(youtube_channel)s,
                instagram_handle        = %(instagram_handle)s,
                best_time_to_call       = %(best_time_to_call)s,

                -- Practical
                entry_fee               = %(entry_fee)s,
                dress_code              = %(dress_code)s,
                best_time_to_visit      = %(best_time_to_visit)s,

                -- Tags
                category_tags           = %(category_tags)s

            WHERE slug = %(slug)s
            RETURNING id, name, slug
        """, cleaned_row)
        result = cur.fetchone()
        return 'updated' if result else 'not_found'


def run_patch(csv_path: str):
    print("\n" + "="*50)
    print("  🔧  BharatMandir Temple Patcher")
    print("="*50)

    if not os.path.exists(csv_path):
        print(f"❌ CSV not found: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path, dtype=str).fillna('')
    print(f"📂 Loaded {len(df)} rows from {csv_path}")

    updated    = []
    not_found  = []
    failed     = []

    for i, raw_row in enumerate(df.to_dict(orient='records')):
        name = raw_row.get('name', 'Unknown')
        try:
            cleaned = clean_temple_row(raw_row)
            result  = patch_temple(cleaned)
            if result == 'updated':
                updated.append(name)
                print(f"  ✅ [{i+1}] Updated: {name}")
            else:
                not_found.append(name)
                print(f"  ⚠️  [{i+1}] Not found in DB (will need insert): {name}")
        except Exception as e:
            failed.append({'name': name, 'error': str(e)})
            print(f"  ❌ [{i+1}] Error: {name} → {e}")

    print(f"\n{'='*50}")
    print(f"  🏁  PATCH COMPLETE")
    print(f"{'='*50}")
    print(f"  ✅ Updated:   {len(updated)} temples")
    print(f"  ⚠️  Not found: {len(not_found)} temples")
    print(f"  ❌ Failed:    {len(failed)} temples")

    if not_found:
        print(f"\n  Temples not in DB (run run_batch1_insert.py for these):")
        for n in not_found:
            print(f"    → {n}")

    if failed:
        print(f"\n  Errors:")
        for f in failed:
            print(f"    → {f['name']}: {f['error']}")
    print()


if __name__ == "__main__":
    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data", "temples.csv"
    )
    run_patch(csv_path)