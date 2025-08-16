import pytest
from kutuphane_yonetim.core.models import Book, Member, BookStatus

#Book Testleri

def test_book_creation():
    """Bir Book nesnesinin doğru niteliklerle oluşturulduğunu test eder."""
    book = Book(
        title="The Hobbit", 
        author="J.R.R. Tolkien", 
        isbn="9780345339683",
        publication_year=1937
    )
    assert book.title == "The Hobbit"
    assert book.author == "J.R.R. Tolkien"
    assert book.status == BookStatus.AVAILABLE

def test_book_borrow_and_return_logic():
    """Book sınıfının ödünç alma ve iade etme mantığını test eder."""
    book = Book(title="Dune", author="Frank Herbert", isbn="9780441013593", publication_year=1965)

    # Başarılı ödünç alma
    book.borrow_book()
    assert book.status == BookStatus.BORROWED

    # Başarılı iade etme
    book.return_book()
    assert book.status == BookStatus.AVAILABLE

def test_borrow_already_borrowed_book_fails():
    """Zaten ödünç alınmış bir kitabın tekrar ödünç alınmaya çalışıldığında hata verdiğini test eder."""
    book = Book(title="Dune", author="Frank Herbert", isbn="9780441013593", publication_year=1965)
    book.borrow_book()

    # İkinci kez ödünç almaya çalışıldığında ValueError
    with pytest.raises(ValueError) as excinfo:
        book.borrow_book()
    
    assert "ödünç alınamaz" in str(excinfo.value)

def test_return_available_book_fails():
    """Zaten mevcut olan bir kitabın iade edilmeye çalışıldığında hata verdiğini test eder."""
    book = Book(title="Dune", author="Frank Herbert", isbn="9780441013593", publication_year=1965)

    with pytest.raises(ValueError) as excinfo:
        book.return_book()
        
    assert "zaten kütüphanede" in str(excinfo.value)


#Member Testleri

def test_member_creation():
    """Bir Member nesnesinin doğru niteliklerle oluşturulduğunu test eder."""
    member = Member(name="Ali Veli", member_id=101)
    
    assert member.name == "Ali Veli"
    assert member.member_id == 101
    assert member.borrowed_books == []