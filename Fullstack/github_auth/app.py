from flask import Flask, request, redirect, session, jsonify, url_for
from flask_cors import CORS
import requests
import os
from urllib.parse import urlencode


app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # 在生产环境中请更改此密钥
CORS(app, supports_credentials=True)

# GitHub OAuth 配置
GITHUB_CLIENT_ID = ''  # 需要在GitHub上创建OAuth应用获取
GITHUB_CLIENT_SECRET = ''  # 需要在GitHub上创建OAuth应用获取
GITHUB_REDIRECT_URI = 'http://localhost:5000/auth/github/callback'

@app.route('/')
def home():
    return jsonify({"message": "GitHub OAuth Flask Backend"})

@app.route('/auth/github')
def github_auth():
    """重定向到GitHub OAuth授权页面"""
    params = {
        'client_id': GITHUB_CLIENT_ID,
        'redirect_uri': GITHUB_REDIRECT_URI,
        'scope': 'user:email',
        'state': 'random-state-string'  # 在生产环境中应使用随机生成的state
    }
    
    github_auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return redirect(github_auth_url)

@app.route('/auth/github/callback')
def github_callback():
    """处理GitHub OAuth回调"""
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return jsonify({"error": "Authorization code not found"}), 400
    
    # 交换访问令牌
    token_data = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code,
        'redirect_uri': GITHUB_REDIRECT_URI
    }
    
    token_headers = {'Accept': 'application/json'}
    token_response = requests.post(
        'https://github.com/login/oauth/access_token',
        data=token_data,
        headers=token_headers
    )
    
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    if not access_token:
        return jsonify({"error": "Failed to get access token"}), 400
    
    # 获取用户信息
    user_headers = {'Authorization': f'token {access_token}'}
    user_response = requests.get('https://api.github.com/user', headers=user_headers)
    user_data = user_response.json()
    
    # 存储用户信息到session
    session['user'] = {
        'id': user_data.get('id'),
        'login': user_data.get('login'),
        'name': user_data.get('name'),
        'email': user_data.get('email'),
        'avatar_url': user_data.get('avatar_url')
    }
    session['access_token'] = access_token
    
    # 重定向到前端成功页面
    return redirect('http://localhost:3000/auth/success')

@app.route('/api/user')
def get_user():
    """获取当前登录用户信息"""
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    return jsonify(session['user'])

@app.route('/api/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@app.route('/api/repos')
def get_repos():
    """获取用户的GitHub仓库列表"""
    if 'access_token' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    headers = {'Authorization': f'token {session["access_token"]}'}
    response = requests.get('https://api.github.com/user/repos', headers=headers)
    
    if response.status_code == 200:
        repos = response.json()
        # 只返回必要的仓库信息
        simplified_repos = [{
            'id': repo['id'],
            'name': repo['name'],
            'full_name': repo['full_name'],
            'description': repo['description'],
            'html_url': repo['html_url'],
            'language': repo['language'],
            'stargazers_count': repo['stargazers_count']
        } for repo in repos]
        return jsonify(simplified_repos)
    else:
        return jsonify({"error": "Failed to fetch repositories"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)