import pytest
import json
from kutuphane_yonetim.core.library import Library
from kutuphane_yonetim.core.models import Book, Member, BookStatus, EBook, AudioBook


@pytest.fixture
def empty_library(tmp_path):
    """Her test için geçici bir dosyayla çalışan boş bir Library nesnesi oluşturur."""
    test_file = tmp_path / "test_library.json"
    return Library(name="Test Kütüphanesi", data_file=str(test_file))

@pytest.fixture
def library_with_data(empty_library):
    """İçinde bir kitap ve bir üye olan bir Library nesnesi hazırlar."""
    library = empty_library
    book = Book(title="Dune", author="Frank Herbert", isbn="9780441013593", publication_year=1965)
    member = Member(name="Ayşe Yılmaz", member_id=101)
    

    library._books.append(book)
    library.register_member(member)
    
    return library, book, member

#Temel İşlev ve Hata Durumu Testleri

def test_register_and_find_member(empty_library):
    library = empty_library
    member = Member(name="Ahmet Çelik", member_id=202)
    library.register_member(member)
    found_member = library.find_member(member_id=202)
    assert found_member is not None
    assert found_member.name == "Ahmet Çelik"

def test_borrow_and_return_book_success(library_with_data):
    library, book, member = library_with_data
    
    library.borrow_book(member_id=101, book_isbn="9780441013593")
    assert book.status == BookStatus.BORROWED
    assert book in member.borrowed_books

    library.return_book(member_id=101, book_isbn="9780441013593")
    assert book.status == BookStatus.AVAILABLE
    assert book not in member.borrowed_books

def test_borrow_nonexistent_book_fails(library_with_data):
    library, book, member = library_with_data
    with pytest.raises(ValueError, match="kitap bulunamadı"):
        library.borrow_book(member_id=101, book_isbn="0000000000")

def test_add_duplicate_member_id_fails(library_with_data):
    library, book, member = library_with_data
    new_member_with_same_id = Member(name="Yeni Üye", member_id=101)
    with pytest.raises(ValueError, match="zaten kayıtlı"):
        library.register_member(new_member_with_same_id)

def test_delete_borrowed_book_fails(library_with_data):
    library, book, member = library_with_data
    library.borrow_book(member_id=member.member_id, book_isbn=book.isbn)
    with pytest.raises(ValueError, match="ödünç alındığı için silinemez"):
        library.delete_book(isbn=book.isbn)

def test_return_book_not_borrowed_by_member_fails(library_with_data):
    library, book, member = library_with_data
    with pytest.raises(ValueError, match="olan kitabı ödünç almamış"):
        library.return_book(member_id=member.member_id, book_isbn=book.isbn)


#API ve ASENKRON TESTLER

@pytest.mark.asyncio
async def test_add_book_from_api_success(empty_library, httpx_mock):
    """API'den başarılı bir şekilde kitap ekleme senaryosunu test eder."""
    library = empty_library
    test_isbn = "9780451524935"
    
    mock_response = {
        "numFound": 1,
        "docs": [{"title": "1984", "author_name": ["George Orwell"], "first_publish_year": 1949}]
    }
    httpx_mock.add_response(url=f"https://openlibrary.org/search.json?q={test_isbn}", json=mock_response)
    
    await library.add_book(test_isbn)
    
    found_book = library.find_book(isbn=test_isbn)
    assert found_book is not None
    assert found_book.title == "1984"
    assert found_book.author == "George Orwell"

@pytest.mark.asyncio
async def test_add_book_from_api_no_results_fails(empty_library, httpx_mock):
    """API aramasında sonuç bulunamayan bir ISBN için hata fırlatıldığını test eder."""
    library = empty_library
    test_isbn = "0000000000000"
    
    mock_response = {"numFound": 0, "docs": []}
    httpx_mock.add_response(url=f"https://openlibrary.org/search.json?q={test_isbn}", json=mock_response)
    
    with pytest.raises(ValueError, match="arama sonucu bulunamadı"):
        await library.add_book(test_isbn)

@pytest.mark.asyncio
async def test_add_duplicate_isbn_from_api_fails(empty_library):
    """API'den eklenecek bir kitabın ISBN'i zaten mevcutsa hata fırlattığını test eder."""
    library = empty_library
    test_isbn = "1234567890"

    existing_book = Book(title="Mevcut Kitap", author="Yazar", isbn=test_isbn, publication_year=2020)
    library._books.append(existing_book)
    
    with pytest.raises(ValueError, match="zaten mevcut"):
        await library.add_book(test_isbn)


#Veri Saklama Testleri

def test_save_data_on_register_member(empty_library):
    """Üye eklendiğinde JSON dosyasının güncellendiğini test eder."""
    library = empty_library
    member = Member(name="Test Üyesi", member_id=505)
    library.register_member(member)
    
    with open(library.data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    assert len(data["members"]) == 1
    assert data["members"][0]["name"] == "Test Üyesi"

def test_load_data_on_startup(tmp_path):
    test_file = tmp_path / "existing_data.json"
    sample_data = {"books": [{"title": "Brave New World", "author": "Aldous Huxley", "publication_year": 1932, "isbn": "9780060850524", "status": "mevcut", "book_type": "book"}], "members": []}
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f)
        
    library = Library(name="Loading Test", data_file=str(test_file))
    
    assert len(library._books) == 1
    loaded_book = library.find_book(isbn="9780060850524")
    assert loaded_book.title == "Brave New World"

def test_delete_book_updates_json(library_with_data):
    library, book_to_delete, member = library_with_data
    library.delete_book(isbn=book_to_delete.isbn)
    
    with open(library.data_file, 'r') as f:
        data_after = json.load(f)
    assert len(data_after['books']) == 0

def test_load_subclass_books_correctly(tmp_path):
    """EBook ve AudioBook gibi alt sınıfların doğru şekilde yüklendiğini test eder."""
    test_file = tmp_path / "subclass_data.json"
    sample_data = {
        "books": [
            {
                "title": "Neuromancer", "author": "William Gibson", "publication_year": 1984,
                "isbn": "9780441569595", "status": "mevcut", "book_type": "ebook",
                "file_format": "EPUB" 
            }
        ],
        "members": []
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f)
        
    library = Library(name="Subclass Test", data_file=str(test_file))
    
    assert len(library._books) == 1
    loaded_book = library._books[0]
    
    assert isinstance(loaded_book, EBook)
    assert loaded_book.file_format == "EPUB"