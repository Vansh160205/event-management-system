# Event Management System API

A robust, secure, and full-featured RESTful API for an Event Management platform. Built with Django and Django REST Framework (DRF), this API allows users to create events, manage attendance via an RSVP system, and leave reviews. The project is secured using JWT token authentication and features a comprehensive, role-based permission system.

-----

## 🚀 Key Features

  * **JWT Authentication:** Secure stateless authentication using `djangorestframework-simplejwt`.
  * **Custom User Model:** Extends the built-in Django `User` model to include `full_name`, `bio`, `location`, and `profile_picture`.
  * **Advanced Role-Based Permissions:**
      * **Organizers:** Only the creator (organizer) of an event can update or delete it.
      * **Private Events:** Events marked as `is_public=False` are only visible to the organizer and users explicitly added to the `invited` list.
  * **Full CRUD Functionality:** A complete `ModelViewSet` for `Event` management.
  * **RSVP & Review System:**
      * Users can RSVP ('Going', 'Maybe', 'Not Going') to any event. The system smartly handles both creating a new RSVP and updating an existing one with a single `POST` request.
      * Users can leave a rating and a comment for an event.
      * `unique_together` constraints prevent users from RSVPing or reviewing the same event multiple times.
  * **Pagination:** All list endpoints are paginated for performance.
  * **Search & Filtering (Optional Feature):** The `Event` list endpoint supports full-text search and field-based filtering.
  * **Comprehensive Test Suite:** Includes 10+ unit tests covering all core functionality, authentication, and permission logic.

-----

## 🛠️ Technical Stack

  * **Backend:** Django, Django REST Framework
  * **Authentication:** `djangorestframework-simplejwt`
  * **Database:** SQLite3 (development)
  * **Filtering:** `django-filter`
  * **Testing:** DRF `APITestCase`

-----

## 🏁 Getting Started

Follow these instructions to set up and run the project locally.

### 1\. Prerequisites

  * Python 3.10 or newer
  * `pip` and `venv`

### 2\. Local Installation

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd event-management
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    *(First, create the `requirements.txt` file if you haven't already)*

    ```bash
    pip freeze > requirements.txt
    ```

    *(Then install)*

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the database:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

    The API will be live at `http://127.0.0.1:8000/`.

-----

## 🧪 Running Tests

The project is configured with a full test suite. To run the tests:

```bash
python manage.py test events
```

You should see all 10 tests pass.

-----

## 🔑 API Endpoint Documentation

All endpoints are prefixed with `/api/`.

### Authentication

#### `POST /api/token/`

Obtain a new JWT access and refresh token pair.

  * **Body:**
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```

#### `POST /api/token/refresh/`

Refresh an expired access token using a refresh token.

  * **Body:**
    ```json
    {
        "refresh": "your_refresh_token"
    }
    ```

-----

### Events (`/api/events/`)

#### `GET /api/events/`

Get a paginated list of all **public** events.

  * **Auth:** Not Required.
  * **Query Parameters (Filtering & Search):**
      * `?search=<term>`: Searches `title` and `description`.
      * `?location=<city>`: Filters by exact location.
      * `?organizer__username=<name>`: Filters by organizer's username.

#### `POST /api/events/`

Create a new event. The authenticated user will be set as the `organizer`.

  * **Auth:** **Bearer Token Required.**
  * **Body:**
    ```json
    {
        "title": "My New Event",
        "description": "A description of the event.",
        "location": "Mumbai",
        "start_time": "2025-12-25T18:00:00Z",
        "end_time": "2025-12-25T22:00:00Z",
        "is_public": true,
        "invited": [2, 3]
    }
    ```

#### `GET /api/events/{id}/`

Get the details of a specific event.

  * **Auth:** **Bearer Token Required.**
  * **Permissions:** Access is granted only if:
    1.  The event is public.
    2.  The user is the event organizer.
    3.  The user is in the event's `invited` list.

#### `PUT /api/events/{id}/`

Update a specific event.

  * **Auth:** **Bearer Token Required.**
  * **Permissions:** Only the **event organizer** can perform this action.

#### `DELETE /api/events/{id}/`

Delete a specific event.

  * **Auth:** **Bearer Token Required.**
  * **Permissions:** Only the **event organizer** can perform this action.

-----

### RSVP (`/api/events/{event_id}/rsvp/`)

#### `POST /api/events/{event_id}/rsvp/`

Create a new RSVP or update an existing one for the authenticated user.

  * **Auth:** **Bearer Token Required.**

  * **Body:**

    ```json
    {
        "status": "Going"
    }
    ```

    *Valid statuses: "Going", "Maybe", "Not Going".*

  * **Design Note:** This single endpoint uses `update_or_create` to handle both `POST` (create) and `PATCH` (update) logic. This is a cleaner, more efficient, and more secure approach than the specified `PATCH /.../{user_id}/`, as it operates directly on the authenticated user.

-----

### Reviews (`/api/events/{event_id}/reviews/`)

#### `GET /api/events/{event_id}/reviews/`

Get a paginated list of all reviews for a specific event.

  * **Auth:** Not Required.

#### `POST /api/events/{event_id}/reviews/`

Create a new review for an event. A user can only review an event once.

  * **Auth:** **Bearer Token Required.**
  * **Body:**
    ```json
    {
        "rating": 5,
        "comment": "This was a fantastic event!"
    }
    ```
