from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# 初始化限流器，使用客户端 IP 作为标识
limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # 默认使用客户端 IP
    default_limits=["100 per hour", "10 per minute"]  # 全局默认限制
)

# 路由1：普通限流（使用全局默认限制）
@app.route('/api/public')
@limiter.limit("5 per minute")  # 覆盖全局设置，更严格的限制
def public_api():
    return jsonify({"message": "Public API"})

# 路由2：根据条件动态限流
@app.route('/api/premium')
def premium_api():
    # 动态设置不同用户组的限制
    if is_premium_user():
        limiter.limit("30 per minute")  # 高级用户限制
    else:
        limiter.limit("3 per minute")   # 普通用户限制
    return jsonify({"message": "Premium API"})

def is_premium_user():
    """模拟检查用户权限的逻辑"""
    # 实际应用中这里会有用户验证逻辑
    return True  # 示例中直接返回 True

# 路由3：豁免限流的白名单
@app.route('/api/internal')
@limiter.exempt  # 完全免除限流
def internal_api():
    return jsonify({"message": " unlimit API "})

# 自定义错误处理器
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "over_limit",
        "message": f"over limit rate: {e.description}",
        "retry_after": e.retry_after
    }), 429

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 