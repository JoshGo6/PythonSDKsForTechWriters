# Python SDK Learning Path for Tech. Writers

This repo contains a tech. writer-oriented Python course with the goals being that when I finish the course, I should be able to do the following:

- Process text files, and in particular, Markdown and JSON files, to include extracting text; changing text; reading and writing files; and deleting, moving, and renaming files.
- Place raw API calls and work with the JSON objects they return.
- Use Python SDKs.

Developing this course required many hours of iteration—first with GPT, and then with Claude—to create the [lesson artifact](./Python%20Lesson%20Plan%20for%20SDKs.md). That document contains the motivation for the course, a description of its 62 lessons (as of this writing), constraints, and output format specifications. Per my requirements, each lesson culminates in a coding exercise.

To generate a lesson, upload the lesson artifact into your LLM, along with a prompt like, "Generate lesson 42 from the uploaded document." The artifact contains all of the information your LLM needs to generate the lesson. (I created a [Claude skill](https://claude.com/skills) in my Claude account to generate the lessons so that I wouldn't have to upload the artifact each time I need a new lesson.)

> [!caution]
> LLMs, like human, are fallible. It's quite common to find errors in LLM output, and I've found errors in these lessons, including in the exercises. If you wish to clone this repo, it is upon you to verify that the material produced is accurate.

As I create new lessons and do the exercises, I upload my exercises to this repo. As of April 3, 2026, I am up to lesson 28, which introduces processing JSON.
