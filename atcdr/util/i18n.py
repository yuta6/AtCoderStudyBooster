import locale
from typing import Dict, Optional


class I18n:
    def __init__(self):
        self._lang: Optional[str] = None
        self._messages: Dict[str, Dict[str, str]] = {'ja': {}, 'en': {}}
        self._load_messages()
        self._detect_language()

    def _detect_language(self) -> None:
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale and system_locale.startswith('ja'):
                self._lang = 'ja'
            else:
                self._lang = 'en'
        except Exception:
            self._lang = 'en'

    def _load_messages(self) -> None:
        self._messages = {
            'ja': {
                # download.py
                'retry_problem': '再試行します。{}',
                'redirect_occurred': 'リダイレクトが発生しました。{}',
                'problem_not_found': '問題が見つかりません。{}',
                'server_error': 'サーバーエラーが発生しました。{}',
                'html_fetch_failed': '{}に対応するHTMLファイルを取得できませんでした。',
                'save_failed': '{}の保存に失敗しました',
                'file_saved': 'ファイルを保存しました: {}',
                'solve_contest_problems': 'コンテストの問題を解きたい',
                'download_one_problem': '1問だけダウンロードする',
                'exit': '終了する',
                'download_atcoder_html': 'AtCoderの問題のHTMLファイルをダウンロードします',
                'navigate_with_arrows': '十字キーで移動,[enter]で実行',
                'input_contest_name': 'コンテスト名を入力してください (例: abc012, abs, typical90)',
                'which_problem_download': 'どの問題をダウンロードしますか?',
                'exiting': '終了します',
                'invalid_selection': '無効な選択です',
                'specify_contest_name': 'コンテスト名を指定してください',
                'invalid_download_args': 'ダウンロードの引数が正しくありません',
                # test.py
                'runner_not_found': '{}の適切な言語のランナーが見つかりませんでした.',
                'test_of': '{}のテスト \n',
                'compile_time': 'コンパイルにかかった時間: [not italic cyan]{}[/] ms[/]',
                'compiler_message': 'コンパイラーのメッセージ',
                'status': 'ステータス ',
                'execution_time': '実行時間   [cyan]{}[/cyan] ms',
                'input': '入力',
                'output': '出力',
                'expected_output': '正解の出力',
                'test_in_progress': 'テスト進行中',
                'test_completed': 'テスト完了',
                'problem_file_not_found': '問題のファイルが見つかりません。\n問題のファイルが存在するディレクトリーに移動してから実行してください。',
                # markdown.py
                'markdown_created': 'Markdownファイルを作成しました.',
                # login.py
                'already_logged_in': 'すでにログインしています. ',
                'username': 'ユーザー名: ',
                'password': 'パスワード: ',
                'solve_captcha': 'キャプチャー認証を解決してください',
                'logging_in': 'ログインします',
                'waiting_login_result': 'ログインの結果の待機中...',
                'login_success': 'ログイン成功!',
                'error': 'エラー: {}',
                # submit.py
                'select_implementation': '以下の一覧から{}の実装/コンパイラーを選択してください',
                'submission_failed': '提出に失敗しました',
                'submission_id_not_found': '提出IDが取得できませんでした',
                'submission_success': '提出に成功しました！',
                'waiting_judge': 'ジャッジ待機中',
                'judge_timeout': '15秒待ってもジャッジが開始されませんでした',
                'judging': 'ジャッジ中',
                'judge_completed': 'ジャッジ完了',
                'not_logged_in': 'ログインしていません.',
                'login_failed': 'ログインに失敗しました.',
                'sample_not_ac': 'サンプルケースが AC していないので提出できません',
                'logout_success': 'ログアウトしました.',
                'submission_details': '提出ID: {}, URL: {}',
                # open.py
                'not_found': 'が見つかりません',
                'url_opened': 'URLを開きました',
                'url_not_found_in': 'にURLが見つかりませんでした',
                # generate.py
                'generating_code': 'コード生成中 (by {})',
                'code_generation_success': 'コードの生成に成功しました. ',
                'code_by_model': '{}による{}コード',
                'code_saved': '{} の出力したコードを保存しました：{}',
                'generating_template': '{}のテンプレートを生成しています...',
                'template_created': 'テンプレートファイルを作成 :{}',
                'nth_code_generation': '{}回目のコード生成中 (by {})',
                'regenerating_with_prompt': '次のプロンプトを{}に与え,再生成します',
                'code_generation_success_file': 'コードの生成に成功しました！：{}',
                'testing_generated_code': '{}が生成したコードをテスト中',
                'test_success': 'コードのテストに成功!',
                'test_failed': 'コードのテストに失敗!',
                'log_saved': '{}の出力のログを保存しました：{}',
                # util/gpt.py
                'api_key_validation_failed': '環境変数に設定されているAPIキーの検証に失敗しました ',
                'get_api_key_prompt': 'https://platform.openai.com/api-keys からchatGPTのAPIキーを入手しましょう。\nAPIキー入力してください: ',
                'api_key_test_success': 'APIキーのテストに成功しました。',
                'save_api_key_prompt': '以下, ~/.zshrcにAPIキーを保存しますか? [y/n]',
                'api_key_saved': 'APIキーを {} に保存しました。次回シェル起動時に読み込まれます。',
                'api_key_required': 'コード生成にはAPIキーが必要です。',
                'api_key_validation_error': 'APIキーの検証に失敗しました。',
                'response_format_error': 'Error:レスポンスの形式が正しくありません. \n',
                # util/fileops.py
                'multiple_files_found': '複数のファイルが見つかりました.ファイルを選択してください:',
                'target_file_not_found': '対象ファイルが見つかりません。',
                'file_not_selected': 'ファイルが選択されませんでした。',
                # util/problem.py and util/parse.py
                'name_required': 'nameは必須です',
                'language_not_supported': '言語は {} に対応していません',
                'form_not_found': '問題ページにフォームが存在しません',
                'problem_table_not_found': '問題のテーブルが見つかりませんでした.',
                'tbody_not_found': 'tbodyが見つかりませんでした.',
                # util/session.py
                'response_info': 'レスポンス情報',
                'item': '項目',
                'content': '内容',
                'status_code': 'ステータスコード',
                'reason': '理由',
                'response_headers': 'レスポンスヘッダー',
                'key': 'キー',
                'value': '値',
                'redirect_history': 'リダイレクト履歴',
                'step': 'ステップ',
                'response_body': 'レスポンスボディ',
                'hello_user': 'こんにちは！[cyan]{}[/] さん',
                'session_check_error': 'セッションチェック中にエラーが発生しました: {}',
                # Click command descriptions
                'cmd_download': 'AtCoder の問題をダウンロード',
                'cmd_test': 'テストを実行',
                'cmd_submit': 'ソースを提出',
                'cmd_generate': 'コードを生成',
                'cmd_login': 'AtCoderへログイン',
                'cmd_logout': 'AtCoderへログアウト',
                'cmd_markdown': 'Markdown形式で問題を表示します',
                'cmd_open': 'HTMLファイルを開く',
                # Click option descriptions
                'opt_no_test': 'テストをスキップ',
                'opt_no_feedback': 'フィードバックをスキップ',
                'opt_lang': '出力する言語を指定',
                'opt_save': '変換結果をファイルに保存',
                'opt_output_lang': '出力するプログラミング言語',
                'opt_model': '使用するGPTモデル',
                'opt_without_test': 'テストケースを省略して生成',
                'opt_template': 'テンプレートを生成',
            },
            'en': {
                # download.py
                'retry_problem': 'Retrying... {}',
                'redirect_occurred': 'Redirect occurred. {}',
                'problem_not_found': 'Problem not found. {}',
                'server_error': 'Server error occurred. {}',
                'html_fetch_failed': 'Failed to fetch HTML file for {}.',
                'save_failed': 'Failed to save {}',
                'file_saved': 'File saved: {}',
                'solve_contest_problems': 'Solve contest problems',
                'download_one_problem': 'Download one problem',
                'exit': 'Exit',
                'download_atcoder_html': 'Download AtCoder problem HTML files',
                'navigate_with_arrows': 'Use arrow keys to navigate, [enter] to execute',
                'input_contest_name': 'Enter contest name (e.g., abc012, abs, typical90)',
                'which_problem_download': 'Which problem to download?',
                'exiting': 'Exiting',
                'invalid_selection': 'Invalid selection',
                'specify_contest_name': 'Please specify contest name',
                'invalid_download_args': 'Invalid download arguments',
                # test.py
                'runner_not_found': 'Appropriate language runner for {} not found.',
                'test_of': 'Testing {} \n',
                'compile_time': 'Compile time: [not italic cyan]{}[/] ms[/]',
                'compiler_message': 'Compiler message',
                'status': 'Status ',
                'execution_time': 'Execution time   [cyan]{}[/cyan] ms',
                'input': 'Input',
                'output': 'Output',
                'expected_output': 'Expected output',
                'test_in_progress': 'Testing in progress',
                'test_completed': 'Test completed',
                'problem_file_not_found': 'Problem file not found.\nPlease navigate to the directory containing the problem file.',
                # markdown.py
                'markdown_created': 'Markdown file created.',
                # login.py
                'already_logged_in': 'Already logged in. ',
                'username': 'Username: ',
                'password': 'Password: ',
                'solve_captcha': 'Please solve the captcha',
                'logging_in': 'Logging in',
                'waiting_login_result': 'Waiting for login result...',
                'login_success': 'Login successful!',
                'error': 'Error: {}',
                # submit.py
                'select_implementation': 'Select {} implementation/compiler from the list below',
                'submission_failed': 'Submission failed',
                'submission_id_not_found': 'Submission ID not found',
                'submission_success': 'Submission successful!',
                'waiting_judge': 'Waiting for judge',
                'judge_timeout': 'Judge did not start after 15 seconds',
                'judging': 'Judging',
                'judge_completed': 'Judge completed',
                'not_logged_in': 'Not logged in.',
                'login_failed': 'Login failed.',
                'sample_not_ac': 'Cannot submit because sample cases are not AC',
                'logout_success': 'Logged out successfully.',
                'submission_details': 'Submission ID: {}, URL: {}',
                # open.py
                'not_found': ' not found',
                'url_opened': 'URL opened',
                'url_not_found_in': 'URL not found in ',
                # generate.py
                'generating_code': 'Generating code (by {})',
                'code_generation_success': 'Code generation successful. ',
                'code_by_model': '{} code by {}',
                'code_saved': 'Code generated by {} saved: {}',
                'generating_template': 'Generating {} template...',
                'template_created': 'Template file created: {}',
                'nth_code_generation': 'Code generation attempt {} (by {})',
                'regenerating_with_prompt': 'Regenerating with the following prompt for {}',
                'code_generation_success_file': 'Code generation successful: {}',
                'testing_generated_code': 'Testing code generated by {}',
                'test_success': 'Code test successful!',
                'test_failed': 'Code test failed!',
                'log_saved': 'Log of {} output saved: {}',
                # util/gpt.py
                'api_key_validation_failed': 'API key validation failed ',
                'get_api_key_prompt': 'Get your ChatGPT API key from https://platform.openai.com/api-keys\nEnter API key: ',
                'api_key_test_success': 'API key test successful.',
                'save_api_key_prompt': 'Save API key to ~/.zshrc? [y/n]',
                'api_key_saved': 'API key saved to {}. Will be loaded on next shell startup.',
                'api_key_required': 'API key required for code generation.',
                'api_key_validation_error': 'API key validation failed.',
                'response_format_error': 'Error: Response format is invalid. \n',
                # util/fileops.py
                'multiple_files_found': 'Multiple files found. Please select a file:',
                'target_file_not_found': 'Target file not found.',
                'file_not_selected': 'No file selected.',
                # util/problem.py and util/parse.py
                'name_required': 'Name is required',
                'language_not_supported': 'Language {} is not supported',
                'form_not_found': 'Form not found on problem page',
                'problem_table_not_found': 'Problem table not found.',
                'tbody_not_found': 'tbody not found.',
                # util/session.py
                'response_info': 'Response Information',
                'item': 'Item',
                'content': 'Content',
                'status_code': 'Status Code',
                'reason': 'Reason',
                'response_headers': 'Response Headers',
                'key': 'Key',
                'value': 'Value',
                'redirect_history': 'Redirect History',
                'step': 'Step',
                'response_body': 'Response Body',
                'hello_user': 'Hello [cyan]{}[/]!',
                'session_check_error': 'Error occurred during session check: {}',
                # Click command descriptions
                'cmd_download': 'Download AtCoder problems',
                'cmd_test': 'Run tests',
                'cmd_submit': 'Submit source code',
                'cmd_generate': 'Generate code',
                'cmd_login': 'Login to AtCoder',
                'cmd_logout': 'Logout from AtCoder',
                'cmd_markdown': 'Display problem in Markdown format',
                'cmd_open': 'Open HTML file',
                # Click option descriptions
                'opt_no_test': 'Skip testing',
                'opt_no_feedback': 'Skip feedback',
                'opt_lang': 'Specify output language',
                'opt_save': 'Save conversion result to file',
                'opt_output_lang': 'Specify output programming language',
                'opt_model': 'GPT model to use',
                'opt_without_test': 'Generate without test cases',
                'opt_template': 'Generate template',
            },
        }

    def get(self, key: str, *args) -> str:
        """
        メッセージを取得する
        Args:
            key: メッセージキー
            *args: フォーマット引数
        Returns:
            フォーマット済みのメッセージ
        """
        message = self._messages.get(self._lang or 'en', {}).get(key, key)
        if args:
            try:
                return message.format(*args)
            except Exception:
                return message
        return message

    def set_language(self, lang: str) -> None:
        """言語を明示的に設定する"""
        if lang in self._messages:
            self._lang = lang

    @property
    def language(self) -> str:
        """現在の言語を取得する"""
        return self._lang or 'en'


# シングルトンインスタンス
i18n = I18n()


# 便利な関数
def _(key: str, *args) -> str:
    """i18n.get()のショートカット"""
    return i18n.get(key, *args)
