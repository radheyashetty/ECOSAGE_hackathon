"""
Geo-coordinate regional climate and biome prior inference module.
Implements PRD Functional Requirement FR-5.3 (Bonus):
"Optional geo-coordinates -> used to infer regional climate/rainfall priors if not supplied directly."

Runs completely offline without external paid GIS APIs.
"""
from typing import Any

from ecosage.logger import get_logger

logger = get_logger("geo_inference")

# Bounding box rules for key ecological and agricultural regions
# Format: (lat_min, lat_max, lng_min, lng_max, region_name, rainfall_category, rainfall_mm, notes)
REGIONAL_BOUNDING_BOXES = [
    # South Asia - Semi-Arid North-West (Thar Desert / Rajasthan / Gujarat / Haryana)
    (23.0, 31.0, 68.0, 77.0, "semi-arid", "low", 400.0, "North-West India semi-arid agro-ecological zone"),
    # South Asia - Deccan Semi-Arid Plateau
    (14.0, 22.0, 74.0, 80.0, "semi-arid", "low", 650.0, "Deccan plateau rain-shadow belt"),
    # South Asia - Indo-Gangetic Plains
    (24.0, 30.5, 77.0, 89.0, "temperate", "moderate", 950.0, "Indo-Gangetic alluvial agricultural belt"),
    # South Asia - Western Ghats & Coastal Humid
    (8.0, 19.0, 73.0, 76.5, "tropical", "high", 2500.0, "Western Ghats tropical humid biodiversity hotspot"),
    
    # Sub-Saharan Africa - Sahelian Transition Belt
    (11.0, 18.5, -17.0, 36.0, "semi-arid", "low", 450.0, "Sahelian semi-arid dryland transition belt"),
    # East Africa - Horn of Africa Arid Belt
    (2.0, 12.0, 40.0, 51.0, "arid", "low", 250.0, "Horn of Africa dryland pastoralist zone"),
    # Equatorial Central Africa
    (-5.0, 5.0, 10.0, 30.0, "tropical", "high", 1800.0, "Congo basin tropical moist forest biome"),
    
    # Mediterranean Basin
    (34.0, 44.0, -9.0, 36.0, "mediterranean", "moderate", 600.0, "Mediterranean dry-summer agricultural zone"),
    
    # North America - Great Plains Dryland Belt
    (31.0, 49.0, -104.0, -96.0, "temperate", "moderate", 550.0, "North American Great Plains grain belt"),
    # North America - Desert South-West
    (31.0, 37.0, -116.0, -105.0, "arid", "low", 220.0, "Southwestern arid dryland biome"),
    
    # South America - Cerrado Savanna
    (-22.0, -5.0, -60.0, -44.0, "tropical", "moderate", 1400.0, "Brazilian Cerrado tropical savanna"),
    # South America - Atacama / Coastal Desert
    (-30.0, -18.0, -72.0, -68.0, "arid", "low", 50.0, "Atacama hyper-arid coastal desert"),
    
    # Australia - Semi-Arid & Arid Interior
    (-35.0, -19.0, 115.0, 142.0, "semi-arid", "low", 300.0, "Australian interior semi-arid pastoral zone"),
]


def infer_climate_priors(lat: float, lng: float) -> dict[str, Any]:
    """
    Infer regional biome and rainfall pattern priors from geographic coordinates.
    
    Args:
        lat (float): Latitude (-90.0 to 90.0)
        lng (float): Longitude (-180.0 to 180.0)
        
    Returns:
        dict: Inferred environmental metrics (region, rainfall, rainfall_mm_annual)
    """
    # 1. Match specific regional bounding boxes
    for lat_min, lat_max, lng_min, lng_max, region, rainfall, mm, desc in REGIONAL_BOUNDING_BOXES:
        if lat_min <= lat <= lat_max and lng_min <= lng <= lng_max:
            logger.info(f"🌍 Geo-inference matched {desc} for ({lat}, {lng}) -> region: {region}, rainfall: {rainfall}")
            return {
                "region": region,
                "rainfall": rainfall,
                "rainfall_mm_annual": mm,
                "_geo_inferred_zone": desc,
            }

    # 2. General latitude band heuristic fallback
    abs_lat = abs(lat)
    if abs_lat <= 15.0:
        region = "tropical"
        rainfall = "high"
        mm = 1600.0
        desc = "Equatorial / tropical zone"
    elif 15.0 < abs_lat <= 32.0:
        region = "semi-arid"
        rainfall = "low"
        mm = 450.0
        desc = "Subtropical dryland / semi-arid belt"
    elif 32.0 < abs_lat <= 55.0:
        region = "temperate"
        rainfall = "moderate"
        mm = 800.0
        desc = "Mid-latitude temperate zone"
    else:
        region = "boreal"
        rainfall = "low"
        mm = 350.0
        desc = "High-latitude boreal zone"

    logger.info(f"🌍 Geo-inference broad latitude band match ({desc}) for ({lat}, {lng}) -> region: {region}, rainfall: {rainfall}")
    return {
        "region": region,
        "rainfall": rainfall,
        "rainfall_mm_annual": mm,
        "_geo_inferred_zone": desc,
    }
