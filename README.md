# Bookie
A backend utility to create and manage a personal library powered by Google Books API.

## Tech Stack
* **Language:** Python
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Migrations:** Alembic
* **Framework:** FastAPI
* **Auth:** JWT
* **Environment:** Developed using Neovim and WezTerm

## Features
* **Dependency Management:** Uses FastAPi Depends to inject services into endpoints for decoupling
* **Persistent Storage:** Uses PostgreSQL integration for storing users and books.
* **JWT Authentication:** Uses FastAPI Depends to create middleware and authenticate the use of each endpoint
* **Procedural Generation:** Uses the Gemini API to create book recommendations.

## Prerequisites
* **Python:** Version 3.14 was used in this project
* **PostgreSQL:** A running instance for data persistence

## Installation & Setup:
1. **Clone and Enter the Repository:**
2. ```
   git clone https://github.com/Barms1218/bookie.git
   ```
   ```
   cd bookie
   ```

   2. **Configure Environment Variables:**
      ```
      db_user=postgres_user_name
      db_password=postgres-password
      db_host=host
      db_port=5432
      db_name=bookie
      google_api_key=google_books_api_key
      gemini_api_key=gemini_api_key
      secret_key=secret key
      algorithm=algorithm
      ```

3. **WIP:**
   
4. **Handle Dependencies:**
   ```
   pip install -r requirements.txt
   ```
5. **Running the App:**
   ```
   fastapi run main.py
   ```

## Engineering Decisions
* PostgreSQL was chosen for its enterprise ability. The dream for this app is to have it be a book club service.
* FastAPI was chosen for its type annotations and its dependency injection system. It also made troubleshooting far smoother.
* SQLAlchemy was chosen for its ability to manage relationships between entities.
* Alembic was chosen because it was developed by the same author as SQLAlchemy.
* Gemini was chosen due to its ability to connect to Google Books

  **Example of a prompt to Gemini**
  ```
        context_payload = [schema.model_dump_json(exclude_none=True) for schema in user_profile]
        system_msg = (
            "You are a sophisticated book recommendation engine. "
            "Analyze the provided reading history where 4-5 stars indicate strong preference. "
            "Provide 3 suggestions for new books NOT in the list. The suggestions must not include a title from the list."
            "Each suggestion must include a reason linking back to  the user's favorite tags and authors."
        )
        response = await self.genai.aio.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"User's top Books History: {user_data}",
                    config=types.GenerateContentConfig(
                        system_instruction=system_msg,
                        response_mime_type="application/json",
                        response_schema={
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "title": {"type": "STRING"},
                                "author": {"type": "STRING"},
                                "reason": {"type": "STRING"},
                                "confidence_score": {"type": "NUMBER"}
                                },
                            "required": ["title", "author", "reason"]
                            } 
                        }
                    )
                )

        content = response.text
  ```

  ## Roadmap
  * [ ] **Expand AI Generation:** Add more AI features such as tag recommendation, and improved book searching.
