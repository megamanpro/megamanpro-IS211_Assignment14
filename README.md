Overview
This project is a Flask based web application that provides a simple blogging platform. The purpose of the application is to allow a user to run their own blog, where posts can be created, edited, and deleted after logging in. Each post contains a title, published date, author, and HTML content. The homepage displays all posts in reverse chronological order so that the newest posts appear first. The application also includes a login system that restricts editing and management features to authenticated users.

How It Works
The application is built using Python and the Flask framework, with SQLite as the database. When the application starts, it initializes the database with two tables: one for users and one for posts. A demo user is seeded automatically to make testing easier. The root URL (/) shows all posts, while the /login route allows users to authenticate. Once logged in, users are redirected to the /dashboard, which provides an interface to manage their posts. From the dashboard, users can add new posts, edit existing ones, or delete them. Each action interacts with the SQLite database through SQL queries.

Details About the Model
The model for this application is straightforward and consists of two main entities: users and posts. The users table stores login credentials, while the posts table stores blog content along with metadata such as title, author, and published date. The relationship between the two tables is defined by the author_id foreign key, which links each post to its author. This design ensures that posts are tied to specific users and that only the author can edit or delete their own posts. The application uses session-based authentication to track logged-in users, and the database connection is managed per request to ensure resources are properly closed after each operation.

Features
Homepage (/): Shows all blog posts in reverse chronological order.
Login (/login): Allows users to log in with a username and password.
Logout (/logout): Ends the user session.
Dashboard (/dashboard): Displays the logged-in user’s posts with options to edit or delete.
New Post (/posts/new): Form to create a new post.
Edit Post (/posts/<id>/edit): Allows editing of an existing post.
Delete Post (/posts/<id>/delete): Deletes a post owned by the logged-in user.
