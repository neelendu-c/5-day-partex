This project is a backend API made for managing a hotel room system, with two prominent features - 

Chat Agent System: Interacts with user requests using an LLM backend using a ReAct agent loop

Room Management System: Handles standard database operations and advanced sorting and filtering on request.


Pre-Requisites:

Python 3.14.5

Ollama 2.41.0 - Llama 3.2 3B Model

MongoDB 8.0.26 - Local or Atlas hosted


Environment Variables:

MongoDB URI

Ollama Model


Libraries:

FastAPI (3.14.5)

Llama-Index libraries (0.14.22)

Uvicorn (0.48.0)

Pydantic (2.13.4) + Pydantic-Core (2.46.4)

PyMongo (4.17.0)


API Endpoints:

1. System Health - Check if the FastAPI instance is online

2. Room Assistant - AI chatbot performing CRUD operations or returning relevant information based on user requests

3. Room Management (CRUD) - Can create, read, update, and delete rooms 

4. Sorting and Filtering - Sorts and filters according to specific parameters such as name, price, etc.