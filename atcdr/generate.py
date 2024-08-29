import json
import os
import re

from rich.console import Console

from atcdr.test import (
	LabeledTestCaseResult,
	ResultStatus,
	create_testcases_from_html,
	judge_code_from,
	render_results,
)
from atcdr.util.execute import execute_files
from atcdr.util.filetype import (
	FILE_EXTENSIONS,
	Filename,
	Lang,
	lang2str,
	str2lang,
)
from atcdr.util.gpt import ChatGPT, set_api_key
from atcdr.util.problem import make_problem_markdown


def get_code_from_gpt_output(output: str) -> str:
	pattern = re.compile(r'```(?:\w+)?\s*(.*?)\s*```', re.DOTALL)
	match = pattern.search(output)
	return match.group(1) if match else ''


def render_result_for_GPT(lresult: LabeledTestCaseResult) -> str:
	output = f'{lresult.label} of Test:\n'
	result = lresult.result
	testcase = lresult.testcase

	if result.passed == ResultStatus.AC:
		output += 'Accepted !! \n'

	elif result.passed == ResultStatus.WA:
		output += (
			f'Wrong Answer\n'
			f'Output:\n{result.output}\n'
			f'Expected Output:\n{testcase.output}\n'
		)

	elif result.passed == ResultStatus.RE:
		output += f'[RE] Runtime Error\n  Output:\n{result.output}'

	elif result.passed == ResultStatus.TLE:
		output += '[TLE] Time Limit Exceeded\n'

	elif result.passed == ResultStatus.CE:
		output += f'[CE] Compile Error\n  Output:\n{result.output}'

	elif result.passed == ResultStatus.MLE:
		output += '[ME] Memory Limit Exceeded\n'

	return output


def generate_code(file: Filename, lang: Lang) -> None:
	console = Console()
	with open(file, 'r') as f:
		html_content = f.read()
	md = make_problem_markdown(html_content, 'en')

	if set_api_key() is None:
		return
	gpt = ChatGPT(
		system_prompt=f"""You are an excellent programmer. You solve problems in competitive programming.When a user provides you with a problem from a programming contest called AtCoder, including the Problem,Constraints, Input, Output, Input Example, and Output Example, please carefully consider these and solve the problem.Make sure that your output code block contains no more than two blocks. Pay close attention to the Input, Input Example, Output, and Output Example.Create the solution in {lang2str(lang)}.""",
	)
	with console.status(f'{gpt.model.value}がコードを生成しています...'):
		reply = gpt.tell(md)

	code = get_code_from_gpt_output(reply)

	saved_filename = (
		os.path.splitext(file)[0] + f'_by_{gpt.model.value}' + FILE_EXTENSIONS[lang]
	)
	with open(saved_filename, 'w') as f:
		console.print(
			f'[green][+][/green] {gpt.model.value} の出力したコードを保存しました：{f.name}'
		)
		f.write(code)

	console.print(f'[info] AI利用にかかったAPIコスト: {gpt.sum_cost}')


def generate_template(file: Filename, lang: Lang) -> None:
	console = Console()
	with open(file, 'r') as f:
		html_content = f.read()
	md = make_problem_markdown(html_content, 'en')

	if set_api_key() is None:
		return
	gpt = ChatGPT(
		system_prompt='You are a highly skilled programmer. Your role is to create a template code for competitive programming.',
		temperature=0.0,
	)

	propmpt = f"""
The user will provide a problem from a programming contest called AtCoder. This problem will include the Problem Statement, Constraints, Input, Output, Input Example, and Output Example. You should focus on the Constraints and Input sections to create the template in {lang2str(lang)}.

- First, create the part of the code that handles input. Then, you should read ###Input Block and ###Constraints Block.
- After receiving the input, define variables in the program by reading ###Constraints Block and explain how to use the variables in the comment of your code block with example.
- Last, define variables needed for output. Then you should read ###Output Block and ###Constraints Block.

You must not solve the problem. Please faithfully reproduce the variable names defined in the problem.
    """
	with console.status(f'{lang2str(lang)}のテンプレートを生成しています...'):
		reply = gpt.tell(md + propmpt)
	code = get_code_from_gpt_output(reply)

	savaed_filename = os.path.splitext(file)[0] + FILE_EXTENSIONS[lang]
	with open(savaed_filename, 'x') as f:
		console.print(
			f'[green][+][/green] テンプレートファイルを作成 :{savaed_filename}'
		)
		f.write(code)

	console.print(f'[info] AI利用にかかったAPIコスト: {gpt.sum_cost}')


def solve_problem(file: Filename, lang: Lang) -> None:
	console = Console()
	with open(file, 'r') as f:
		html_content = f.read()
	md = make_problem_markdown(html_content, 'en')
	labeled_cases = create_testcases_from_html(html_content)

	if set_api_key() is None:
		return
	gpt = ChatGPT(
		system_prompt=f"""You are a brilliant programmer. Your task is to solve an AtCoder problem. AtCoder is a platform that hosts programming competitions where participants write programs to solve algorithmic challenges.Please solve the problem in {lang2str(lang)}.""",
	)

	file_without_ext = os.path.splitext(file)[0]

	for i in range(1, 4):
		with console.status(f'{i}回目のコード生成 (by {gpt.model.value})...'):
			test_report = ''
			if i == 1:
				reply = gpt.tell(md)
			else:
				reply = gpt.tell(f"""The following is the test report for the code you provided:
	{test_report}
	Please provide an updated version of the code in {lang2str(lang)}.""")

		code = get_code_from_gpt_output(reply)

		saved_filename = (
			f'{i}_'
			+ file_without_ext
			+ f'_by_{gpt.model.value}'
			+ FILE_EXTENSIONS[lang]
		)
		with open(saved_filename, 'w') as f:
			console.print(
				f'[green][+][/green] {gpt.model.value} の出力したコードを保存しました：{f.name}'
			)
			f.write(code)

		labeled_results = judge_code_from(labeled_cases, saved_filename)
		test_report = '\n'.join(
			render_result_for_GPT(lresult) for lresult in labeled_results
		)

		console.rule(f'{i}回目のコード生成でのテスト結果')
		render_results(saved_filename, labeled_results)

		if all(
			labeled_result.result.passed == ResultStatus.AC
			for labeled_result in labeled_results
		):
			console.print('[green]コードのテストに成功![/green]')
			break

	with open(
		'log_'
		+ file_without_ext
		+ f'_by_{gpt.model.value}'
		+ FILE_EXTENSIONS[Lang.JSON],
		'w',
	) as f:
		console.print(
			f'[green][+][/green] {gpt.model.value}の出力のログを保存しました：{f.name}'
		)
		f.write(json.dumps(gpt.messages, indent=2))
	console.print(f'AI利用にかかったAPIコスト:{gpt.sum_cost}')
	return


def generate(
	*source: str,
	lang: str = 'Python',
	without_test: bool = False,
	template: bool = False,
) -> None:
	la = str2lang(lang)

	if template:
		execute_files(
			*source,
			func=lambda file: generate_template(file, la),
			target_filetypes=[Lang.HTML],
		)
	elif without_test:
		execute_files(
			*source,
			func=lambda file: generate_code(file, la),
			target_filetypes=[Lang.HTML],
		)
	else:
		execute_files(
			*source,
			func=lambda file: solve_problem(file, la),
			target_filetypes=[Lang.HTML],
		)
