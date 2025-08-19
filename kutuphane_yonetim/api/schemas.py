from pydantic import BaseModel, Field
from typing import List


#temel veri modelleri

class BookResponse(BaseModel):
    """API'den bir kitap yanıtı döndürülürken kullanılacak model."""
    title: str
    author: str
    isbn: str
    publication_year: int
    status: str

class MemberResponse(BaseModel):
    """API'den bir üye yanıtı döndürülürken kullanılacak model."""
    name:str
    member_id: int
    borrowed_books: List[BookResponse] = []

class MessageResponse(BaseModel):
    """Genel başarı veya bilgi mesajları için kullanılacak model."""
    message: str


#Giriş Modelleri

class CreateMemberRequest(BaseModel):
    """Yeni üye kaydetme isteği."""
    name: str = Field(..., description="Üyenin Adı")
    member_id: int = Field(..., gt=0, description="Üye ID(pozitif olmalı)")

class BorrowRequest(BaseModel):
    """ID ve ISBN ile kitap ödünç verme isteği."""
    member_id: int
    book_isbn: str

class ReturnBookRequest(BaseModel):
    """ID ve ISBN ile kitap iade alma isteği."""
    member_id: int
    book_isbn: str

class CreateBookRequest(BaseModel):
    """API üzerinden manuel olarak yeni bir kitap oluşturma isteği."""
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    isbn: str = Field(..., min_length=10, max_length=13)
    publication_year: int = Field(..., gt=1400)

    