import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from ItsPrompt.prompt import Prompt
import re
from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style
from rich.text import Text

# Function to get available interviews
def get_interview_list(directory):
    return [file[:-3] for file in os.listdir(directory) if file.endswith('.md')]

def display_options(question, options):
    # Reformat the options to exclude the scoring number from the display text
    # but include it in the return value.
    formatted_options = []
    for idx, option in enumerate(options, start=1):
        # Strip the leading score number from the display text, but keep it for the value.
        display_text = re.sub(r"^\d+\.\s+", "", option)
        formatted_options.append((display_text, str(idx)))

    # Display the question and options using ItsPrompt raw_select,
    # allowing the user to make a selection using the keyboard.
    selected_index = int(Prompt.raw_select(
        question=question,
        options=formatted_options,
        allow_keyboard=True
    )) - 1  # Subtract 1 because options are 1-indexed for display

    # Return the option that includes the scoring number
    return options[selected_index]


def extract_score(response_text):
    if 'N/A' in response_text:
        return None  # Return None for 'N/A' responses
    match = re.match(r"(\d+)", response_text)
    return int(match.group(1)) if match else 0

def display_markdown_header_content(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # Find the first markdown header section
    header_section = re.search(r'^# .+?(?=^## |\Z)', content, re.MULTILINE | re.DOTALL)

    # Check if the header section is found
    if header_section:
        header_content = header_section.group(0).strip()

        # Parse the markdown using the `rich` library
        console = Console(file=open(os.devnull, 'w'))
        md = Markdown(header_content)

        # Obtain the segments without rendering
        segments = console.render(md)
        
        # Now, use a real console to render the new text
        real_console = Console()

        # Iterate over the segments to highlight the '==' enclosed text
        highlight_open = False
        for segment in segments:
            if highlight_open or '==' in segment.text:
                # Split the text to handle starting and ending highlight separately
                parts = re.split(r'==', segment.text)
                for i, part in enumerate(parts):
                    if i % 2 == 0 and part:  # Regular text
                        real_console.print(part, style=segment.style, end="")
                    elif part:  # Highlighted text
                        real_console.print(part, style="black on yellow", end="")
                    highlight_open = not highlight_open and part.endswith('==')
                print()  # Ensure a newline at the end of each processed line
            else:
                real_console.print(segment.text, style=segment.style, end="")
                print()  # Ensure a newline at the end of each processed line
        print("\n")  # Additional newline for separating sections


# Load questions from an external markdown file, skipping scoring
def load_questions(filename):
    questions = []
    current_question = []
    reading_questions = False
    collecting_score = False
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if not reading_questions and line.startswith('## '):
                if line.strip() == '## Scoring':
                    collecting_score = True
                else:
                    reading_questions = True
            elif reading_questions and not collecting_score:
                if line.startswith('## '):  # New question block
                    if current_question:
                        questions.append('\n'.join(current_question))
                    current_question = [line.strip('# ').strip()]
                elif line.strip():
                    current_question.append(line.strip())
        if current_question and not collecting_score:  # Add the last question block if there was one
            questions.append('\n'.join(current_question))
    return questions



# Load scoring categories from an external markdown file
def load_scoring_categories(filename):
    scoring_categories = {}
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
        scoring_section_index = lines.index('## Scoring')  # Locate the scoring section
        for line in lines[scoring_section_index + 1:]:
            if line.strip() and not line.startswith('## '):
                category, score_range = line.split(':')
                scoring_categories[category.strip()] = tuple(map(int, score_range.split('-')))
            elif line.startswith('## '):
                break
    return scoring_categories

# Get category by score
def get_category_by_score(score, scoring_categories):
    for category, score_range in scoring_categories.items():
        if score_range[0] <= score <= score_range[1]:
            return category
    return "unknown"

# Main application logic
def main():
    interviews_dir = './interviews'
    results_dir = './results'
    interviews = get_interview_list(interviews_dir)

    # Select an interview
    chosen_interview = display_options("Choose an interview:", interviews)
    interview_file = os.path.join(interviews_dir, f"{chosen_interview}.md")

    # Load questions and scoring categories
    questions = load_questions(interview_file)
    scoring = load_scoring_categories(interview_file)
    # Display the interview title
    display_markdown_header_content(interview_file)
    # Ask what to do with the selected interview
    action = display_options(f"What would you like to do with {chosen_interview}?", ["Take the interview", "View results only"])

    if action == "Take the interview":
        # Track the number of 'N/A' responses
        na_count = 0

        responses = []
        for question_group in questions:
            os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
            question, *statements = question_group.split('\n')
            print(f"\033[92m{question}\033[0m")  # Print the question in green
            response_text = display_options(question, statements)
            score = extract_score(response_text)
            if score is None:  # If 'N/A' was chosen
                na_count += 1
                if na_count > 2:
                    print("Too many 'N/A' responses. Please try to provide specific answers to the questions.")
                    break  # Exit the loop if more than 2 'N/A' responses are detected
            else:
                responses.append(score)

        # Check if we exited the loop early due to 'N/A' responses
        if na_count > 2:
            print("You have provided too many 'N/A' responses. The interview requires specific answers for accurate scoring and cannot proceed with more than two 'N/A' selections. Please retake the interview with more specific responses.")
            return  # Exit the interview process


        # Filter out 'N/A' responses before calculating total score
        filtered_responses = [response for response in responses if response is not None]
        total_score = sum(filtered_responses)

        score_category = get_category_by_score(total_score, scoring)
        result = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'score': total_score,
            'category': score_category
        }

        # Ensure results directory exists
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        # Update results
        results_file = os.path.join(results_dir, f"{chosen_interview}_results.json")
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                results = json.load(f)
        else:
            results = []
        results.append(result)

        # Save results
        with open(results_file, 'w') as f:
            json.dump(results, f)

        print(f"Final score: {total_score}")
        print(f"Category: {score_category}") 

    # else:
    # View past results
    results_file = os.path.join(results_dir, f"{chosen_interview}_results.json")
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            results = json.load(f)
        # Display results (e.g., plot graph)
        timestamps = [datetime.strptime(r['timestamp'], '%Y-%m-%d %H:%M:%S') for r in results]
        scores = [r['score'] for r in results]
        fig, ax = plt.subplots()

        # Display the filled areas according to scoring categories
        for category, score_range in scoring.items():
            ax.fill_between(timestamps, score_range[0], score_range[1], label=category, alpha=0.5)


        ax.plot(timestamps, scores, marker='o')
        ax.set_xlabel('Date')
        ax.set_ylabel(f"{chosen_interview} Score")
        ax.set_title('Results Over Time')
        plt.legend()
        plt.show()
    else:
        print("No results available for this interview.")

# Run the main function if this module is being executed
if __name__ == "__main__":
    main()
