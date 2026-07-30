# read json first n objects
import json

def read_json_first_n_objects(file_path, n) -> list[dict]:
    with open(file_path, 'r') as file:
        objects = []
        for _ in range(n):
            line = file.readline()
            if not line:
                break
            objects.append(json.loads(line.strip()))
    return objects


def main():
    file_path = 'C:\\Users\\pedro\\Downloads\\goodreads_reviews_dedup.json\\goodreads_reviews_dedup.json'  # Replace with your JSON file path
    first_100_objects = read_json_first_n_objects(file_path, 20)
    for book in first_100_objects:
        print(book)
        #print(f'ISBN: {book.get("isbn")} or ISBN13: {book.get("isbn13")}')
        #print(f'ISBN: {book.get("isbn")}, Title: {book.get("title")}, Author: {book.get("authors")[0].get("author_id")}, Publisher: {book.get("publisher")}, Publication Year: {book.get("publication_year")}, Number of Pages: {book.get("num_pages")}, Ratings Count: {book.get("ratings_count")}, Average Rating: {book.get("average_rating")}, Description: {book.get("description")}')
        print("\n")
if __name__ == "__main__":
    main()