from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_sources():
    response = client.get("/sources")
    assert response.status_code == 200
    data = response.json()
    print("GET /sources returned successfully, count:", len(data['data']))

    # Test Add Source
    new_source = {
        "name": "Test Source",
        "type": "rss",
        "url": "http://test.com/rss",
        "category": "test-news",
        "enabled": True
    }
    response = client.post("/sources", json=new_source)
    assert response.status_code == 200
    print("POST /sources returned:", response.json())

    # Get updated sources
    response = client.get("/sources")
    sources = response.json()['data']
    test_source_id = next(s['id'] for s in sources if s['name'] == "Test Source")

    # Test Toggle Source
    response = client.patch(f"/sources/{test_source_id}/toggle", json={"enabled": False})
    assert response.status_code == 200
    print("PATCH /sources toggle returned:", response.json())

test_sources()
