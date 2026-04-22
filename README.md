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
      DB_USER=your_user
      DB_PASSWORD=your_password
      DB_HOST=localhost
      DB_PORT=5432
      DB_NAME=bookie
      GOOGLE_API_KEY=your_google_books_key
      GEMINI_API_KEY=your_gemini_key
      SECRET_KEY=your_jwt_secret
      ALGORITHM=HS256
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
* **PostgreSQL:** Chosen for its enterprise-grade reliability and native support for complex relational data, supporting a future vision of a multi-user "Book Club" service.
* **FastAPI:** Selected for its robust type annotations and dependency injection system, which significantly streamlined the development and troubleshooting process.
* **SQLAlchemy & Alembic:** Paired together to manage complex entity relationships and version-controlled database migrations.
* **Gemini 2.5 Flash:** Utilized for its deep integration with the Google ecosystem and its ability to process reading history for high-context recommendations.

  **Structured AI Prompting**
  This project utilizes Gemini's response_schema to enforce strict JSON output, ensuring the recommendation engine always returns valid, consumable data:
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
  * [ ] **Book Club Service:** Add social features for book clubs such as invitations, chat, and book-of-the-month tracking.
