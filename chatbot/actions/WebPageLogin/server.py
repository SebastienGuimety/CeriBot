import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
parent_directory = os.path.dirname(os.getcwd())

# Define a directory to serve static files (e.g., the HTML file)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define a Jinja2Templates instance for rendering templates (HTML pages)
templates = Jinja2Templates(directory="templates")

# Define a route to serve the login form
@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    # Render the HTML file using Jinja2Templates
    return templates.TemplateResponse("login.html", {"request": request})

# Define a route to handle form submission
@app.post("/login")
async def process_login(
    request: Request,
    nom_receiver: str = Form(...),  # Retrieve the 'username' field from the form
    prenom_receiver: str = Form(...)   # Retrieve the 'password' field from the form
):
    # Handle the username and password as needed
    # For example, you can print them or perform authentication
    
    # Print the received data (for demonstration purposes)
    print(f"Received Username: {nom_receiver}")
    print(f"Received Password: {prenom_receiver}")

    login_results_file = os.path.join(parent_directory, "login_results.txt")

    # Implement your logic to use the username and password here
    # For example, you can perform authentication or any other actions
    # Write the received data to a text file
  
        
    with open(login_results_file, "w") as file:
        file.write(f"Nom: {nom_receiver}\n")
        file.write(f"Prenom: {prenom_receiver}\n")
        file.write("-" * 20 + "\n")
        
    # Redirect to a success page or return a response as needed
    return {"message": "Login successful"}  # Modify this response accordingly
