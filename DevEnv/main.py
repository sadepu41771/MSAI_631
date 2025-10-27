#import required library
from flask import Flask

#now create the flask appl
app = Flask(__name__)

# Define the route
@app. route("/")
def hello_world():
    return "Hello, World!"

# Run the app
if __name__ == "__main__":
    app.run()