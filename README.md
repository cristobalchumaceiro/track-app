# TrackApp, Your Personal Fitness Tracker
#### Video Demo:  [YouTube](https://www.youtube.com/watch?v=wQrDNld70Pw)
## About TrackApp
TrackApp is your new personal fitness tracker. It is a web application developed using Python, Javascript, and SQL, that serves as your own activity log for any fitness activity you undertake. It provides a convenient way to upload and keep track of your runs, swims, hikes, and anything in between! It's as easy as creating an account on the website, and navigating to the upload page. Once there you can upload any .FIT file containing data about a workout that you've completed. FIT stands for Flexible and Interoperable Data Transfer files. These files contain a myriad of information pertaining not just to some key vital signs such as heart rate and blood oxygen levels, but also sweat, power, stride, vertical oscillation, and many, many more. Once an activity is uploaded, the program with parse the file and add it to your Activity Log, which is a page to keep track of all of the activities you have so far uploaded, including some information such as the date, the distance, name of the activity, and more. The program will also extract GPS data (if included) from the file to produce a map containing the route of the activity. This is especially useful for runs, hikes, and walks, allowing you to revisit special places and keep track of your favourite routes.

This program is comprised of a number of files, the main application residing in app.py, a python file containing the entire backend of the app, along with trackapp.db, a SQL database housing the user and activity data for the application. Along with these two files are a number of different HTML templates used to render the login and logout screens, the activity log, the upload page, as well as the activity and edit activity pages. Along with these files there is also helper.py, another python file containing a few self-created functions that enable the data to be parsed correctly and presented in an appropriate manner.

## App Structure
### Registering, Logging in/out, and the Activity Log
In app.py, we have a number of routes, self-explanatory ones like the login, logout, and register page all use various aspects of python, flask, and SQLite3 libraries to achieve their goals. We also use sessions to keep some data pertaining to logged in users, as well as to use the message flashing functionality to present the user with contextual messaging for each action that they complete. After a user has registered, and subsequently logged into the application, we welcome them to their Activity Log. The activity log will display some information about the user, such as their first and last name, giving it a more personal touch to the application. And it will show a table with various kinds of data pertaining to the activities that they have uploaded, including: sport (run, hike, walk, etc.) activity name (that the user has chosen themselves when uploading), date recorded, duration, and distance.

### Uploading an Activity

In order to upload an activity, the user must navigate to the page via the navigation bar located at the top of the screen. Once on the page, the user is shown 3 input fields along with a submission button. The only required input is the top one for uploading a .FIT file, the name and description are optional and can be added (or edited) after the fact. When an activity is uploaded, the application reads the file into a SQLite3 database for storage, and parses the file using the python library fitparse for metrics such as date, duration, distance, pace, calories, and heart rate. This is done in order to lessen the burden on the application when displaying the activity as all of the stats have been pre-processed and stored. The activity is given an ID number, and is stored alongside the ID of the user that uploaded it.

### Viewing an Activity

Once an activity is uploaded, it redirects you to the activity page. The activity page serves to provide a graphical interface with which to view the .FIT file that was uploaded. The metrics mentioned beforehand are displayed in a small table, and just above this we have a map, showing the GPS route that was recorded (if supplied in the .FIT). This was achieved using some javascript, in the form of the Leaflet.js javascript library, and using map data from Open Street Maps.

### Editing an Activity

Finally, within the activity page, we have the 'edit activity' button. This will take you to a functionally and visually similar page containing all the data from the activity page, alongside two new input boxes for editing the name and description of the activity. This is included as an additional functionality as users may not be away of what activity belongs to a certain .FIT file. So they are able to add a title and short description afterwards once their memory is jogged!

### Future Functionality

I would also like to mention some additional functionality that I would choose to implement with more time, the application currently supports multiple users, and so the development of an activity "feed" with your friend's activities would be good. Moreover, I would also like to implement a weekly/monthly goal measure, that would let you know whether or not you are under or over a user-determined distance goal for the current month/week.

## Credits and Thanks

I would like to give my final thanks to those who help develop and maintain the following python libraries used:\
[flask](https://flask.palletsprojects.com/en/stable/)\
[werkzeug.security](https://werkzeug.palletsprojects.com/en/stable/)\
[fitparse](https://github.com/dtcooper/python-fitparse)

As well as:\
[Boostrap](https://getbootstrap.com)\
[Jinja](https://jinja.palletsprojects.com/en/stable/)\
[Garmin FIT SDK](https://developer.garmin.com/fit/overview/)\
[Leaflet.js](https://leafletjs.com) and\
[OpenStreetMaps](https://www.openstreetmap.org/copyright)

And finally to the organisers of the CS50 course, David J. Malan, all the teaching assistants, and my [brother](https://github.com/sendelivery) for serving as my fatihful rubberduck.
