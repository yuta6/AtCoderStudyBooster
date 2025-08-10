# AtCoderStudyBooster

[日本語版 README はこちら](README.ja.md)

## Overview

🚧 This project is still in experimental stage. We are continuously adding features to help with daily AtCoder practice.

![demo image](./.images/demo0.gif)

AtCoderStudyBooster is a CLI tool designed to accelerate your AtCoder learning journey. It supports downloading problems locally, testing, submitting, and generating solutions. Python installation is required. If you have Python installed, you can install this tool with:

```sh
pip install AtCoderStudyBooster
```

(Python 3.8 or higher is required)

Even after CAPTCHA authentication was introduced, you can still login and submit semi-automatically from CLI. However, you need to manually solve the CAPTCHA through GUI. This tool does not bypass CAPTCHA authentication.

This project is strongly influenced by:
- [online-judge-tools](https://github.com/online-judge-tools)
- [atcoder-cli](https://github.com/Tatamo/atcoder-cli)

## Use Cases

Let's start by using the `download` command to download problems locally.

### 1. Download a Specific Contest

Examples for downloading problems from a single contest.

#### Download all problems from ABC350
```sh
❯ atcdr download abc350
```

#### Download problems A-D from ABC350
```sh
❯ atcdr download abc350 {A..D}
```

#### Download Typical 90 Problems
```sh
❯ atcdr download typical90
```

### 2. Batch Download Multiple Contests

Examples for downloading multiple contests at once. Utilizes bash brace expansion.

#### All problems from ABC001 to ABC010
```sh
❯ atcdr download abc{001..010}
```

#### Specific problems from multiple contests
```sh
❯ atcdr download abc{301..310} {A..C}
```

### 3. Download Specific Difficulty Problems

Examples for collecting problems of the same difficulty across different contests.

#### Download all A problems from ABC301-310
```sh
❯ atcdr download A abc{301..310}
```

This creates the following directory structure:
```
A/
├── abc301/
│   ├── Problem.html
│   └── Problem.md
├── abc302/
│   ├── Problem.html
│   └── Problem.md
└── ...
```

#### Download all B problems from ABC300-302
```sh
❯ atcdr download B abc{300..302}
```

Creates:
```
B/
├── abc300/
│   ├── Problem.html
│   └── Problem.md
├── abc301/
│   ├── Problem.html
│   └── Problem.md
└── abc302/
    ├── Problem.html
    └── Problem.md
```
This directory structure allows you to efficiently practice problems of the same difficulty level in one place.

### Solving Problems

You can view problems by opening Markdown or HTML files with VS Code's HTML Preview or Markdown Preview. In VS Code, you can display the text editor on the left and work on problems while viewing them on the right.

### Testing Samples Locally

Navigate to the folder where you downloaded the problem.

```sh
❯ cd abc224/B
```

After creating your solution file in the folder, run the test command to test against sample cases.

```sh
~/.../abc224/B
❯ atcdr t
```

For Wrong Answer (WA) cases, the display looks like this:

### Submitting Solutions

```sh
~/.../abc224/B
❯ atcdr s
```

Running this command will submit your solution. Login to AtCoder website is required for submission.

### Generating Solutions with GPT

```sh
~/.../abc224/B
❯ atcdr g
```

This command generates a solution using OpenAI's GPT model. An OpenAI API key is required. On first run, you'll be prompted to input your API key.

### Login to AtCoder

```sh
❯ atcdr login
```

Logs into AtCoder. A browser window will open for CAPTCHA verification. After solving the CAPTCHA, login completes automatically.

### Create Markdown File

```sh
~/.../abc224/B
❯ atcdr m
```

Creates a Markdown file from the HTML file in the current directory. This command is automatically executed during `atcdr download`.

### Open Problem in Browser

```sh
~/.../abc224/B
❯ atcdr o
```

Opens the problem page in your browser. Convenient for checking detailed problem statements or constraints.

## Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `atcdr download` | `atcdr d` | Download problems |
| `atcdr test` | `atcdr t` | Test with sample cases |
| `atcdr submit` | `atcdr s` | Submit solution |
| `atcdr generate` | `atcdr g` | Generate solution with GPT |
| `atcdr login` | - | Login to AtCoder |
| `atcdr logout` | - | Logout from AtCoder |
| `atcdr markdown` | `atcdr m` | Create Markdown file |
| `atcdr open` | `atcdr o` | Open problem in browser |

## GPT Code Generation

`atcdr generate` command uses GPT to generate solutions. It requires an OpenAI API key.

### Generate Solution with Test

By default, generated code is tested against sample cases:

```sh
~/.../abc224/B
❯ atcdr generate
```

### Specify Language

Specify the programming language for generation. Default is Python.

```sh
~/.../abc224/B
❯ atcdr generate --lang cpp
```

Supported languages:
- `python` (default)
- `cpp`
- `java`
- `rust`

### Specify GPT Model

```sh
~/.../abc224/B
❯ atcdr generate --gpt gpt-4o
```

Available models:
- `gpt-4o-mini` (default) - Fast and cost-effective
- `gpt-4o` - More accurate but slower

### Generate Code Only Without Testing

To generate code without testing:

```sh
~/.../abc224/B
❯ atcdr generate --lang rust --without_test
```
