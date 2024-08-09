import os
import re
import json

from atcdr.test import (
    ResultStatus,
    create_testcases_from_html,
    judge_code_from,
    render_result,
)
from atcdr.util.filename import (
    FILE_EXTENSIONS,
    Filename,
    Lang,
    execute_files,
    lang2str,
    str2lang,
)
from atcdr.util.gpt import ChatGPT, set_api_key
from atcdr.util.problem import make_problem_markdown


def get_code_from_gpt_output(output: str) -> str:
    pattern = re.compile(r"```(?:\w+)?\s*(.*?)\s*```", re.DOTALL)
    match = pattern.search(output)
    return match.group(1) if match else ""


def generate_code(file: Filename, lang: Lang) -> None:
    with open(file, "r") as f:
        html_content = f.read()
    md = make_problem_markdown(html_content, "en")

    if set_api_key() is None:
        return
    gpt = ChatGPT(
        system_prompt=f"""You are an excellent programmer. You solve problems in competitive programming.When a user provides you with a problem from a programming contest called AtCoder, including the Problem,Constraints, Input, Output, Input Example, and Output Example, please carefully consider these and solve the problem.Make sure that your output code block contains no more than two blocks. Pay close attention to the Input, Input Example, Output, and Output Example.Create the solution in {lang2str(lang)}.""",
    )
    reply = gpt.tell(md)
    code = get_code_from_gpt_output(reply)
    print(f"AI利用にかかったAPIコスト: {gpt.sum_cost}")

    saved_filename = (
        os.path.splitext(file)[0] + f"by_{gpt.model}" + FILE_EXTENSIONS[lang]
    )
    with open(saved_filename, "w") as f:
        print(f"コードを保存しました：{saved_filename}")
        f.write(code)


def generate_template(file: Filename, lang: Lang) -> None:
    with open(file, "r") as f:
        html_content = f.read()
    md = make_problem_markdown(html_content, "en")

    if set_api_key() is None:
        return
    gpt = ChatGPT(
        system_prompt=f"""You are a highly skilled programmer. Your role is to create a template code for competitive programming.The user will provide you with a problem from a programming contest called AtCoder, including the Problem, Constraints, Input, Output, Input Example, and Output Example. While you should consider the entire problem, you should pay particular attention to the Input, Input Example sections to create the template.The purpose is to handle the boring parts of the problem that are not directly related to the problem’s logic, such as receiving arguments, defining variables, or defining constants necessary for output, on behalf of the competitor. You should create a template in {lang2str(lang)} that maximizes assistance to the competitor, considering the problem statement. However, you should not solve the problem.""",
        temperature=0.0,
    )

    reply = gpt.tell(md)
    code = get_code_from_gpt_output(reply)
    print(f"AI利用にかかったAPIコスト:{gpt.sum_cost}")

    savaed_filename = (
        os.path.splitext(file)[0] + f"_by_{gpt.model}" + FILE_EXTENSIONS[lang]
    )
    with open(savaed_filename, "w") as f:
        f.write(code)


def solve_problem(file: Filename, lang: Lang) -> None:
    with open(file, "r") as f:
        html_content = f.read()
    md = make_problem_markdown(html_content, "en")
    labeled_cases = create_testcases_from_html(html_content)

    if set_api_key() is None:
        return

    file_without_ext = os.path.splitext(file)[0]

    gpt = ChatGPT(
        system_prompt=f"""You are a brilliant programmer. Your task is to solve an AtCoder problem. AtCoder is a platform that hosts programming competitions where participants write programs to solve algorithmic challenges.Please solve the problem in {lang2str(lang)}.""",
    )

    reply = gpt.tell(md)

    for i in range(1, 4):
        code = get_code_from_gpt_output(reply)

        saved_filename = (
            file_without_ext + f"_by_{gpt.model}_try{i}" + FILE_EXTENSIONS[lang]
        )
        with open(saved_filename, "w") as f:
            f.write(code)

        labeled_results = judge_code_from(labeled_cases, saved_filename)
        test_report = "\n".join(render_result(lresult) for lresult in labeled_results)

        print(f"{i}回目のコード生成でのテスト結果:---")
        print(test_report)

        reply = gpt.tell(f"""
The following is the test report for the code you provided:
{test_report}
Please provide an updated version of the code in {lang2str(lang)}.""")

        if all(
            labeled_result.result.passed == ResultStatus.AC
            for labeled_result in labeled_results
        ):
            print("コードのテストに成功!")
            with open(
                file_without_ext + f"_by_{gpt.model}" + FILE_EXTENSIONS[Lang.JSON], "w"
            ) as f:
                f.write(json.dumps(gpt.messages, indent=2))
            break
        else:
            pass

    print(f"AI利用にかかったAPIコスト：{gpt.sum_cost}")


def generate(
    *source: str,
    lang: str = "Python",
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
