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
    name: str = Form(...),  # Retrieve the 'username' field from the form
    password: str = Form(...),  # Retrieve the 'password' field from the form
    destinataire: str = Form(...),
):
    # Handle the username and password as needed
    # For example, you can print them or perform authentication
    
    # Print the received data (for demonstration purposes)
    print(f"Received Username: {name}")
    print(f"Received Password: {destinataire}")

    login_results_file = os.path.join(parent_directory, "login_results.txt")

    # Split the destinataire and sender names into first name and last name
    destinataire_parts = destinataire.split()
    sender_parts = name.split()

    if len(destinataire_parts) == 2 and len(sender_parts) == 2:
        prenom_destinataire, nom_destinataire = destinataire_parts
        prenom_sender, nom_sender = sender_parts

        # Implement your logic to use the username and password here
        # For example, you can perform authentication or any other actions
        # Write the received data to a text file
        with open(login_results_file, "w") as file:
            file.write(f"email_sender: {prenom_sender}.{nom_sender}\n")  # Ajoutez le point au milieu
            file.write(f"email_receiver: {prenom_destinataire}.{nom_destinataire}\n")  # Ajoutez le point au milieu
            file.write(f"password: {password}\n")
            file.write("-" * 20 + "\n")
        
        # Redirect to a success page or return a response as needed
        return {"message": "Login successful"}  # Modify this response accordingly
    else:
        return {"error": "Invalid input format"}  # Handle invalid input format
