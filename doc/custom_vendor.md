# 自定义供应商支持指南

本项目现已支持配置自定义的大语言模型供应商，只要该供应商支持OpenAI兼容接口，即可轻松集成到系统中。

## 配置步骤

### 1. 环境变量配置

在您的 `.env` 文件中，添加以下配置：

```bash
# 将LLM_PROVIDER设置为custom
LLM_PROVIDER=custom

# 自定义供应商配置
CUSTOM_API_KEY=sk-your-api-key
CUSTOM_API_BASE_URL=https://your-custom-api-endpoint/v1
CUSTOM_API_MODEL=your-model-name
```

### 2. 参数说明

| 参数 | 描述 | 示例 |
|------|------|------|
| `CUSTOM_API_KEY` | 您的自定义供应商API密钥 | `sk-xxxxxxxx` |
| `CUSTOM_API_BASE_URL` | API基础URL，需要包含到版本部分 | `https://api.your-provider.com/v1` |
| `CUSTOM_API_MODEL` | 您想要使用的模型名称 | `your-model-name` |

### 3. 兼容性要求

自定义供应商必须满足以下要求：

1. 支持OpenAI格式的Chat Completion API
2. 响应格式需与OpenAI兼容
3. 支持如下格式的请求：

```json
{
  "model": "your-model-name",
  "messages": [
    {"role": "system", "content": "系统提示内容"},
    {"role": "user", "content": "用户提示内容"}
  ]
}
```

以及类似的响应格式：

```json
{
  "choices": [
    {
      "message": {
        "content": "模型生成的内容"
      }
    }
  ]
}
```

## 常见自定义供应商配置示例

### Azure OpenAI

```bash
CUSTOM_API_KEY=your-azure-api-key
CUSTOM_API_BASE_URL=https://your-resource-name.openai.azure.com/openai/deployments/your-deployment-name
CUSTOM_API_MODEL=your-deployment-name
```

### Claude API (通过兼容层)

```bash
CUSTOM_API_KEY=your-anthropic-api-key
CUSTOM_API_BASE_URL=https://your-claude-compatible-endpoint/v1
CUSTOM_API_MODEL=claude-3-opus-20240229
```

### 本地托管模型 (使用兼容适配器)

```bash
CUSTOM_API_KEY=dummy-key # 有些本地部署的模型不需要API密钥
CUSTOM_API_BASE_URL=http://localhost:8000/v1
CUSTOM_API_MODEL=your-local-model
```

## 故障排除

如果您在使用自定义供应商时遇到问题，请检查：

1. API基础URL是否正确，包括版本路径
2. API密钥是否有效
3. 模型名称是否正确
4. 网络连接是否畅通
5. 查看日志文件 `log/app.log` 获取更多错误信息

如果您确认以上都正确，但仍然遇到问题，可能是您的供应商API与OpenAI格式不完全兼容。在这种情况下，您可能需要实现一个更专用的客户端类。 