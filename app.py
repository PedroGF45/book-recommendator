from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database.connection_manager import ConnectionManager
from logs.log_manager import LogManager
from services.book_service import BookService

# 1 Core Services Initializations
log_manager = LogManager()
connection_manager = ConnectionManager(log_manager=log_manager)
book_service = BookService(log_manager=log_manager, connection_manager=connection_manager, api_base_url="https://api.example.com/books/")

app = FastAPI(title="Book Recommendator")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# 2 Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/books/add", response_class=HTMLResponse)
async def add_book_by_isbn(request: Request, isbn: str = Form(...)):
    try:
        book = book_service.get_book_by_isbn(isbn)
        if not book:
            return templates.TemplateResponse(
            "index.html", 
            {"request": request, "error": f"Book with ISBN '{isbn}' not found."}
        )

        log_manager.log("INFO", f"Book with ISBN {isbn} not found.")
        
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        log_manager.log("ERROR", f"Error adding book with ISBN {isbn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")