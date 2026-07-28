from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database.connection_manager import ConnectionManager
from logs.log_manager import LogManager
from services.book_service import BookService

# 1 Core Services Initializations
log_manager = LogManager()
connection_manager = ConnectionManager(log_manager=log_manager)
book_service = BookService(log_manager=log_manager, connection_manager=connection_manager, api_base_url="https://www.googleapis.com/books/v1/volumes?q=isbn:")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Clean shutdown of connection pool when server stops/reloads
    connection_manager.close_connection_pool()

app = FastAPI(title="Book Recommendator", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# 2 Routes
# --- READ ALL ---
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    books = book_service.get_all_books()
    return templates.TemplateResponse("index.html", {"request": request, "books": books})

# --- CREATE (Manual or ISBN) ---
@app.get("/books/new", response_class=HTMLResponse)
def new_book_form(request: Request):
    return templates.TemplateResponse("book_form.html", {"request": request, "book": None})

@app.post("/books/add-isbn")
def add_by_isbn(request: Request, isbn: str = Form(...)):
    book = book_service.get_or_fetch_book_by_isbn(isbn.strip())
    if not book:
        books = book_service.get_all_books()
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "books": books, "error": f"ISBN '{isbn}' not found online."}
        )
    return RedirectResponse(url="/", status_code=303)

@app.post("/books/create")
def create_manual_book(
    title: str = Form(...),
    author: str = Form(...),
    genres: str = Form(""),
    isbn: str = Form(""),
    description: str = Form("")
):
    book_service.create_book(title=title, author=author, description=description, genres=genres, isbn=isbn)
    return RedirectResponse(url="/", status_code=303)

# --- UPDATE ---
@app.get("/books/{book_id}/edit", response_class=HTMLResponse)
def edit_book_form(request: Request, book_id: int):
    book = book_service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return templates.TemplateResponse("book_form.html", {"request": request, "book": book})

@app.post("/books/{book_id}/update")
def update_book(
    book_id: int,
    title: str = Form(...),
    author: str = Form(...),
    genres: str = Form(""),
    isbn: str = Form(""),
    description: str = Form("")
):
    book_service.update_book(book_id, title, author, description, genres, isbn)
    return RedirectResponse(url="/", status_code=303)

# --- DELETE ---
@app.post("/books/{book_id}/delete")
def delete_book(book_id: int):
    book_service.delete_book(book_id)
    return RedirectResponse(url="/", status_code=303)