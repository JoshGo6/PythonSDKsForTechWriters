"""
LESSON 4 – EXERCISES
(Use only material from Lessons 1–4:
- Running Python (REPL and scripts)
- Variables and basic types
- print() and type()
- String literals (single, double, triple quotes)
- Escaping with backslash
- Indexing with [ ]
- String concatenation using +)

----------------------------------------
Exercise 1 – Escaping and Quotes
----------------------------------------

1. Create a variable named doc_line that stores this exact text:

   The editor shows "modified" when it's tracking changes.

2. The string must:
   - Be written as a single string literal.
   - Use at least one escaped quote (\" or \').

3. Use print(doc_line) to verify that the output matches the sentence exactly.

4. Create a second variable named doc_line_alt that stores a similar sentence
   but uses the opposite outer quote style from doc_line.

5. Print both variables.


----------------------------------------
Exercise 2 – Multi-line Text and Indexing
----------------------------------------

1. Create a variable named help_text using triple quotes.
   When printed, it must display exactly:

   Usage: myscript FILE

   FILE is a Markdown document to process.

   (That is: one line, a blank line, then a second line.)

2. Print help_text to verify formatting.

3. Create a separate variable named title that stores only:

   Usage: myscript FILE

   (This must be a regular single-line string.)

4. Using indexing with [ ], create:
   - first_char  (the first character of title)
   - second_char (the second character of title)

5. Print the following using print():

   Full title: <title>
   First two characters: <first_char> <second_char>


----------------------------------------
Exercise 3 – Concatenation and Indexing
----------------------------------------

1. Create two variables:
   - first = "Git"
   - second = "Hub"

2. Create:
   - combined (the two words joined together with no space)
   - spaced   (the two words joined with a single space in between)

3. Print both combined and spaced.

4. Create a variable named language with the value "Python".

5. Using indexing only, create:
   - first_letter  (the first character)
   - third_letter  (the third character)
   - last_letter   (the final character, determined by counting)

6. Print all three letters on one line using print().


----------------------------------------
Exercise 4 – Escape Sequences
----------------------------------------

1. Create a variable named block that contains two lines of text using "\n"
   inside a single-line string literal.

2. When printed, it must appear as two separate lines.

3. Create another variable named block_triple that produces the same
   visible output but uses triple quotes instead of "\n".

4. Print both variables to verify that the output is visually identical.
"""

doc_line1 = "The editor shows \"modified\" when it's tracking changes."
doc_line2 = 'The editor shows "modified" when it\'s tracking changes.'

print(doc_line1)
print(f"{doc_line2}")

help_message = '''Usage: myscript FILE

FILE is a Markdown document to process.'''

end_pos = help_message.find("\n")
end_pos = end_pos - 1
print(help_message[0:(end_pos + 1)])
third_line_start = help_message.find("FILE is")
print("The final line:")
print(help_message[third_line_start:])
print(f"The second letter of the final line is {help_message[third_line_start + 1]}")


first = "Josh"
second = "G"
combined = first + second
print(first + second)
print(first, second)
print(f"{first} {second}")
print(combined)
print(f"{combined}")

