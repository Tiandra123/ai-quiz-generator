"""
AI Quiz Generator Module
- Handles all AI interactions for generating quiz questions.

Tiandra M Taylor
"""

# Imports
import anthropic as anth
import json

# Functions
def generate_quiz(topic, api_key, max_retries=3):
    """
    Generate mulitple choice quz about user given topic using Claude
    Function needs to handle
    - create specific prompt for quiz generation
    - call API
    - parse through and validate response
    - auto retry if quiz generation fails
    - Notes:
        - return quiz data in JSON
        - model? probably claude-sonnet-4 (speed and accuracy balance)
        - max_toxens? 2000 - enough for 5 questions per quiz but not wasteful 
        - temperature? 0.7 - 1? balance for creativity and coherence
    """
    connection = anth.Anthropic(api_key=api_key)

    # specify all prompt requirements
    prompt = f"""Generate a multiple choice quiz about the topic: {topic}
    Requirements:
    - Create EXACTLY 5 questions
    - Each question MUST have EXACTLY 4 answer options labeled A, B, C, D
    - Each question MUST have ONLY 1 correct answer
    - Questions should be educational and factually accurate
    - Vary difficulty from easier to hard questions

    Return your response as VALID JSON with this EXACT structure (no extra text):
    {{
        "questions":[
            {{
                "question": "Question text here",
                "options": {{
                    "A": "Option A text",
                    "B": "Option B text",
                    "C": "Option C text",
                    "D": "Option D text"
                }},
                "correct_answer": "A"  # Correct option label
            }},
            ...
        ]
    }}
    Return ONLY the JSON. No markdown code blocks, no explanations, just the JSON."""
    # through this in a try loop to handle quiz generation failures
    for attempt in range(max_retries):
        try:
            print(f" Attempt {attempt + 1} of {max_retries} to generate quiz about '{topic}'.")

            # Call Claude API
            message = connection.messages.create(
                model = "claude-sonnet-4-20250514",  # Latest Sonnet model
                max_tokens = 2000,
                temperature = 0.8,
                messages = [
                    {
                        "role": "user", # we're the user
                        "content": prompt # needs to use our prompt
                    }
                ]
            )
            response_text = message.content[0].text # only need text from object

            # remove markdown code blocks if any - just in case
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                    response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                    response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                    response_text = response_text[:-3]  # Remove trailing ```
            response_text = response_text.strip()

            # Parse JSON into dict - if nothing is returned it will fail and kick to except
            quiz_data = json.loads(response_text) 

            # Validate quiz data structure - reference tuple returned
            is_valid, validation_message = validate_quiz(quiz_data)

            if is_valid == False:
                raise ValueError(f" Quiz validation failed: {validation_message}")

            quiz_data["topic"] = topic
            print(f" Quiz about {topic} has been successfully generated with {len(quiz_data['questions'])} questions!") 
            # return the quiz data
            return quiz_data   

        except json.JSONDecodeError as json_err:
            # no valid JSON was returned
            print(f" Attempt {attempt + 1} failed.")
            print(f" JSON parsing error: {json_err}.")
            print(f" Response text preview: {response_text[:100]}...")  # Show first 100 chars for debugging - will get way too long 
            if attempt == max_retries -1: # count starts at zero
                print(" Max retries reached. Quiz generation failed.")
                return None
        
        except ValueError as val_err:
            # valid JSON returned but failed validation
            print(f" Attempt {attempt + 1} failed.")
            print(f" Error: {val_err}.")
            if attempt == max_retries -1: 
                print(" Max retries reached. Quiz generation failed.")
                return None

        except anth.APIError as api_err:
            # API errors
            print(f" Attempt {attempt + 1} failed.")
            print(f" API error: {api_err}.")
            if attempt == max_retries -1:
                print(" Max retries reached. Quiz generation failed.")
                return None

        except Exception as e:
            # catch all for any other errors
            print(f"Attempt {attempt + 1} failed.")
            print(f" Error type: {type(e)}, Error message: {e}.")
            if attempt == max_retries -1:
                print(" Max retries reached. Quiz generation failed.")
                return None
    

def validate_quiz(quiz_data):
    """
    Make sure the quiz is actually valid and legit before showing it to user (requirements specified in prompt need to be met)
    """
     # check for 'questions' overall 
    if "questions" not in quiz_data:
        return False, "Response is missing the 'questions' field"
            
    if not isinstance(quiz_data["questions"], list):
        return False, "'questions' field is not a list"
            
    if len(quiz_data["questions"]) != 5:
        return False, f"Expected exactly 5 questions, got {len(quiz_data['questions'])}"
        
    # check each specific question dictionary - force start at 1 not 0
    for idx, question_dict in enumerate(quiz_data["questions"], 1):
        # check for fields - must exist
        if "question" not in question_dict:
            return False, f"Question {idx} is missing the 'question' field"
        if "options" not in question_dict:
            return False, f"Question {idx} is missing the 'options' field"
        if "correct_answer" not in question_dict:
            return False, f"Question {idx} is missing the 'correct_answer' field"
        
        # check options structure & choices
        options = question_dict["options"]
        if not isinstance(options, dict):
            return False, f"'options' in question {idx} is not a dictionary"
        required_letters = ["A", "B", "C", "D"]
        for letter in required_letters:
            if letter not in options:
                return False, f"Option '{letter}' is missing in question {idx}"
            
        # check correct answer is valid - must be one of A, B, C, D
        if question_dict["correct_answer"] not in required_letters:
            return False, f"'correct_answer' in question {idx} is not one of {required_letters}"
        
    return True, "Quiz data is valid!!"


def display_quiz(quiz_data):
    """
    print out quiz - for testing & debugging
    """
    if quiz_data is None:
        print(" No quiz data to display.")
        return
    
    print(f"\n QUIZ: {quiz_data['topic']}\n")
    
    for idx, question_dict in enumerate(quiz_data["questions"], 1):
        print(f" Question {idx}: {question_dict['question']}")
        for letter in ["A", "B", "C", "D"]:
            print(f"  {letter}. {question_dict['options'][letter]}")
        print(f"  ✓ Correct Answer: {question_dict['correct_answer']}")
        print()

# BONUS ADDITION 
def generate_explanation(question, correct_answer, correct_option_text, api_key):
    """
    generate an explanation for why an answer is correct 
    - should only show on answers that were answered incorrectly
    """
    connection = anth.Anthropic(api_key=api_key)

    prompt = f"""Explain why this answer is correct in 2-3 sentences. Be educational, factual, and concise.
    Question: {question}
    Correct Answer: {correct_answer}. {correct_option_text}
    provide a brief explanation of why this is the correct answer."""

    try:
        message = connection.messages.create(
            model = "claude-sonnet-4-20250514",  # Latest Sonnet model
            max_tokens = 200, # only short explanations
            temperature = 0.7,
            messages = [{"role": "user", "content": prompt}]    
        )

        explanation = message.content[0].text.strip()
        return explanation
    
    except Exception as e:
        print(f" Error generation explanation: {e}")
        return None

# test code - body
if __name__ == "__main__":
    # only runs if this file is executed directly
    api_key = "your_anthropic_api_key_here"  # replace with actual API key
    test_topic = str(input(" Enter a quiz topic: "))
    print(f"testing quiz generation for topic: {test_topic}")

    quiz = generate_quiz(test_topic, api_key)

    try:
        display_quiz(quiz)
        print(f" \n Raw JSON:\n {json.dumps(quiz, indent=4)}")
    except:
        print("Failed - nothing to display.")