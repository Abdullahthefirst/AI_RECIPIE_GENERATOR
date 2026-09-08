import asyncio
import streamlit as st
from gemini_webapi import GeminiClient

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Food Recipe Planner",
    page_icon="🍳",
    layout="centered"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 850px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.7rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR - GEMINI WEB SESSION COOKIES
# =========================================================

with st.sidebar:

    st.header("⚙️ Settings")

    st.write(
        "Enter your Gemini Web session cookies extracted from gemini.google.com."
    )

    secure_1psid = st.text_input(
        "__Secure-1PSID Cookie",
        type="password",
        placeholder="Paste __Secure-1PSID here"
    )

    secure_1psidts = st.text_input(
        "__Secure-1PSIDTS Cookie",
        type="password",
        placeholder="Paste __Secure-1PSIDTS here"
    )

    st.caption(
        "🔒 Cookies are used only to authenticate with gemini.google.com "
        "and are not stored."
    )

    st.divider()

    st.markdown("### About")

    st.write(
        "AI Food Recipe Planner creates practical recipes based "
        "on your available time, cooking experience, and budget."
    )

# =========================================================
# CREATE RECIPE PROMPT
# =========================================================

def build_recipe_prompt(food_name, expertise, max_time):

    return f"""
You are an expert home-cooking recipe planner.

Create ONE practical recipe for the user.

USER REQUEST

Food / Recipe:
{food_name}

Cooking expertise:
{expertise}

Maximum total available time:
{max_time} minutes


IMPORTANT RULES

1. The recipe must genuinely be for "{food_name}".
2. Adjust the instructions for a {expertise} cook.
3. Preparation time + cooking time should stay within {max_time} minutes.
4. Prefer affordable and commonly available ingredients.
5. Give exact practical quantities for every important ingredient.
6. Give clear numbered cooking instructions.


OUTPUT FORMAT

Return the recipe in clean Markdown using this structure:

# [Recipe Name]
A short description of the dish.

## ⏱️ Time
- Preparation Time: X minutes
- Cooking Time: X minutes
- Total Time: X minutes

## 👨‍🍳 Difficulty
{expertise}

## 🛒 Ingredients
- quantity + ingredient

## 🍳 Instructions
1. First step
2. Second step

Return only the completed recipe.
"""

# =========================================================
# GENERATE RECIPE VIA GEMINI WEB API
# =========================================================

async def fetch_from_gemini_web(psid, psidts, prompt):
    # Initialize the web wrapper client using browser cookies
    client = GeminiClient(psid, psidts)
    await client.init(timeout=30)
    
    # Send the prompt directly to gemini.google.com
    response = await client.generate_content(prompt)
    return response.text

def generate_recipe(psid, psidts, food_name, expertise, max_time):
    prompt = build_recipe_prompt(food_name, expertise, max_time)
    
    # Run the asynchronous web request synchronously for Streamlit
    response_text = asyncio.run(fetch_from_gemini_web(psid, psidts, prompt))
    
    if not response_text:
        raise RuntimeError("Gemini Web returned an empty response.")
        
    return response_text

# =========================================================
# APP HEADER
# =========================================================

st.title("🍳 AI Food Recipe Planner")

st.write(
    "Create practical, budget-friendly recipes based on your "
    "cooking experience and available time."
)

st.divider()

# =========================================================
# USER INPUTS
# =========================================================

food_name = st.text_input(
    "🍽️ Food / Recipe Name",
    placeholder="Example: Chicken Biryani, Pasta, Pancakes..."
)

expertise = st.selectbox(
    "👨‍🍳 Cooking Expertise",
    [
        "Beginner",
        "Intermediate",
        "Advanced"
    ]
)

max_time = st.slider(
    "⏱️ Maximum Available Cooking Time",
    min_value=10,
    max_value=180,
    value=45,
    step=5
)

st.info(
    f"⏰ The recipe will aim to stay within **{max_time} minutes total**."
)

# =========================================================
# GENERATE BUTTON & LOGIC
# =========================================================

generate_button = st.button(
    "✨ Generate Recipe",
    type="primary",
    use_container_width=True
)

if generate_button:

    food_name = food_name.strip()

    if not secure_1psid or not secure_1psidts:
        st.error(
            "🔑 Please enter both __Secure-1PSID and __Secure-1PSIDTS cookies in the sidebar."
        )

    elif not food_name:
        st.warning(
            "🍽️ Please enter the food or recipe you want to make."
        )

    else:
        try:
            with st.spinner(f"🌐 Sending request to gemini.google.com for {food_name}..."):
                recipe = generate_recipe(
                    secure_1psid,
                    secure_1psidts,
                    food_name,
                    expertise,
                    max_time
                )

            st.success("✅ Your recipe is ready!")
            st.divider()
            st.markdown(recipe)
            st.divider()

            st.caption(
                "🤖 AI-generated recipe scraped via Gemini Web."
            )

        except Exception as error:
            st.error(
                "😕 Could not retrieve response from gemini.google.com. "
                "Check if your session cookies expired."
            )

            with st.expander("🔧 Technical error details"):
                st.code(str(error))

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🍳 AI Food Recipe Planner • Powered by Gemini Web"
)
