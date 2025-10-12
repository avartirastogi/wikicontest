

##  WikiContest  – Setup Guide

This project contains both frontend and backend code for wikicontest platform.

### Demo 
![alt text](demo.gif)
---

##  Project Structure

```
wikicontest/
├── backend/
│   ├── index.js
│   └── ...other server files
└── frontend/
    ├── src/
    └── ...React app files
```

---

##  Prerequisites

* **Node.js** (v18+ recommended)
* **npm**

---

## Backend Setup

1. **Navigate to the backend folder:**

   ```bash
   cd backend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Run the backend:**

   ```bash
   npm start
   ```

   The backend will start on [http://localhost:3000](http://localhost:3000).

---

## Frontend Setup

1. **Navigate to the frontend folder:**

   ```bash
   cd ../frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Start the React app:**

   ```bash
   npm start
   ```

   The frontend will start on [http://localhost:5173](http://localhost:3000).


##  Scripts

### Backend

```bash
npm start       # Runs the backend
npm run dev     # (if using nodemon)
```

### Frontend

```bash
npm start       # Runs the React app
```


***

### **What is the WikiContest Tool?**

The WikiContest Tool is a dynamic web platform designed for hosting and participating in collaborative online competitions, particularly those centered around content creation for wiki-based projects like Wikipedia. It provides a comprehensive suite of features for contest organizers, participants, and judges to manage every aspect of a contest from start to finish.
- This tool is inspired by the **Fountain Tool**.
### **What is it Used For?**

This tool is used to foster community engagement and encourage the creation of high-quality content. It is the perfect solution for communities, organizations, or user groups who want to:

*   **Organize Writing Competitions:** Easily set up contests where users submit articles or other content to be reviewed and scored.
*   **Track Contributions:** Provide a centralized platform for participants to submit their work and for organizers to track all entries for a specific contest.
*   **Automate Scoring and Leaderboards:** Simplify the judging process by allowing designated jury members to review submissions, assign scores, and automatically update a public leaderboard.
*   **Enhance Community Collaboration:** Create a fun and competitive environment that motivates users to contribute to a shared goal, such as improving the content of a specific wiki or project.

### **Key Features for Different Users**

*   **For Contest Organizers (Creators):**
    *   Create and customize new contests with unique names, descriptions, rules, and timelines.
    *   Define the scoring system by setting points for accepted or rejected submissions.
    *   Appoint a panel of judges (jury members) to review the entries.
    *   Monitor all submissions for the contests they've created.

*   **For Participants:**
    *   Register for an account and browse current, upcoming, and past contests.
    *   Submit their work (e.g., an article link and title) to any active contest.
    *   Track the status and score of their own submissions through a personal dashboard.
    *   View their overall score and how they rank against others in contest-specific leaderboards.

*   **For Judges (Jury Members):**
    *   Access a dedicated view to see all submissions for the contests they are assigned to judge.
    *   Review each submission and update its status to "accepted" or "rejected."
    *   The system automatically assigns the score based on the contest's predefined settings, ensuring fair and consistent judging.

In essence, the WikiContest Tool streamlines the entire process of running an online content competition, making it easy, transparent, and engaging for everyone involved.


### **Can a user create a contest, be a participant, and be a jury member?**

**Yes, absolutely.** A single user account can perform all of these roles simultaneously, just typically not all within the *same* contest.

Here’s a practical scenario:

*   User **`Alex`** can **create** "Contest A".
*   `Alex` can then **participate** in "Contest B" (created by someone else) by submitting an article.
*   Finally, `Alex` can be appointed as a **jury member** for "Contest C" by its creator.

The system is designed to be flexible. A user's permissions are not limited to a single function; they are based on their actions and the specific context of each contest.

---

### **Breakdown of User Roles**

Your system has two types of roles: **Static Roles** that are assigned to a user account, and **Contextual Roles** that a user gains based on their relationship to a specific contest.

#### **1. Static Roles**

These are the primary roles stored directly in the `users` database table.

##### **Admin**

*   **How they become one:** An administrator must have their `role` field set to `'admin'` in the database, likely done manually by a developer or another admin.
*   **Permissions (Super User):**
    *   Has all the permissions of a Standard User.
    *   Can view a list of **all users** on the platform.
    *   Can view a list of **all submissions** across **all contests**.
    *   Can **delete any contest**, regardless of who created it.
    *   Can **judge any submission** in **any contest**, effectively acting as a universal jury member.

##### **Standard User**

*   **How they become one:** This is the default role assigned to any new user who registers on the platform.
*   **Permissions:**
    *   Can log in and manage their own account.
    *   Can view their personal dashboard with their scores and submission history.
    *   Can browse all public contests (current, upcoming, and past).
    *   **Can create new contests.**
    *   **Can participate** in any active contest by submitting an entry.

#### **2. Contextual Roles**

These roles are not stored in the user's profile. Instead, they are temporary privileges a user has in the context of a *specific contest*.

##### **Contest Creator (`creator_contest`)**

*   **How they become one:** A user automatically becomes the "Creator" of a contest the moment they successfully create it.
*   **Permissions (for their own contests only):**
    *   Can view all submissions made to the contests they created.
    *   Can delete the contests they created.

##### **Jury Member (`jury_contest` / `jury_submission`)**

*   **How they become one:** A Contest Creator must add their username to the `jury_members` list when creating or editing a contest.
*   **Permissions (for their assigned contests only):**
    *   Can view all submissions made to the contests they are a judge for.
    *   Can review individual submissions and update their status to "accepted" or "rejected".
    *   When they update a submission's status, the system automatically assigns the correct score based on the contest's settings.

##### **Participant (Submission Owner)**

*   **How they become one:** A user becomes a "Participant" in a contest as soon as they submit an entry. The code refers to this as the `owner` of a submission.
*   **Permissions:**
    *   Can view the details and status of their own submissions.



## Backend Documentation

### **1. Introduction**

This document outlines the backend functionality of the WikiContest tool, a platform for hosting and managing wiki-based contests. It allows users to register, create contests, submit entries, and have those entries judged. The system is built with Node.js and Express.js, using a SQLite database.

### **2. Database Schema**

The application uses a SQLite database to store its data. The database consists of three main tables: `users`, `contests`, and `submissions`.

#### **`users` Table**

This table stores information about the users of the platform.

| Column | Type | Description |
| --- | --- | --- |
| id | INTEGER | Primary Key, Auto-incrementing |
| username | TEXT | Unique username |
| email | TEXT | Unique email address |
| role | TEXT | User role (e.g., 'admin', 'user') |
| password | TEXT | Hashed password |
| score | INTEGER | User's total score, defaults to 0 |
| created_at | TIMESTAMP | Timestamp of user creation |

#### **`contests` Table**

This table stores information about the contests created on the platform.

| Column | Type | Description |
| --- | --- | --- |
| id | INTEGER | Primary Key, Auto-incrementing |
| name | TEXT | Name of the contest |
| code_link | TEXT | Link to the contest's code repository |
| project_name | TEXT | Name of the associated project (e.g., 'Wikimedia') |
| created_by | TEXT | Username of the user who created the contest (Foreign Key to `users.username`) |
| description | TEXT | A description of the contest |
| start_date | DATE | The start date of the contest |
| end_date | DATE | The end date of the contest |
| rules | TEXT | JSON string containing the contest rules |
| marks_setting_accepted | INTEGER | Marks awarded for an accepted submission, defaults to 0 |
| marks_setting_rejected | INTEGER | Marks awarded for a rejected submission, defaults to 0 |
| jury_members | TEXT | Comma-separated list of usernames of the jury members |
| created_at | TIMESTAMP | Timestamp of contest creation |

#### **`submissions` Table**

This table stores information about the submissions made by users to contests.

| Column | Type | Description |
| --- | --- | --- |
| id | INTEGER | Primary Key, Auto-incrementing |
| user_id | INTEGER | ID of the user who made the submission (Foreign Key to `users.id`) |
| contest_id | INTEGER | ID of the contest the submission is for (Foreign Key to `contests.id`) |
| article_title | TEXT | Title of the submitted article |
| article_link | TEXT | URL link to the submitted article |
| status | TEXT | Status of the submission (e.g., 'pending', 'accepted', 'rejected') |
| score | INTEGER | Score awarded to the submission, defaults to 0 |
| submitted_at | TIMESTAMP | Timestamp of when the submission was made |

### **3. API Endpoints**

The application exposes a set of RESTful API endpoints to interact with the aplication's resources.

#### **3.1. User Endpoints**

These endpoints are related to user management.

*   **`POST /api/user/register`**
    *   **Description:** Registers a new user.
    *   **Request Body:**
        *   `username` (string, required): The user's desired username.
        *   `email` (string, required): The user's email address.
        *   `password` (string, required): The user's password.
        *   `role` (string, optional): The user's role (defaults to 'user').
    *   **Response:**
        *   `201 Created`: Returns a success message and the new user's ID and username.
        *   `500 Internal Server Error`: If there is a server-side error.

*   **`POST /api/user/login`**
    *   **Description:** Logs in a user.
    *   **Request Body:**
        *   `email` (string, required): The user's email address.
        *   `password` (string, required): The user's password.
    *   **Response:**
        *   `200 OK`: Returns a success message, user ID, and username. Sets a `uid` cookie for session management.
        *   `401 Unauthorized`: If the email or password is a invalid.
        *   `500 Internal Server Error`: If there is a server-side error.

*   **`POST /api/user/logout`**
    *   **Description:** Logs out the currently logged-in user.
    *   **Permissions:** Logged-in user.
    *   **Response:**
        *   `200 OK`: Returns a success message and clears the `uid` cookie.

*   **`GET /api/user/dashboard`**
    *   **Description:** Retrieves the dashboard information for the currently logged-in user.
    *   **Permissions:** Logged-in user.
    *   **Response:**
        *   `200 OK`: Returns a JSON object containing the user's total score, contest-wise scores, submissions by contest, created contests, and contests they are a jury member for.
        *   `401 Unauthorized`: If the user is not logged in.
        *   `500 Internal Server Error`: If there is a server-side error.

*   **`GET /api/user/all`**
    *   **Description:** Retrieves a list of all users.
    *   **Permissions:** `admin` role.
    *   **Response:**
        *   `200 OK`: Returns an array of user objects.
        *   `401 Unauthorized`: If the user is not logged in.
        *   `403 Forbidden`: If the user does not have the 'admin' role.
        *   `500 Internal Server Error`: If there is a server-side error.

#### **3.2. Contest Endpoints**

These endpoints are for managing contests.

*   **`GET /api/contest`**
    *   **Description:** Retrieves a list of all contests, categorized as 'current', 'upcoming', and 'past'.
    *   **Response:**
        *   `200 OK`: Returns an object with arrays of contests for each category.
        *   `500 Internal Server Error`: If there is a server-side error.

*   **`POST /api/contest`**
    *   **Description:** Creates a new contest.
    *   **Permissions:** Logged-in user.
    *   **Request Body:**
        *   `name` (string, required): The name of the contest.
        *   `code_link` (string, optional): A link to the contest's code repository.
        *   `project_name` (string, required): The name of the project.
        *   `description` (string, optional): A description of the contest.
        *   `start_date` (Date, optional): The start date of the contest.
        *   `end_date` (Date, optional): The end date of the contest.
        *   `rules` (object, optional): A JSON object containing the rules.
        *   `marks_setting_accepted` (integer, optional): Marks for an accepted submission.
        *   `marks_setting_rejected` (integer, optional): Marks for a rejected submission.
        *   `jury_members` (array of strings, required): An array of usernames for the jury.
    *   **Response:**
        *   `201 Created`: Returns a success message and the new contest's ID.
        *   `400 Bad Request`: If jury members are not a non-empty array or if any jury members do not exist.
        *   `401 Unauthorized`: If the user is not logged in.
        *   `500 Internal Server Error`: If there is a server-side error.

*   **`GET /api/contest/:id`**
    *   **Description:** Retrieves a single contest by its ID.
    *   **URL Parameters:**
        *   `id` (integer, required): The ID of the contest.
    *   **Response:**
        *   `200 OK`: Returns the contest object.
        *   `404 Not Found`: If the contest is not found.
        *   `500 Internal Server Error`: If there is a server-side error.

*   **`GET /api/contest/:id/leaderboard`**
    *   **Description:** Retrieves the leaderboard for a specific contest.
    *   **URL Parameters:**
        *   `id` (integer, required): The ID of the contest.
    *   **Response:**
        *   `200 OK`: Returns an array of objects, each containing `user_id`, `username`, and `total_score`, sorted by `total_score` in descending order.
        *   `500 Internal Server Error`: If there is a server-side error.

*   **`DELETE /api/contest/:id`**
    *   **Description:** Deletes a contest.
    *   **Permissions:** `admin` role or the creator of the contest (`creator_contest`).
    *   **URL Parameters:**
        *   `id` (integer, required): The ID of the contest to delete.
    *   **Response:**
        *   `200 OK`: Returns a success message.
        *   `403 Forbidden`: If the user is not the creator or an admin.
        *   `404 Not Found`: If the contest is not found.
        *   `500 Internal Server Error`: If there is a server-side error.

*   **`POST /api/contest/:id/submit`**
    *   **Description:** Submits an entry to a contest.
    *   **Permissions:** Logged-in user.
    *   **URL Parameters:**
        *   `id` (integer, required): The ID of the contest.
    *   **Request Body:**
        *   `article_title` (string, required): The title of the article.
        *   `article_link` (string, required): A valid URL to the article.
    *   **Response:**
        *   `201 Created`: Returns a success message, submission ID, contest ID, and article title.
        *   `400 Bad Request`: If the article title is empty, the link is not a valid URL, the contest has not started or has ended, or the user has already submitted to the contest.
        *   `401 Unauthorized`: If the user is not logged in.
        *   `404 Not Found`: If the contest is not found.
        *   `500 Internal Server Error`: If there is a server-side error.

*   **`GET /api/contest/:id/submissions`**
    *   **Description:** Retrieves all submissions for a specific contest.
    *   **Permissions:** `admin`, `jury_contest`, or `creator_contest`.
    *   **URL Parameters:**
        *   `id` (integer, required): The ID of the contest.
    *   **Response:**
        *   `200 OK`: Returns an array of submission objects.
        *   `401 Unauthorized`: If the user is not logged in.
        *   `403 Forbidden`: If the user does not have the required permissions.
        *   `404 Not Found`: If the contest is not found.
        *   `500 Internal Server Error`: If there is a server-side error.

#### **3.3. Submission Endpoints**

These endpoints are for managing individual submissions.

*   **`GET /api/submission`**
    *   **Description:** Retrieves all submissions across all contests.
    *   **Permissions:** `admin` role.
    *   **Response:**
        *   `200 OK`: Returns an array of all submission objects.
        *   `401 Unauthorized`: If the user is not logged in.
        *   `403 Forbidden`: If the user does not have the 'admin' role.
        *   `500 Internal Server Error`: If there is a server-side error.

*   **`GET /api/submission/:id`**
    *   **Description:** Retrieves a single submission by its ID.
    *   **Permissions:** `owner` of the submission, `jury_submission`, or `admin`.
    *   **URL Parameters:**
        *   `id` (integer, required): The ID of the submission.
    *   **Response:**
        *   `200 OK`: Returns the submission object.
        *   `401 Unauthorized`: If the user is not logged in.
        *   `403 Forbidden`: If the user does not have the required permissions.
        *   `404 Not Found`: If the submission is not found.
        *   `500 Internal Server Error`: If there is a server-side error.

*   **`PUT /api/submission/:id`**
    *   **Description:** Updates the status and score of a submission.
    *   **Permissions:** `jury_submission` or `admin`.
    *   **URL Parameters:**
        *   `id` (integer, required): The ID of the submission to update.
    *   **Request Body:**
        *   `status` (string, required): The new status of the submission ('accepted' or 'rejected').
    *   **Response:**
        *   `200 OK`: Returns a success message, the new status, and the new score.
        *   `401 Unauthorized`: If the user is not logged in.
        *   `403 Forbidden`: If the user does not have the required permissions.
        *   `404 Not Found`: If the submission is not found.
        *   `500 Internal Server Error`: If there is a server-side error.

### **4. Authentication and Authorization**

*   **Authentication:** The application uses JSON Web Tokens (JWT) for authentication. When a user logs in, a JWT is generated and stored in an `httpOnly` cookie named `uid`. This token is then used to authenticate subsequent requests.

*   **Authorization:** The application uses a role-based access control (RBAC) system. The `restrictTo` middleware checks the user's role and grants or denies access to certain endpoints based on the defined permissions. The available roles are:
    *   `admin`: Has access to all endpoints.
    *   `creator_contest`: The user who created a specific contest. Has permission to delete the contest and view its submissions.
    *   `jury_contest`: A user who is a jury member for a specific contest. Has permission to view the contest's submissions.
    *   `owner`: The user who made a specific submission. Has permission to view their own submission.
    *   `jury_submission`: A user who is a jury member for the contest to which a submission belongs. Has permission to view and update the submission.
.