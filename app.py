import streamlit as st
from google import genai


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
# SIDEBAR - GEMINI API KEY
# =========================================================

with st.sidebar:

    st.header("⚙️ Settings")

    st.write(
        "Enter your Gemini API key to generate recipes."
    )

    gemini_api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Paste your Gemini API key here"
    )

    st.caption(
        "🔒 Your key is used to connect to Gemini and is not "
        "saved by this app."
    )

    st.divider()

    st.markdown("### About")

    st.write(
        "AI Food Recipe Planner creates practical recipes based "
        "on your available time, cooking experience, and budget."
    )


# =========================================================
# CREATE GEMINI CLIENT
# =========================================================

def get_gemini_client(api_key):

    if not api_key:
        raise ValueError(
            "Please enter your Gemini API key in the sidebar."
        )

    return genai.Client(api_key=api_key)


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

3. Preparation time + cooking time should stay within
   {max_time} minutes whenever realistically possible.

4. Never give an unrealistic cooking time simply to fit
   the user's limit.

5. If the traditional recipe cannot realistically be completed
   within {max_time} minutes:
   - briefly explain this
   - provide the fastest practical adaptation

6. Prefer affordable and commonly available ingredients.

7. Avoid unnecessary:
   - luxury ingredients
   - premium ingredients
   - imported ingredients
   - difficult-to-find specialty ingredients

8. When an expensive ingredient is normally required,
   suggest a cheaper substitute when possible.

9. Give exact practical quantities for every important ingredient.

10. Do not use important ingredients in the instructions
    unless they are included in the ingredient list.

11. Give clear numbered cooking instructions.

12. Include useful heat levels, cooking times, and visual
    signs of doneness when appropriate.

13. Keep food-safety instructions sensible.


EXPERTISE GUIDANCE

If the user is Beginner:
- use simple techniques
- explain steps clearly
- avoid unnecessarily complicated equipment
- explain unfamiliar terms
- give useful visual clues

If the user is Intermediate:
- assume basic cooking knowledge
- moderate techniques are acceptable
- keep instructions clear

If the user is Advanced:
- advanced techniques may be used
- provide more detailed cooking guidance
- still keep the recipe practical


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


## 🍽️ Servings

Number of servings.


## 🛒 Ingredients

- quantity + ingredient
- quantity + ingredient
- quantity + ingredient


## 💰 Cheaper Substitutions

Suggest useful cheaper alternatives.

If no substitutions are necessary, mention that the ingredients
are already budget-friendly.


## 🍳 Instructions

1. First step
2. Second step
3. Third step
4. Continue until complete


## 💡 Budget-Saving Tips

Provide 3 to 5 useful budget-saving tips specifically for
this recipe.


## ✅ Quick Success Tips

Provide 2 to 4 useful tips for a {expertise} cook.


FINAL CHECK

Before responding, verify that:

- the recipe matches "{food_name}"
- ingredient quantities are included
- prep time + cooking time = total time
- the time estimate is realistic
- the recipe stays within {max_time} minutes when possible
- ingredients are reasonably affordable
- instructions match the {expertise} level

Return only the completed recipe.
"""


# =========================================================
# GENERATE RECIPE
# =========================================================

def generate_recipe(api_key, food_name, expertise, max_time):

    client = get_gemini_client(api_key)

    prompt = build_recipe_prompt(
        food_name,
        expertise,
        max_time
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response. Please try again."
        )

    return response.text


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
    f"⏰ The recipe will aim to stay within "
    f"**{max_time} minutes total**."
)


# =========================================================
# GENERATE BUTTON
# =========================================================

generate_button = st.button(
    "✨ Generate Recipe",
    type="primary",
    use_container_width=True
)


# =========================================================
# GENERATE RECIPE
# =========================================================

if generate_button:

    food_name = food_name.strip()

    # Check API key
    if not gemini_api_key:

        st.error(
            "🔑 Please enter your Gemini API key in the sidebar."
        )

    # Check recipe name
    elif not food_name:

        st.warning(
            "🍽️ Please enter the food or recipe you want to make."
        )

    else:

        try:

            with st.spinner(
                f"👨‍🍳 Creating your {food_name} recipe..."
            ):

                recipe = generate_recipe(
                    gemini_api_key,
                    food_name,
                    expertise,
                    max_time
                )

            st.success("✅ Your recipe is ready!")

            st.divider()

            st.markdown(recipe)

            st.divider()

            st.caption(
                "🤖 AI-generated recipe. Check allergies and "
                "follow safe food-handling practices."
            )

        except Exception as error:

            st.error(
                "😕 The recipe could not be generated. "
                "Check your Gemini API key and try again."
            )

            with st.expander("🔧 Technical error details"):
                st.code(str(error))


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🍳 AI Food Recipe Planner • Powered by Google Gemini"
)

