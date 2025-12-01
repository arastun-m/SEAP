## Conversational-Agent: Search Index Setup

### Running Setup (local)
```
az login
bash run_search_setup.sh <storage-account-name> <storage-account-key> <blob-container-name>

bash infra/scripts/run_search_setup.sh stcqbkrzqutptu2 cUpDvJbH4Lb1Oq1iN0kaXinvxFu1zH7a6e4uwhDBsO52LV/tndT8vkZlZkPTSJb4dY3yVb8nOj3h+AStXc8c5w== energy-system-manuals
```

```
az storage account update \
  --name <your_storage_account_name> \
  --resource-group <your_rg_name> \
  --allow-shared-key-access true
```


## Conversational-Agent: Language Setup

### Running Setup (local)
```
az login
bash run_language_setup.sh
```

### Testing CLU and CQA

CLU key-based access
```bash
curl -X POST "https://aif-gn3kyxpqly3ug.cognitiveservices.azure.com/language/:analyze-conversations?api-version=2023-04-01" \
  -H "Ocp-Apim-Subscription-Key: 7MgOtCbsKGYcr6Aj3spHEGbAMp6wA2HzHtAAgvfA1xErmXjfA04MJQQJ99BGACHYHv6XJ3w3AAAAACOGXZum" \
  -H "Content-Type: application/json" \
  -d '{
        "analysisInput": {
          "conversationItem": {
            "id": "1",
            "participantId": "user",
            "text": "What is the status of my order with id = 2?"
          }
        },
        "parameters": {
          "projectName": "conv-assistant-clu",
          "deploymentName": "clu-m1-d1"
        },
        "kind": "Conversation"
      }'
```

CQA key-based access
```bash
curl -X POST "https://aif-cqbkrzqutptu2.cognitiveservices.azure.com/language/:query-knowledgebases?projectName=conv-assistant-cqa&deploymentName=production&api-version=2023-04-01" \
  -H "Ocp-Apim-Subscription-Key: 9s9DKuOiEVUNRMMp4o5LiInAk8jydj3zR7qtDlBsjILR0YxmyMIbJQQJ99BGACfhMk5XJ3w3AAAAACOG0Z2E" \
  -H "Content-Type: application/json" \
  -d '{
        "question": "What is your refund policy?",
        "top": 5,
        "confidenceScoreThreshold": 0.6,
        "rankerType": "Default"
      }'
```