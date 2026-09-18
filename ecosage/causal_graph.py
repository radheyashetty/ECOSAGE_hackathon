"""
EcoSage Causal Graph Module
Encodes documented relationships between environmental variables as a source-tagged graph.
"""

from collections import deque
from typing import TypedDict


class CausalEdge(TypedDict, total=False):
    source_metric: str
    target_metric: str
    relationship: str
    direction: str  # "positive" or "negative"
    source_id: str
    quantification: str | None

# Causal Edges defined based on PRD Section 5.4
CAUSAL_EDGES: list[CausalEdge] = [
    # Soil-Biodiversity cluster
    {
        "source_metric": "soil_organic_carbon",
        "target_metric": "microbial_diversity",
        "relationship": "Higher SOC supports greater microbial biomass and diversity",
        "direction": "positive",
        "source_id": "FAO-SOC-2017",
        "quantification": "Each 1% SOC increase associated with 20-40% higher microbial biomass"
    },
    {
        "source_metric": "microbial_diversity",
        "target_metric": "nutrient_cycling",
        "relationship": "Diverse microbial communities enhance N and P mineralization",
        "direction": "positive",
        "source_id": "MICRO-SOIL-2021",
        "quantification": "Nutrient cycling efficiency increases by 25-45%"
    },
    {
        "source_metric": "root_diversity",
        "target_metric": "soil_organic_carbon",
        "relationship": "Diverse root systems increase organic matter input to soil",
        "direction": "positive",
        "source_id": "INTERCROP-2021",
        "quantification": "Root diversity from intercropping increases SOC by 10-20%"
    },
    {
        "source_metric": "soil_organic_carbon",
        "target_metric": "soil_moisture_retention",
        "relationship": "Higher SOC improves soil water holding capacity",
        "direction": "positive",
        "source_id": "FAO-SOC-2017",
        "quantification": "Each 1% SOC increase improves water retention by 1-3%"
    },
    {
        "source_metric": "microbial_diversity",
        "target_metric": "plant_health",
        "relationship": "Beneficial microbes suppress pathogens and enhance nutrient uptake",
        "direction": "positive",
        "source_id": "MICRO-SOIL-2021"
    },
    {
        "source_metric": "mycorrhizal_networks",
        "target_metric": "water_access",
        "relationship": "Mycorrhizal fungi extend plant root water access",
        "direction": "positive",
        "source_id": "MICRO-SOIL-2021",
        "quantification": "Water access extended by 200-400% in drought conditions"
    },
    # Water-Species cluster
    {
        "source_metric": "rainfall",
        "target_metric": "species_richness",
        "relationship": "Water availability is a primary driver of species diversity",
        "direction": "positive",
        "source_id": "IPCC-AR6-LU"
    },
    {
        "source_metric": "soil_moisture_retention",
        "target_metric": "species_survival",
        "relationship": "Soil moisture buffers against drought stress for flora and fauna",
        "direction": "positive",
        "source_id": "FAO-SOC-2017"
    },
    {
        "source_metric": "rainfall",
        "target_metric": "soil_moisture_retention",
        "relationship": "Rainfall is primary input to soil moisture",
        "direction": "positive",
        "source_id": "IPCC-AR6-LU"
    },
    {
        "source_metric": "water_stress",
        "target_metric": "species_survival",
        "relationship": "Prolonged water stress reduces survival of non-adapted species",
        "direction": "negative",
        "source_id": "IPCC-AR6-LU",
        "quantification": "Water stress reduces species survival by 30-60% in semi-arid zones"
    },
    # Land-use-Habitat cluster
    {
        "source_metric": "land_use_intensification",
        "target_metric": "habitat_fragmentation",
        "relationship": "Intensive monoculture reduces habitat patch size and connectivity",
        "direction": "positive",
        "source_id": "FRAG-ECO-2018"
    },
    {
        "source_metric": "habitat_fragmentation",
        "target_metric": "species_richness",
        "relationship": "Fragmentation reduces species richness through isolation effects",
        "direction": "negative",
        "source_id": "FRAG-ECO-2018",
        "quantification": "Species richness declines 20-50% below 10 hectare threshold"
    },
    {
        "source_metric": "habitat_connectivity",
        "target_metric": "species_movement",
        "relationship": "Connected habitats allow gene flow and species migration",
        "direction": "positive",
        "source_id": "FRAG-ECO-2018",
        "quantification": "Corridors restore 60-80% of species movement"
    },
    {
        "source_metric": "crop_diversity",
        "target_metric": "pollinator_diversity",
        "relationship": "Diverse cropping provides varied floral resources for pollinators",
        "direction": "positive",
        "source_id": "POLLIN-ECO-2020",
        "quantification": "Pollinator diversity increases 30-50% vs monoculture"
    },
    {
        "source_metric": "pollinator_diversity",
        "target_metric": "crop_yield",
        "relationship": "Pollinators enhance crop reproduction and yield",
        "direction": "positive",
        "source_id": "POLLIN-ECO-2020"
    },
    {
        "source_metric": "pollinator_diversity",
        "target_metric": "species_richness",
        "relationship": "Pollinator diversity indicates overall ecosystem health",
        "direction": "positive",
        "source_id": "POLLIN-ECO-2020"
    },
    # Intervention edges
    {
        "source_metric": "agroforestry",
        "target_metric": "root_diversity",
        "relationship": "Tree-crop combinations create multi-layered root systems",
        "direction": "positive",
        "source_id": "AGROFOR-BIO-2020"
    },
    {
        "source_metric": "agroforestry",
        "target_metric": "habitat_connectivity",
        "relationship": "Agroforestry corridors link habitat fragments",
        "direction": "positive",
        "source_id": "AGROFOR-BIO-2020"
    },
    {
        "source_metric": "cover_cropping",
        "target_metric": "soil_organic_carbon",
        "relationship": "Cover crops add organic matter and prevent erosion",
        "direction": "positive",
        "source_id": "COVER-CROP-2019",
        "quantification": "SOC increases 8-15% over 3-5 years"
    },
    {
        "source_metric": "intercropping",
        "target_metric": "root_diversity",
        "relationship": "Multiple crop species create diverse root architecture",
        "direction": "positive",
        "source_id": "INTERCROP-2021"
    },
    {
        "source_metric": "intercropping",
        "target_metric": "water_use_efficiency",
        "relationship": "Complementary root depths improve water utilization",
        "direction": "positive",
        "source_id": "INTERCROP-2021",
        "quantification": "Water use efficiency improves 15-25%"
    },
    # Bridging edges to complete causal chains
    {
        "source_metric": "intercropping",
        "target_metric": "crop_diversity",
        "relationship": "Intercropping inherently increases crop diversity on the parcel",
        "direction": "positive",
        "source_id": "INTERCROP-2021",
        "quantification": "Land equivalent ratio increases by 20-40%"
    },
    {
        "source_metric": "agroforestry",
        "target_metric": "crop_diversity",
        "relationship": "Agroforestry combines trees with crops, increasing overall plant diversity",
        "direction": "positive",
        "source_id": "AGROFOR-BIO-2020",
        "quantification": "Bird species richness increases 40-60% vs monoculture"
    },
    {
        "source_metric": "nutrient_cycling",
        "target_metric": "plant_health",
        "relationship": "Efficient nutrient cycling supports plant growth and resilience",
        "direction": "positive",
        "source_id": "MICRO-SOIL-2021"
    },
    {
        "source_metric": "plant_health",
        "target_metric": "crop_yield",
        "relationship": "Healthy plants produce higher yields and support more biodiversity",
        "direction": "positive",
        "source_id": "MICRO-SOIL-2021"
    },
    {
        "source_metric": "soil_organic_carbon",
        "target_metric": "species_richness",
        "relationship": "Higher SOC supports greater overall ecosystem biodiversity through improved soil habitat",
        "direction": "positive",
        "source_id": "FAO-SOC-2017",
        "quantification": "SOC above 2% correlates with significantly higher species richness indices"
    },
]

# Build adjacency dict
ADJACENCY_DICT: dict[str, list[CausalEdge]] = {}
for edge in CAUSAL_EDGES:
    source = edge["source_metric"]
    if source not in ADJACENCY_DICT:
        ADJACENCY_DICT[source] = []
    ADJACENCY_DICT[source].append(edge)

def get_causal_chain(start: str, end: str, max_depth: int = 5) -> list[list[CausalEdge]]:
    """BFS to find all paths from start metric to end metric (up to max_depth).
    Returns list of paths, each path is a list of CausalEdge objects."""
    queue = deque([(start, [])])
    valid_chains = []
    
    while queue:
        current, path = queue.popleft()
        if len(path) > max_depth:
            continue
            
        if current == end and len(path) > 0:
            valid_chains.append(path)
            continue
            
        for edge in ADJACENCY_DICT.get(current, []):
            next_node = edge["target_metric"]
            # Avoid cycles
            if not any(e["source_metric"] == next_node for e in path) and next_node != start:
                queue.append((next_node, path + [edge]))
                
    return valid_chains

def get_related_metrics(metric: str, depth: int = 2) -> dict[str, list[CausalEdge]]:
    """Get all metrics reachable from the given metric within depth hops.
    Returns dict mapping metric name to the edges that connect to it."""
    related: dict[str, list[CausalEdge]] = {}
    
    queue = deque([(metric, [])])
    visited = {metric}
    
    while queue:
        current, path = queue.popleft()
        if len(path) >= depth:
            continue
            
        for edge in ADJACENCY_DICT.get(current, []):
            next_node = edge["target_metric"]
            if next_node not in visited:
                visited.add(next_node)
                new_path = path + [edge]
                related[next_node] = new_path
                queue.append((next_node, new_path))
                
    return related

def get_edges_for_intervention(intervention: str) -> list[CausalEdge]:
    """Get all edges activated by a specific intervention (e.g., 'agroforestry').
    Searches for edges where source_metric matches the intervention."""
    return ADJACENCY_DICT.get(intervention, [])

def get_all_metrics() -> set[str]:
    """Return all unique metric names in the graph."""
    metrics = set()
    for edge in CAUSAL_EDGES:
        metrics.add(edge["source_metric"])
        metrics.add(edge["target_metric"])
    return metrics

def render_chain_text(chain: list[CausalEdge]) -> str:
    """Convert a causal chain to human-readable text.
    E.g.: 'intercropping → root diversity (increases SOC by 10-20%) → soil organic carbon → microbial diversity (20-40% higher microbial biomass)'"""
    if not chain:
        return ""
    
    parts = []
    for i, edge in enumerate(chain):
        if i == 0:
            parts.append(edge["source_metric"])
        
        quant_text = f" ({edge['quantification']})" if edge.get("quantification") else ""
        parts.append(f"→ {edge['target_metric']}{quant_text}")
        
    return " ".join(parts)

def get_graph_summary() -> dict:
    """Return summary stats: number of nodes, edges, connected components."""
    metrics = get_all_metrics()
    
    # A simple connected components counter (undirected graph representation)
    adj_undirected: dict[str, set[str]] = {m: set() for m in metrics}
    for edge in CAUSAL_EDGES:
        adj_undirected[edge["source_metric"]].add(edge["target_metric"])
        adj_undirected[edge["target_metric"]].add(edge["source_metric"])
        
    visited = set()
    components = 0
    
    for m in metrics:
        if m not in visited:
            components += 1
            queue = deque([m])
            visited.add(m)
            while queue:
                curr = queue.popleft()
                for neighbor in adj_undirected[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        
    return {
        "nodes": len(metrics),
        "edges": len(CAUSAL_EDGES),
        "connected_components": components
    }

if __name__ == '__main__':
    chains = get_causal_chain("intercropping", "species_richness", max_depth=5)
    for i, chain in enumerate(chains):
        print(f"Chain {i+1}:")
        print(render_chain_text(chain))
        print()
