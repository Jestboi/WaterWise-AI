import json
import random

def generate_variations(question, answer):
    variations = []
    
    # Original format
    variations.append({
        "text": f"### Human: {question}\n### Assistant: {answer}"
    })
    
    # Add variations with different prefixes
    prefixes = [
        "Can you tell me",
        "I'd like to know",
        "Could you explain",
        "Please tell me",
        "I'm curious about",
        "Help me understand"
    ]
    
    for prefix in prefixes:
        if not question.lower().startswith("what") and not question.lower().startswith("how"):
            continue
        
        # Remove the question word and create new variation
        q = question.lower()
        for word in ["what", "how"]:
            if q.startswith(word):
                new_q = prefix + question[len(word):].lower()
                variations.append({
                    "text": f"### Human: {new_q}\n### Assistant: {answer}"
                })
    
    return variations

def convert_json_to_jsonl(input_json, train_output, validate_output, validation_ratio=0.2):
    # Read the JSON file
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert each example and generate variations
    examples = []
    for item in data:
        user_msg = item['messages'][0]['content']
        assistant_msg = item['messages'][1]['content']
        
        # Generate variations for each example
        variations = generate_variations(user_msg, assistant_msg)
        examples.extend(variations)
    
    # Shuffle the examples
    random.shuffle(examples)
    
    # Split into train and validation sets
    total_examples = len(examples)
    validation_size = int(total_examples * validation_ratio)
    train_examples = examples[:-validation_size]
    validate_examples = examples[-validation_size:]
    
    # Write training data
    with open(train_output, 'w', encoding='utf-8') as f:
        for example in train_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    # Write validation data
    with open(validate_output, 'w', encoding='utf-8') as f:
        for example in validate_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"Created {len(train_examples)} training examples and {len(validate_examples)} validation examples")

if __name__ == "__main__":
    convert_json_to_jsonl(
        "dataset/meta-llama-Llama-3.2-3B-Instruct/wc-train.json",
        "dataset/wc-train.jsonl",
        "dataset/wc-validate.jsonl"
    )
