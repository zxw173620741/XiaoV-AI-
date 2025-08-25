import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def send_qq_email(subject, content, is_html=True):
    """
    使用QQ邮箱发送邮件
    
    参数:
        sender (str): 发件人邮箱地址
        password (str): QQ邮箱授权码(不是登录密码)
        receiver (str/list): 收件人邮箱地址，可以是单个地址或地址列表
        subject (str): 邮件主题
        content (str): 邮件内容
        is_html (bool): 是否为HTML内容，默认为False(纯文本)
    
    返回:
        bool: 发送成功返回True，失败返回False
    """
    sender="2456789074@qq.com"
    password="tlrpmckesykjdjhi"
    receiver="1483757317@qq.com"
    try:
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = Header(sender)  # 发件人
        msg['To'] = Header(receiver if isinstance(receiver, str) else ', '.join(receiver))  # 收件人
        msg['Subject'] = Header(subject, 'utf-8')  # 主题
        
        # 添加邮件正文

        html="""
<!DOCTYPE html>
<html lang="zh-CN">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>重要预警通知</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }

        .alert-container {
            border: 2px solid #e74c3c;
            border-radius: 5px;
            padding: 15px;
            background-color: #fdecea;
        }

        .alert-header {
            color: #e74c3c;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }

        .alert-icon {
            margin-right: 10px;
            font-size: 24px;
        }

        .alert-content {
            margin-bottom: 15px;
        }

        .alert-footer {
            font-size: 14px;
            color: #666;
            border-top: 1px dashed #ccc;
            padding-top: 10px;
        }

        .important {
            font-weight: bold;
            color: #e74c3c;
        }

        .action-button {
            display: inline-block;
            background-color: #e74c3c;
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 10px;
        }

        @media only screen and (max-width: 480px) {
            body {
                padding: 10px;
            }

            .alert-header {
                font-size: 18px;
            }
        }
    </style>
</head>

<body>
    <div class="alert-container">
        <div class="alert-header">
            <span class="alert-icon">⚠</span>
            <span>重要预警通知</span>
        </div>

        <div class="alert-content">
            <p>尊敬的<span class="important">[用户名]</span>：</p>

            <p>我们检测到您的<span class="important">[账户/系统]</span>存在异常情况：</p>

            <ul>
                <li>异常类型：<span class="important">[异常描述]</span></li>
                <li>发生时间：<span class="important">[时间]</span></li>
                <li>影响范围：<span class="important">[影响描述]</span></li>
            </ul>

            <p>请立即采取以下措施：</p>
            <ol>
                <li>[第一步操作说明]</li>
                <li>[第二步操作说明]</li>
                <li>[第三步操作说明]</li>
            </ol>

            <a href="https://www.baidu.com/" class="action-button">立即处理</a>
        </div>

        <div class="alert-footer">
            <p>此为系统自动发送邮件，请勿直接回复。</p>
            <p>如非本人操作或已解决问题，请忽略此邮件。</p>
            <p>如有疑问，请联系客服：xxxxxxxxxxx</p>
        </div>
    </div>
</body>

</html>
        """
        if is_html:
            msg.attach(MIMEText(html, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
        # 连接QQ邮箱SMTP服务器
        smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)  # QQ邮箱的SSL端口是465
        smtp.login(sender, password)  # 登录邮箱
        smtp.sendmail(sender, receiver, msg.as_string())  # 发送邮件
        smtp.quit()  # 关闭连接
        print("邮件发送成功")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


# 使用示例
if __name__ == "__main__":
    # 配置信息
    email_subject = "王晶🐖"
    email_content = "666"
    
    # 发送邮件
    send_qq_email(
        subject=email_subject,
        content=email_content
    )