import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Dashboard() {
  const [user, setUser] = useState(null);
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 获取用户信息
        const userResponse = await axios.get('http://localhost:5000/api/user', {
          withCredentials: true
        });
        setUser(userResponse.data);

        // 获取仓库列表
        const reposResponse = await axios.get('http://localhost:5000/api/repos', {
          withCredentials: true
        });
        setRepos(reposResponse.data);
      } catch (err) {
        if (err.response?.status === 401) {
          // 未认证，跳转到首页
          navigate('/');
        } else {
          setError('获取数据失败');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  const handleLogout = async () => {
    try {
      await axios.post('http://localhost:5000/api/logout', {}, {
        withCredentials: true
      });
      navigate('/');
    } catch (err) {
      console.error('登出失败:', err);
    }
  };

  if (loading) {
    return <div className="loading">加载中...</div>;
  }

  if (error) {
    return (
      <div className="container">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>用户仪表板</h1>
        <button className="auth-button" onClick={handleLogout}>
          登出
        </button>
      </div>

      {user && (
        <div className="user-info">
          <img src={user.avatar_url} alt="Avatar" className="user-avatar" />
          <h2>{user.name || user.login}</h2>
          <p>@{user.login}</p>
          {user.email && <p>邮箱: {user.email}</p>}
        </div>
      )}

      <h2>我的仓库 ({repos.length})</h2>
      <div className="repos-grid">
        {repos.map(repo => (
          <div key={repo.id} className="repo-card">
            <h3>
              <a href={repo.html_url} target="_blank" rel="noopener noreferrer">
                {repo.name}
              </a>
            </h3>
            <p>{repo.description || '暂无描述'}</p>
            <div className="repo-stats">
              {repo.language && <span>语言: {repo.language}</span>}
              <span>⭐ {repo.stargazers_count}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;