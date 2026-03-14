import json
import os
import time

DATA_FILE = "library_data.json"

class Book:
    def __init__(self, title, author, genre, year, description, book_id=None):
        self.id = book_id if book_id else int(time.time() * 1000)
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year
        self.description = description
        self.is_read = False
        self.is_favorite = False

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "year": self.year,
            "description": self.description,
            "is_read": self.is_read,
            "is_favorite": self.is_favorite
        }

    @staticmethod
    def from_dict(data):
        book = Book(
            data['title'], data['author'], data['genre'], 
            data['year'], data['description'], data['id']
        )
        book.is_read = data.get('is_read', False)
        book.is_favorite = data.get('is_favorite', False)
        return book

    def __str__(self):
        status = "Прочитана" if self.is_read else "Не прочитана"
        fav = "★" if self.is_favorite else " "
        return f"[{self.id}] {fav} '{self.title}' - {self.author} ({self.year}) | {self.genre} | Статус: {status}"


class LibraryManager:
    def __init__(self):
        self.books = []
        self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.books = [Book.from_dict(b) for b in data]
                print(f"Загружено {len(self.books)} книг из файла.")
            except Exception as e:
                print(f"Ошибка при загрузке файла: {e}. Начинаем с пустой библиотекой.")
        else:
            print("Файл данных не найден. Создаем новую библиотеку.")

    def save_data(self):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([b.to_dict() for b in self.books], f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

    def add_book(self, title, author, genre, year, description):
        new_book = Book(title, author, genre, year, description)
        self.books.append(new_book)
        self.save_data()
        print(f"Книга '{title}' добавлена в библиотеку (ID: {new_book.id}).")

    def get_books(self, sort_by='title', filter_genre=None, filter_status=None):
        result = self.books[:]

        if filter_genre:
            result = [b for b in result if b.genre.lower() == filter_genre.lower()]
        if filter_status is not None:
            result = [b for b in result if b.is_read == filter_status]

        if sort_by == 'title':
            result.sort(key=lambda x: x.title.lower())
        elif sort_by == 'author':
            result.sort(key=lambda x: x.author.lower())
        elif sort_by == 'year':
            result.sort(key=lambda x: x.year)
        
        return result

    def search_books(self, query):
        query = query.lower()
        return [b for b in self.books if (query in b.title.lower() or 
                                          query in b.author.lower() or 
                                          query in b.description.lower())]

    def toggle_status(self, book_id):
        book = self._find_book(book_id)
        if book:
            book.is_read = not book.is_read
            self.save_data()
            status = "прочитана" if book.is_read else "не прочитана"
            print(f"Статус книги '{book.title}' изменен на '{status}'.")
            return True
        return False

    def toggle_favorite(self, book_id):
        book = self._find_book(book_id)
        if book:
            book.is_favorite = not book.is_favorite
            self.save_data()
            action = "добавлена в" if book.is_favorite else "удалена из"
            print(f"Книга '{book.title}' {action} избранное.")
            return True
        return False

    def delete_book(self, book_id):
        book = self._find_book(book_id)
        if book:
            self.books.remove(book)
            self.save_data()
            print(f"Книга '{book.title}' удалена из библиотеки.")
            return True
        return False

    def _find_book(self, book_id):
        for book in self.books:
            if book.id == book_id:
                return book
        return None


def print_menu():
    print("\n" + "="*40)
    print("         T-БИБЛИОТЕКА  ")
    print("="*40)
    print("1. Добавить книгу")
    print("2. Просмотреть все книги (Сортировка/Фильтр)")
    print("3. Поиск книги")
    print("4. Избранные книги")
    print("5. Изменить статус (Прочитана/Не прочитана)")
    print("6. Добавить/Удалить из избранного")
    print("7. Удалить книгу")
    print("8. Выход")
    print("="*40)

def get_int_input(prompt):
    while True:
        try:
            value = input(prompt)
            if value.strip() == "":
                print("Ввод не может быть пустым.")
                continue
            return int(value)
        except ValueError:
            print("Пожалуйста, введите корректное целое число.")

def main():
    manager = LibraryManager()

    while True:
        print_menu()
        choice = input("Выберите действие (1-8): ")

        if choice == '1':
            print("\n--- Добавление новой книги ---")
            title = input("Название: ")
            author = input("Автор: ")
            genre = input("Жанр: ")
            year = get_int_input("Год издания: ")
            desc = input("Краткое описание: ")
            manager.add_book(title, author, genre, year, desc)

        elif choice == '2':
            print("\n--- Просмотр библиотеки ---")
            print("Сортировать по: 1-Название, 2-Автор, 3-Год")
            sort_choice = input("Выбор (Enter для названия): ")
            sort_key = 'title'
            if sort_choice == '2': sort_key = 'author'
            elif sort_choice == '3': sort_key = 'year'

            print("Фильтр по жанру (оставьте пустым для всех): ")
            genre_filter = input("Жанр: ")
            
            print("Фильтр по статусу: 1-Прочитана, 2-Не прочитана, Enter-Все")
            status_filter = input("Статус: ")
            status_val = None
            if status_filter == '1': status_val = True
            elif status_filter == '2': status_val = False

            books = manager.get_books(sort_by=sort_key, filter_genre=genre_filter if genre_filter else None, filter_status=status_val)
            
            if not books:
                print("Книг не найдено.")
            else:
                print(f"\nНайдено книг: {len(books)}")
                for book in books:
                    print(book)

        elif choice == '3':
            query = input("\nВведите ключевое слово для поиска: ")
            results = manager.search_books(query)
            if not results:
                print("Ничего не найдено.")
            else:
                print(f"\nРезультаты поиска ({len(results)}):")
                for book in results:
                    print(book)

        elif choice == '4':
            favorites = [b for b in manager.books if b.is_favorite]
            print("\n--- Избранные книги ---")
            if not favorites:
                print("Список избранного пуст.")
            else:
                for book in favorites:
                    print(book)

        elif choice == '5':
            book_id = get_int_input("\nВведите ID книги для изменения статуса: ")
            if not manager.toggle_status(book_id):
                print("Книга с таким ID не найдена.")

        elif choice == '6':
            book_id = get_int_input("\nВведите ID книги для изменения в избранном: ")
            if not manager.toggle_favorite(book_id):
                print("Книга с таким ID не найдена.")

        elif choice == '7':
            book_id = get_int_input("\nВведите ID книги для удаления: ")
            confirm = input(f"Вы уверены? (да/нет): ")
            if confirm.lower() == 'да':
                if not manager.delete_book(book_id):
                    print("Книга с таким ID не найдена.")
            else:
                print("Удаление отменено.")

        elif choice == '8':
            print("До свидания! Хорошего чтения!")
            break
        
        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    main()