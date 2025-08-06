

from flask import Flask, render_template, request, jsonify
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")
    
API_URL = "https://data.gov.il/api/3/action/datastore_search"

def fetch_records_cached(res_id, filter_field, val):
    try:
        resp = requests.get(API_URL, params={
            "resource_id": res_id,
            "filters": json.dumps({filter_field: val})
        }, timeout=10)
        resp.raise_for_status()
        return resp.json().get("result", {}).get("records", [])
    except:
        return []

 
APIS = {
    "API 1 - Private Vehicles": "053cea08-09bc-40ec-8f7a-156f0677aff3",
    "API 2 - Price Info": "39f455bf-6db0-4926-859d-017f34eacbcb",
    "API 4 - Bus Fleet": "91d298ed-a260-4f93-9d50-d5e3c5b82ce1", 
    "API 3 - Heavy Vehicles": "cd3acc5c-03c3-4c89-9c54-d40f93c0d790", 
    "API 5 - Motorcycles": "bf9df4e2-d90d-4c0a-a400-19e15af8e95f",
    "API 6 - Personal Imports": "03adc637-b6fe-402b-9937-7c3d3afc9140",
    "API 7 - Car History": "56063a99-8a3e-4ff4-912e-5966c0279bad",
    "API 8 - Public Transportation Vehicles": "cf29862d-ca25-4691-84f6-1be60dcb4a1e",
    "API 9 - Inactive Vehicles With Model Code": "f6efe89a-fb3d-43a4-bb61-9bf12a9b9099",
    "API 10 - Inactive Vehicles Without Model Code": "6f6acd03-f351-4a8f-8ecf-df792f4f573a",
    "API 11 - Cancelled Vehicles 2000-2009": "ec8cbc34-72e1-4b69-9c48-22821ba0bd6c",
    "API 12 - Cancelled Vehicles 2010-2016": "4e6b9724-4c1e-43f0-909a-154d4cc4e046",
    "API 13 - Cancelled Vehicles 2017-": "851ecab1-0622-4dbe-a6c7-f950cf82abf9",
    "API 14 - Vehicle Technical Data (WLTP)": "142afde2-6228-49f9-8a29-9b6c3a0cbe40",
    "API 15 - Disabled Parking Permit": "c8b9f9c8-4612-4068-934f-d4acd2e3c06e",
    "API 16 - Recalls": "36bf1404-0be4-49d2-82dc-2f1ead4a8b93",
    "API 17 - Tzamah Equipment": "58dc4654-16b1-42ed-8170-98fadec153ea"
}

# Field names mapping
FIELD_LABELS = {
    "mispar_rechev": "מספר לוחית רישוי",
    "tozeret_nm": "יצרן",
    "kinuy_mishari": "דגם",
    "ramat_gimur": "רמת גימור",
    "mispar_shilda": "מספר שלדה",
    "shnat_yitzur": "שנת ייצור",
    "moed_aliya_lakvish": "תאריך עלייה לכביש",
    "mivchan_acharon_dt": "תאריך טסט אחרון",
    "tokef_dt": "תוקף טסט",
    "baalut": "סוג בעלות",
    "tzeva_rechev": "צבע",
    "sug_delek_nm": "סוג דלק",
    "shem_yevuan": "שם יבואן",
    "mehir": "מחיר מכירה כחדש",
    "bus_license_id": "מספר לוחית רישוי",
    "production_year": "שנת ייצור",
    "operator_nm": "שם המפעיל",
    "cluster_nm": "אשכול",
    "stone_proof_nm": "ממוגן אבנים",
    "bullet_proof_nm": "ממוגן ירי",
    "BusSize_nm": "גודל האוטובוס",
    "BusType_nm": "סוג האוטובוס",
    "SeatsNum": "מספר מושבים",
    "total_kilometer": "קילומטראז'",
    "tkina_EU": "תקינה",
    "kvutzat_sug_rechev": "סוג רכב",
    "nefach_manoa": "נפח מנוע",
    "hanaa_nm": "סוג הנעה",
    "mishkal_kolel": "משקל כולל",
    "grira_nm": "וו גרירה",
    "bitul_nm": "סטטוס",
    "kilometer_test_aharon": "ק״מ בטסט האחרון",
    "degem_nm": "דגם",
    "tozeret_eretz_nm": "ארץ ייצור",
    "misgeret": "מספר שלדה",
    "sug_rechev_EU_cd": "קוד סוג רכב",
    "sug_rechev_nm": "סוג רכב",
    "hespek": "הספק מנוע",
    "delek_nm": "סוג דלק",
    "nefah_manoa": "נפח מנוע",
    "koah_sus": "הספק מנוע",
    "technologiat_hanaa_nm": "סוג הנעה",
    "automatic_ind": "תיבת הילוכים",
    "sug_tkina_nm": "סוג תקינה",
    "merkav": "מרכב",
    "mispar_dlatot": "מספר דלתות",
    "halon_bagg_ind": "גג שמש",
    "galgaley_sagsoget_kala_ind": "חישוקים קלים",
    "kvuzat_agra_cd": "קבוצת אגרה",
    "degem_cd": "קוד דגם",
    "rishum_rishon_dt": "תאריך רישום ראשון",
    "mkoriut_nm": "מקוריות רישוי",
    "sug_yevu": "סוג ייבוא",
    "shilda": "מספר שלדה",
    "degem_manoa": "דגם מנוע",
    "mispar_mekomot": "מספר מושבים",
    "MISPAR RECHEV": "מספר לוחית רישוי",
    "TAARICH HAFAKAT TAG": "תאריך הפקת תו",
    "SUG TAV": "סוג תו",
    "tozar": "יצרן",
    "MISPAR_RECHEV": "מספר לוחית רישוי",
    "RECALL_ID": "מספר ריקול",
    "SUG_RECALL": "סוג ריקול",
    "SUG_TAKALA": "סוג תקלה",
    "TEUR_TAKALA": "תיאור תקלה",
    "TAARICH_PTICHA": "תאריך פתיחת תקלה",
    "mispar_tzama": "מספר לוחית",
    "shilda_totzar_en_nm": "חברה",
    "degem_nm": "דגם",
    "shnat_yitzur": "שנת ייצור",
    "sug_tzama_nm": "סוג ציוד",
    "mispar_shilda": "מספר שילדה",
    "hanaa_nm": "סוג דלק",
    "koah_sus": "הספק מנוע",
    "mishkal_ton": "משקל",
    "mishkal_kolel_ton": "משקל כולל",
    "kosher_harama_ton": "כושר הרמה",
    "rishum_date": "תאריך רישום",
    "tokef_date": "תוקף רישיון",
    "hagbala_nm_1": "הגבלות",
    "hagbala_nm_2": "הגבלות",
    "hagbala_nm_3": "הגבלות",
    "hagbala_nm_4": "הגבלות",
    "bitul_dt": "תאריך ביטול"
}


# API display names for each section
API_DISPLAY_NAMES = {
    "API 1 - Private Vehicles": "רכבים פרטיים",
    "API 2 - Price Info": "יבואנים ומחירוני רכב חדש",
    "API 3 - Heavy Vehicles": "מאגר כלי רכב מעל 3.5 טוןData",
    "API 4 - Bus Fleet": "🚌 ציי רכב אוטובוסים",
    "API 5 - Motorcycles": "🛵 כלי רכב דו גלגליים",
    "API 6 - Personal Imports": "כלי רכב בייבוא אישי",
    "API 7 - Car History": "היסטוריית כלי רכב פרטיים",
    "API 8 - Public Transportation Vehicles": "🚕 כלי רכב ציבוריים פעילים",
    "API 9 - Inactive Vehicles With Model Code": "רכבים לא פעילים (עם קוד דגם)",
    "API 10 - Inactive Vehicles Without Model Code": "רכבים לא פעילים (ללא קוד דגם)",
    "API 11 - Cancelled Vehicles 2000-2009": "❌ כלי רכב שירדו מהכביש (2000-2009)",
    "API 12 - Cancelled Vehicles 2010-2016": "❌ כלי רכב שירדו מהכביש (2010-2016)",
    "API 13 - Cancelled Vehicles 2017-": "❌ כלי רכב שירדו מהכביש (2017-)",
    "API 14 - Vehicle Technical Data (WLTP)": "⚙ נתונים טכניים (WLTP)",
    "API 15 - Disabled Parking Permit": "♿ תו חניה לנכה",
    "Vehicle Registrations History": "היסטוריית לוחיות רישוי של הרכב",
    "API 16 - Recalls": "🔧 קריאות לתיקון (ריקול)",
    "API 17 - Tzamah Equipment": '🏗️ ציוד מכני הנדסי (צמ"ה)'
}

CANCELLED_APIS = [
    "API 11 - Cancelled Vehicles 2000-2009",
    "API 12 - Cancelled Vehicles 2010-2016",
    "API 13 - Cancelled Vehicles 2017-"
]

CURRENT_APIS = [
    "API 1 - Private Vehicles",
    "API 3 - Heavy Vehicles",
    "API 5 - Motorcycles",
    "API 6 - Personal Imports",
    "API 9 - Inactive Vehicles With Model Code",
    "API 10 - Inactive Vehicles Without Model Code"
]


# Field order per API
FIELD_ORDER = {
    "API 1 - Private Vehicles": ["mispar_rechev","tozeret_nm","kinuy_mishari","ramat_gimur",
                                  "mispar_shilda","misgeret","shilda","shnat_yitzur","moed_aliya_lakvish",
                                  "mivchan_acharon_dt","tokef_dt","baalut",
                                  "tzeva_rechev","sug_delek_nm"],
    "API 2 - Price Info": ["shem_yevuan","mehir","shnat_yitzur","tozeret_nm","kinuy_mishari"],
    "API 4 - Bus Fleet": ["bus_license_id","operator_nm","cluster_nm","stone_proof_nm",
                          "bullet_proof_nm","BusSize_nm","BusType_nm",
                          "SeatsNum","total_kilometer"],
    "API 3 - Heavy Vehicles": ["mispar_rechev","tozeret_nm","degem_nm","mispar_shilda","misgeret","shilda",
                             "shnat_yitzur","moed_aliya_lakvish",
                             "tkina_EU","kvutzat_sug_rechev","sug_delek_nm",
                             "nefach_manoa","hanaa_nm","mishkal_kolel","grira_nm"],
    "API 5 - Motorcycles": ["mispar_rechev","tozeret_nm","degem_nm","shnat_yitzur","moed_aliya_lakvish",
                            "sug_delek_nm","nefach_manoa","hespek","mispar_shilda","misgeret","shilda",
                            "sug_rechev_EU_cd","sug_rechev_nm","baalut","mkoriut_nm"],
    "API 6 - Personal Imports": ["mispar_rechev","tozeret_nm","degem_nm","mispar_shilda","misgeret","shilda",
                                 "shnat_yitzur","moed_aliya_lakvish","mivchan_acharon_dt",
                                 "tokef_dt","sug_delek_nm","nefach_manoa","degem_manoa",
                                 "sug_rechev_nm","tozeret_eretz_nm","sug_yevu"],
    "API 7 - Car History": ["mispar_rechev","kilometer_test_aharon","rishum_rishon_dt","mkoriut_nm"],
    "API 8 - Public Transportation Vehicles": ["mispar_rechev","tozeret_nm","degem_nm",
                                               "kinuy_mishari","shnat_yitzur","tokef_dt",
                                               "bitul_nm","bitul_dt","sug_rechev_EU_cd",
                                               "sug_rechev_nm","mispar_mekomot",
                                               "tzeva_rechev","mishkal_kolel"],
    "API 9 - Inactive Vehicles With Model Code": ["mispar_rechev","tozeret_nm","kinuy_mishari",
                                               "degem_nm","ramat_gimur","mispar_shilda","misgeret","shilda",
                                               "shnat_yitzur","moed_aliya_lakvish","mivchan_acharon_dt",
                                               "tokef_dt","baalut",
                                               "tzeva_rechev","sug_delek_nm"],
    "API 10 - Inactive Vehicles Without Model Code": ["mispar_rechev","tozeret_nm","degem_nm",
                                               "mispar_shilda","misgeret","shilda","shnat_yitzur","tkina_EU",
                                               "sug_delek_nm","nefach_manoa","hanaa_nm",
                                               "mishkal_kolel","tozeret_eretz_nm"],
    "API 11 - Cancelled Vehicles 2000-2009": ["bitul_dt","mispar_rechev","tozeret_nm",
                                               "degem_nm","kinuy_mishari","ramat_gimur",
                                               "mispar_shilda","misgeret","shilda","shnat_yitzur","moed_aliya_lakvish","baalut","sug_rechev_nm","degem_manoa",
                                               "mishkal_kolel","sug_delek_nm","tzeva_rechev"],
    "API 12 - Cancelled Vehicles 2010-2016": ["bitul_dt","mispar_rechev","tozeret_nm",
                                               "degem_nm","kinuy_mishari","ramat_gimur",
                                               "mispar_shilda","misgeret","shilda","shnat_yitzur","moed_aliya_lakvish","baalut","sug_rechev_nm","degem_manoa",
                                               "mishkal_kolel","sug_delek_nm","tzeva_rechev"],
    "API 13 - Cancelled Vehicles 2017-": ["bitul_dt","mispar_rechev","tozeret_nm",
                                               "degem_nm","kinuy_mishari","ramat_gimur",
                                               "mispar_shilda","misgeret","shilda","shnat_yitzur","moed_aliya_lakvish","baalut","sug_rechev_nm","degem_manoa",
                                               "mishkal_kolel","sug_delek_nm","tzeva_rechev"],
    "API 14 - Vehicle Technical Data (WLTP)": ["tozar","kinuy_mishari","ramat_gimur","shnat_yitzur",
                                               "tozeret_eretz_nm","delek_nm","nefah_manoa","koah_sus",
                                               "hanaa_nm","technologiat_hanaa_nm","automatic_ind","sug_tkina_nm",
                                               "merkav","mispar_dlatot","mishkal_kolel","halon_bagg_ind",
                                               "galgaley_sagsoget_kala_ind","kvuzat_agra_cd"],
    "API 15 - Disabled Parking Permit": ["MISPAR RECHEV","TAARICH HAFAKAT TAG","SUG TAV"],
    "Vehicle Registrations History": ["mispar_rechev", "bitul_dt"],
    "API 16 - Recalls": ["MISPAR_RECHEV","TAARICH_PTICHA","RECALL_ID","SUG_RECALL","SUG_TAKALA","TEUR_TAKALA"],
    "API 17 - Tzamah Equipment": ["mispar_tzama","shilda_totzar_en_nm","degem_nm","shnat_yitzur",
                                  "sug_tzama_nm","mispar_shilda","hanaa_nm","koah_sus","mishkal_ton",
                                  "mishkal_kolel_ton","kosher_harama_ton","rishum_date","tokef_date",
                                  "hagbala_nm_1","hagbala_nm_2","hagbala_nm_3","hagbala_nm_4"]

}





@app.route("/api/fetch_records")
def fetch_records_route():
    res_id = request.args.get("res_id")
    field = request.args.get("field")
    val = request.args.get("val")

    if not all([res_id, field, val]):
        return jsonify({"error": "Missing required parameters"}), 400

    records = fetch_records_cached(res_id, field, val)
    return jsonify(records)
    
    
    
    
def API_2_fetch_price(rec):
    cd = rec.get("degem_cd", "")
    nm = rec.get("degem_nm", "")
    yr = rec.get("shnat_yitzur", "")
    try:
        resp = requests.get(API_URL, params={
            "resource_id": APIS["API 2 - Price Info"],
            "q": f"{cd} {nm} {yr}".strip()
        })
        resp.raise_for_status()
        return resp.json().get("result", {}).get("records", [])
    except:
        return []

@app.route("/api/price_info", methods=["POST"])
def price_info():
    try:
        rec = request.get_json()
        if not isinstance(rec, dict):
            return jsonify({"error": "Invalid input"}), 400
        results = API_2_fetch_price(rec)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500   


def fetch_vin_records(api_name, vin, field="misgeret"):
    try:
        records = fetch_records_cached(APIS[api_name], field, vin)
        return (api_name, records)
    except:
        return (api_name, [])

@app.route("/api/fetch_vin", methods=["GET"])
def fetch_vin():
    api_name = request.args.get("api")
    vin = request.args.get("vin")
    field = request.args.get("field", "misgeret")

    if not api_name or not vin:
        return jsonify({"error": "Missing required parameters"}), 400

    api, records = fetch_vin_records(api_name, vin, field)
    return jsonify({ "api": api, "records": records })




###########################################################
############### FORMATTING HELPER #########################
###########################################################

# Format a section's records as HTML string for display

def format_section(title, recs):
    if not recs:
        return ""

    if title == "Vehicle Registrations History":
        header = API_DISPLAY_NAMES.get(title, title)
        sorted_recs = sorted(recs, key=lambda x: (x.get("bitul_dt") == "", x.get("bitul_dt", "")))
        out = (
            f"<div style='"
            "font-size: 14pt; "
            "font-weight: bold; "
            "color: #833C0C; "
            "text-align: right; "
            "margin-top: 20px; "
            "margin-bottom: 0px;'>"
            f"{header}"
            "</div>\n"
            "<div style='text-align:right; font-family:Calibri; font-size:17px;'>"
            "<b>לוחית רישוי ותאריך הורדה מהרכב:</b><br>"
        )

        for rec in sorted_recs:
            plate_raw = str(rec.get("mispar_rechev", "")).lstrip("0")
            if len(plate_raw) == 8:
                plate = f"{plate_raw[:3]}-{plate_raw[3:5]}-{plate_raw[5:]}"
            elif len(plate_raw) == 7:
                plate = f"{plate_raw[:2]}-{plate_raw[2:5]}-{plate_raw[5:]}"
            elif len(plate_raw) == 6:
                plate = f"{plate_raw[:3]}-{plate_raw[3:]}"
            elif len(plate_raw) == 5:
                plate = f"{plate_raw[:2]}-{plate_raw[2:]}"
            else:
                plate = plate_raw
            bitul = rec.get("bitul_dt")
            spaces = "&nbsp;" * (26 - len(plate))
            if not bitul or str(bitul).strip().lower() in {"", "current registration"}:
                out += f"— <b>{plate}</b>{spaces}לוחית רישוי נוכחית<br>"
            else:
                bitul_clean = str(bitul).split(" ")[0]
                try:
                    bitul_clean = f"{bitul_clean[8:]}/{bitul_clean[5:7]}/{bitul_clean[:4]}"
                except:
                    pass
                out += f"— <b>{plate}</b>{spaces}תאריך ביטול: {bitul_clean}<br>"
        return out + "</div>\n"

    header = API_DISPLAY_NAMES.get(title, title)
    out = (
        f"<div style='"
        "font-size:14pt; "
        "font-weight:bold; "
        "color:#003366; "
        "text-align:right; "
        "margin-top:14px; "
        "margin-bottom:0px;'>"
        f"{header}"
        "</div>\n"
    )
    out += "<pre style='font-family: Calibri; font-size: 17px; margin-top: 0px;'>"

    added = set()
    for rec in recs:
        for key in FIELD_ORDER.get(title, []):
            if key in rec and rec[key] is not None:
                if title == "API 17 - Tzamah Equipment" and key.startswith("hagbala_nm_"):
                    continue
                val = rec[key]
                if key in {"bitul_dt", "rishum_rishon_dt", "rishum_date", "tokef_date"}:
                    val = str(val).split(" ")[0]

                if key == "bitul_dt" and title in {
                    "API 11 - Cancelled Vehicles 2000-2009",
                    "API 12 - Cancelled Vehicles 2010-2016",
                    "API 13 - Cancelled Vehicles 2017-"
                }:
                    try:
                        val = f"{val[8:]}/{val[5:7]}/{val[:4]}"
                    except:
                        pass
                    label = f"<span style='color:#FF0000; font-weight:bold;'>{FIELD_LABELS.get(key, key)}:</span>"
                    val = f"<span style='color:#FF0000; font-weight:bold;'>{val}</span>"
                    out += f"{label}   {val}\n"
                    added.add(key)
                    continue

                if key == "tokef_dt" and title == "API 9 - Inactive Vehicles With Model Code":
                    label = f"<span style='color:#FF0000; font-weight:bold;'>{FIELD_LABELS.get(key, key)}:</span>"
                    val = f"<span style='color:#FF0000; font-weight:bold;'>{val}</span>"
                    out += f"{label}   {val} - טסט פג תוקף לפני יותר מ-13 חודשים\n"
                    added.add(key)
                    continue

                if key in {"mispar_rechev", "bus_license_id", "MISPAR RECHEV", "MISPAR_RECHEV", "mispar_tzama"}:
                    digits = str(val).lstrip("0")
                    if len(digits) == 8:
                        val = f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
                    elif len(digits) == 7:
                        val = f"{digits[:2]}-{digits[2:5]}-{digits[5:]}"
                    elif len(digits) == 6:
                        val = f"{digits[:3]}-{digits[3:]}"
                    elif len(digits) == 5:
                        val = f"{digits[:2]}-{digits[2:]}"
                    else:
                        val = digits

                if title == "API 14 - Vehicle Technical Data (WLTP)" and key == "automatic_ind":
                    val = "אוטומטית" if str(val).strip() == "1" else "ידנית"
                if title == "API 14 - Vehicle Technical Data (WLTP)" and key == "halon_bagg_ind":
                    val = "כן" if str(val).strip() == "1" else "לא"
                if title == "API 14 - Vehicle Technical Data (WLTP)" and key == "galgaley_sagsoget_kala_ind":
                    val = "כן" if str(val).strip() == "1" else "לא"
                if title == "API 15 - Disabled Parking Permit" and key == "SUG TAV":
                    val = "נכה רגיל" if str(val).strip() == "1" else "נכה עם כיסא גלגלים"

                if title == "API 9 - Inactive Vehicles With Model Code" and key == "tokef_dt":
                    try:
                        val = f"{val[8:]}/{val[5:7]}/{val[:4]} - טסט פג תוקף לפני יותר מ-13 חודשים"
                    except:
                        pass

                if title == "API 15 - Disabled Parking Permit" and key == "TAARICH HAFAKAT TAG":
                    try:
                        val = str(val)
                        val = f"{val[6:]}/{val[4:6]}/{val[:4]}"
                    except:
                        pass

                if key in {"tokef_dt", "mivchan_acharon_dt", "rishum_rishon_dt", "rishum_date", "tokef_date"}:
                    try:
                        val = f"{val[8:]}/{val[5:7]}/{val[:4]}"
                    except:
                        pass

                if key == "moed_aliya_lakvish" and len(str(val)) > 5:
                    try:
                        val = f"{val[5:]}/{val[0:4]}"
                    except:
                        pass

                if key in {"mehir"}:
                    try:
                        val = f"{int(val):,} ₪"
                    except:
                        pass

                if key in {"mishkal_kolel"}:
                    try:
                        val = f'{int(val):,} ק"ג'
                    except:
                        pass

                if key in {"total_kilometer", "kilometer_test_aharon"}:
                    try:
                        val = f'{int(val):,} ק"מ'
                    except:
                        pass

                if key in {"nefach_manoa", "nefah_manoa"}:
                    try:
                        val = f'{int(val):,} סמ"ק'
                    except:
                        pass

                if key in {"hespek", "koah_sus"}:
                    try:
                        val = f'{int(val):,} כ"ס'
                    except:
                        pass

                if key in {"mishkal_ton", "mishkal_kolel_ton", "kosher_harama_ton"}:
                    try:
                        val = f"{(val)} טון"
                    except:
                        pass

                label = FIELD_LABELS.get(key, key)
                out += f"<b>{label}:</b>   {val}\n"
                added.add(key)

        if title == "API 16 - Recalls":
            out += "\n"

        if title == "API 17 - Tzamah Equipment":
            limitation_lines = []
            for i in range(1, 5):
                lim_key = f"hagbala_nm_{i}"
                lim_val = rec.get(lim_key, "").strip()
                if lim_val:
                    limitation_lines.append(lim_val)

            if limitation_lines:
                out += "\n<span style='color:#833C0C; font-weight:bold;'>הגבלות:</span>\n"
                for line in limitation_lines:
                    out += f"–  {line}\n"
                added.add("limitations")

    return out + "</pre>\n" if added else ""



###########################################################
############### VIN SEARCH LOGIC ##########################
###########################################################

# Search all current and cancelled APIs for vehicles linked to this VIN

def search_vin(vin):
    results = []
    seen_plates = set()

    with ThreadPoolExecutor(max_workers=8) as executor:
        cancelled_futures = [executor.submit(fetch_vin_records, api, vin, "misgeret") for api in CANCELLED_APIS]
        current_futures = [executor.submit(fetch_vin_records, api, vin, "misgeret") for api in CURRENT_APIS]

        for future in cancelled_futures:
            api_name, records = future.result()
            for rec in records:
                plate = str(rec.get("mispar_rechev", "")).zfill(8)
                if plate and plate not in seen_plates:
                    seen_plates.add(plate)
                    bitul_dt = rec.get("bitul_dt", "").strip()
                    if not bitul_dt:
                        bitul_dt = "Current registration"
                    results.append({"mispar_rechev": plate, "bitul_dt": bitul_dt})

        for future in current_futures:
            api_name, records = future.result()
            for rec in records:
                plate = str(rec.get("mispar_rechev", "")).zfill(8)
                if plate and plate not in seen_plates:
                    seen_plates.add(plate)
                    results.append({"mispar_rechev": plate, "bitul_dt": ""})

    return results

@app.route("/api/search_vin", methods=["GET"])
def search_vin_route():
    vin = request.args.get("vin", "").strip()
    if not vin:
        return jsonify({"error": "Missing VIN parameter"}), 400

    results = search_vin(vin)
    return jsonify(results)








######################################################################
############### SEARCHWORKER - THREAD LOGIC ##########################
######################################################################

# Background worker to perform vehicle search logic without freezing the GUI

@app.route("/api/search_plate", methods=["GET"])
def search_plate():
    plate = request.args.get("plate", "").strip()
    mode = request.args.get("mode", "Regular")

    if not plate.isdigit():
        return jsonify({"error": "Invalid plate number"}), 400

    plate = plate.zfill(6 if mode == 'צמ"ה' else 7)
    start_time = time.time()
    res = ""

    if mode == 'צמ"ה':
        res_id = APIS["API 17 - Tzamah Equipment"]
        records = fetch_records_cached(res_id, "mispar_tzama", int(plate))
        if records:
            res += format_section("API 17 - Tzamah Equipment", records)
        else:
            res = (
                "<div style='"
                "font-family: Calibri; "
                "font-size: 20px; "
                "margin-top: 0px;'>"
                'לא נמצא כלי צמ"ה עם לוחית רישוי זו.'
                "</div>"
            )
        return jsonify({"html": res})

    vin = ""
    fallback_record = None
    sections = {}
    former_regs = []

    r1 = fetch_records_cached(APIS["API 1 - Private Vehicles"], "mispar_rechev", plate)
    if r1:
        record_plate = str(r1[0].get("mispar_rechev", "")).lstrip("0")
        if record_plate == plate.lstrip("0"):
            sections["API 1 - Private Vehicles"] = r1
        fallback_record = r1[0]

    def fetch_and_store(api_name):
        field = (
            "bus_license_id" if "Bus Fleet" in api_name else
            "MISPAR_RECHEV" if api_name == "API 16 - Recalls" else
            "MISPAR RECHEV" if api_name == "API 15 - Disabled Parking Permit" else
            "mispar_rechev"
        )
        value = plate.zfill(8) if api_name in {"API 11 - Cancelled Vehicles 2000-2009", "API 12 - Cancelled Vehicles 2010-2016"} else plate
        try:
            resp = requests.get(API_URL, params={
                "resource_id": APIS[api_name],
                "filters": json.dumps({field: str(value)})
            }, timeout=10)
            resp.raise_for_status()
            records = resp.json().get("result", {}).get("records", [])
            return (api_name, records) if records else None
        except:
            return None

    api_list = [
        "API 3 - Heavy Vehicles", "API 4 - Bus Fleet", "API 5 - Motorcycles",
        "API 6 - Personal Imports", "API 7 - Car History",
        "API 8 - Public Transportation Vehicles", "API 9 - Inactive Vehicles With Model Code",
        "API 10 - Inactive Vehicles Without Model Code", "API 11 - Cancelled Vehicles 2000-2009",
        "API 12 - Cancelled Vehicles 2010-2016", "API 13 - Cancelled Vehicles 2017-",
        "API 15 - Disabled Parking Permit", "API 16 - Recalls"
    ]

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_results = executor.map(fetch_and_store, api_list)
    for result in future_results:
        if result:
            api_name, recs = result
            sections[api_name] = recs

    vin_set = set()
    if r1:
        vin_from_r1 = r1[0].get("misgeret", "") or r1[0].get("shilda", "") or r1[0].get("mispar_shilda", "")
        if vin_from_r1:
            vin_set.add(vin_from_r1)
    if not vin_set:
        for source in [
            sections.get("API 3 - Heavy Vehicles", [{}])[0],
            sections.get("API 5 - Motorcycles", [{}])[0],
            sections.get("API 6 - Personal Imports", [{}])[0]
        ]:
            for field in ["misgeret", "shilda", "mispar_shilda"]:
                val = source.get(field, "").strip()
                if val:
                    vin_set.add(val)
                    break
    for source in [
        r1[0] if r1 else {},
        sections.get("API 3 - Heavy Vehicles", [{}])[0],
        sections.get("API 5 - Motorcycles", [{}])[0],
        sections.get("API 6 - Personal Imports", [{}])[0],
        sections.get("API 9 - Inactive Vehicles With Model Code", [{}])[0],
        sections.get("API 10 - Inactive Vehicles Without Model Code", [{}])[0],
    ]:
        for field in ["misgeret", "shilda", "mispar_shilda"]:
            val = source.get(field, "").strip()
            if val:
                vin_set.add(val)

    for api_name in ["API 11 - Cancelled Vehicles 2000-2009",
                     "API 12 - Cancelled Vehicles 2010-2016",
                     "API 13 - Cancelled Vehicles 2017-"]:
        for rec in sections.get(api_name, []):
            for field in ["misgeret", "shilda", "mispar_shilda"]:
                val = rec.get(field, "").strip()
                if val:
                    vin_set.add(val)

    former_regs = []
    vin_results_cache = {}

    def safe_search_vin(vin):
        if vin in vin_results_cache:
            return vin_results_cache[vin]
        result = search_vin(vin)
        vin_results_cache[vin] = result
        return result

    with ThreadPoolExecutor(max_workers=10) as executor:
        all_results = executor.map(safe_search_vin, vin_set)
    for result in all_results:
        former_regs.extend(result)
    if former_regs:
        sections["Vehicle Registrations History"] = former_regs

    if not fallback_record:
        for api in ["API 6 - Personal Imports", "API 9 - Inactive Vehicles With Model Code"]:
            if api in sections and sections[api]:
                fallback_record = sections[api][0]
                break

    if fallback_record:
        if "API 2 - Price Info" not in sections:
            p2 = API_2_fetch_price(fallback_record)
            if p2:
                sections["API 2 - Price Info"] = p2
        if "API 7 - Car History" not in sections:
            r7 = fetch_records_cached(APIS["API 7 - Car History"], "mispar_rechev", fallback_record.get("mispar_rechev", ""))
            if r7:
                sections["API 7 - Car History"] = r7
        if "API 14 - Vehicle Technical Data (WLTP)" not in sections:
            cd = fallback_record.get("degem_cd", "")
            nm = fallback_record.get("degem_nm", "")
            yr = fallback_record.get("shnat_yitzur", "")
            qval = f"{cd} {nm} {yr}".strip()
            try:
                resp14 = requests.get(API_URL, params={
                    "resource_id": APIS["API 14 - Vehicle Technical Data (WLTP)"],
                    "q": qval
                })
                resp14.raise_for_status()
                r14 = resp14.json().get("result", {}).get("records", [])
                if r14:
                    sections["API 14 - Vehicle Technical Data (WLTP)"] = r14
            except:
                pass

    desired_api_order = [
        "API 1 - Private Vehicles",
        "API 11 - Cancelled Vehicles 2000-2009",
        "API 12 - Cancelled Vehicles 2010-2016",
        "API 13 - Cancelled Vehicles 2017-",
        "API 9 - Inactive Vehicles With Model Code",
        "API 10 - Inactive Vehicles Without Model Code",
        "API 3 - Heavy Vehicles",
        "API 5 - Motorcycles",
        "API 6 - Personal Imports",
        "Vehicle Registrations History",
        "API 2 - Price Info",
        "API 4 - Bus Fleet",
        "API 7 - Car History",
        "API 15 - Disabled Parking Permit",
        "API 8 - Public Transportation Vehicles",
        "API 14 - Vehicle Technical Data (WLTP)",
        "API 16 - Recalls"
    ]

    for t in desired_api_order:
        if t in sections:
            res += format_section(t, sections[t])

    if not res:
        res = (
            "<div style='"
            "font-family: Calibri; "
            "font-size: 20px; "
            "margin-top: 0px;'>"
            "לא נמצא כלי רכב עם לוחית רישוי זו."
            "</div>"
        )

    elapsed = time.time() - start_time
    return jsonify({"html": res, "time": round(elapsed, 2)})



if __name__ == "__main__":
    app.run(debug=True)

