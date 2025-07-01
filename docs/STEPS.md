#### **Step 1: Project Setup and Environment Configuration**

1.  **Initialize Project Structure:** Create a new project directory with a standard FastAPI layout (e.g., a main `app` directory with sub-modules for routes, models, schemas, and services).
2.  **Set Up `requirements.txt`:** Create a `requirements.txt` file and add the initial dependencies:
      * `fastapi`
      * `uvicorn`
      * `sqlalchemy`
      * `psycopg2-binary`
      * `alembic`
      * `python-dotenv`
      * `pytest`
      * `httpx` (for TestClient)
      * `datasets` (for Hugging Face access).
3.  **Basic FastAPI App:** Create a `main.py` file with a basic "Hello World" FastAPI application instance to ensure the setup works.
4.  **Database Setup (Docker):** Create a `docker-compose.yml` file to run a PostgreSQL service. Configure it with environment variables for the database user, password, and name.
5.  **README (Initial):** Create a `README.md` file and add initial setup instructions for installing dependencies and starting the database with Docker Compose.

-----

#### **Step 2: Database Modeling and Migrations**

1.  **SQLAlchemy Models:** Inside your application's models module, define the database schema using SQLAlchemy. Create at least two tables: one for the support tickets and another for the AI classification results, or a single table that can store all required fields. The schema must accommodate fields like `subject`, `body`, `queue`, `category`, `priority`, `language`, and the AI-generated results.
2.  **Alembic Setup:** Initialize Alembic in your project to manage database migrations.
3.  **Create Initial Migration:** Generate the first Alembic migration script (`alembic revision --autogenerate`) that creates the tables based on your SQLAlchemy models.
4.  **Apply Migration:** Add a command to the `README.md` explaining how to apply the migration (`alembic upgrade head`).

-----

#### **Step 3: Implement Core API Endpoints and Schemas**

1.  **Pydantic Schemas:** In a schemas module, define Pydantic models for request and response validation. Create schemas for:
      * A request body that accepts either `{"text": "..."}` or `{"subject": "...", "body": "..."}`.
      * A response model that includes the stored record fields along with the AI-generated fields (category, confidence_score, summary).
2.  **API Routes:** Create a routes module for your API endpoints.
3.  **Implement Endpoints (No AI yet):**
      * **`POST /requests`:** Implement the endpoint to validate the incoming payload, store the raw data in the database (leaving AI fields null for now), and return the created record.
      * **`GET /requests/{id}`:** Implement the endpoint to retrieve a single record by its ID from the database.

-----

#### **Step 4: Database Seeding with Hugging Face Dataset**

1.  **Create Seeding Script:** Create a script named `scripts/seed_db.py`.
2.  **Load Dataset:** Inside the script, use the `datasets` library to load the `tobi-bueck/customer-support-tickets` dataset from Hugging Face. Filter for English-language tickets only.
3.  **Populate Database:** Iterate through the dataset rows. For each row, concatenate the `subject` and `body` fields and insert a new record into your support tickets table. Store other relevant fields like `queue`, `priority`, and `language` as well.

-----

#### **Step 5: AI/ML Service Integration**

1.  **Create AI Service Module:** Create a dedicated module (e.g., `services/ai_classifier.py`) for the AI/ML logic.
2.  **Choose Model:** Select and configure a pre-trained model for text classification (e.g., from Hugging Face, OpenAI, or a `scikit-learn` pipeline). Manage API keys using environment variables.
3.  **Implement Classification Logic:** Create a function that takes text as input and performs the following:
      * Classifies the text into `technical`, `billing`, or `general` based on the required mapping:
          * `Technical Support`/`IT Support` -\> `technical`
          * `Billing and Payments` -\> `billing`
          * `Customer Service`/`Product Support` -\> `general`
      * Generates a confidence_score score. You can reference the dataset's `priority` field for this logic (`Critical` -\> high, `Medium` -\> medium, `Low` -\> low).
      * (https://www.google.com/search?q=Optional) Generates a one-sentence summary, using the dataset's `answer` field as a reference if needed.
4.  **Integrate with API:** Modify the `POST /requests` endpoint. After storing the initial record, trigger the AI processing asynchronously. Once the AI processing is complete, update the record in the database with the `category`, `confidence_score`, and `summary`.

-----

#### **Step 6: Finalize API Endpoints**

1.  **Implement Filtered GET:** Implement the logic for `GET /requests?category=<category>` to filter and list records based on their mapped category.
2.  **Implement Stretch Goal `GET /stats`:** Implement the `GET /stats` endpoint to return the counts of requests per category over the past seven days.
3.  **Refine Error Handling:** Ensure all endpoints return appropriate HTTP status codes with clear error messages for events like validation errors or records not being found.

-----

#### **Step 7: Testing**

1.  **Unit Tests:** In your tests directory, create unit tests for the core logic. At a minimum, test the category mapping function to ensure it correctly maps `queue` values to `technical`, `billing`, or `general`.
2.  **Integration Tests:** Use FastAPI's `TestClient` to write integration tests for the API endpoints. Test the full flow:
      * `POST` a new request.
      * `GET` the request by its ID to verify it was stored correctly and that the (mocked or real) AI fields are populated.
      * Use the filtering and stats endpoints to verify their functionality.
3.  **Single Command Execution:** Configure your project so that `pytest` runs the entire test suite.

-----

#### **Step 8: Final Write-Up and Documentation**

1.  **Complete the README.md:** Finalize the `README.md` file with comprehensive instructions covering all setup, configuration, migration, and execution commands.
2.  **Generate Write-Up:** Create a separate `WRITE_UP.md` file. Based on the code you have generated, write content addressing the following key points:
      * **Architecture & Design:** Explain your FastAPI structure and data model choices.
      * **Security Approach:** Detail how you handled secrets and input validation and suggest next steps for production security.
      * **AI/ML Integration:** Justify your model choice, describe the integration strategy, and list limitations.
      * **Testing Strategy:** Describe your test coverage and any gaps you'd address later.
      * **Trade-offs & Next Steps:** Document any assumptions made and outline what features you would prioritize next.