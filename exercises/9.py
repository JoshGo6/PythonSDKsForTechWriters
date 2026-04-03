import string

'''
items = ["alpha", "beta", "gamma"]

for i in range(len(items)):
    print(i, items[i])
for i in range(len(items)):
    print(items[i])
print("")
for i in items:
    print(i)


    Create a Python script that defines a nested list where each inner list represents a documentation page and contains exactly two elements: the page title and its word count as an integer. Include at least four pages. Your script must loop over the outer list, and for each page print a formatted line that shows the page number (starting at 1), the title, and the word count. After the loop, print the total word count across all pages.
Run your script from the terminal and verify that every page is listed and the total is correct.

    Create a Python script that defines a string containing a short sentence of your choice (at least 20 characters). Your script must loop over the string character by character and count how many characters are uppercase letters. To check whether a character is uppercase, use the .upper() string method you learned in Lesson 5: compare the character to its own .upper() form and count it only when they are equal and the character is a letter (you can verify it is a letter by checking that it appears in a known alphabet string using the in membership test from this lesson).
After the loop, print the original string and the uppercase letter count using an f-string.
Run your script and verify the count against the sentence you chose.
    '''

sentences = []
sentences.append("The quick, brown fox jumped.")
sentences.extend(["His name is Jack Frost.", "Why do you act this way?"])
print(sentences)

upper_letters = set(string.ascii_uppercase)
count = 0
for sentence in sentences:
    print(sentence.upper())
    print(sentence)
    for char in sentence:
        if char in upper_letters:
            count += 1
print(count)