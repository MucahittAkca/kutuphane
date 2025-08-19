# Kütüphane Yönetim Sistemi

Bu proje, bir kütüphane yönetim sistemi sunar. Kullanıcılar, kitapları ve üyeleri yönetmek için hem bir komut satırı arayüzü (CLI) hem de bir FastAPI tabanlı RESTful API kullanabilir. Sistem, kitap ekleme, silme, ödünç alma, iade etme ve üye yönetimi gibi temel kütüphane işlemlerini destekler. Ayrıca, Open Library API'sini kullanarak ISBN numarasına göre kitap bilgilerini otomatik olarak çekebilir.

## Özellikler
- **Kitap Yönetimi**: Kitapları manuel olarak veya Open Library API'sinden ekleme, silme ve listeleme.
- **Üye Yönetimi**: Yeni üyeler kaydetme ve üyeleri listeleme.
- **Ödünç Alma ve İade**: Üyelerin kitapları ödünç alması ve iade etmesi.
- **Veri Kalıcılığı**: Kitap ve üye bilgileri JSON formatında bir dosyada saklanır.
- **API Desteği**: RESTful API ile tüm işlemlerin uzaktan gerçekleştirilmesi.
- **Testler**: Hem çekirdek kütüphane işlevleri hem de API endpoint'leri için kapsamlı test senaryoları.

## Kurulum

### 1. Repoyu Klonlama
Projeyi yerel makinenize klonlamak için aşağıdaki komutu çalıştırın:

```bash
git clone https://github.com/MucahittAkca/kutuphane.git
cd kutuphane
```

### 2. Sanal Ortam Oluşturma (İsteğe Bağlı)
Python sanal ortamı oluşturarak bağımlılıkları izole edin:

```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
```

### 3. Bağımlılıkları Yükleme
Projenin bağımlılıklarını yüklemek için aşağıdaki komutu çalıştırın:

```bash
pip install -r requirements.txt
```

Gerekli kütüphaneler:
- `pydantic==2.11.7`: Veri doğrulama ve modelleme.
- `httpx==0.28.1`: HTTP istekleri için asenkron istemci.
- `pytest==8.4.1`: Test framework'ü.
- `fastapi==0.116.1`: API geliştirme için.
- `pytest-httpx==0.35.0`: HTTPX ile test entegrasyonu.
- `pytest-asyncio==1.1.0`: Asenkron testler için.
- `uvicorn[standard]`: API sunucusunu çalıştırmak için.

## Kullanım

### Komut Satırı Arayüzü (CLI)
CLI arayüzü, kütüphane işlemlerini interaktif bir şekilde gerçekleştirmenizi sağlar. Uygulamayı başlatmak için:

```bash
python main.py
```

Bu komut, bir menü sunar ve aşağıdaki işlemleri destekler:
- **0. Kitap Ekle**: Manuel olarak kitap ekler.
- **1. API ile Kitap Ekle**: Open Library API'sinden ISBN ile kitap ekler.
- **2. Kitap Sil**: ISBN ile bir kitabı siler.
- **3. Tüm Kitapları Listele**: Kütüphanedeki tüm kitapları listeler.
- **4. Kitap Ara**: ISBN ile bir kitabı arar.
- **5. Üye Ekle**: Yeni bir üye kaydeder.
- **6. Tüm Üyeleri Listele**: Kayıtlı tüm üyeleri listeler.
- **7. Kitap Ödünç Ver**: Bir üyeye kitap ödünç verir.
- **8. Kitap İade Al**: Bir üyenin iade ettiği kitabı alır.
- **9. Çıkış**: Programdan çıkar.

### API Sunucusu
API sunucusunu başlatmak için aşağıdaki komutu çalıştırın:

```bash
uvicorn kutuphane_yonetim.api.main:app --reload
```

- `--reload` bayrağı, geliştirme sırasında kod değişikliklerini otomatik olarak algılar.
- API, varsayılan olarak `http://127.0.0.1:8000` adresinde çalışır.
- API dokümantasyonuna erişmek için tarayıcınızda `http://127.0.0.1:8000/docs` adresini ziyaret edin.

## API Dokümantasyonu

Aşağıda, sistemin sunduğu tüm API endpoint'leri, açıklamaları ve örnek istek gövdeleri listelenmiştir.

### 1. Genel Endpoint
- **GET /**  
  **Açıklama**: API'nin ana sayfasına hoş geldiniz mesajı döndürür.  
  **Yanıt**: `{"message": "Kütüphane API'sine hoş geldiniz!"}`  
  **Örnek İstek**:
  ```bash
  curl http://127.0.0.1:8000/
  ```

### 2. Kitap Endpoint'leri
- **GET /books/**  
  **Açıklama**: Kütüphanedeki tüm kitapların listesini döndürür.  
  **Yanıt Modeli**: `List[BookResponse]`  
  **Örnek İstek**:
  ```bash
  curl http://127.0.0.1:8000/books/
  ```
  **Örnek Yanıt**:
  ```json
  [
      {
          "title": "Neuromancer",
          "author": "William Gibson",
          "isbn": "9780441569595",
          "publication_year": 1984,
          "status": "mevcut"
      },
      {
          "title": "Nineteen Eighty-Four",
          "author": "George Orwell",
          "isbn": "9780451524935",
          "publication_year": 1949,
          "status": "mevcut"
      }
  ]
  ```

- **GET /books/{isbn}**  
  **Açıklama**: Belirtilen ISBN'e sahip kitabı döndürür.  
  **Yanıt Modeli**: `BookResponse`  
  **Hata Durumları**:
  - 404: Kitap bulunamadı.  
  **Örnek İstek**:
  ```bash
  curl http://127.0.0.1:8000/books/9780451524935
  ```
  **Örnek Yanıt**:
  ```json
  {
      "title": "Nineteen Eighty-Four",
      "author": "George Orwell",
      "isbn": "9780451524935",
      "publication_year": 1949,
      "status": "mevcut"
  }
  ```

- **POST /books/add-manually/**  
  **Açıklama**: Manuel olarak yeni bir kitap ekler.  
  **İstek Gövdesi**: `CreateBookRequest`  
  **Yanıt Modeli**: `BookResponse`  
  **Hata Durumları**:
  - 409: ISBN zaten mevcut.  
  **Örnek İstek**:
  ```bash
  curl -X POST http://127.0.0.1:8000/books/add-manually/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Dune", "author": "Frank Herbert", "isbn": "9780441013593", "publication_year": 1965}'
  ```
  **Örnek Yanıt**:
  ```json
  {
      "title": "Dune",
      "author": "Frank Herbert",
      "isbn": "9780441013593",
      "publication_year": 1965,
      "status": "mevcut"
  }
  ```

- **POST /books/add-from-api/{isbn}**  
  **Açıklama**: Open Library API'sinden ISBN ile kitap bilgilerini çeker ve kütüphaneye ekler.  
  **Yanıt Modeli**: `BookResponse`  
  **Hata Durumları**:
  - 400: ISBN ile kitap bulunamadı veya API hatası.  
  - 409: ISBN zaten mevcut.  
  **Örnek İstek**:
  ```bash
  curl -X POST http://127.0.0.1:8000/books/add-from-api/9780451524935
  ```
  **Örnek Yanıt**:
  ```json
  {
      "title": "1984",
      "author": "George Orwell",
      "isbn": "9780451524935",
      "publication_year": 1949,
      "status": "mevcut"
  }
  ```

- **DELETE /books/delete/{isbn}**  
  **Açıklama**: Belirtilen ISBN'e sahip kitabı kütüphaneden siler.  
  **Yanıt**: 204 No Content  
  **Hata Durumları**:
  - 404: Kitap bulunamadı.  
  - 400: Kitap ödünç alınmış, silinemez.  
  **Örnek İstek**:
  ```bash
  curl -X DELETE http://127.0.0.1:8000/books/delete/9780451524935
  ```

- **GET /books/search/{isbn}**  
  **Açıklama**: Belirtilen ISBN'e sahip kitabı arar (GET /books/{isbn} ile aynı işlev).  
  **Yanıt Modeli**: `BookResponse`  
  **Hata Durumları**:
  - 404: Kitap bulunamadı.  
  **Örnek İstek**:
  ```bash
  curl http://127.0.0.1:8000/books/search/9780451524935
  ```

### 3. Üye Endpoint'leri
- **GET /members/**  
  **Açıklama**: Kütüphanedeki tüm üyelerin listesini döndürür.  
  **Yanıt Modeli**: `List[MemberResponse]`  
  **Örnek İstek**:
  ```bash
  curl http://127.0.0.1:8000/members/
  ```
  **Örnek Yanıt**:
  ```json
  [
      {
          "name": "muco",
          "member_id": 101,
          "borrowed_books": []
      }
  ]
  ```

- **POST /members/**  
  **Açıklama**: Yeni bir üye kaydeder.  
  **İstek Gövdesi**: `CreateMemberRequest`  
  **Yanıt Modeli**: `MemberResponse`  
  **Hata Durumları**:
  - 409: Üye ID zaten kayıtlı.  
  **Örnek İstek**:
  ```bash
  curl -X POST http://127.0.0.1:8000/members/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Ayşe Yılmaz", "member_id": 102}'
  ```
  **Örnek Yanıt**:
  ```json
  {
      "name": "Ayşe Yılmaz",
      "member_id": 102,
      "borrowed_books": []
  }
  ```

### 4. İşlem Endpoint'leri
- **POST /borrow/**  
  **Açıklama**: Bir üyenin bir kitabı ödünç almasını sağlar.  
  **İstek Gövdesi**: `BorrowRequest`  
  **Yanıt Modeli**: `MessageResponse`  
  **Hata Durumları**:
  - 400: Üye veya kitap bulunamadı, veya kitap zaten ödünç alınmış.  
  **Örnek İstek**:
  ```bash
  curl -X POST http://127.0.0.1:8000/borrow/ \
  -H "Content-Type: application/json" \
  -d '{"member_id": 101, "book_isbn": "9780451524935"}'
  ```
  **Örnek Yanıt**:
  ```json
  {"message": "Kitap başarıyla ödünç verildi."}
  ```

- **POST /return-book/**  
  **Açıklama**: Bir üyenin bir kitabı iade etmesini sağlar.  
  **İstek Gövdesi**: `ReturnBookRequest`  
  **Yanıt Modeli**: `MessageResponse`  
  **Hata Durumları**:
  - 404: Üye veya kitap bulunamadı, veya kitap üye tarafından ödünç alınmamış.  
  **Örnek İstek**:
  ```bash
  curl -X POST http://127.0.0.1:8000/return-book/ \
  -H "Content-Type: application/json" \
  -d '{"member_id": 101, "book_isbn": "9780451524935"}'
  ```
  **Örnek Yanıt**:
  ```json
  {"message": "Kitap başarıyla iade edildi."}
  ```

## Test Senaryoları

Proje, hem çekirdek işlevler (`core`) hem de API endpoint'leri için kapsamlı testler içerir. Testleri çalıştırmak için:

```bash
pytest
```

### Çekirdek Testler (`tests/core/`)
- **test_models.py**:
  - Kitap (`Book`) nesnesi oluşturma ve temel niteliklerin doğruluğu.
  - Kitap ödünç alma ve iade etme mantığı.
  - Zaten ödünç alınmış bir kitabı tekrar ödünç almaya çalışma (hata testi).
  - Mevcut bir kitabı iade etmeye çalışma (hata testi).
  - Üye (`Member`) nesnesi oluşturma ve temel niteliklerin doğruluğu.

- **test_library.py**:
  - Manuel kitap ekleme ve arama.
  - Üye kaydetme ve bulma.
  - Kitap ödünç alma ve iade etme (başarılı senaryo).
  - Var olmayan kitabı ödünç alma (hata testi).
  - Aynı üye ID'si ile kayıt denemesi (hata testi).
  - Ödünç alınmış bir kitabı silme (hata testi).
  - Üyenin ödünç almadığı bir kitabı iade etme (hata testi).
  - Open Library API'sinden kitap ekleme (başarılı ve başarısız senaryolar).
  - JSON veri dosyasının güncellenmesi (kitap ve üye ekleme, silme).
  - `EBook` ve `AudioBook` gibi alt sınıfların doğru yüklenmesi.

### API Testleri (`tests/api/`)
- **test_api.py**:
  - Tam kütüphane iş akışı: Boş kütüphane kontrolü, kitap ekleme, üye ekleme, ödünç alma, iade etme ve kitap silme.
  - Aynı üye ID'si ile tekrar üye ekleme (409 hatası testi).

## Veri Yapısı
- **data/library.json**: Kitap ve üye bilgilerini saklar. Örnek yapı:
  ```json
  {
      "books": [
          {
              "title": "Neuromancer",
              "author": "William Gibson",
              "publication_year": 1984,
              "isbn": "9780441569595",
              "status": "mevcut",
              "book_type": "book"
          }
      ],
      "members": [
          {
              "name": "muco",
              "member_id": 101,
              "borrowed_isbns": []
          }
      ]
  }
  ```

## Notlar
- Proje, veri doğrulama için `pydantic` kullanır ve ISBN, yayın yılı gibi alanlar için kısıtlamalar içerir.
- Testler, geçici dosyalar kullanarak izole bir ortamda çalışır.
