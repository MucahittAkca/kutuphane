import pytest
from kutuphane_yonetim.core.library import Library
from kutuphane_yonetim.core.models import Book, Member, BookStatus

@pytest.fixture
def empty_library():
    """Her test için boş bir Library nesnesi oluşturan bir fixture."""
    return Library(name="Test Kütüphanesi")

@pytest.fixture
def library_with_data(empty_library):
    """İçinde bir kitap ve bir üye olan bir Library nesnesi hazırlayan fixture."""
    library = empty_library
    book = Book(title="Dune", author="Frank Herbert", isbn="9780441013593", publication_year=1965)
    member = Member(name="Ayşe Yılmaz", member_id=101)
    
    library.add_book(book)
    library.register_member(member)
    
    return library, book, member



def test_add_and_find_book(empty_library):
    """Kütüphaneye kitap ekleme ve bulma işlevini test eder."""
    library = empty_library
    book = Book(title="1984", author="George Orwell", isbn="9780451524935", publication_year=1949)
    library.add_book(book)

    found_book = library.find_book(isbn="9780451524935")
    assert found_book is not None
    assert found_book.title == "1984"

def test_register_and_find_member(empty_library):
    """Kütüphaneye üye kaydetme ve bulma işlevini test eder."""
    library = empty_library
    member = Member(name="Ahmet Çelik", member_id=202)
    library.register_member(member)

    found_member = library.find_member(member_id=202)
    assert found_member is not None
    assert found_member.name == "Ahmet Çelik"

def test_borrow_book_success(library_with_data):
    """Başarılı bir kitap ödünç alma senaryosunu test eder."""
    library, book, member = library_with_data
    
    library.borrow_book(member_id=101, book_isbn="9780441013593")
    
    assert book.status == BookStatus.BORROWED
    assert book in member.borrowed_books

def test_return_book_success(library_with_data):
    """Başarılı bir kitap iade etme senaryosunu test eder."""
    library, book, member = library_with_data
    
    library.borrow_book(member_id=101, book_isbn="9780441013593")
    
    library.return_book(member_id=101, book_isbn="9780441013593")
    
    assert book.status == BookStatus.AVAILABLE
    assert book not in member.borrowed_books

def test_borrow_nonexistent_book_fails(library_with_data):
    """Var olmayan bir kitabın ödünç alınmaya çalışıldığında hata verdiğini test eder."""
    library, book, member = library_with_data
    
    with pytest.raises(ValueError) as excinfo:
        library.borrow_book(member_id=101, book_isbn="0000000000")
        
    assert "kitap bulunamadı" in str(excinfo.value)

def test_add_duplicate_member_id_fails(library_with_data):
    """Aynı ID'ye sahip ikinci bir üyenin kaydedilmeye çalışıldığında hata verdiğini test eder."""
    library, book, member = library_with_data
    
    new_member_with_same_id = Member(name="Yeni Üye", member_id=101)
    
    with pytest.raises(ValueError) as excinfo:
        library.register_member(new_member_with_same_id)
        
    assert "zaten kayıtlı" in str(excinfo.value)