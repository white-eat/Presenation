# 编码规范
这是一个教学演示项目，使用最简单的技术实现，如果没有必要，不要增加复杂度。
每次完成工作，都要清理多余的无用的代码。
# 技术架构
生成的代码应该严格按照已经指定的第三方库的版本开发，不得随意变更。
后端使用:

    - python 3.10
    - Flask 3.0.3
    - PyMySQL 1.1.1
前端使用:

    - Bootstrap 4.5.3 
    - jinja2 模板引擎
# 工作流程
每次工作前，先思考完成任务的步聚，思考完成后跟我确认后，再进行实施。

# 评测标准
### 数据库
    - 使用MySQL数据库 8.4 Host=localhost Port=3306 User=root Password=
    - 数据库db_test.user_accounts数据已经创建，创建代码如下
        create table db_test.user_accounts
        (
            id               int auto_increment
            primary key,
            user_name        varchar(50)    null comment '用户姓名',
            phone_number     varchar(11)    null comment '手机号码',
            id_card_number   varchar(18)    null comment '身份证号码',
            account_type     varchar(20)    null comment '账户类型',
            opening_date     date           null comment '开户日期',
            account_balance  decimal(10, 2) null comment '账户余额',
            loan_type        varchar(20)    null comment '贷款类型',
            loan_amount      decimal(10, 2) null comment '贷款金额',
            loan_date        date           null comment '贷款日期',
            loan_term        int            null comment '贷款期限',
            loan_channel     varchar(20)    null comment '贷款渠道',
            repayment_status varchar(20)    null comment '还款状态'
        );

    - 数据已经填充好。

### 页面：
    base.html是模板页面，作为所有页面的基础模板。 包含一个TopBar,一个侧边栏和一个主区域.
    侧边栏与主区域的宽度比例是1：5.
    侧边栏有两个菜单：
       - 插入数据 /db
       - 浏览数据 /list
    在所有模板中，确认 {% endblock %} 标签，确保正确闭合。
### 大模型参数
    provider: str = "siliconflow"  # LLM提供者
    api_key: str = "sk-diihbejqkjogqdvjipgbiiewmnwompshmnysafdztsooiabu"  # 硅基流动API密钥
    model: str = "Qwen/Qwen3-30B-A3B"  # 硅基流动模型名称
    base_url: str = "https://api.siliconflow.cn/v1"
### 