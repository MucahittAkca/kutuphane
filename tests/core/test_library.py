import pytest
from kutuphane_yonetim.core.library import Library
from kutuphane_yonetim.core.models import *
import json

@pytest.fixture
def empty_library(tmp_path):
    """
    Her test için geçici bir dosyayla çalışan boş bir Library nesnesi oluşturur.
    """
    test_file = tmp_path / "test_library.json"
    return Library(name="Test Kütüphanesi", data_file=str(test_file))

@pytest.fixture
def library_with_data(empty_library):
    """İçinde bir kitap ve bir üye olan bir Library nesnesi hazırlar."""
    library = empty_library
    book = Book(title="Dune", author="Frank Herbert", isbn="9780441013593", publication_year=1965)
    member = Member(name="Ayşe Yılmaz", member_id=101)
    
    library.add_book(book)
    library.register_member(member)
    
    return library, book, member



def test_add_and_find_book(empty_library):
    library = empty_library
    book = Book(title="1984", author="George Orwell", isbn="9780451524935", publication_year=1949)
    library.add_book(book)
    found_book = library.find_book(isbn="9780451524935")
    assert found_book is not None
    assert found_book.title == "1984"

def test_register_and_find_member(empty_library):
    library = empty_library
    member = Member(name="Ahmet Çelik", member_id=202)
    library.register_member(member)
    found_member = library.find_member(member_id=202)
    assert found_member is not None
    assert found_member.name == "Ahmet Çelik"

def test_borrow_and_return_book_success(library_with_data):
    library, book, member = library_with_data
    
    # Ödünç alma testi
    library.borrow_book(member_id=101, book_isbn="9780441013593")
    assert book.status == BookStatus.BORROWED
    assert book in member.borrowed_books

    # İade etme testi
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

#VERİ SAKLAMA TESTLERİ

def test_save_data_on_add_book(empty_library):
    """Kitap eklendiğinde JSON dosyasının doğru şekilde oluşturulduğunu ve güncellendiğini test eder."""
    library = empty_library
    book = Book(title="Fahrenheit 451", author="Ray Bradbury", isbn="9781451673319", publication_year=1953)
    
    library.add_book(book)
    
    with open(library.data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    assert len(data["books"]) == 1
    assert data["books"][0]["title"] == "Fahrenheit 451"
    assert data["books"][0]["isbn"] == "9781451673319"
    assert len(data["members"]) == 0

def test_load_data_on_startup(tmp_path):
    """Mevcut bir JSON dosyasının, Library başlatıldığında doğru yüklendiğini test eder."""
    #Test için sahte bir JSON dosyası oluşturur
    test_file = tmp_path / "existing_data.json"
    sample_data = {
        "books": [
            {
                "title": "Brave New World",
                "author": "Aldous Huxley",
                "publication_year": 1932,
                "isbn": "9780060850524",
                "status": "mevcut"
            }
        ],
        "members": []
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f)
        
    #Library'yi bu dosyayla başlatır
    library = Library(name="Loading Test", data_file=str(test_file))
    
    #Verilerin doğru yüklendiğini kontrol eder
    assert len(library._books) == 1
    assert len(library._members) == 0
    loaded_book = library.find_book(isbn="9780060850524")
    assert loaded_book is not None
    assert loaded_book.title == "Brave New World"

def test_delete_book_updates_json(library_with_data):
    """Kitap silindiğinde JSON dosyasının güncellendiğini test eder."""
    library, book_to_delete, member = library_with_data
    
    #Silmeden önce dosyada 1 kitap olmalı
    with open(library.data_file, 'r') as f:
        data_before = json.load(f)
    assert len(data_before['books']) == 1
    
    #Kitabı siler
    library.delete_book(isbn=book_to_delete.isbn)
    
    #Sildikten sonra dosyayı tekrar okur
    with open(library.data_file, 'r') as f:
        data_after = json.load(f)
    
    #Dosyadaki kitap listesi artık boş olmalı
    assert len(data_after['books']) == 0

def test_add_duplicate_isbn_fails(empty_library):
    """Aynı ISBN'e sahip ikinci bir kitabın eklenmeye çalışıldığında hata verdiğini test eder."""
    library = empty_library
    book1 = Book(title="Book One", author="Author", isbn="1234567890", publication_year=2000)
    book2 = Book(title="Book Two", author="Author", isbn="1234567890", publication_year=2001)
    
    library.add_book(book1)
    
    with pytest.raises(ValueError, match="zaten mevcut"):
        library.add_book(book2)

def test_delete_borrowed_book_fails(library_with_data):
    """Ödünç alınmış bir kitabın silinmeye çalışıldığında hata verdiğini test eder."""
    library, book, member = library_with_data
    
    #Önce kitabı ödünç al
    library.borrow_book(member_id=member.member_id, book_isbn=book.isbn)
    
    #silmeye çalış ve hata bekle
    with pytest.raises(ValueError, match="ödünç alındığı için silinemez"):
        library.delete_book(isbn=book.isbn)

def test_return_book_not_borrowed_by_member_fails(library_with_data):
    """Bir üyenin ödünç almadığı bir kitabı iade etmeye çalıştığında hata verdiğini test eder."""
    library, book, member = library_with_data
    
    #Kitap hiç ödünç alınmadı
    with pytest.raises(ValueError, match="olan kitabı ödünç almamış"):
        library.return_book(member_id=member.member_id, book_isbn=book.isbn)

def test_load_subclass_books_correctly(tmp_path):
    """EBook ve AudioBook gibi alt sınıfların doğru şekilde yüklendiğini test eder."""
    test_file = tmp_path / "subclass_data.json"
    sample_data = {
        "books": [
            {
                "title": "Neuromancer", "author": "William Gibson", "publication_year": 1984,
                "isbn": "9780441569595", "status": "mevcut",
                "file_format": "EPUB", "book_type": "ebook"
            }
        ],
        "members": []
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f)
        
    library = Library(name="Subclass Test", data_file=str(test_file))
    
    assert len(library._books) == 1
    loaded_book = library._books[0]
    
    #Yüklenen nesnenin doğru tipte olduğunu kontrol et
    assert isinstance(loaded_book, EBook)
    #EBook'a özel alanın doğru yüklendiğini kontrol et
    assert loaded_book.file_format == "EPUB"