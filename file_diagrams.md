# deepwiki_to_md 個別ファイル詳細図

このドキュメントでは、deepwiki_to_md プロジェクトの各ファイルの詳細な関数とクラスの関係を Mermaid 図を使って視覚化しています。

## deepwiki_to_md.py の詳細構造

```mermaid
graph TD
    subgraph DeepwikiScraper
        init["__init__(output_dir, use_direct_scraper, use_alternative_scraper)"] --> is_domain_reachable
        is_domain_reachable["is_domain_reachable(domain, timeout)"] --> get_page_content
        get_page_content["get_page_content(url, max_retries, base_delay, library_name)"] --> extract_navigation_items
        extract_navigation_items["extract_navigation_items(html_content, current_url)"] --> extract_content
        extract_content["extract_content(html_content, url)"] --> convert_to_markdown
        convert_to_markdown["convert_to_markdown(content)"] --> save_markdown
        save_markdown["save_markdown(markdown_content, library_name, page_path)"] --> scrape_page
        scrape_page["scrape_page(url, library_name)"] --> scrape_library
        scrape_library["scrape_library(library_url, library_name)"] --> run
        run["run(libraries)"]
    end

    get_page_content --> direct_scraper["DirectDeepwikiScraper.scrape_page()"]
    scrape_page --> direct_md_scraper["DirectMarkdownScraper.scrape_page()"]
    scrape_library --> fix_links["fix_markdown_links()"]
```

## direct_scraper.py の詳細構造

```mermaid
graph TD
    subgraph scrape_deepwiki
        sd_func["scrape_deepwiki(url, debug)"] --> sd_session["session.get(url, headers, timeout)"]
        sd_session --> sd_return["return response"]
    end

    subgraph DirectDeepwikiScraper
        dds_init["__init__(output_dir)"] --> dds_extract_content
        dds_extract_content["extract_content(html_content)"] --> dds_save_markdown
        dds_save_markdown["save_markdown(markdown_content, library_name, page_path, save_html, html_content)"] --> dds_scrape_page
        dds_scrape_page["scrape_page(url, library_name, save_html, debug)"] --> dds_extract_navigation_items
        dds_extract_navigation_items["extract_navigation_items(html_content, current_url)"] --> dds_scrape_library
        dds_scrape_library["scrape_library(library_url, library_name, save_html)"] --> dds_run
        dds_run["run(libraries)"]
    end

    dds_scrape_page --> sd_func
    dds_extract_content --> bs4["BeautifulSoup"]
    dds_extract_navigation_items --> bs4
```

## direct_md_scraper.py の詳細構造

```mermaid
graph TD
    subgraph scrape_deepwiki
        sd_func["scrape_deepwiki(url)"] --> sd_session["session.get(url, headers, timeout)"]
        sd_session --> sd_return["return response"]
    end

    subgraph DirectMarkdownScraper
        dms_init["__init__(output_dir)"] --> dms_save_markdown
        dms_save_markdown["save_markdown(content, library_name, page_path)"] --> dms_split_by_headings
        dms_split_by_headings["_split_by_headings(content)"] --> dms_scrape_page
        dms_scrape_page["scrape_page(url, library_name)"] --> dms_extract_navigation_items
        dms_extract_navigation_items["extract_navigation_items(response_text, current_url)"] --> dms_scrape_library
        dms_scrape_library["scrape_library(library_url, library_name)"]
    end

    dms_scrape_page --> sd_func
    dms_save_markdown --> re["正規表現処理"]
    dms_split_by_headings --> re
    dms_extract_navigation_items --> bs4["BeautifulSoup"]
    dms_scrape_library --> fix_links["fix_markdown_links()"]
```

## fix_markdown_links.py の詳細構造

```mermaid
graph TD
    subgraph fix_markdown_links
        fml_start["fix_markdown_links(directory)"] --> fml_check_dir["ディレクトリ存在確認"]
        fml_check_dir --> fml_find_files["Markdownファイル検索"]
        fml_find_files --> fml_process_files["各ファイル処理"]
        fml_process_files --> fml_read_file["ファイル読み込み"]
        fml_read_file --> fml_find_links["リンクパターン検索"]
        fml_find_links --> fml_replace_links["リンク置換"]
        fml_replace_links --> fml_write_file["ファイル書き込み"]
    end

    fml_find_links --> re["正規表現処理"]
    fml_replace_links --> re
```

## run_scraper.py の詳細構造

```mermaid
graph TD
    subgraph run_scraper
        rs_parse_arguments["parse_arguments()"] --> rs_main
        rs_main["main()"] --> rs_create_scraper["DeepwikiScraper作成"]
        rs_create_scraper --> rs_run_scraper["scraper.run(libraries)"]
    end

    rs_parse_arguments --> argparse["argparse"]
    rs_main --> DeepwikiScraper["DeepwikiScraper"]
```

## run_direct_scraper.py の詳細構造

```mermaid
graph TD
    subgraph run_direct_scraper
        rds_parse_arguments["parse_arguments()"] --> rds_main
        rds_main["main()"] --> rds_create_scraper["DirectDeepwikiScraper作成"]
        rds_create_scraper --> rds_run_scraper["scraper.run(libraries)"]
    end

    rds_parse_arguments --> argparse["argparse"]
    rds_main --> DirectDeepwikiScraper["DirectDeepwikiScraper"]
```

## コンポーネント間の依存関係

```mermaid
graph LR
    subgraph エントリーポイント
        run_scraper["run_scraper.py"]
        run_direct_scraper["run_direct_scraper.py"]
    end

    subgraph コアモジュール
        deepwiki_to_md["deepwiki_to_md.py"]
        direct_scraper["direct_scraper.py"]
        direct_md_scraper["direct_md_scraper.py"]
        fix_markdown_links["fix_markdown_links.py"]
    end

    run_scraper --> deepwiki_to_md
    run_direct_scraper --> direct_scraper
    deepwiki_to_md --> direct_scraper
    deepwiki_to_md --> direct_md_scraper
    deepwiki_to_md --> fix_markdown_links
    direct_md_scraper --> fix_markdown_links
```

## データ処理フロー

```mermaid
flowchart TD
    input["入力URL"] --> fetch["HTMLコンテンツ取得"]
    fetch --> extract["コンテンツ抽出"]
    extract --> convert["Markdown変換"]
    convert --> split["見出しごとに分割"]
    split --> save["ファイル保存"]
    save --> fix["リンク修正"]

    subgraph 使用ライブラリ
        requests["requests"]
        bs4["BeautifulSoup4"]
        re["正規表現"]
        markdownify["markdownify"]
    end

    fetch --> requests
    extract --> bs4
    split --> re
    convert --> markdownify
    fix --> re
```