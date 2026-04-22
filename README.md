# Python SDK Learning Path for Tech. Writers

This repo contains a tech. writer-oriented Python course. The goals of the course are that the student, upon completion, should be able to do the following:

- Use Python to process text files, and in particular, Markdown and JSON files, to include extracting text; changing text; reading and writing files; and deleting, moving, and renaming files.
- Use Python to place raw API calls and work with the JSON objects they return.
- Use Python SDKs.

I am in the middle of taking this course, which I developed over the course of many hours—first with GPT, and then with Claude. The course is represented in the [lesson artifact](./Python%20Lesson%20Plan%20for%20SDKs.md). That document contains the motivation for the course, a description of its 62 lessons (as of this writing), constraints, and output format specifications. Per my requirements, each lesson culminates in a coding exercise.

To generate a lesson, upload the lesson artifact into your LLM, along with a prompt like, "Generate lesson 42 from the uploaded document." The lesson artifact contains all of the information your LLM needs to generate the lesson. (I created a [Claude skill](https://claude.com/skills) in my Claude account to generate the lessons so that I wouldn't have to upload the lesson artifact each time I need a new lesson.)

> [!caution]
> LLMs, like human, are fallible. It's quite common to find errors in LLM output, and I've found errors in the generated lessons, including in the exercises. If you wish to clone this repo, it is upon you to verify that the material produced is accurate.

As I create new lessons and do the exercises, I upload my exercises to this repo. As of April 21, 2026, I am up to lesson 32, [pip, Packages, and Reading Signatures](./32nd%20Lesson%20-%20pip,%20Packages,%20and%20Reading%20Signatures.md).

> [!important]
> None of the completed exercises are vibe coded. I have done all of the work by hand, because it makes no sense to vibe code when you're *learning* to code.