import os
from typing import List, Dict, Any

import bson
from dotenv import load_dotenv
from flask import Flask, render_template, request
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

# Access your MongoDB Atlas cluster and get a `Cursor` to its `books` collection.
load_dotenv()
connection_string: str = os.environ.get("CONNECTION_STRING")
mongo_client: MongoClient = MongoClient(connection_string)
bookshelf_database: Database = mongo_client.get_database("bookshelf")
books_collection: Collection = bookshelf_database.get_collection("books")

app: Flask = Flask(__name__)


# The default endpoints "/"
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/books", methods=["GET", "POST"])
def books():
    if request.method == "POST":
        # CREATE
        title: str = request.json["title"]
        pages: str = request.json["pages"]
        books_collection.insert_one({"title": title, "pages": pages})
        return f"CREATE: Your book {title} ({pages} pages) has been added to your bookshelf.\n"

    elif request.method == "GET":
        # READ
        book_list: List[Dict[Any, Any]] = list(books_collection.find())
        book_list = list(
            map(lambda book: {"id": str(book["_id"]), "title": book["title"], "pages": book["pages"]}, book_list))
        return book_list

    else:
        return "Method not allowed!\n"


# UPDATE
@app.route("/books/<string:book_id>", methods=["PUT"])
def update_book(book_id: str):
    title: str = request.json["title"]
    pages: str = request.json["pages"]
    books_collection.update_one({"_id": bson.ObjectId(book_id)},
                                {"$set": {"book": title, "pages": pages}})

    return f"Update: Your book has been updated to: {title} ({pages} pages)\n"


# DELETE
@app.route("/books/<string:book_id>", methods=["DELETE"])
def remove_book(book_id: str):
    books_collection.delete_one({"_id": bson.ObjectId(book_id)})

    return f"DELETE: Your book (id = {book_id}) has been removed from your bookshelf.\n"
