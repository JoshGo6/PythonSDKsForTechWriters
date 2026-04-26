# Python SDK Learning Path for Tech. Writers

This repo contains a tech. writer-oriented Python course that I've developed over the course of many hours (and continue to periodically refine)—first with GPT, and then with Claude. There are many Python courses available, but their scopes vary widely. Some courses are small, and some are geared to making the student a full-blown Python developer. I wanted a course specific to the needs of a senior tech. writer.

## Scope of the Course

After finishing the course, the student should be able to do the following with Python:

- Process text files—in particular, Markdown, YAML, JSON, and CSV files—to include extracting text; changing text; reading and writing files; and deleting, moving, and renaming files.
- Place raw API calls and extract and transform the JSON objects they return.
- Use Python SDKs.

This course is **not** designed to make the student into a full-blown Python developer. After finishing the course, the student will be able to skillfully work with objects, but not to author classes. A typical use case addressed by this course is a situation where a Markdown document contains headings with sequential digits (for instance, "Lesson 1," "Lesson 2,", "Lesson 3," and so forth). When you insert a new heading in the middle of the document, the subsequent heading numbers are all off by one.

Using the tools taught in this course, you can write a Python script that programmatically increments all of the numbers in the headings that come after the new heading. As I've refined the course and needed to add additional lessons, I had that exact challenge. Instead of renumbering the headings by hand, using the material I learned in this course, I wrote a Python script to do the renumbering.

## Instructions for use

The [lesson artifact](./Python%20Lesson%20Plan%20for%20SDKs.md) in this repo contains the motivation for the course, a description of its 63 lessons (as of this writing), course constraints, and output format specifications. Each lesson culminates in a coding exercise. To generate a lesson, upload the lesson artifact into your LLM, along with a prompt like, "Generate lesson 42 from the uploaded document." The lesson artifact contains all of the information your LLM needs to generate the lesson.

> [!caution]
> LLMs, like human, are fallible. It's quite common to find errors in LLM output, and I've found errors in the generated lessons, including in the exercises. If you wish to clone this repo, it is upon you to verify that the material produced is accurate.

## Personal progress with the course

As I create new lessons and do the exercises, I upload my exercises to this repo. As of April 25, 2026, I am up to lesson 33, [Virtual Environments with `venv` (Repeatable Setups)](./33rd%20Lesson%20-%20Virtual%20Environments%20with%20`venv`%20(Repeatable%20Setups).md).

> [!important]
> None of the completed exercises I've uploaded are vibe coded. I do all of the work by hand, because it makes no sense to vibe code when you're *learning* to code.
