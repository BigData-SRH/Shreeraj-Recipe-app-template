# 👨‍🍳 Chef's Compass: Interactive Recipe Finder (Navigate your ingredients, discover your next favorite recipe.)

Chef's Compass is a Streamlit-based application designed to help Home Cooks and Meal Planners maximize the use of existing ingredients. It provides instant, ranked recipe suggestions based on what you have in your kitchen, minimizing guesswork and maximizing existing ingredients.

✨ Key Features
Intelligent Ingredient Matching: Find recipes that match your selected ingredients above a customizable Ingredient Match Threshold (0-100%).

Recipe Complexity Ranking: Recipes are sorted from Simple to Complex for ease of use.

Data-Driven Insights: Tracks key performance indicators like Ingredient Match Score and Average Recipe Complexity.

Robust Data Preparation: Uses cleaned and clustered ingredients (e.g., 'scallion' clustered as 'onion') for simple, effective matching.

Favorites Management: Easily save and manage your preferred recipes on the dedicated Favorites page.

Detailed Overview: A separate page provides a summary of the massive recipe dataset (around 25,000 recipes).

💡 User Notes & Disclaimer
Volume Warning: If you enter a broad list of common ingredients, you might receive a large number of results, sometimes over 1,000.

Detailed View: To see the full recipe after selecting it in the breakdown table, you currently need to scroll down a little on the main page.

Future Enhancement: An improvement is planned so that clicking the Recipe Title will automatically take you to the detailed view.

The project includes:

- A Home page (`app.py`)
- A multi-page setup (`pages/` folder)
- A dataset (`data/example_data.csv`)
- A simple theme configuration (`.streamlit/config.toml`)
- A complete environment setup guide (steps below)
- A `requirements.txt` file for reproducible installs

Click here to see the Streamlit Dashboard for this project: https://shreeraj-recipe-app.streamlit.app/

---

## 1. Prerequisites

You will need:

- Python 3.9 or higher  
- pip (Python package manager)  
- Optional: Git, if you want to clone the repository instead of downloading the ZIP file  

Check your versions:

```bash
python --version
pip --version
```

---

## 2. Get the project

### Option A — Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/streamlit-app-template.git
cd streamlit-app-template
```

### Option B — Download ZIP

1. Click "Code" → "Download ZIP"
2. Extract the ZIP file
3. Open the folder in your code editor

---

## 3. Create a virtual environment (recommended)

This isolates your project dependencies so they do not affect system-wide packages.

Inside the project folder:

```bash
python -m venv .venv
```

### Activate the virtual environment

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

When activated, your terminal will show a prefix similar to:

```
(.venv)
```

---

## 4. Install dependencies

With the virtual environment activated:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs Streamlit, pandas, numpy, and any other required packages.

---

## 5. Run the Streamlit app

Run the main entry file:

```bash
streamlit run app.py
```

Streamlit will open a local server, typically at:

```
http://localhost:8501
```

If the browser does not open automatically, copy and paste this URL into your browser.

Use the sidebar navigation to switch between:

- Home  
- Overview  
- Data Explorer  
- About  

---

## 6. Project Structure

```text
streamlit-app-template/
├─ app.py
├─ pages/
│  ├─ 01_Dataset Overview.py
│  └─ 02_About us.py
├─ requirements.txt
├─ .gitignore
├─ README.md
├─ data/
│  └─ deduplicated_recipes_with_complexity.csv
└─ .streamlit/
   └─ config.toml
```

### Description of folders and files

| Path | Explanation |
|------|-------------|
| `app.py` | Main entry point for the app (Home page) |
| `pages/` | Additional pages; Streamlit automatically detects them |
| `data/` | Contains datasets |
| `.streamlit/config.toml` | Optional theme and server configuration |
| `requirements.txt` | List of Python dependencies |
| `.gitignore` | Specifies which files Git should ignore |
| `README.md` | This documentation file |

---

## 7. Adding New Pages

Streamlit automatically adds any `.py` file inside the `pages/` directory as a page.

To add a new page:

1. Create a new file in `pages/`
2. Use a filename with a numeric prefix to control order, for example:

```
pages/04_Analysis.py
```

3. Add content such as:

```python
import streamlit as st

st.title("New Page")
st.write("This is a custom page.")
```

4. Run the app again:

```bash
streamlit run app.py
```

The new page will appear in the sidebar.

---

## 8. Updating Dependencies

If you install additional libraries, update the requirements file:

```bash
pip install NEW_PACKAGE
pip freeze > requirements.txt
```

This ensures others can reproduce your environment.

---

## 9. Deployment (Short Overview)

You can deploy this Streamlit app to:

- Streamlit Community Cloud  
- Render  
- HuggingFace Spaces  
- Fly.io  
- Your own server using Docker  

For most classroom or project cases, running locally with:

```bash
streamlit run app.py
```

is sufficient.

---

## 10. Troubleshooting

### Streamlit command not found  
Your virtual environment may not be activated.

### Example dataset not found  
Ensure the file exists at:

```
data/example_data.csv
```

### Pages do not appear  
The folder must be named exactly:

```
pages
```

(lowercase)

---

## 11. Using This Template for Student Projects

You can:

- Fork this repository  
- Replace the example data with your own dataset  
- Add new multipage views  
- Build data dashboards or analysis tools  
- Submit their Streamlit project as a reproducible environment  

This ensures consistency across all student groups.

---

## 12. License

MIT License (or replace with your own license)
