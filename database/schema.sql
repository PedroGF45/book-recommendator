CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    goodreads_id VARCHAR(64) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE books (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    goodreads_id BIGINT NOT NULL UNIQUE,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    publisher VARCHAR(255) NOT NULL,
    publication_year INT CHECK (publication_year >= 0),
    num_pages INT CHECK (num_pages >= 0),
    ratings_count INT CHECK (ratings_count >= 0),
    average_rating FLOAT CHECK (average_rating BETWEEN 0.0 AND 5.0),
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_book_reviews (
    user_id BIGINT NOT NULL,
    book_id BIGINT NOT NULL,
    rating FLOAT CHECK (rating BETWEEN 1.0 AND 5.0),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, book_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);