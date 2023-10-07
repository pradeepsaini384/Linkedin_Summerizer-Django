from django.shortcuts import render


# myapp/views.py
import os
from django.shortcuts import render, redirect
from django.urls import reverse
 
from linkedin_scraper import Person, actions
from selenium import webdriver
# Import your model if needed
import openai  # Assuming you've installed the OpenAI package
import json
import re

def tokeniztion(input_string):
    
    person_pattern = r"Person (.*?)\n"
    experience_pattern = r"Experience\n\((\[Experience.*?\)\])"
    education_pattern = r"Education\n\((\[Education.*?\)\])"

    # Extract the values using regular expressions
    person_match = re.search(person_pattern, input_string)
    experience_match = re.search(experience_pattern, input_string, re.DOTALL)
    education_match = re.search(education_pattern, input_string, re.DOTALL)

    # Extracted values
    person_value = person_match.group(1) if person_match else ""
    experience_value = experience_match.group(1) if experience_match else ""
    education_value = education_match.group(1) if education_match else ""

    # Combine the values into a single string
    combined_string = f"Person: {person_value}\nExperience: {experience_value}\nEducation: {education_value}"
    cleaned_combined_string = re.sub(r"\w+=None,? *", "", combined_string)
    return(cleaned_combined_string)


file_name = "data.json"
def load_from_json(file_name):
    try:
        with open(file_name, 'r') as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        return None
def check_user_in_json(url):
    data= load_from_json(file_name)
    for i in data:
        if url in i['name']:
            return i['details']
    else:
        return None
def user_data_in_json(url):
    data= load_from_json(file_name)
    for i in data:
        if url in i['name']:
            return i['output']
        else:
            return None
def check_user_len_in_json(url):
    data= load_from_json(file_name)
    for i in data:
        if url in i['name']:
            return len(i['output'])
        else:
            return None
def save_new_user_in_json(url,person):
    
    dic = {
        "name": url ,
        "details": person,
        "output":[]
    }
    data = load_from_json(file_name)
    data.append(dic)
    with open(file_name, 'w') as json_file:
            json.dump(data, json_file)
def save_output_in_json(url,output):
    data = load_from_json(file_name)
    for i in data :
        if url in i['name']:
            if len(i['output']) <2:
                i['output'].insert(0,output)
                with open(file_name, 'w') as json_file:
                    json.dump(data, json_file, indent=4)
                output_saved = i['output']
                return output_saved
            else:
                return i['output']
       
def landing_page(request):
    return render(request, 'Linkedin/index.html')
def output(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        already_store = check_user_in_json(url)
        
        if already_store is None:
            email = os.environ.get('email')
            password = os.environ.get('password')
            driver = webdriver.Chrome()
            actions.login(driver, email, password)
            person = str(Person(f"{url}", driver=driver))
            detail = tokeniztion(person)
            save_new_user_in_json(url, detail)
            output = call_ai(detail, url)
            data = save_output_in_json(url,output)
            return render(request, 'Linkedin/output.html', {'url': url, 'output': data})
        else:
            output = call_ai(already_store, url)
            # output = "Okay"
            data = save_output_in_json(url,output)
        
            return render(request, 'Linkedin/output.html', {'url': url, 'output': data})
    
    return render(request, 'Linkedin/output.html')  # Create the input template

def call_ai(person, url):
    user_len = check_user_len_in_json(url)
    
    if user_len == 2:
        answer = user_data_in_json(url)
        return answer
    
    else:
        api_key = os.environ.get('OPENAI_API_KEY')
        openai.api_key = api_key
        prompt = f"""You Are A Best Ai Tool who can generate a short paragraph for linkedin About section .You have the ability to understand the parameter according to a list or python generated output . 
                so being a smart reader you have to understand all parameters  and generate a summary of  on his given details and make sure the output format  is like a person expressing about himself like hey i'm person_name and so on.
                details = {person}"""  # Define your AI prompt here
        
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=500,
            stop=None,
            temperature=1
        )
        
        answer = response.choices[0].text.strip()
        return answer

def result(request, url, answer):
    data = save_output_in_json(url, answer)
    return render(request, 'Linkedin/output.html', {'url': url, 'output': data})
