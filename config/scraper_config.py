"""
Configuration for website scrapers.
"""
from datetime import date

# Columns written to the combined CSV, in order.
OUTPUT_COLUMNS = [
    "location",
    "basis",
    "delivery_start",
    "delivery_end",
    "symbol",
    "cash_price",
    "commodity",
]

# Only keep delivery periods through this month.
# Set cutoff to end of February 2027 (inclusive).
DELIVERY_END_CUTOFF = date(2027, 2, 28)

# Group and scraper display order for the combined CSV.
GROUP_ORDER = [
    "river_bids",
    "corn_processors",
    "corn_rail_other",
    "bean_processors",
    "bean_other",
    "srw_wheat",
]

SCRAPER_ORDER = [
    "CGB_hennepin",
    "ADM_havana",
    "Cargill_keithsburg",
    "ADM_e_st_louis",
    "ADM_evansville_in",
    "BioUrja_peoria",
    "Alto_pekin",
    "ADM_decatur_corn_processor",
    "ADM_cedar_rapids_corn_processor",
    "ADM_clinton_corn_processor",
    "Tate_Lyle_lafayette",
    "Big_River_w_burlington",
    "Marquis_hennepin",
    "Cargill_blair_ne",
    "Andersons_clymers",
    "POET_fostoria_oh",
    "POET_macon_mo",
    "Mid_Missouri_Energy_malta_bend",
    "Cardinal_colwich_ks",
    "Necedah_wi",
    "KCS_jacksonville_il",
    "BNSF_waverly",
    "MFA_hamilton",
    "JBS_smithton",
    "Bartlett_atchison",
    "ADM_decatur_bean_processor",
    "Bunge_cairo_il_beans",
    "ADM_fostoria_oh_beans",
    "Cargill_sidney_oh_beans",
    "ADM_quincy_il_beans",
    "ADM_mexico_mo_beans",
    "Cargill_kc_beans",
    "Cargill_cedar_rapids_ia_beans",
    "Cargill_bloomington_yellow_beans",
    "ADM_mankato_mn_beans",
    "Quality_Roasting_valders_beans",
    "CGB_joliet_container",
    "ADM_st_louis_river_srw_wheat",
    "Mennel_fostoria_oh_srw_wheat",
]

# Dictionary to hold scraper configurations.

SCRAPERS = {
    "CGB_hennepin": {
        "type": "cgb",
        "location_id": "20592",
        "location_filter": "Hennepin",
        "allowed_commodities": ["Corn", "Beans"],
        "group": "river_bids",
        "enabled": True,
    },
    "ADM_havana": {
        "type": "gradable",
        "group": "river_bids",
        "location": "ADM Havana",
        "url": (
            "https://adm.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/331845413?offer_type=public"
        ),
        "allowed_commodities": ["Corn", "Beans"],
        "enabled": True,
    },
    "Cargill_keithsburg": {
        "type": "barchart_jsonp",
        "group": "river_bids",
        "location": "Cargill Keithsburg",
        "url": (
            "https://cargillus.websol.barchart.com/?"
            "jsonpFunction=jQuery370012079542848600255_1781718222665"
            "&module=cashbids&location=5843&output=json"
            "&commOverviewByLocation=1&commRoots=%2CZC%2CZS&_=1781718222666"
        ),
        "allowed_commodities": ["Corn", "Beans"],
        "enabled": True,
    },
    "ADM_e_st_louis": {
        "type": "gradable",
        "group": "river_bids",
        "location": "ADM E St Louis",
        "url": (
            "https://adm.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/331847261?offer_type=public"
        ),
        "allowed_commodities": ["Corn", "Beans"],
        "enabled": True,
    },
    "ADM_evansville_in": {
        "type": "gradable",
        "group": "river_bids",
        "location": "ADM Evansville IN",
        "url": (
            "https://adm.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/500234520?offer_type=public"
        ),
        "allowed_commodities": ["Corn", "Beans"],
        "enabled": True,
    },
    "BioUrja_peoria": {
        "type": "bushel_html",
        "group": "corn_processors",
        "location": "BioUrja Peoria",
        "url": "https://www.akronservices.com/cash-bids",
        "section_filter": "Biourja Peoria",
        "forced_commodity": "Corn",
        "enabled": True,
    },
    "Alto_pekin": {
        "type": "alto_pekin",
        "group": "corn_processors",
        "location": "Alto Pekin",
        "url": "https://www.altoingredients.com/corn-pricing/",
        "enabled": True,
    },
    "ADM_decatur_corn_processor": {
        "type": "gradable",
        "group": "corn_processors",
        "location": "ADM Decatur Corn",
        "url": (
            "https://adm.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/331847072?offer_type=public"
        ),
        "allowed_commodities": ["Corn"],
        "enabled": True,
    },
    "ADM_cedar_rapids_corn_processor": {
        "type": "gradable",
        "group": "corn_processors",
        "location": "ADM Cedar Rapids Corn",
        "url": (
            "https://adm.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/331844986?offer_type=public"
        ),
        "allowed_commodities": ["Corn"],
        "enabled": True,
    },
    "ADM_clinton_corn_processor": {
        "type": "gradable",
        "group": "corn_processors",
        "location": "ADM Clinton Corn",
        "url": (
            "https://adm.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/331846859?offer_type=public"
        ),
        "allowed_commodities": ["Corn"],
        "enabled": True,
    },
    "Tate_Lyle_lafayette": {
        "type": "agricharts_embed",
        "group": "corn_processors",
        "location": "Tate & Lyle Lafayette",
        "url": (
            "https://tateandlylegrain.agricharts.com/inc/cashbids/"
            "cashbids-js.php?filter=location&location=22033&commodity="
            "&groupby=ccommodity&width=&showtimestamp=1&hidenav=1"
            "&format=table&fields=name%2Cdelivery_start%2Cdelivery_end"
            "%2Cprice%2Cbasismonth%2Cfutures%2Cfutureschange%2Cbasis"
            "&groupheading=table&bidsort=commodity&dateformat=%25m%2F"
            "%25d%2F%25y&months=8&&acCnt=1"
        ),
        "forced_commodity": "Corn",
        "enabled": True,
    },
    "Big_River_w_burlington": {
        "type": "bushel_html",
        "group": "corn_processors",
        "location": "Big River West Burlington",
        "url": "https://www.bigriverresources.com/cashbidssingle-2164",
        "section_filter": "W. Burlington",
        "forced_commodity": "Corn",
        "enabled": True,
    },
    "Marquis_hennepin": {
        "type": "agricharts_embed",
        "group": "corn_processors",
        "location": "Marquis Hennepin",
        "url": (
            "https://marquis.agricharts.com/inc/cashbids/cashbids-js.php?"
            "filter=all&location=&commodity=&groupby=location&width="
            "&showtimestamp=1&showchart=1&asp=1&enableScrollIntoView=1"
            "&format=table&fields=name%2Cdelivery_start%2Cdelivery_end"
            "%2Cbasismonth%2Cfutures%2Cfutureschange%2Cbasis%2Cprice"
            "&groupheading=table&bidsort=commodity&dateformat=%25m%2F"
            "%25d%2F%25Y&months=8&locations=&commodities=&&acCnt=1"
        ),
        "location_filter": "Hennepin",
        "forced_commodity": "Corn",
        "enabled": True,
    },
    "Cargill_blair_ne": {
        "type": "barchart_jsonp",
        "group": "corn_processors",
        "location": "Cargill Blair NE",
        "url": (
            "https://cargillus.websol.barchart.com/?"
            "jsonpFunction=jQuery370011158244705428633_1781720842346"
            "&module=cashbids&location=50899&output=json"
            "&commOverviewByLocation=1&commRoots=%2CZC&_=1781720842347"
        ),
        "allowed_commodities": ["Corn"],
        "enabled": True,
    },
    "Andersons_clymers": {
        "type": "andersons_clymers",
        "group": "corn_processors",
        "location": "Andersons Clymers",
        "url": "https://www.andersonsgrain.com/locations/in/clymers/",
        "enabled": True,
    },
    "POET_fostoria_oh": {
        "type": "gradable",
        "group": "corn_processors",
        "location": "POET Fostoria OH",
        "url": (
            "https://poet.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/331847641?offer_type=public"
        ),
        "allowed_commodities": ["Corn"],
        "enabled": True,
    },
    "POET_macon_mo": {
        "type": "gradable",
        "group": "corn_processors",
        "location": "POET Macon MO",
        "url": (
            "https://poet.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/331847269?offer_type=public"
        ),
        "allowed_commodities": ["Corn"],
        "enabled": True,
    },
    "Mid_Missouri_Energy_malta_bend": {
        "type": "mid_mo_energy",
        "group": "corn_processors",
        "location": "Mid Missouri Energy Malta Bend MO",
        "url": "https://www.midmissourienergy.com/markets/cash.php",
        "enabled": True,
    },
    "Cardinal_colwich_ks": {
        "type": "cihedging",
        "group": "corn_processors",
        "location": "Cardinal Colwich KS",
        "company_id": "165345",
        "forced_commodity": "Corn",
        "enabled": True,
    },
    "Aztalan_johnson_creek_wi": {
        "type": "cihedging",
        "group": "corn_processors",
        "location": "Aztalan Johnson Creek WI",
        "company_id": "134941",
        "forced_commodity": "Corn",
        "enabled": True,
    },
    "Necedah_wi": {
        "type": "agricharts_embed",
        "group": "corn_processors",
        "location": "Necedah WI",
        "url": (
            "https://necedah.agricharts.com/inc/cashbids/cashbids-js.php?"
            "filter=location&location=85381&commodity=&groupby=location&width="
            "&showtimestamp=1&hidenav=1&showchart=1&asp=1"
            "&enableScrollIntoView=1&format=table"
            "&fields=name%2Cdelivery_start%2Cdelivery_end%2Cbasismonth"
            "%2Cfutureschange%2Cbasis%2Cprice&groupheading=table"
            "&bidsort=commodity&dateformat=%25m%2F%25d%2F%25Y"
            "&months=8&locations=85381&commodities=&&acCnt=1"
        ),
        "forced_commodity": "Corn",
        "enabled": True,
    },
    "ADM_decatur_bean_processor": {
        "type": "gradable",
        "group": "bean_processors",
        "location": "ADM Decatur Beans",
        "url": (
            "https://adm.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/638325236?offer_type=public"
        ),
        "allowed_commodities": ["Beans"],
        "enabled": True,
    },
    "Cargill_gibson_city_beans": {
        "type": "barchart_jsonp",
        "group": "bean_processors",
        "location": "Cargill Gibson City Beans",
        "url": (
            "https://cargillus.websol.barchart.com/?"
            "jsonpFunction=jQuery37008212194060100316_1781719275619"
            "&module=cashbids&location=9847&output=json"
            "&commOverviewByLocation=1&commRoots=%2CZS&_=1781719275620"
        ),
        "allowed_commodities": ["Beans"],
        "enabled": True,
    },
    "ADM_fostoria_oh_beans": {
        "type": "gradable",
        "group": "bean_processors",
        "location": "ADM Fostoria OH Beans",
        "url": (
            "https://adm.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/331847375?offer_type=public"
        ),
        "allowed_commodities": ["Beans"],
        "enabled": True,
    },
    "Cargill_sidney_oh_beans": {
        "type": "barchart_jsonp",
        "group": "bean_processors",
        "location": "Cargill Sidney OH Beans",
        "url": (
            "https://cargillus.websol.barchart.com/?"
            "jsonpFunction=jQuery37005869808551110683_1781719349473"
            "&module=cashbids&location=5864&output=json"
            "&commOverviewByLocation=1&commRoots=%2CZS%2CZM&_=1781719349474"
        ),
        "allowed_commodities": ["Beans"],
        "enabled": True,
    },
    "ADM_quincy_il_beans": {
        "type": "gradable",
        "group": "bean_processors",
        "location": "ADM Quincy IL Beans",
        "url": (
            "https://adm.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/331846008?offer_type=public"
        ),
        "allowed_commodities": ["Beans"],
        "enabled": True,
    },
    "ADM_mexico_mo_beans": {
        "type": "gradable",
        "group": "bean_processors",
        "location": "ADM Mexico MO Beans",
        "url": (
            "https://adm.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/331847418?offer_type=public"
        ),
        "allowed_commodities": ["Beans"],
        "enabled": True,
    },
    "Cargill_kc_beans": {
        "type": "barchart_jsonp",
        "group": "bean_processors",
        "location": "Cargill KC Beans",
        "url": (
            "https://cargillus.websol.barchart.com/?"
            "jsonpFunction=jQuery37003281897281272491_1781719651062"
            "&module=cashbids&location=63226&output=json"
            "&commOverviewByLocation=1&commRoots=%2CZS&_=1781719651063"
        ),
        "allowed_commodities": ["Beans"],
        "enabled": True,
    },
    "Cargill_bloomington_yellow_beans": {
        "type": "barchart_jsonp",
        "group": "bean_processors",
        "location": "Cargill Bloomington Yellow Beans",
        "url": (
            "https://cargillus.websol.barchart.com/?"
            "jsonpFunction=jQuery37007274726507964236_1782160231242"
            "&module=cashbids&location=62677&output=json"
            "&commOverviewByLocation=1&commRoots=%2CZS%2CZS&_=1782160231243"
        ),
        "allowed_commodities": ["Beans"],
        "product_filter": "yellow soybeans",
        "product_filter_exclude": "non gmo",
        "enabled": True,
    },
    "Cargill_cedar_rapids_ia_beans": {
        "type": "barchart_jsonp",
        "group": "bean_processors",
        "location": "Cargill Cedar Rapids IA Beans",
        "url": (
            "https://cargillus.websol.barchart.com/?"
            "jsonpFunction=jQuery37009377875392055518_1781719715829"
            "&module=cashbids&location=56950&output=json"
            "&commOverviewByLocation=1&commRoots=%2CZS&_=1781719715830"
        ),
        "allowed_commodities": ["Beans"],
        "enabled": True,
    },
    "ADM_mankato_mn_beans": {
        "type": "gradable",
        "group": "bean_processors",
        "location": "ADM Mankato MN Beans",
        "url": (
            "https://adm.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/331846476?offer_type=public"
        ),
        "allowed_commodities": ["Beans"],
        "enabled": True,
    },
    "Quality_Roasting_valders_beans": {
        "type": "quality_roasting",
        "group": "bean_processors",
        "location": "Quality Roasting Valders Beans",
        "url": "https://fj.qtmarketcenter.com/js/cashbids.php?loc=454",
        "forced_commodity": "Beans",
        "enabled": True,
    },
    "ADM_st_louis_river_srw_wheat": {
        "type": "gradable",
        "group": "srw_wheat",
        "location": "ADM St Louis River SRW Wheat",
        "url": (
            "https://adm.gradable.com/api/commodities/v2/merchandising/"
            "instruments/market/331847261?offer_type=public"
        ),
        "allowed_commodities": ["SRW Wheat"],
        "enabled": True,
    },
    "Mennel_fostoria_oh_srw_wheat": {
        "type": "agricharts_embed",
        "group": "srw_wheat",
        "location": "Mennel Fostoria OH SRW Wheat",
        "url": (
            "https://mennelmilling.agricharts.com/inc/cashbids/"
            "cashbids-json.php?filter=location&location=47437&showtimestamp=1"
            "&commodity=&groupby=ccommodity&width=&format=table&fields="
            "&groupheading=table&bidsort=commodity&dateformat=%25b%20%25d,%20%25Y"
            "&months=8"
        ),
        "forced_commodity": "SRW Wheat",
        "enabled": True,
    },
    "CGB_joliet_container": {
        "type": "agricharts_embed",
        "group": "bean_other",
        "location": "CGB Joliet Container",
        "url": (
            "https://cgb.agricharts.com/inc/cashbids/cashbids-js.php?"
            "filter=all&location=cgblocation&commodity=&groupby=location"
            "&width=90%25&showtimestamp=1&showchart=1&format=table"
            "&fields=name%2Cdelivery_start%2Cdelivery_end%2Cbasismonth%2Cfutures"
            "%2Cfutureschange%2Cbasis%2Cprice&groupheading=table"
            "&bidsort=commodity&dateformat=%25m%2F%25d%2F%25Y&months=11"
            "&&acCnt=1&format=table&groupby=location&setLocation=81116"
            "&commodity=&location=81116"
        ),
        "forced_commodity": "Bean/Other",
        "enabled": True,
    },
    "KCS_jacksonville_il": {
        "type": "agricharts_embed",
        "group": "corn_rail_other",
        "location": "KCS Jacksonville IL",
        "url": "https://bartlettandco.agricharts.com/inc/cashbids/cashbids-json.php",
        "forced_commodity": "Corn",
        "location_filter": "Jacksonville",
        "enabled": True,
    },
    "BNSF_waverly": {
        "type": "bushel_html",
        "group": "corn_rail_other",
        "location": "BNSF Waverly",
        "url": "https://scoularview.com/cashbidssingle-1941?loc=n",
        "section_filter": "Waverly",
        "forced_commodity": "Corn",
        "enabled": True,
    },
    "MFA_hamilton": {
        "type": "mfa_rail",
        "group": "corn_rail_other",
        "location": "MFA Hamilton",
        "url": "http://www.mfarailfacility.com/index.cfm?show=11&mid=2",
        "enabled": True,
    },
    "JBS_smithton": {
        "type": "jbs_cash",
        "group": "corn_rail_other",
        "location": "JBS Smithton",
        "url": "https://www.jbslivepork.com/markets/cash.php?location_filter=73266",
        "enabled": True,
    },
    "Bartlett_atchison": {
        "type": "agricharts_embed",
        "group": "corn_rail_other",
        "location": "Bartlett Atchison",
        "url": "https://bartlettandco.agricharts.com/inc/cashbids/cashbids-json.php",
        "location_filter": "Atchison",
        "allowed_commodities": ["Corn"],
        "enabled": True,
    },
    "Bunge_cairo_il_beans": {
        "type": "bunge_location",
        "group": "bean_processors",
        "location": "Bunge Cairo IL Beans",
        "url": "https://www.bungeag.com/locations/cairo-il/",
        "commodity_tab": "soybeans",
        "forced_commodity": "Beans",
        "enabled": True,
    },
    "Bunge_bellevue_oh_beans": {
        "type": "bunge_location",
        "group": "bean_processors",
        "location": "Bunge Bellevue OH Beans",
        "url": "https://www.bungeag.com/locations/bellevue-oh/",
        "commodity_tab": "soybeans",
        "forced_commodity": "Beans",
        "enabled": False,
    },
}

# Data directory for saving CSV files
DATA_DIRECTORY = "data"

# Optional: Add request headers
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
