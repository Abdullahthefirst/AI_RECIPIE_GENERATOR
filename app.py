import os
import streamlit as st
from google import genai


# =========================================================
# PAGE SETTINGS
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

        .app-description {
            font-size: 1.05rem;
            color: #666;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# GEMINI CLIENT
# =========================================================

def get_gemini_client():
    """
    Get the Gemini API key.

    On Streamlit Cloud:
        The key comes from Streamlit Secrets.

    Locally:
        The key can come from the GEMINI_API_KEY
        environment variable.
    """

    api_key = None

    # First try Streamlit Secrets
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    # If not found, try environment variable
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key was not found. "
            "Add GEMINI_API_KEY to Streamlit Secrets."
        )

    return genai.Client(api_key=api_key)


# =========================================================
# CREATE GEMINI PROMPT
# =========================================================

def build_recipe_prompt(food_name, expertise, max_time):
    """
    Creates a strong prompt so Gemini follows:
    - requested food
    - expertise level
    - maximum cooking time
    - budget requirements
    """

    return f"""
You are an expert home-cooking recipe planner.

Create ONE practical recipe based on the user's request.

USER DETAILS

Recipe requested:
{food_name}

Cooking expertise:
{expertise}

Maximum available TOTAL time:
{max_time} minutes


==============================
STRICT REQUIREMENTS
==============================

1. RECIPE ACCURACY

The recipe must genuinely be for:

"{food_name}"

Do not change the requested dish into something unrelated.

You may make practical adjustments when necessary, but the final
recipe must still clearly represent the requested food.


2. MAXIMUM TIME

The user only has {max_time} minutes.

Preparation time + cooking time should stay within
{max_time} minutes whenever realistically possible.

Calculate the times carefully.

For example:

Preparation: 10 minutes
Cooking: 25 minutes
Total: 35 minutes

The numbers must be mathematically consistent.

Never claim an unrealistic cooking time simply to satisfy
the user's limit.

If the traditional version genuinely cannot be completed within
{max_time} minutes:

- clearly mention that
- create the fastest realistic version
- explain briefly what was simplified


3. EXPERIENCE LEVEL

The user selected:

{expertise}

Adjust the instructions accordingly.

BEGINNER:

- Use simple techniques
- Explain steps clearly
- Avoid unnecessary complicated equipment
- Explain unfamiliar cooking terms
- Include useful visual clues such as
  "cook until lightly golden"

INTERMEDIATE:

- Assume basic cooking knowledge
- Moderate techniques are acceptable
- Keep the instructions clear and practical

ADVANCED:

- More sophisticated techniques are acceptable
- More detailed cooking techniques may be included
- Still keep the recipe practical


4. BUDGET

The recipe should be affordable.

Prefer:

- common supermarket ingredients
- inexpensive vegetables
- normal pantry ingredients
- commonly available spices
- affordable proteins

Avoid unnecessarily using:

- luxury ingredients
- premium imported products
- very expensive ingredients
- difficult-to-find specialty ingredients

If the dish normally uses an expensive ingredient:

Suggest a cheaper substitute whenever possible.

Do not ruin the identity of the dish just to make it cheaper.


5. INGREDIENTS

Every ingredient must include a clear quantity.

Examples:

- 2 cups rice
- 500 g chicken
- 1 medium onion
- 2 tablespoons cooking oil
- 1 teaspoon salt

Clearly mark optional ingredients.

Do not use important ingredients in the instructions that
were not included in the ingredient list.


6. INSTRUCTIONS

Provide numbered step-by-step instructions.

The instructions must be:

- practical
- clear
- easy to follow
- appropriate for a {expertise} cook

Mention useful information such as:

- approximate cooking time for important steps
- heat level
- visual signs of doneness
- when ingredients should be added


7. FOOD SAFETY

Include safe and sensible cooking instructions.

For meat, poultry, seafood, or eggs, ensure the recipe does not
encourage unsafe cooking practices.


==============================
OUTPUT FORMAT
==============================

Write the answer using clean Markdown in exactly this general
structure:


# [Recipe Name]

A short 1-2 sentence description of the dish.


## ⏱️ Time

- Preparation Time: X minutes
- Cooking Time: X minutes
- Total Time: X minutes


## 👨‍🍳 Difficulty

{expertise}


## 🍽️ Servings

Give a reasonable number of servings.


## 🛒 Ingredients

- quantity + ingredient
- quantity + ingredient
- quantity + ingredient


## 💰 Cheaper Substitutions

List useful cheaper alternatives for ingredients.

If the recipe already uses inexpensive ingredients, say so.


## 🍳 Instructions

1. First step
2. Second step
3. Third step
4. Continue until finished


## 💡 Budget-Saving Tips

Give 3 to 5 useful budget-saving tips specifically related
to this recipe.


## ✅ Quick Success Tips

Give 2 to 4 short tips that are especially helpful for a
{expertise} cook.


==============================
FINAL CHECK
==============================

Before answering, silently verify:

- The recipe actually matches "{food_name}"
- Every important ingredient has a quantity
- Prep time + cooking time = total time
- Total time stays within {max_time} minutes whenever realistic
- Ingredients are reasonably affordable
- Expensive ingredients have cheaper substitutes when possible
- Instructions match the {expertise} expertise level
- Instructions are practical and easy to follow

Return ONLY the completed recipe.
"""


# =========================================================
# GENERATE RECIPE
# =========================================================

def generate_recipe(food_name, expertise, max_time):
    """
    Send the user's request to Gemini and return
    the generated recipe.
    """

    client = get_gemini_client()

    prompt = build_recipe_prompt(
        food_name=food_name,
        expertise=expertise,
        max_time=max_time
    )

    system_instruction = """
You are AI Food Recipe Planner, an expert home-cooking assistant.

Your recipes should prioritize:

1. Accuracy to the requested dish
2. The user's available cooking time
3. The user's cooking experience
4. Affordable ingredients
5. Easy-to-find ingredients
6. Clear quantities
7. Practical instructions
8. Sensible food safety

Do not pretend an impossible cooking time is realistic.

If a traditional dish cannot realistically be prepared within
the requested time, make the fastest practical adaptation and
briefly explain the adjustment.

Write the final recipe in clean Markdown that looks good inside
a Streamlit application.
"""

    # Current Gemini Interactions API
    interaction = client.interactions.create(
        model="gemini-3.7-flash",
        system_instruction=system_instruction,
        input=prompt,
    )

    recipe = interaction.output_text

    if not recipe or not recipe.strip():
        raise RuntimeError(
            "Gemini returned an empty response. Please try again."
        )

    return recipe


# =========================================================
# APP HEADER
# =========================================================

st.title("🍳 AI Food Recipe Planner")

st.markdown(
    """
    <div class="app-description">
        Tell the AI what you want to cook, your cooking experience,
        and how much time you have. It will create a practical,
        budget-friendly recipe for you.
    </div>
    """,
    unsafe_allow_html=True
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
    options=[
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
    step=5,
    format="%d minutes"
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
# GENERATE AND DISPLAY RECIPE
# =========================================================

if generate_button:

    # Remove unnecessary spaces
    cleaned_food_name = food_name.strip()

    # Check for missing food name
    if not cleaned_food_name:

        st.warning(
            "🍽️ Please enter the name of the food or recipe "
            "you would like to make."
        )

    elif len(cleaned_food_name) < 2:

        st.warning(
            "Please enter a valid recipe or food name."
        )

    else:

        try:

            with st.spinner(
                f"👨‍🍳 Creating your {cleaned_food_name} recipe..."
            ):

                recipe = generate_recipe(
                    food_name=cleaned_food_name,
                    expertise=expertise,
                    max_time=max_time
                )

            st.success("✅ Your recipe is ready!")

            st.divider()

            # Display Gemini's Markdown response
            st.markdown(recipe)

            st.divider()

            st.caption(
                "🤖 This recipe was generated by AI. "
                "Always check ingredient allergies and use safe "
                "food-handling and cooking practices."
            )


        except ValueError as error:

            st.error(
                f"🔑 Configuration Error: {error}"
            )


        except Exception as error:

            st.error(
                "😕 We couldn't generate your recipe right now. "
                "Please try again."
            )

            # Technical information can be useful when developing
            with st.expander("🔧 Technical error details"):

                st.code(str(error))


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🍳 AI Food Recipe Planner • Powered by Google Gemini"
)

