import requests
from urllib.parse import urlparse

def scrape_deepwiki(url):
    """
    指定されたURLからdeepwikiコンテンツをスクレイピングする関数
    
    Args:
        url: スクレイピングするdeepwikiのURL（例：https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization）
    
    Returns:
        requests.Response: レスポンスオブジェクト
    """
    # URLからドメインとパスを抽出
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path
    
    # セッションの作成
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    })
    
    # URLを解析してリファラーを作成（URLの一部を使用）
    path_parts = path.strip('/').split('/')
    referer_path = '/'.join(path_parts[:-1]) if len(path_parts) > 1 else path
    
    # クエリパラメータを保持
    query = parsed_url.query
    full_url = f"{parsed_url.scheme}://{domain}{path}"
    if query:
        full_url += f"?{query}"
    
    # ヘッダーの設定（動的に生成）
    headers = {
        "authority": domain,
        "method": "GET",
        "path": f"/?_rsc=13l95",
        "scheme": parsed_url.scheme,
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ja,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "next-router-prefetch": "1",
        "pragma": "no-cache",
        "priority": "i",
        "referer": f"{parsed_url.scheme}://{domain}/{referer_path}",
        "rsc": "1",
        "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }
    
    # リクエストの実行
    response = session.get(full_url, headers=headers)
    return response

if __name__ == "__main__":
    # 例として使用
    url = "https://deepwiki.com/python/mypy/1-overview"
    
    # 引数で別のURLを指定するには以下のようにします
    # import sys
    # if len(sys.argv) > 1:
    #     url = sys.argv[1]
    
    response = scrape_deepwiki(url)
    
    # ステータスコードと応答の確認
    print(f"ステータスコード: {response.status_code}")
    print(f"レスポンスの内容: {response.text}")
    
    # 使用例:
    # 他のURLに対しても同じ関数を使用できます
    # response2 = scrape_deepwiki("https://deepwiki.com/python/cpython/6.2-cicd-pipeline")
    # print(f"ステータスコード: {response2.status_code}")