# Manuskit 文档中心

欢迎使用 Manuskit 工业级自动化智能网页内容提取平台文档。

## 📖 文档导航

### 核心文档

- **[架构设计文档 (ARCHITECTURE.md)](ARCHITECTURE.md)**  
  深度解析系统架构、模块设计、数据流、技术选型和核心流程

- **[API 接口文档 (API.md)](API.md)**  
  完整的 RESTful API 参考、数据模型、错误码和最佳实践

- **[部署文档 (DEPLOYMENT.md)](DEPLOYMENT.md)**  
  生产环境部署指南、配置方案、监控日志和运维手册

## 🚀 快速开始

### 新用户

1. 阅读 [项目主 README](../README.md) 了解项目概况
2. 按照 [快速开始](../README.md#-快速开始) 配置开发环境
3. 查看 [API 文档](API.md) 学习接口使用
4. 访问 `http://localhost:8080/docs` 查看交互式 API 文档

### 架构师/开发者

1. 研究 [架构设计文档](ARCHITECTURE.md) 理解系统设计
2. 查看 [技术栈](ARCHITECTURE.md#12-技术栈) 和 [模块设计](ARCHITECTURE.md#3-模块设计)
3. 阅读 [核心流程](ARCHITECTURE.md#4-核心流程) 了解业务逻辑
4. 参考 [数据模型](API.md#7-数据模型) 进行集成开发

### 运维工程师

1. 阅读 [系统要求](DEPLOYMENT.md#1-系统要求)
2. 选择合适的 [部署方式](DEPLOYMENT.md#3-部署方式)
3. 配置 [监控与日志](DEPLOYMENT.md#6-监控与日志)
4. 学习 [故障排查](DEPLOYMENT.md#9-故障排查) 方法

## 📋 文档概要

### 架构设计文档

**内容涵盖**：
- 项目概述与核心特性
- 系统架构与数据流
- 模块设计（API 层、服务层、数据模型层）
- 核心流程（异步任务、浏览器自动化、错误处理）
- 安全性设计与性能优化
- 可扩展性与监控方案
- 技术债务与改进方向

**适用读者**：架构师、高级开发者、技术决策者

### API 接口文档

**内容涵盖**：
- API 概述与快速开始
- 系统接口（健康检查、统计信息）
- 内容提取接口（异步/同步）
- 任务管理接口（查询、列表、取消）
- 完整数据模型定义
- 错误码说明
- 最佳实践（轮询、错误处理、并发控制）

**适用读者**：前端开发者、后端开发者、集成工程师

### 部署文档

**内容涵盖**：
- 系统要求与环境准备
- 多种部署方式（Systemd、Supervisor、Docker、K8s）
- 详细配置指南（环境变量、Gunicorn、Nginx）
- Steel 部署选项
- 监控与日志配置
- 安全加固措施
- 性能调优建议
- 故障排查与维护升级

**适用读者**：运维工程师、DevOps 工程师、系统管理员

## 🔍 按需查找

### 我想了解...

**系统如何工作？**  
→ [架构设计文档 - 数据流架构](ARCHITECTURE.md#22-数据流架构)

**如何调用 API？**  
→ [API 文档 - 快速开始](API.md#12-快速开始)

**如何部署到生产环境？**  
→ [部署文档 - 部署方式](DEPLOYMENT.md#3-部署方式)

**如何配置 Steel？**  
→ [部署文档 - Steel 部署](DEPLOYMENT.md#5-steel-部署)  
→ [架构文档 - Steel 配置模式](ARCHITECTURE.md#322-提取服务-srcservicesextraction_servicepy)

**遇到错误怎么办？**  
→ [API 文档 - 错误码](API.md#8-错误码)  
→ [部署文档 - 故障排查](DEPLOYMENT.md#9-故障排查)

**如何监控系统运行？**  
→ [部署文档 - 监控与日志](DEPLOYMENT.md#6-监控与日志)  
→ [架构文档 - 监控与日志](ARCHITECTURE.md#8-监控与日志)

**性能如何优化？**  
→ [部署文档 - 性能调优](DEPLOYMENT.md#8-性能调优)  
→ [架构文档 - 性能优化](ARCHITECTURE.md#6-性能优化)

**如何扩展系统？**  
→ [架构文档 - 可扩展性](ARCHITECTURE.md#7-可扩展性)

## 📚 相关资源

### 在线文档

启动服务后访问交互式文档：
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

### 外部参考

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Steel SDK 文档](https://docs.steel.dev/)
- [browser-use 文档](https://docs.browser-use.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)

## 🆘 获取帮助

### 问题反馈

- **Bug 报告**: 提交 GitHub Issue
- **功能建议**: 提交 GitHub Issue 或 PR
- **使用问题**: 查看文档或提交 Issue

### 更新日志

查看项目主 README 的 [路线图](../README.md#-路线图) 了解未来计划。

## 📝 文档维护

文档版本：**1.0.0**  
最后更新：**2024-01-15**

如发现文档错误或需要补充，欢迎提交 PR！

---

**返回 [项目主页](../README.md)**
