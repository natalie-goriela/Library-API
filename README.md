# Library-API

API service that helps to manage borrowings from the library.

### This project includes following features:

1. JWT authentication
2. CRUD operations: The API includes basic CRUD (Create, Read, Update, Delete) operations on resources such as books, borrowers, and borrowing records.
3. Filtering books by title and authors.
4. Filtering borrowing by active borrowing and user_id.
5. Pagination implemented.

### To run this project locally:

To run this projects locally, use the following steps:

1. Clone repo from GIT:

`git clone git@github.com:natalie-goriela/Library-API.git`

2. If you are using PyCharm - it may propose you to automatically create venv for your project 
and install requirements in it, but if not: 

```python
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
```

3. Run the migrations:

`python manage.py migrate`

### Environment variables

The secret key to this project is saved within .env file, which is hidden.
You can create your own `.env` file to store your `SECRET_KEY` and other environment 
variables like it is shown in `.env_sample` file. 
