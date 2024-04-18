import query_llama
import csv
import random

"""
CS 232 HW 8: Prompt Engineering for PuzzleQA dataset
"""

def readDataset():
	with open("puzzleQA.tsv",'r') as of:
		reader = csv.DictReader(of, delimiter="\t",)
		lines = [row for row in reader]
	return lines

def basic_mc_prompt(item):
	prompt = f"Explanation: {item['explanation']}\nQuestion: {item['question']}\n"
	choices = [item[f"opt{i}"] for i in range(4)]
	correct = choices[int(item["gold"])]
	random.shuffle(choices)
	for i,c in enumerate(choices):
		prompt += f"Choice {i}: {c}\n"
	prompt+="Answer: Choice"
	return prompt, str(choices.index(correct))

def custom_mc_prompt(item):
    prompt = f"**Explanation:** {item['explanation']}\n"
    prompt += f"**Question:** What is the best choice for '{item['question']}'?\n"

    choices = [item[f"opt{i}"] for i in range(4)]
    correct_index = int(item["gold"])
    correct_answer = choices[correct_index]
    random.shuffle(choices)

    for i, c in enumerate(choices):
        prompt += f"{chr(65 + i)}. {c}\n"

    prompt += "\nSelect the letter corresponding to the correct answer."
    return prompt, str(chr(65 + choices.index(correct_answer)))



def fewshot_mc_prompt(item):
    exampleProbs = [
        {
            'explanation': "It's our annual year-end news quiz, compiled with the help of Kathie Baker and Tim Goodman. You are given new names in the news — people you probably never heard of before 2011, but who became famous during the past 12 months. Explain why they're famous.",
            'question': "Why is Kim Jong Un famous?",
            'opt0': "He married Kim Kardashian for 72 days",
            'opt1': "He's the new North Korean leader",
            'opt2': "The new intelligence software system for the iPhone that answers questions for you",
            'opt3': "Gilad Shalit is the Israeli soldier who was released from captivity in exchange for many Palestinians",
            'gold': "1"
        },
        {
            'explanation': "It's our annual year-end news quiz, compiled with the help of Kathie Baker and Tim Goodman. You are given new names in the news — people you probably never heard of before 2011, but who became famous during the past 12 months. Explain why they're famous.",
            'question': "Why is Gilad Shalit famous?",
            'opt0': "Gilad Shalit is the Israeli soldier who was released from captivity in exchange for many Palestinians",
            'opt1': "The new intelligence software system for the iPhone that answers questions for you",
            'opt2': "He was a Tunisian street vendor whose self-immolation martyrdom triggered the Arab Spring and led to the overthrow of the Tunisian government",
            'opt3': "He's the new North Korean leader",
            'gold': "0"
        },
        {
            'explanation': "It's our annual year-end news quiz, compiled with the help of Kathie Baker and Tim Goodman. You are given new names in the news — people you probably never heard of before 2011, but who became famous during the past 12 months. Explain why they're famous.",
            'question': "Why is Mohammed Bouazizi famous?",
            'opt0': "Gilad Shalit is the Israeli soldier who was released from captivity in exchange for many Palestinians",
            'opt1': "He's the new North Korean leader",
            'opt2': "He was a Tunisian street vendor whose self-immolation martyrdom triggered the Arab Spring and led to the overthrow of the Tunisian government",
            'opt3': "The new intelligence software system for the iPhone that answers questions for you",
            'gold': "2"
        }
    ]
    example = [basic_mc_prompt(example)[0] for example in exampleProbs]

    prompt, answer = basic_mc_prompt(item)

    fullPrompt = f"Look at this example prompt: {example}\n\nAnswer the question:\n{prompt}"

    return fullPrompt, answer

def cot_mc_prompt(item):
	exampleProbs = [
		{ 'question': 'Given a four-letter word and a six-letter word, rearrange the letters of one of them to get a synonym of the other for the words "dare" and "peruse"',
   'explanation': "To peruse means to look over or through and to dare means a challenge, especially to prove courage. Given the choices read, flow, tore, and keep if you move the words around, you get read, which is a synonym of peruse. Read is the value for key 'opt0', so 0 should be returned. The 'gold' key is the answer, which is also 0. Return 0.",
	'opt0': 'read',
   'opt1':"flow",
   'opt2':'tore',
   'opt3':'keep',
   'gold':'0',
   }, 
   	{ 'question': 'Given a four-letter word and a six-letter word, rearrange the letters of one of them to get a synonym of the other for the words "tame" and "coiled"',
   'explanation': "Tame means to domesticate and coiled means arranged in a series of circles, one above or inside the other. Given the choices: keep, docile,tore, and lather, if you move the words around, you get docile, which means easily taught or handled. 'Docile' is a synonym of coiled. Docile is the value for 'opt3', so 3 should be returned. The 'gold' key is the answer, which is also 3. Return 3. ",
      'opt0': 'coat',
   'opt1':"ring",
   'opt2':'tore',
   'opt3':'docile',
   'gold':'3',
   }, 
   	{ 'question': 'Given a four-letter word and a six-letter word, rearrange the letters of one of them to get a synonym of the other for the words "taco" and "jacket"',
   'explanation': "A taco is a Mexican food item and a jacket is a long sleeve clothing item. If you move the words around, you get 'coat', which is a synonym of 'jacket'. Coat is the value for key 'opt0', so 0 should be returned. The 'gold' key is the answer, which is also 0. Return 0.",
	'opt0': 'coat',
   'opt1':"flow",
   'opt2':'keep',
   'opt3':'laid',
   'gold':'0',
   },  
	]
	example = [basic_mc_prompt(example)[1] for example in exampleProbs]
	prompt, answer = basic_mc_prompt(item)
	# print(prompt)

	# print(answer)
	fullPrompt = f"Look at this example prompt: {example}\n\nAnswer the question:\n{prompt}"
	
	return fullPrompt, answer

def mc_score(response,correctAnswer):
	return 1 if correctAnswer in response else 0

def runMCtask(data,prompt_fn,token_limit=100):
	total = 0
	for item in data:
		prompt, answerNumber = prompt_fn(item)
		response = query_llama.completion_query(prompt,max_tokens=token_limit)
		total += mc_score(response,answerNumber)
	print("Percent correct: ",total/len(data))
	return total


def generation_prompt():
    examplePrompts = [
        {"category": "OTHER",
         "explanation": "It's our annual year-end news quiz, compiled with the help of Kathie Baker and Tim Goodman. You are given new names in the news — people you probably never heard of before 2011, but who became famous during the past 12 months. Explain why they're famous.",
         "question": "Kim Jong Un",
         "opt0": "He married Kim Kardashian for 72 days",
         "opt1": "He's the new North Korean leader",
         "opt2": "the new intelligence software system for the iPhone that answers questions for you.",
         "opt3": "Gilad Shalit is the Israeli soldier who was released from captivity in exchange for many Palestinians",
         "gold": "1",
         },
        {"category": "OTHER",
         "explanation": "It's our annual year-end news quiz, compiled with the help of Kathie Baker and Tim Goodman. You are given new names in the news — people you probably never heard of before 2011, but who became famous during the past 12 months. Explain why they're famous.",
         "question": "Gilad Shalit",
         "opt0": "Gilad Shalit is the Israeli soldier who was released from captivity in exchange for many Palestinians",
         "opt1": "the new intelligence software system for the iPhone that answers questions for you.",
         "opt2": "He was a Tunisian street vendor whose self-immolation martyrdom triggered the Arab Spring and led to the overthrow of the Tunisian government",
         "opt3": "He's the new North Korean leader",
         "gold": "0",
         }
    ]

    examplePromptsFormatted = [f"{ep['category']}\t{ep['explanation']}\t{ep['question']}\t{ep['opt0']}\t{ep['opt1']}\t{ep['opt2']}\t{ep['opt3']}\t{ep['gold']}" for ep in examplePrompts]

    header = "category\texplanation\tquestion\topt0\topt1\topt2\topt3\tgold"

    fullPrompt = f"Look at the following prompts labeled as category, explanation, question, opt0, opt1, opt2, opt3, gold. There are four options and one gold, which is the index of the correct answer. Create new prompts in the same format.\n\n{header}\n"
    fullPrompt += '\n'.join(examplePromptsFormatted)

    return fullPrompt



def runGenerationTask(tries, token_limit=300):
    games = []

    for _ in range(tries): #do it this amount of times
        prompt = generation_prompt() #calling generation prompt
        response = query_llama.completion_query(prompt, max_tokens=token_limit) #same as other prompt calling
        games.append(response)

    return games


def export(games,fn="generated_games.txt"):
	with open(fn,'w') as of:
		for i,g in enumerate(games):
			of.write(f"GAME {i}\n{g}\n")

def main():
	# dataset = readDataset()
	# score = runMCtask(dataset,basic_mc_prompt) #Original
	# score = runMCtask(dataset,custom_mc_prompt) #new 
	# score = runMCtask(dataset,fewshot_mc_prompt)
	# score = runMCtask(dataset,cot_mc_prompt)
    export(runGenerationTask(10))
	
if __name__ == "__main__":
    main()
