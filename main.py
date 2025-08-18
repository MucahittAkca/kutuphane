from kutuphane_yonetim.core.library import Library
from kutuphane_yonetim.core.models import Book, Member
import asyncio


def wait_for_user_input():
    input("\nAna menüye dönmek için Enter tuşuna basın...")

def print_menu():
    """Kullanıcıya menüyü gösterir."""
    print("\n--- Kütüphane Yönetim Sistemi ---")
    print("1. Kitap Ekle")
    print("2. Kitap Sil")
    print("3. Tüm Kitapları Listele")
    print("4. Kitap Ara")
    print("5. Üye Ekle")
    print("6. Tüm Üyeleri Listele")
    print("7. Kitap Ödünç Ver")
    print("8. Kitap İade Al")
    print("9. Çıkış")
    print("---------------------------------")


async def main():
    library = Library(name="Proje Özel", data_file="data/library.json")

    while True:
        print_menu()
        choice = input("Lütfen bir işlem seçin (1-9): ")

        try:
            if choice == '1':
                #Kitap Ekle
                isbn = input("ISBN: ")
                await library.add_book(isbn=isbn)

            elif choice == '2':
                #Kitap Sil
                isbn = input("Silinecek kitabın ISBN'ini girin: ")
                library.delete_book(isbn)

            elif choice == '3':
                #Tüm Kitapları Listele
                library.list_books()

            elif choice == '4':
                #Kitap Ara
                isbn = input("Aranacak kitabın ISBN'ini girin: ")
                book = library.find_book(isbn=isbn)
                if book:
                    print("\n--- Bulunan Kitap ---")
                    print(book.display_info())
                else:
                    print("Bu ISBN ile bir kitap bulunamadı.")

            elif choice == '5':
                #Üye Ekle
                name = input("Üye Adı: ")
                member_id = int(input("Üye ID: "))
                new_member = Member(name=name, member_id=member_id)
                library.register_member(new_member)
            
            elif choice == '6':
                #Tüm Üyeleri Listele
                library.list_members()

            elif choice == '7':
                #Kitap Ödünç Ver
                member_id = int(input("Üye ID: "))
                isbn = input("Ödünç alınacak kitabın ISBN'i: ")
                library.borrow_book(member_id, isbn)

            elif choice == '8':
                #Kitap İade Al
                member_id = int(input("Üye ID: "))
                isbn = input("İade edilecek kitabın ISBN'i: ")
                library.return_book(member_id, isbn)

            elif choice == '9':
                #Çıkış
                print("Programdan çıkılıyor...")
                break
            
            else:
                print("Geçersiz seçim. Lütfen 1-9 arasında bir numara girin.")

            if choice != '9':
                wait_for_user_input()

        except (ValueError, TypeError) as e:
            print(f"\nHATA: {e}")
            wait_for_user_input()
        except Exception as e:
            print(f"\nBEKLENMEDİK BİR HATA OLUŞTU: {e}")
            wait_for_user_input()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except asyncio.CancelledError:
        pass