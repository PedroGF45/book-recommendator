CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    author VARCHAR(100) NOT NULL,
    genres VARCHAR(100) NOT NULL,
    description TEXT NOT NULL
);

CREATE TYPE reading_status AS ENUM ('reading', 'completed', 'on-hold', 'dropped', 'plan to read');

CREATE TABLE user_books (
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    status reading_status NOT NULL,
    rating FLOAT CHECK (rating BETWEEN 1.0 AND 5.0),
    review TEXT,
    PRIMARY KEY (user_id, book_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);