from tkinter import N
from .models import Book, EBook, AudioBook, Member

class Library:
    def __init__(self, name):
        self.name = name
        self._books = []
        self._members = []


    ### KİTAP METHODLARI ###
    def add_book(self, book: Book):
        """Kütüphaneye yeni bir kitap ekler."""
        for existing_book in self._books:
            if existing_book.isbn == book.isbn:
                raise ValueError(f"ISBN: {book.isbn} zaten mevcut!")
        self._books.append(book)
        print(f"{book.title} başarıyla kütüphaneye eklendi.")

    def find_book(self, *, isbn: str = None, title: str = None):
        """ISBN'e veya başlığa göre tek bir kitap bulur. ISBN önceliklidir."""
        if isbn:
            for book in self._books:
                if book.isbn == isbn:
                    return book
        elif title:
            for book in self._books:
                if book.title.lower() == title.lower():
                    return book
        return None
    
    def list_books(self):
        if not self._books:
            print("Kütüphanede hiç kitap yok.")
            return
        
        print(f"--- {self.name} kütüphanesi kitap listesi ---")
        for book in self._books:
            print(book.display_info())
    
    @property
    def total_books(self) -> int:
        """Kütüphane sistemine kayıtlı kaç kitap olduğunu gösterir."""
        return len(self._books)
    

    ### ÜYE METHODLARI ###
    def register_member(self, member: Member):
        for existing_member in self._members:
            if existing_member.member_id == member.member_id:
                raise ValueError(f"Üye ID {member.member_id} zaten kayıtlı.")
        self._members.append(member)
        print(f"Kullanıcı başarıyla kaydoldu: {member.name} - {member.member_id}")

    def find_member(self, member_id:int):
        for member in self._members:
            if member.member_id == member_id:
                return member
            
        return None
    
    def list_members(self):
        """Tüm üyeleri ve ödünç aldıkları kitap sayısını listeler."""
        if not self._members:
            print("Kütüphanede kayıtlı kullanıcı bulunamadı.")
            return
        
        print(f"--- {self.name} Kütüphanesi Üye Listesi ---")
        for member in self._members:
            print(f"ID: {member.member_id}, İsim: {member.name}, Ödünç Alınan Kitap Sayısı: {len(member.borrowed_books)}")


    ### İŞLEM METHODLARI ###


    def borrow_book(self, member_id: int, book_isbn: str):
        """Bir üyenin bir kitabı ödünç almasını sağlar."""
        member = self.find_member(member_id)
        if not member:
            raise ValueError(f"{member_id} --> Bu ID ile kullanıcı bulunamadı!")
        
        book = self.find_book(isbn=book_isbn)
        if not book:
            raise ValueError(f"{book_isbn} --> Bu ISBN ile kitap bulunamadı!")

        book.borrow_book()

        member.borrowed_books.append(book)
        print(f"'{book.title}', '{member.name}' adlı üyeye ödünç verildi.")


    def return_book(self, member_id: int, book_isbn: str):
        """Bir üyenin bir kitabı iade etmesini sağlar."""
        member = self.find_member(member_id)
        if not member:
            raise ValueError(f"{member_id} --> Bu ID ile kullanıcı bulunamadı!")
        
        book_to_return = None

        for book in member.borrowed_books:
            if book.isbn == book_isbn:
                book_to_return = book
                break
        
        if not book_to_return:
            raise ValueError(f"{member.name} adlı üye, ISBN: {book.isbn} olan kitabı ödünç almamış!")
        
        book_to_return.return_book()

        member.borrowed_books.remove(book_to_return)
        print(f"'{book_to_return.title}', '{member.name}' tarafından iade edildi.")



    

