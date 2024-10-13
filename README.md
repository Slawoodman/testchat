# Simple chat

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone <repo_url>
   cd messaging_app

2. Install dependencies:

    ```bash
    pip install -r requirements.txt

3. Apply migrations and load test data:

    ```bash
        python manage.py migrate
        python manage.py loaddata test_data.json

4. Run the server:
    ```bash
    python manage.py runserver

5. User info:
    ```bash
    username: admin
    password: admin