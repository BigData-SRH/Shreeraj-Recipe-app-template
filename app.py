import streamlit as st
import pandas as pd
import numpy as np
import ast
import re

# --- Configuration and Initial Setup ---
st.set_page_config(layout="wide", page_title="Chef's Compass")

# -------------------------------------------------
# Load Data Configuration
# -------------------------------------------------
# IMPORTANT: Update this path to where your CSV file is located.
DATA_PATH = 'data/deduplicated_recipes_with_complexity.csv'

# Dashboard Name and Tagline
DASHBOARD_NAME = "👨‍🍳 Chef's Compass"
TAGLINE = "Navigate your ingredients, discover your next favorite recipe."

# Placeholders for About Us section
USER_GMAIL = "shreerajpatil98@gmail.mail.com"
USER_LINKEDIN_URL = "https://www.linkedin.com/in/shreeraj-patil-142011136?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app"
DATASET_LINK = "https://www.kaggle.com/datasets/prashantsingh001/recipes-dataset-64k-dishes" 

page_element="""
<style>
[data-testid="stAppViewContainer"]{
  background-image: url("https://img.freepik.com/free-photo/white-flower-with-cooking-ingredients-table_181624-1096.jpg?semt=ais_se_enriched&w=740&q=80");
  background-size: cover;
}
[data-testid="stHeader"]{
  background-color: rgba(0,0,0,0);
}

</style>
"""
st.markdown(page_element, unsafe_allow_html=True)


# --- Custom Styling (Kept as before to maintain layout consistency) ---
CUSTOM_CSS = """
<style>
    /* Global Background and Main Content */
    .main {
        background-color: #FAFAFA; 
        color: #333333; 
        padding: 0 2rem;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #FFF4F2; /* Soft Mint Sidebar */
        color: #5D5D81; 
        border-right: 2px solid #5D5D81;
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown strong {
        color: #5D5D81 !important; 
    }
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stRadio label {
        color: #5D5D81 !important; 
        font-weight: bold;
    }
    [data-testid="stSidebar"] .stButton button {
        background-color: #5D5D81; 
        color: white;
        border-radius: 8px;
    }
    
    /* --- Recipe Count Box (Custom Metric) --- */
    .recipe-count-box {
        text-align: center;
        margin-bottom: 30px;
        padding: 25px;
        border: 3px solid #F0A0A0; /* Soft Coral border */
        border-radius: 18px;
        background-color: #FFFFFF; /* White background */
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        width: 100%; 
    }
    .recipe-count-label {
        font-size: 1.5rem;
        color: #5D5D81; 
        font-weight: bold;
        margin: 0;
        text-transform: uppercase;
    }
    /* Target the h1 element inside the custom box */
    .recipe-count-box h1 {
        font-size: 4.5rem !important;
        color: #008000 !important; /* Standard Green for high contrast value */
        margin: 0 !important;
        padding-top: 5px !important;
        line-height: 1 !important;
        font-weight: 700;
    }
    
    /* --- Main Content Headings --- */
    h1, h2, h3 {
        color: #5D5D81; 
        font-weight: 700;
    }
    
    /* FIX: Target the container holding the complexity dataframe for the custom white box */
    #complexity-table-container [data-testid="stDataFrame"] {
        background-color: white; 
        border-radius: 12px; 
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); 
        border: 1px solid #eee;
        padding: 10px; 
        margin-top: 15px; 
    }
    
    /* Styles for the Detailed Recipe List scrollable container */
    #detailed_recipe_container_wrapper > div > div {
        max-height: 550px; 
        overflow-y: auto; 
        padding: 10px; 
        border: 1px solid #ccc; 
        border-radius: 8px;
        background-color: #f7f7f7; 
    }
    
</style>
"""

# --- Utility Functions (All utility functions remain unchanged) ---

def render_html_component_box(html_content, key):
    """Utility to reliably render complex HTML components using st.empty."""
    if key not in st.session_state:
        st.session_state[key] = st.empty()
    st.session_state[key].markdown(html_content, unsafe_allow_html=True)

@st.cache_data
def convert_df_to_csv(df):
    """Converts the DataFrame to a CSV string for download."""
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data
def load_data(path):
    """Loads and preprocesses the recipe data."""
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        st.error(f"Error: Data file not found at {path}")
        return pd.DataFrame(), [], []

    q1 = df['num_steps'].quantile(0.25)
    q3 = df['num_steps'].quantile(0.75)

    def get_complexity(steps):
        if steps <= q1:
            return 'Simple'
        elif steps <= q3:
            return 'Medium'
        else:
            return 'Complex'

    df['Complexity'] = df['num_steps'].apply(get_complexity)

    if 'cleaned_ingredients_filtered' in df.columns:
        all_ingredients_list = df['cleaned_ingredients_filtered'].astype(str).str.lower().str.split(', ').explode().dropna().unique()
        all_ingredients_set = set(all_ingredients_list)
        all_ingredients_set.discard('')
    else:
        all_ingredients_set = set()

    all_categories = sorted(list(df['category'].unique()))

    return df, sorted(list(all_ingredients_set)), all_categories

@st.cache_data
def filter_recipes(df, selected_ingredients, keywords, threshold_percent, selected_category):
    """Filters the recipes based on selected category, ingredients, keywords, and match threshold."""
    
    if not selected_ingredients and selected_category == 'All Categories' and threshold_percent > 0:
        return df.head(0) 

    filtered_df = df.copy()
    threshold = threshold_percent / 100.0
    is_strict_match = (threshold_percent == 100) and (selected_ingredients)

    if selected_category != 'All Categories':
        filtered_df = filtered_df[filtered_df['category'] == selected_category].copy()
        
    if filtered_df.empty:
        return filtered_df.head(0)

    if selected_ingredients:
        recipe_ingredients = filtered_df['cleaned_ingredients_filtered'].fillna('').astype(str).str.lower().str.split(', ')
        filtered_df['recipe_ing_count'] = recipe_ingredients.apply(lambda x: len([i for i in x if i and i != '']))

        def calculate_match_score(recipe_ing_list):
            if not selected_ingredients: 
                return 1.0 
            
            cleaned_recipe_ing_list = set([i for i in recipe_ing_list if i and i != ''])
            
            if not cleaned_recipe_ing_list:
                return 0 
            
            matched_count = len(set(selected_ingredients) & cleaned_recipe_ing_list)
            return matched_count / len(selected_ingredients)

        filtered_df['match_score'] = recipe_ingredients.apply(calculate_match_score)
        
        filtered_df = filtered_df[filtered_df['match_score'] >= threshold].copy()
        
        if is_strict_match:
            num_selected = len(selected_ingredients)
            filtered_df = filtered_df[filtered_df['recipe_ing_count'] == num_selected].copy()

    return filtered_df.drop(columns=['match_score', 'recipe_ing_count'], errors='ignore')

def add_to_favorites(df, recipe_title):
    """Adds a recipe to the session state favorites list."""
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []

    if recipe_title not in [r['recipe_title'] for r in st.session_state.favorites]:
        recipe_data = df[df['recipe_title'] == recipe_title].iloc[0]
        favorite_entry = {
            'recipe_title': recipe_data['recipe_title'],
            'Ingredients list': recipe_data['cleaned_ingredients_filtered'],
            'Directions': recipe_data['directions'],
            'Complexity': recipe_data['Complexity']
        }
        st.session_state.favorites.append(favorite_entry)
        st.success(f"Added **{recipe_title}** to favorites!")
    else:
        st.warning(f"**{recipe_title}** is already in favorites.")

def remove_from_favorites(recipe_title):
    """Removes a recipe from the session state favorites list."""
    st.session_state.favorites = [
        r for r in st.session_state.favorites
        if r['recipe_title'] != recipe_title
    ]
    st.success(f"Removed **{recipe_title}** from favorites.")

def generate_qr_code_html(data_to_encode, label, qr_color='000000'): 
    """Generates and displays a colorful QR code (scannable)."""
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={data_to_encode}&color={qr_color}"
    
    html_content = f"""
    <div style="text-align: center; margin-bottom: 20px; border: 1px solid #ccc; padding: 15px; border-radius: 8px; background-color: white;">
        <p style="font-size: large; font-weight: bold; margin-bottom: 10px; color: #5D5D81;">{label}</p>
        <p style="font-size: small; color: #333; margin-bottom: 10px;">Scan Code:</p>
        <img src="{qr_code_url}" alt="QR code for {label}" style="width:150px; height:150px; display: block; margin: auto;">
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)


# --- Page Functions ---

def render_recipe_count_box(num_recipes):
    """Renders the custom HTML box for the recipe count."""
    html_content = f"""
    <div class="recipe-count-box">
        <p class="recipe-count-label">NUMBER OF POSSIBLE RECIPES</p>
        <h1>{num_recipes:,}</h1>
    </div>
    """
    render_html_component_box(html_content, key='recipe_count_placeholder')


def page_recipe_explorer(df):
    """Handles the filtering and results display for recipes."""
    
    # --- HEADER REMOVED: st.header("Recipe Explorer 🔍")
    
    # --- Sidebar Filtering Logic ---
    st.sidebar.markdown("## Ingredient Filters")

    category_options = ['All Categories'] + st.session_state.all_categories
    default_cat = st.session_state.get('selected_category_selectbox', 'All Categories')
    default_cat_index = category_options.index(default_cat) if default_cat in category_options else 0
    
    st.sidebar.selectbox(
        '**Filter by Category**:',
        category_options,
        index=default_cat_index,
        key='selected_category_selectbox'
    )

    st.sidebar.multiselect(
        '**Select Ingredients** (from all available ingredients):',
        st.session_state.all_ingredients,
        key='selected_ingredients_dropdown'
    )

    threshold_percent = st.sidebar.slider(
        '**Ingredient Match Threshold** (%)',
        min_value=0, max_value=100, 
        value=st.session_state.get('threshold_slider', 50), 
        step=5,
        key='threshold_slider'
    )

    selected_ingredients = st.session_state.selected_ingredients_dropdown
    
    st.sidebar.button(
        '**Apply Filters**',
        on_click=apply_filter_action, 
        type='primary'
    )
    
    # --- Main Page Display ---
    
    if st.session_state.filtered_results is None:
        apply_filter_action(should_scroll=False) 
        
    filtered_df = st.session_state.filtered_results
    
    # --- SORTING LOGIC ---
    complexity_order = ['Simple', 'Medium', 'Complex']
    
    if not filtered_df.empty:
        filtered_df['Complexity'] = pd.Categorical(
            filtered_df['Complexity'], 
            categories=complexity_order, 
            ordered=True
        )
        filtered_df = filtered_df.sort_values(by='Complexity').reset_index(drop=True)
    
    num_recipes = len(filtered_df)

    # RENDER RECIPE COUNT BOX 
    render_recipe_count_box(num_recipes)
    
    if num_recipes == 0:
        if selected_ingredients:
            st.warning(f"No recipes use {threshold_percent}% or more of your selected ingredients.")
        else:
            st.warning("No recipes match your current filter criteria.")
        return

    st.markdown("---")

    # Complexity Table 
    st.subheader("Recipe Complexity Breakdown")


    def color_complexity(val):
        """Applies CSS styling based on the Complexity value."""
        if val == 'Complex':
            return 'color: #D9534F; font-weight:bold;'
        elif val == 'Medium':
            return 'color: #F0AD4E; font-weight:bold;'
        elif val == 'Simple':
            return 'color: #5CB85C; font-weight:bold;'
        return 'color: #333333;'

    # Prepare the DataFrame for display
    complexity_table_df = filtered_df[['recipe_title', 'Complexity']].copy()
    complexity_table_df.rename(columns={'recipe_title': 'Recipe Title'}, inplace=True)
    
    # Apply color coding using Styler
    styled_df = complexity_table_df.style.applymap(
        color_complexity, 
        subset=['Complexity'] 
    )
    
    # Inject an anchor ID for CSS targeting of the white box
    st.markdown('<div id="complexity-table-container">', unsafe_allow_html=True)
    
    with st.container():
        # Display the styled dataframe. 
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=450 
        )
    
    st.markdown('</div>', unsafe_allow_html=True) 

    st.markdown("---")

    # Detailed Recipe List with Favorite Button

    st.markdown('<div id="detailed_list_anchor"></div>', unsafe_allow_html=True) 
    st.subheader("Detailed Recipe List")
    
    st.markdown('<div id="detailed_recipe_container_wrapper" style="margin-top: 15px;">', unsafe_allow_html=True)
    
    with st.container():
        for index, row in filtered_df.iterrows():
            title = row['recipe_title']
            
            with st.expander(f"**{title}** - *{row['Complexity']}*"):
                
                st.markdown("**Ingredients List:**")
                ingredients_list = [ing.strip().capitalize() for ing in str(row['cleaned_ingredients_filtered']).split(',') if ing.strip()]
                st.markdown("- " + "\n- ".join(ingredients_list))
                
                st.markdown("**Directions:**")
                try:
                    directions_list = ast.literal_eval(row['directions'])
                    if isinstance(directions_list, list):
                        for i, step in enumerate(directions_list, 1):
                            st.markdown(f"**Step {i}**: {step.strip()}")
                    else:
                        st.write(row['directions'])
                except:
                    st.write(row['directions'])

                st.button(
                    '⭐ Add to Favorites',
                    key=f'fav_btn_{index}', 
                    on_click=add_to_favorites,
                    args=(df, title) 
                )
    
    st.markdown('</div>', unsafe_allow_html=True)


def page_overview(df):
    """Displays an overview of the dataset and allows full data download."""
    st.header("Recipe Dataset Overview 📚")
    st.markdown("---")
    st.markdown("""
        This dashboard provides an interactive way to explore and filter a large dataset of recipes.
        You can search for recipes based on the ingredients you have and save your favorites!
    """)
    st.subheader("Dataset Summary")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Recipes", f"{len(df):,}")
    col2.metric("Total Ingredients", f"{len(st.session_state.all_ingredients):,}")
    col3.metric("Average Steps", f"{df['num_steps'].mean():.1f}")
    
    st.subheader("Data Columns Preview")
    
    preview_cols = ['recipe_title', 'category', 'num_ingredients', 'num_steps', 'Complexity', 'cleaned_ingredients_filtered']
    df_preview = df[preview_cols].head() 

    st.dataframe(df_preview, use_container_width=True)
    
    csv_full = convert_df_to_csv(df)

    st.download_button(
        label="Download Full Recipe Dataset (CSV)",
        data=csv_full,
        file_name='64k_dishes_full_dataset.csv',
        mime='text/csv',
        type="primary"
    )

    with st.expander("Detailed Data Information"):
        st.write(f"The dataset contains **{len(df)}** recipes across **{df['category'].nunique()}** categories.")
        st.write("Key columns used for the dashboard:")
        st.markdown("""
        * **Recipe Title**: The name of the recipe.
        * **Cleaned Ingredients Filtered**: A cleaned, comma-separated list of ingredients, used for filtering.
        * **Directions**: The steps to make the recipe.
        * **Num Steps**: The total number of steps in the recipe, used to calculate **Complexity**.
        * **Complexity**: Categorized as Simple ($\le$ Q1 steps), Medium ($\le$ Q3 steps), or Complex ($>$ Q3 steps).
        """)
    st.markdown("---")


def page_favorites():
    """Displays the list of favorite recipes."""
    st.header("My Favorite Recipes ❤️")
    st.markdown("---")

    if 'favorites' not in st.session_state or not st.session_state.favorites:
        st.info("You haven't added any recipes to your favorites yet. Explore recipes to find some!")
        return

    fav_df = pd.DataFrame(st.session_state.favorites)
    
    st.subheader(f"Total Favorites: {len(fav_df)}")
    
    st.markdown('<div id="favorites_list_container_wrapper" style="margin-top: 15px;"></div>', unsafe_allow_html=True)

    with st.container():
        for index, row in fav_df.iterrows():
            title = row['recipe_title']
            
            with st.expander(f"**{title}** - *{row['Complexity']}*"):
                
                st.markdown("**Ingredients List:**")
                ingredients_content = row['Ingredients list']
                ingredients_list = [ing.strip().capitalize() for ing in str(ingredients_content).split(',') if ing.strip()]
                st.markdown("- " + "\n- ".join(ingredients_list))
                
                st.markdown("**Directions:**")
                directions_content = row['Directions']
                try:
                    directions_list = ast.literal_eval(directions_content)
                    if isinstance(directions_list, list):
                        for i, step in enumerate(directions_list, 1):
                            st.markdown(f"**Step {i}**: {step.strip()}")
                    else:
                        st.write(directions_content)
                except:
                    st.write(directions_content)

                st.button(
                    '🗑️ Remove from Favorites',
                    key=f'unfav_btn_{index}',
                    on_click=remove_from_favorites,
                    args=(title,)
                )
    st.markdown("---")


def page_about_us():
    """Displays the About Us page content."""
    st.header("About Us ℹ️")
    st.markdown("---")
    
    st.subheader("Dashboard Details")
    # NOTE: The f-string is used here. LaTeX curly braces must be escaped with double braces {{}}
    st.markdown(f"""
        **{DASHBOARD_NAME}** is an interactive recipe finder built on Streamlit. 
        It helps you discover recipes based on ingredients you have, applying a flexible match threshold. 
        Recipes are conveniently sorted from **Simple** to **Complex** for ease of use.
        
        ---
        
        **Raw Dataset Source**
        
        [Recipes Dataset : 64k Dishes]({DATASET_LINK})
        
        ---
        
        **Target Users and Core Objective** 🎯
        
        * **Key Users:** The **Home Cook** & the **Meal Planner**, who are busy professionals needing to maximize the use of existing ingredients to save on grocery bills.
        * **Core Goal:** Instant recipe rankings that **maximize existing ingredients** and **minimize guesswork**.
        
        **Key Performance Indicators (KPIs)** 📊
        
        The dashboard uses these metrics to provide actionable insights:
        
        1.  **Ingredient Match Score:** A normalized score showing the percentage of a recipe's required ingredients that the user currently has.
            
            Match Score= # of ingredients matched/num_ingredients in recipe X 100
            
            *Purpose:* Ranks recipes so users see the best possible dishes first.
        
        2.  **Number of Possible Recipes:** The count of all recipes that can be made with the given ingredients (either full match or partial match above a set threshold).
            
            *Purpose:* Shows the user how many options they have based on what’s available in their kitchen.
        
        3.  **Average Recipe Complexity:** Measures how complex the suggested recipes are, derived from dataset fields.
            
            Complexity = (num_ingredients + num_steps)/2
            
            *Purpose:* Lets the user filter for quick & simple vs. detailed & involved dishes.
        
        **Future Engineering & Data Preparation** 🛠️
        
        * **Ingredient Cleaning:** We performed vigorous cleaning on the ingredients column to create a separate, normalized list of ingredients for accurate matching.
        * **Ingredient Clustering:** Different types of ingredients (e.g., 'green onion', 'scallion', 'onion powder') have been **clustered** into a single category (e.g., 'onion') for simple, effective matching. This removes friction for the user.
        * **Duplicate Removal:** Duplicated recipes were removed from the dataset to ensure an effortless user experience.
        
        **How to use the Dashboard** 💡
        
        * **Recipe Explorer Tab:**
            * **Filter by Category:** Filter options like "Desserts," "Indian," "Fruit salads," etc.
            * **Select Ingredients:** User inputs the names of the ingredients they currently have.
            * **Ingredients Match Threshold (%):** Used to see either a full match or partial match. Setting this to **100%** shows only recipes where *all* required ingredients match the user's input.
        * **Favorites Page:** User can add and manage their favorite recipes by clicking on the **"Add to favorites"** button on the Recipe Explorer page.
        
        ---
        
        **Contact & Connect**
        
        Scan the colorful QR codes below to retrieve the contact details.
    """)

    col1, col2 = st.columns(2)
    
    with col1:
        generate_qr_code_html(USER_GMAIL, "Gmail ID", qr_color='EA4335')

    with col2:
        generate_qr_code_html(USER_LINKEDIN_URL, "LinkedIn ID", qr_color='0A66C2')
    st.markdown("---")


def apply_filter_action(should_scroll=True):
    """
    Handler for the 'Apply Filters' button click.
    Calculates results and optionally scrolls the page.
    """
    selected_cat = st.session_state.selected_category_selectbox
    selected_ing = st.session_state.selected_ingredients_dropdown
    keywords = "" 
    threshold = st.session_state.threshold_slider
    
    st.session_state.filtered_results = filter_recipes(
        st.session_state.data, 
        selected_ing, 
        keywords, 
        threshold,
        selected_cat
    )

    if should_scroll:
        st.success("Filters applied! Results updated.")
        # Inject JavaScript to smoothly scroll
        scroll_script = """
            <script>
                var element = document.getElementById('detailed_list_anchor');
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            </script>
        """
        st.markdown(scroll_script, unsafe_allow_html=True)


# --- Main App Execution ---

if __name__ == '__main__':
    
    # 1. Apply Custom CSS first
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # 2. Load data on app startup
    try:
        data, all_ingredients, all_categories = load_data(DATA_PATH)
        st.session_state.data = data
        st.session_state.all_ingredients = all_ingredients
        st.session_state.all_categories = all_categories
    except Exception:
        st.error(f"Error initializing data. Please check the data file: `{DATA_PATH}`.")
        st.stop()
    
    # 3. Initialize session state
    STARTER_INGREDIENTS = ["yam", "salmon"]
    valid_starter_ingredients = [
        ing for ing in STARTER_INGREDIENTS 
        if ing in st.session_state.all_ingredients
    ]

    # FIX: Initialize 'page' first to prevent AttributeError in st.sidebar.radio
    if 'page' not in st.session_state:
        st.session_state.page = 'Recipe Explorer' 
        
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []
    
    if 'selected_category_selectbox' not in st.session_state:
        st.session_state.selected_category_selectbox = 'All Categories'
    
    if 'selected_ingredients_dropdown' not in st.session_state:
        st.session_state.selected_ingredients_dropdown = valid_starter_ingredients

    if 'threshold_slider' not in st.session_state:
        st.session_state.threshold_slider = 50
    
    # 4. Calculate initial results on first load
    if 'filtered_results' not in st.session_state:
        apply_filter_action(should_scroll=False)

    # --- Sidebar Navigation ---
    st.sidebar.title(DASHBOARD_NAME)
    st.sidebar.markdown(f"**_{TAGLINE}_**")
    
    page_options = ('Recipe Explorer', 'Favorites', 'Dataset Overview', 'About Us')
    
    page_selection = st.sidebar.radio(
        "**Navigation**",
        page_options,
        index=page_options.index(st.session_state.page) if st.session_state.page in page_options else 0,
        key='page_radio_select'
    )
    
    if st.session_state.page != page_selection:
        st.session_state.page = page_selection
        st.rerun() 

    # --- Page Router ---
    if st.session_state.page == 'Dataset Overview':
        page_overview(data)
    elif st.session_state.page == 'Recipe Explorer':
        page_recipe_explorer(data)
    elif st.session_state.page == 'Favorites':
        page_favorites()
    elif st.session_state.page == 'About Us':
        page_about_us()