from cli import CLIInterface

LOCAL_HTML = "<html><head><title>Local Page</title></head><body>content</body></html>"


def test_local_html_file_writes_markdown_to_stdout(tmp_path, capsys):
    html_file = tmp_path / "sample.html"
    html_file.write_text(LOCAL_HTML, encoding="utf-8")

    exit_code = CLIInterface().run([str(html_file)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# Local Page" in captured.out
    assert not (tmp_path / "sample.html.md").exists()


def test_local_html_file_does_not_save_when_path_is_given(tmp_path, capsys):
    html_file = tmp_path / "sample.html"
    output_dir = tmp_path / "output"
    html_file.write_text(LOCAL_HTML, encoding="utf-8")

    exit_code = CLIInterface().run([str(html_file), "--path", str(output_dir)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# Local Page" in captured.out
    assert not output_dir.exists()


def test_url_input_is_saved(tmp_path, capsys):
    cli = CLIInterface()
    cli.extractor.extract_from_url = lambda url: "# Overview\ncontent"

    exit_code = cli.run(
        ["https://deepwiki.com/example/project", "--path", str(tmp_path)]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Content split into 1 files:" in captured.out
    assert (tmp_path / "example" / "project" / "Overview.md").is_file()
    assert (tmp_path / "example" / "project.md").is_file()
