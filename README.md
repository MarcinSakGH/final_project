Daily Activity Tracker App
Technologies: Python, Django, PostgreSQL, OpenAI API, Celery, pdfkit

Project description:
A web application for tracking daily activities and the emotions associated with them. Users can record their activities, assign emotions to them, add comments and create summaries of the day. The application uses OpenAI API to generate automatic summaries based on the data entered. In addition, the app offers the generation of PDF reports for selected periods and automatic email notifications if the user has not entered any data on a given day.

Main functionalities:

View of the day: Add, edit and delete activities, assign emotions, add comments, create daily summaries.
Day summaries using OpenAI API: Generate summaries based on user input.
Email notifications: Automatic notifications when no data has been entered by the end of the day.
PDF report generation: Create reports with summaries for a selected period.


Responsibilities:

Backend: Design and implementation of functions to add, edit and delete activities and generate daily summaries.
Integration with OpenAI API: Use of OpenAI API to generate summaries based on user data.
Task automation: Implementation of email notifications using Celery to monitor user activity.
PDF report generation: Implementation of PDF report generation using pdfkit.
Database: Designing and implementing a database structure in PostgreSQL, including migrations and queries.
Testing: Create unit and integration tests to ensure application stability.
