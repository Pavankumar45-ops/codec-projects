# Simple Python Chatbot
A beginner-friendly, rule-based chatbot script that demonstrates basic natural language processing (NLP) through keyword matching. 
This project is an excellent introduction to conditional logic, infinite loops, and string manipulation in Python.

##  How It Works

The chatbot operates on a simple "Listen and Respond" loop. It captures user input, 
converts it to lowercase for consistency, and checks for specific keywords to trigger a predefined response.

###  Supported Interactions

The bot is currently programmed to recognize and respond to the following phrases:

Greetings:Responds to "hello" or "hi".
Well-being:Answers questions about how it is doing.
Identity:Shares its name when asked.
Termination:Ends the session when the user types "bye".

## Code Structure

The project is encapsulated in a single function:

| Component |Description 
| while True | The main loop that keeps the chatbot "alive" and listening. |
| user_input | Captures and cleans the string entered by the user. |
| if/elif/else | The logic "brain" that maps inputs to specific outputs. |
| break | (Recommended addition) To cleanly exit the loop when "bye" is detected. |

## Getting Started

### Prerequisites

* Python 3.x installed.

### Running the Bot

1. Copy the code into a file named chatbot.py.
2. Open your terminal or command prompt.
3. Execute the script:
bash
python chatbot.py



