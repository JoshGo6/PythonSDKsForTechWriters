# Python SDK Learning Path for Tech. Writers

This repo contains a tech. writer-oriented Python course that I've developed over the course of many hours (and continue to periodically refine)—first with GPT, and then with Claude. There are many Python courses available, but their scopes vary widely. Some courses are small, and some are geared to making the student a full-blown Python developer. I wanted a course specific to the needs of a senior tech. writer.

## Scope of the Course

After finishing the course, the student should be able to do the following with Python:

- Process text files—in particular, Markdown, YAML, JSON, and CSV files—to include extracting text; changing text; reading and writing files; and deleting, moving, and renaming files.
- Place raw API calls and extract and transform the JSON objects they return.
- Use Python SDKs skillfully to the point that they can document them for others.

> [!note]
> This course is **not** designed to make the student into a full-blown Python developer. After finishing the course, the student will be able to skillfully work with objects, but not to author classes.

A typical use case addressed by this course is a situation where a Markdown document contains headings with sequential digits (for instance, "Lesson 1," "Lesson 2,", "Lesson 3," and so forth). When you insert a new heading in the middle of the document, the subsequent heading numbers are all off by one. Using the tools taught in this course, you can author a Python script to fix this numbering. I had this problem, and using the skills in this course, I authored a Python script to fix the problem.

## Instructions for use

The [lesson artifact](./Python%20Lesson%20Plan%20for%20SDKs.md) in this repo contains the motivation for the course, a description of its 63 lessons (as of this writing), course constraints, and output format specifications. Each lesson culminates in a coding exercise. To generate a lesson, upload the lesson artifact into your LLM, along with a prompt like, "Generate lesson 42 from the uploaded document." The lesson artifact contains all of the information your LLM needs to generate the lesson.

> [!caution]
> LLMs, like human, are fallible. It's quite common to find errors in LLM output, and I've found errors in the generated lessons, including in the exercises. If you wish to clone this repo, it is upon you to verify that the material produced is accurate.

## Personal progress 

As of July 12, 2026, I am up to lesson 37, [Making HTTP Requests with `requests` — GET and Response Basics](./37th%20Lesson%20—%20Making%20HTTP%20Requests%20with%20`requests`%20—%20GET%20and%20Response%20Basics.md).
