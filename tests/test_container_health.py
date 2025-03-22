import pytest
import requests
import time
from pathlib import Path

@pytest.fixture(scope="session")
def docker_compose_command():
    return "docker-compose"

@pytest.fixture(scope="session")
def docker_compose_project_directory():
    return str(Path(__file__).parent.parent)

def test_container_health():
    """Test if the container is healthy and the app is responding"""
    url = "http://localhost:8080/health"
    max_retries = 30
    retry_interval = 1

    for _ in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Check response content
                data = response.json()
                assert "status" in data, "Health check response missing status"
                assert data["status"] == "healthy", "Service not healthy"
                assert "timestamp" in data, "Health check missing timestamp"
                assert "version" in data, "Health check missing version info"
                return
        except requests.exceptions.ConnectionError:
            time.sleep(retry_interval)
            continue
        except requests.exceptions.JSONDecodeError:
            pytest.fail("Health check endpoint did not return valid JSON")

    pytest.fail("Container health check failed after maximum retries")


def test_container_memory_usage():
    """Test container memory usage is within limits"""
    import docker
    client = docker.from_env()
    container = client.containers.get('weather-app')
    stats = container.stats(stream=False)

    memory_usage = stats['memory_stats']['usage']
    memory_limit = stats['memory_stats']['limit']
    memory_percent = (memory_usage / memory_limit) * 100

    assert memory_percent < 80, "Container memory usage too high"

def test_response_time():
    """Test API response time"""
    url = "http://localhost:8080"
    start_time = time.time()
    response = requests.get(url)
    end_time = time.time()

    response_time = end_time - start_time
    assert response_time < 0.5, f"Response time too slow: {response_time} seconds"