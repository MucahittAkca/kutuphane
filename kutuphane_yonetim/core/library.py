from .models import *
import json
from typing import List, Union
import httpx

OPEN_LIBRARY_URL = "https://openlibrary.org/search.json?isbn="

class Library:
    def __init__(self, name, data_file="library.json"):
        self.name = name
        self._books: List[Union[Book, EBook, AudioBook]] = []
        self._members: List[Member] = []
        self.data_file = data_file
        self._load_data()


    ### Veri Methodları ###
    
    def _save_data(self):
        """Kütüphanedeki tüm kitap ve üye verilerini JSON dosyasına kaydeder."""
        try:
            books_data = []
            for book in self._books:
                book_data = book.model_dump(mode='json')
                if isinstance(book, EBook):
                    book_data['book_type'] = 'ebook'
                elif isinstance(book, AudioBook):
                    book_data['book_type'] = 'audiobook'
                else:
                    book_data['book_type'] = 'book'
                books_data.append(book_data)

            members_data = []
            for member in self._members:
                borrowed_isbns = [book.isbn for book in member.borrowed_books]
                members_data.append({
                    "name": member.name,
                    "member_id": member.member_id,
                    "borrowed_isbns": borrowed_isbns 
                })

            data_to_save = {
                "books": books_data,
                "members": members_data
            }

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            
        except Exception as e:
            print(f"[HATA] Veri kaydetme sırasında bir sorun oluştu: {e}")

    def _load_data(self):
        """JSON dosyasından kitap ve üye verilerini yükler."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for book_data in data.get("books", []):
                    book_type = book_data.pop("book_type", "book")
                    if book_type == 'ebook':
                        self._books.append(EBook.model_validate(book_data))
                    elif book_type == 'audiobook':
                        self._books.append(AudioBook.model_validate(book_data))
                    else:
                        self._books.append(Book.model_validate(book_data))

                loaded_members = data.get("members", [])
                for member_data in loaded_members:
                    borrowed_isbns = member_data.pop("borrowed_isbns", [])
                    member = Member(**member_data)
                    
                    for isbn in borrowed_isbns:
                        book_obj = self.find_book(isbn=isbn)
                        if book_obj:
                            member.borrowed_books.append(book_obj)
                            
                    self._members.append(member)

                print(f"{len(self._books)} kitap ve {len(self._members)} üye başarıyla yüklendi.")

        except FileNotFoundError:
            print("Veri dosyası bulunamadı. Kütüphane boş olarak başlatılıyor.")
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Veri dosyası okunamadı veya bozuk. Kütüphane boş olarak başlatılıyor. Hata: {e}")




    ### KİTAP METHODLARI ###
    def add_book(self, book: Union[Book, EBook, AudioBook]):
        """Kütüphaneye yeni bir kitap (veya alt türü) ekler."""
        # ISBN'nin benzersiz olduğunu kontrol etmek iyi bir pratiktir.
        for existing_book in self._books:
            if existing_book.isbn == book.isbn:
                raise ValueError(f"ISBN {book.isbn} zaten mevcut.")
        self._books.append(book)
        self._save_data()
        print(f"'{book.title}' kütüphaneye eklendi.")

    async def add_book_from_api(self, isbn: str):
        """Verilen ISBN'i kullanarak Open Library API'sinden kitap bilgilerini çeker
        ve kütüphaneye yeni bir Book nesnesi olarak ekler."""
        if self.find_book(isbn=isbn):
            raise ValueError(f"ISBN {isbn} zaten mevcut!")
        
        params = {"q": isbn}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(OPEN_LIBRARY_URL, params=params, follow_redirects=True)
                response.raise_for_status()

            data = response.json()

            if not data.get("docs") or len(data["docs"]) == 0:
                raise ValueError(f"ISBN {isbn} ile Open Library'de arama sonucu bulunamadı.")
            
            first_result = data["docs"][0]
            title = first_result.get("title", "Başlık Bilinmiyor")
            author = first_result.get("author_name", ["Yazar Bilinmiyor"])[0]
            publication_year = first_result.get("first_publish_year", 9999)

            print(f"{isbn} ile {data.get('numFound', 0)} sonuç bulundu.")
            new_book = Book(
                title=title,
                author=author,
                isbn=isbn,
                publication_year=publication_year
            )

            self._books.append(new_book)
            self._save_data()
            print(f"İlk sıradaki sonuç eklendi: '{new_book.title}' by {new_book.author}")


        except httpx.HTTPStatusError as e:
            raise IOError(f"API isteği başarısız oldu: Sunucu hatası {e.response.status_code}")
        
        except httpx.RequestError:
            raise IOError("Ağ hatası. Lütfen internet bağlantınızı kontrol edin.")
        
        except (KeyError, IndexError, TypeError):
            raise IOError(f"API'den gelen veri formatı beklenmedik veya bozuk. ISBN: {isbn}")



    def find_book(self, *, isbn: str = None, title: str = None):
        """ISBN'e veya başlığa göre tek bir kitap bulur."""
        if isbn:
            for book in self._books:
                if book.isbn == isbn:
                    return book
        elif title:
            for book in self._books:
                if book.title.lower() == title.lower():
                    return book
        return None
    

    def delete_book(self, isbn: str):
        book_to_delete = self.find_book(isbn=isbn)
        if not book_to_delete:
            raise ValueError(f"ISBN {isbn} ile eşleşen kitap bulunamadı.")
        
        if book_to_delete.status == BookStatus.BORROWED:
            raise ValueError(f"'{book_to_delete.title}' ödünç alındığı için silinemez.")
            
        self._books.remove(book_to_delete)
        self._save_data()
        print(f"'{book_to_delete.title}' başarıyla silindi.")


    
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
        self._save_data()
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
            raise ValueError(f"Bu ID ile kullanıcı bulunamadı! --> {member_id}")
        
        book = self.find_book(isbn=book_isbn)
        if not book:
            raise ValueError(f"Bu ISBN ile kitap bulunamadı!--> {book_isbn}")

        book.borrow_book()

        member.borrowed_books.append(book)
        self._save_data()
        print(f"'{book.title}', '{member.name}' adlı üyeye ödünç verildi.")


    def return_book(self, member_id: int, book_isbn: str):
        """Bir üyenin bir kitabı iade etmesini sağlar."""
        member = self.find_member(member_id)
        if not member:
            raise ValueError(f"Bu ID ile kullanıcı bulunamadı! --> {member_id}")
        
        book_to_return = None

        for book in member.borrowed_books:
            if book.isbn == book_isbn:
                book_to_return = book
                break
        
        if not book_to_return:
            raise ValueError(f"'{member.name}' adlı üye, ISBN {book_isbn} olan kitabı ödünç almamış.")

        book_to_return.return_book()

        member.borrowed_books.remove(book_to_return)
        self._save_data()
        print(f"'{book_to_return.title}', '{member.name}' tarafından iade edildi.")



    

