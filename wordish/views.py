from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def start_page(request):
    if request.method == "GET":
        context = {"status": "Welcome to Wordish"}
        return render(request, "wordish/start-page.html", context)
    try:
        target = valid_word(request.POST["target_text"])
        context = {"target": target, "status": "start"}
        return render(request, "wordish/new-guess.html", context)
    except Exception as e:
        context = {"status": str(e)}
        return render(request, "wordish/start-page.html", context)

def valid_word(word):
    if not word or len(word) != 5 or not word.isalpha():
        raise ValueError("invalid input")
    return word

def new_guess(request):
    if request.method == "GET":
        context = {"status": "You're hacking. Try again!"}
        return render(request, "wordish/start-page.html", context)
    try:
        target = valid_target(request.POST, "target")
        old_guesses = valid_old_guesses(request.POST, "old_guesses")
    except Exception as e:
        return render(request, "wordish/start-page.html", {"status": f"Fatal error: {e}"})
    try:
        new_guess = valid_word(request.POST["new_guess"])
        context = guess(target, old_guesses + [new_guess])
    except Exception as e:
        context = guess(target, old_guesses)
        context["status"] = f"invalid input: {e}"
    return render(request, 'wordish/new-guess.html', context)

def valid_target(data, key):
    target = data.get(key, "").strip()
    if not valid_word(target):
        raise ValueError("You're hacking.")
    return target

def valid_old_guesses(data, key):
    if len(data[key]) != 0:
        old_guesses_str = ''.join(char for char in data[key] if char not in ["[", "]", "'", ",", " "])
    else:
        old_guesses_str = data[key]
    old_guesses_lst = []
    for i in range(0, len(old_guesses_str), 5):  
        word = old_guesses_str[i: i + 5]
        if not valid_word(word):
            raise ValueError("You're hacking.")
        old_guesses_lst.append(word)
    return old_guesses_lst if old_guesses_str else []

def guess(target, guesses):
    print('start compute')
    num_cols = 5
    num_rows = len(guesses)
    print('number of guesses: ', len(guesses))
    status = ''
    if num_rows > 6:
        raise ValueError("lose")
    matrix = [[{} for _ in range(num_cols)] for _ in range(num_rows)]
    for guess_id in range(num_rows):
        colors = change_color(target, guesses[guess_id])
        for char_id in range(num_cols):
            cell = {'id': f'cell_{guess_id}_{char_id}', 'letter': guesses[guess_id][char_id], 'color': colors[char_id]}
            matrix[guess_id][char_id] = cell
        win = ["green", "green", "green", "green", "green"]
        if num_rows == 6:
            status = 'lose'
        elif colors == win:
            status = 'win'
        else:
            status = f'{6 - num_rows} guesses left'
    context = {
        "status": status,
        "matrix": matrix,
        "target": target,
        "old_guesses": guesses,
    }
    return context

def change_color(target, guess):
    guess_copy = list(guess)
    target_copy = list(target)
    colors = [""] * 5
    
    for i in range(5):
        if guess_copy[i] == target_copy[i]:
            colors[i] = "green"
            target_copy[i] = None
    
    for i in range(5):
        if guess_copy[i] in target_copy and colors[i] != "green":
            colors[i] = "yellow"
            target_copy[target_copy.index(guess_copy[i])] = None
    
    for i in range(5):
        if colors[i] not in ["green", "yellow"]:
            colors[i] = "grey"
    
    return colors
