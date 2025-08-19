import stat
from fastapi import FastAPI, HTTPException, status, Depends
from typing import List


from kutuphane_yonetim.core.library import Library
from kutuphane_yonetim.core.models import Member, Book, BookStatus
from enum import Enum

from .schemas import *


app = FastAPI(
    title="Kütüphane Yönetim Sistemi API",
    description="Kitapları ve üyeleri yönetmek için kullanılan API."
    )

def get_library():
    """Library nesnesini bir bağımlılık olarak sağlar."""
    return Library(name="API Kütüphanesi", data_file="data/library.json")


@app.get("/")
def read_root():
    return {"message": "Kütüphane API'sine hoş geldiniz!"}

@app.get("/books/", response_model=List[BookResponse], tags=["Books"])
def list_all_books(library: Library = Depends(get_library)):
    """Kütüphanedeki tüm kitapların bir listesini döndürür."""
    return library._books

@app.get("/books/{isbn}", response_model=BookResponse, tags=["Books"])
def get_book_by_isbn(isbn: str, library: Library = Depends(get_library)):
    """Verilen ISBN'e sahip tek bir kitabı döndürür ve kütüphaneye ekler."""
    book = library.find_book(isbn=isbn)

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bu ISBN ile bir kitap bulunamadı.")
    
    return book

@app.post("/books/add-manually/", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["Books"])
def add_book_manually(book_request: CreateBookRequest, library: Library = Depends(get_library)):
    """
    Verilen bilgilerle manuel olarak yeni bir kitap oluşturur ve kütüphaneye ekler.
    Veriler Request Body içinde JSON olarak gönderilmelidir.
    """
    try:
        new_book = Book(**book_request.model_dump())
        library.add_book(new_book)
        return new_book
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@app.post("/books/add-from-api/{isbn}", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["Books"])
async def add_new_book_from_api(isbn:str, library: Library = Depends(get_library)):
    """Verilen ISBN ile Open Library'den bir kitap bulur ve kütüphaneye ekler."""
    try:
        await library.add_book_from_api(isbn)
        new_book = library.find_book(isbn=isbn)
        return new_book
    except (ValueError, IOError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete("/books/delete/{isbn}", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
def delete_existing_book(isbn: str, library: Library = Depends(get_library)):
    """Verilen ISBN'e sahip bir kitabı kütüphaneden siler."""
    try:

        library.delete_book(isbn=isbn)

        return
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    

@app.get("books/search/{isbn}", response_model=BookResponse, tags=["Books"])
def get_book_by_isbn(isbn: str, library: Library = Depends(get_library)):
    """Verilen ISBN'e sahip tek bir kitap döndürür."""
    book = library.find_book(isbn=isbn)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ISBN {isbn} ile kitap bulunamadı.")

    return book    

#üye endpointleri

@app.get("/members/", response_model=List[MemberResponse], tags=["Members"])
def list_all_members(library: Library = Depends(get_library)):
    """Kütüphanedeki tüm üyelerin bir listesini döndürür."""
    return library._members

@app.post("/members/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED, tags=["Members"])
def register_new_member(member_request: CreateMemberRequest, library: Library = Depends(get_library)):
    """Yeni bir kütüphane üyesi oluşturur."""
    try:
        new_member = Member(name=member_request.name, member_id=member_request.member_id)
        library.register_member(new_member)

        return new_member
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    


#işlem endpointleri

@app.post("/borrow/", tags=["Actions"])
def borrow_a_book(request: BorrowRequest, library: Library = Depends(get_library)):
    """Bir üyenin bir kitabı ödünç almasını sağlar."""
    try:
        library.borrow_book(member_id=request.member_id, book_isbn=request.book_isbn)

        return {"message": "Kitap başarıyla ödünç verildi."}
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@app.post("/return-book/", tags=["Actions"])
def return_a_book(request: ReturnBookRequest, library: Library = Depends(get_library)):
    """Bir üyenin bir kitabı iade etmesini sağlar."""
    try:
        library.return_book(member_id=request.member_id, book_isbn=request.book_isbn)
        
        return {"message": "Kitap başarıyla iade edildi."}
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))