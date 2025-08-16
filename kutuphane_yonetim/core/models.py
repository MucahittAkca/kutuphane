from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from dataclasses import dataclass, field

class BookStatus(str, Enum):
    """Kitabın kütüphanedeki durumunu belirten Enum.
    """
    AVAILABLE = "mevcut"
    BORROWED = "ödünç alınmış"
    LOST = "kayıp"

class Book(BaseModel):
    """
    Kütüphanedeki bir kitabı temsil eden temel Pydantic modeli.
    """
    title: str
    author: str
    publication_year: int = Field(..., gt=1400, description="Yayın yılı 1400'den büyük olmalı.")
    isbn: str = Field(..., min_length=10, max_length=13, description="ISBN 10 veya 13 karakter olmalıdır.")
    status: BookStatus = BookStatus.AVAILABLE
    
    def get_base_info(self) -> str:
        """Kitabın başlık, yazar ve yıl bilgilerini döndürür."""
        return f"'{self.title}' by {self.author} ({self.publication_year})"

    def display_info(self) -> str:
        """Kitabın tüm bilgilerini ve durumunu okunaklı bir formatta döndürür."""
        return f"{self.get_base_info()} - Durum: {self.status.value}"

    def borrow_book(self): 
        """Kitabı ödünç alır ve durumunu günceller."""
        if self.status == BookStatus.AVAILABLE:
            self.status = BookStatus.BORROWED
        else:
            raise ValueError(f"'{self.title}' kitabı şu anda ödünç alınamaz. Durum: {self.status.value}")

    def return_book(self):
        """Kitabı iade eder ve durumunu günceller."""
        if self.status == BookStatus.BORROWED:
            self.status = BookStatus.AVAILABLE
        else:
            raise ValueError(f"'{self.title}' kitabı zaten kütüphanede, iade edilemez.")
        
        
class EBook(Book):
    file_format: str = Field(..., description="Dosya formatı (örn: EPUB, PDF)")

    def display_info(self) -> str:
        return f"{self.get_base_info()} [Format: {self.file_format}] - Durum: {self.status.value}"


class AudioBook(Book):
    duration_in_minutes: int = Field(..., gt=0, description="Dakika cinsinden süre.")

    def display_info(self) -> str:
        return f"{self.get_base_info()} [Süre: {self.duration_in_minutes} dk] - Durum: {self.status.value}"
    

@dataclass
class Member:
    """Bir kütüphane üyesini temsil eden dataclass."""
    name: str
    member_id: int

    borrowed_books: List[Book] = field(default_factory=list)