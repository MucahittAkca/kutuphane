import pytest
from fastapi.testclient import TestClient
import os

from kutuphane_yonetim.api.main import app, get_library
from kutuphane_yonetim.core.library import Library


@pytest.fixture(scope="function")
def client(tmp_path):
    """
    Her test fonksiyonu için tamamen izole bir TestClient oluşturur.
    Her client, kendi geçici JSON dosyasıyla çalışan kendi Library nesnesine sahiptir.
    """
    test_data_file = tmp_path / "test_data.json"

    def override_get_library():
        return Library(name="Test API Kütüphanesi", data_file=str(test_data_file))

    app.dependency_overrides[get_library] = override_get_library
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()
    if os.path.exists(test_data_file):
        os.remove(test_data_file)


#Test Verileri
TEST_BOOK_ISBN = "9780451524935"
TEST_BOOK_PAYLOAD = {"title": "1984", "author": "George Orwell", "isbn": TEST_BOOK_ISBN, "publication_year": 1949}
TEST_MEMBER_ID = 101
TEST_MEMBER_PAYLOAD = {"name": "Ayşe Yılmaz", "member_id": TEST_MEMBER_ID}



def test_full_library_workflow(client):
    """Tüm API akışını baştan sona test eden bir sistem testi."""
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []

    response = client.post("/books/add-manually/", json=TEST_BOOK_PAYLOAD)
    assert response.status_code == 201, response.text
    assert response.json()["isbn"] == TEST_BOOK_ISBN

    response = client.post("/members/", json=TEST_MEMBER_PAYLOAD)
    assert response.status_code == 201, response.text
    assert response.json()["member_id"] == TEST_MEMBER_ID

    borrow_payload = {"member_id": TEST_MEMBER_ID, "book_isbn": TEST_BOOK_ISBN}
    response = client.post("/borrow/", json=borrow_payload)
    assert response.status_code == 200, response.text

    return_payload = {"member_id": TEST_MEMBER_ID, "book_isbn": TEST_BOOK_ISBN}
    response = client.post("/return-book/", json=return_payload)
    assert response.status_code == 200, response.text

    response = client.delete(f"/books/delete/{TEST_BOOK_ISBN}")
    assert response.status_code == 204

def test_add_duplicate_member_fails(client):
    """Aynı ID ile ikinci bir üye eklenmeye çalışıldığında 409 hatası alındığını test eder."""
    response = client.post("/members/", json=TEST_MEMBER_PAYLOAD)
    assert response.status_code == 201

    response = client.post("/members/", json=TEST_MEMBER_PAYLOAD)
    assert response.status_code == 409
    assert "zaten kayıtlı" in response.json()["detail"]