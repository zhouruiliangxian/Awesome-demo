import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function AuthSuccess() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // 验证认证状态
    const checkAuth = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/user', {
          withCredentials: true
        });
        
        if (response.data) {
          // 认证成功，跳转到仪表板
          setTimeout(() => {
            navigate('/dashboard');
          }, 2000);
        }
      } catch (err) {
        setError('认证失败，请重试');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [navigate]);

  if (loading) {
    return (
      <div className="container">
        <h2>认证中...</h2>
        <p>正在验证您的GitHub账号，请稍候...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error">
          <h2>认证失败</h2>
          <p>{error}</p>
          <button className="auth-button" onClick={() => navigate('/')}>
            返回首页
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h2>认证成功！</h2>
      <p>正在跳转到仪表板...</p>
    </div>
  );
}

export default AuthSuccess;