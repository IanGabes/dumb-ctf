
questions = [
    {
        "id": 1,
        "question": "What is the capital of France?",
        "answer": "Paris"
    },
    {
        "id": 2,
        "question": "What is 2 + 2?",
        "answer": "4"
    },
    # Template: Add 18 more questions here
    # {
    #     "id": X,
    #     "question": "Your question here?",
    #     "answer": "Correct answer"
    # },
]

# Fill to 20 for skeleton
for i in range(3, 21):
    questions.append({
        "id": i,
        "question": f"Placeholder Question {i}?",
        "answer": "answer"
    })
