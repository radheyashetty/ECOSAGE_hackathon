"""Manual verification script for all FastAPI endpoints."""
from fastapi.testclient import TestClient
from ecosage.api import app

def main():
    client = TestClient(app)
    
    # 1. Health check
    health = client.get("/health")
    print("1. Health check:", health.json())
    assert health.status_code == 200
    
    # 2. Adversarial input (incomplete data -> asks clarifying questions)
    resp_adv = client.post("/chat", json={
        "session_id": "test-session-api-1",
        "query_text": "Help my land"
    })
    data_adv = resp_adv.json()
    print("\n2. Adversarial input clarifying questions:")
    for q in data_adv.get("clarifying_questions", []):
        print(f"   - {q}")
    assert len(data_adv.get("clarifying_questions", [])) > 0
    assert len(data_adv.get("recommendations", [])) == 0
    
    # 3. Section 6 scenario
    print("\n3. Testing PRD Section 6 scenario...")
    resp = client.post("/chat", json={
        "session_id": "test-session-api-2",
        "metrics": {
            "soil_organic_carbon_pct": 0.3,
            "rainfall": "low",
            "crop": "monoculture wheat",
            "region": "semi-arid",
            "land_use_type": "monoculture"
        },
        "query_text": "Biodiversity is declining on my land. What agroforestry or intercropping practices should I use?"
    })
    data = resp.json()
    recs = data.get("recommendations", [])
    print(f"   Generated {len(recs)} recommendations:")
    for i, r in enumerate(recs, 1):
        print(f"\n   --- Recommendation {i} ---")
        print(f"   Action: {r['action']}")
        print(f"   Mechanism: {r['mechanism'][:130]}...")
        print(f"   Impacted Metrics: {r['impacted_metrics']}")
        print(f"   Quantified: {r['quantified_estimate']}")
        print(f"   Confidence: {r['confidence']}")
        print(f"   Time Horizon: {r['time_horizon']}")
        sources_str = ", ".join([f"{s['name']} ({s['id']})" for s in r['sources']])
        print(f"   Sources: {sources_str}")
        
    assert len(recs) > 0
    
    # 4. Debug retrieval trace endpoint (FR-1.4)
    trace_resp = client.get("/debug/retrieval/test-session-api-2")
    trace_data = trace_resp.json()
    print(f"\n4. /debug/retrieval endpoint status: {trace_resp.status_code}")
    print(f"   Traces recorded for session: {len(trace_data.get('traces', []))}")
    if trace_data.get("traces"):
        t0 = trace_data["traces"][0]
        print(f"   Query: {t0.get('query')}")
        print(f"   Results retrieved: {len(t0.get('results', []))}")
        for res in t0.get("results", [])[:2]:
            print(f"     * [{res.get('source_id')}] score: {res.get('similarity_score', 0):.3f}")
            
    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
