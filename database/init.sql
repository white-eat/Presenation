create database if not exists db_test;
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