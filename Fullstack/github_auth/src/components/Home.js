import React from 'react';

function Home() {
  const handleGitHubLogin = () => {
    // 重定向到Flask后端的GitHub认证路由
    window.location.href = 'http://localhost:5000/auth/github';
  };

  return (
    <div className="container">
      <h1>GitHub OAuth 认证示例</h1>
      <p>点击下面的按钮使用GitHub账号登录</p>
      <button className="auth-button" onClick={handleGitHubLogin}>
        使用 GitHub 登录
      </button>
      <div style={{ marginTop: '40px', textAlign: 'left' }}>
        <h2>功能说明：</h2>
        <ul>
          <li>GitHub OAuth 认证</li>
          <li>获取用户基本信息</li>
          <li>显示用户的GitHub仓库列表</li>
          <li>安全的会话管理</li>
        </ul>
      </div>
    </div>
  );
}

export default Home;