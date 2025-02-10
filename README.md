Application for tracking the daily activities and associated with them emotions, using OpenAI API to create summaries of the day based on the data provided by the user. 

Main application functionalities:
- Day view with adding/edition/removal of activities, related emotions, comments, creation of daily summaries
- Day summarues using OpenAI API, based on the data entered by the user
- Automatic email notifications to the user if the day ends and there is no data entered for current day
- Generation of PDF reports with summaries from a selected date range
- 
Technologies used:
Python, Django, PostgreSQL, OpenAI API, Celery, pdfkit
