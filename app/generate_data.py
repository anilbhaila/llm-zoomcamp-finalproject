import time
import random

from metrics import LLMCallRecord
from db_save import save_conversation
from db_feedback import save_feedback

SAMPLE_QUESTIONS = [
    "How do I create my account?",
    "Can i get refund after i return my product?",
    "How many days for shipping?",
    "Is there a way to add gift message to my order?",
    "What are methods of communication?",
]

SAMPLE_ANSWERS = [
    "By clicking the 'Sign Up' button on the top right corner of our website and follow the instructions.",
    "Yes, 30 days return policy to get a full refund, provided they are in original condition and packaging.",
    "Shipping times depends on the destination and shipping method chosen. Standard shipping usually takes 3-5 business days, while express shipping can take 1-2 business days.",
    "Yes, you can add a gift message during the checkout process.",
    "You can reach us by phone or email or live chat.",
]

RELEVANCE = ["RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]

def fake_record(question, answer):
    return LLMCallRecord(
        model="gpt-5.4-mini",
        prompt=question,
        instructions="",
        answer=answer,
        prompt_tokens=random.randint(50, 200),
        completion_tokens=random.randint(50, 300),
        total_tokens=random.randint(100, 500),
        response_time=random.uniform(0.5, 5.0),
        cost=random.uniform(0.0001, 0.01),
    )

def random_score():
    return random.choice([1, 1, 1, 1, -1])

def generate_one():
    question = random.choice(SAMPLE_QUESTIONS)
    answer = random.choice(SAMPLE_ANSWERS)
    record = fake_record(question, answer)

    conversation_id = save_conversation(
        record, question
    )

    if random.random() < 0.7:
        relevance = random.choice(RELEVANCE)
        save_feedback(
            conversation_id, "judge",
            relevance=relevance,
            explanation=f"Answer is {relevance.lower()}.",
        )

    if random.random() < 0.5:
        score = random_score()
        save_feedback(conversation_id, "user", score=score)

def generate_live():
    print("Starting live data generation (Ctrl+C to stop)...", flush=True)
    while True:
        generate_one()
        time.sleep(1)

if __name__ == "__main__":
    try:
        generate_live()
    except KeyboardInterrupt:
        print("Stopped.")