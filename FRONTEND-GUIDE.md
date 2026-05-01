# Unified RAG Frontend - User Guide

## Overview

The frontend now supports **TWO modes** in a single interface:
1. **CX Intelligence** - For customer service agents
2. **Developer Intelligence** - For developers and SREs

## Features

### Mode Switcher
Located in the sidebar - toggle between CX and Developer modes.

### CX Intelligence Mode

**Purpose:** Help customer service agents with policy and complaint queries

**UI Elements:**
- Query input box
- Query mode selector:
  - General Query
  - Policy Guidance
  - Complaint Analysis
- Data type selector (policy/complaint/both)

**Example Queries:**
```
"How should I handle a refund request?"
"What does our privacy policy say about data retention?"
"Show me similar complaints about online banking"
```

**Response Includes:**
- Answer
- Confidence score
- Recommended next action
- Risk alerts (if any)
- Policy citations

### Developer Intelligence Mode

**Purpose:** Help developers understand services, APIs, and troubleshoot

**UI Elements:**
- Service code input (required)
- Query input box

**Example Queries:**
```
Service Code: PAPSS-001
Query: "How does PAPSS settlement work?"

Service Code: NIP-001
Query: "What endpoint initiates a payment?"

Service Code: PAPSS-001
Query: "What does error code 5001 mean?"
```

**Response Includes:**
- Answer
- Confidence score
- Query intent classification
- Service code
- Documentation sources with versions

### Sidebar Features

**Control Panel:**
- Mode indicator (CX/Developer)
- System status check
- Service registry viewer (Developer mode only)
- Query history (last 5 queries)

**Service Registry (Developer Mode):**
- View all registered services
- Shows service codes and names

**Query History:**
- Last 5 queries
- Shows mode, service code (if applicable), answer preview, confidence
- Clear history button

## Usage Examples

### Example 1: Customer Service Agent

1. Select **CX Intelligence** mode
2. Choose "General Query"
3. Select data type: "both"
4. Enter: "How to handle a customer complaint about delayed refund?"
5. Click "Ask IRIS"
6. Review answer, next action, and policy citations

### Example 2: Developer Onboarding

1. Select **Developer Intelligence** mode
2. Enter service code: "PAPSS-001"
3. Enter: "How does PAPSS authentication work?"
4. Click "Query Docs"
5. Review technical answer with documentation sources

### Example 3: Production Debugging

1. Select **Developer Intelligence** mode
2. Enter service code: "NIP-001"
3. Enter: "What does error code 5001 mean?"
4. Click "Query Docs"
5. Review error explanation from documentation

## Configuration

Update `API_URL` in Streamlit secrets or environment:

```toml
# .streamlit/secrets.toml
API_URL = "http://localhost:8080"
```

Or use default:
```python
API_URL = st.secrets.get("API_URL", "http://localhost:8080")
```

## Running the Frontend

```bash
cd cx-rag-ui
streamlit run app.py
```

Access at: http://localhost:8501

## API Endpoints Used

### CX Intelligence
- `/api/cx/answer` - General queries
- `/api/cx/policy-guidance` - Policy guidance
- `/api/cx/complaint-analysis` - Complaint analysis
- `/api/query/ask` - Unified endpoint

### Developer Intelligence
- `/api/query/ask` - Unified endpoint (with serviceCode)
- `/api/services` - List services
- `/api/health` - System status

## Visual Indicators

**Confidence Badges:**
- 🟢 HIGH CONFIDENCE - Green gradient
- 🟡 MEDIUM CONFIDENCE - Orange gradient
- 🔴 LOW CONFIDENCE - Red gradient

**Mode Indicators:**
- 🎯 CX Mode Active - Green badge
- 💻 Developer Mode Active - Blue badge

## Tips

1. **Service Code Format:** Use consistent format like "SERVICE-001"
2. **Query Clarity:** Be specific in your questions
3. **Check History:** Review past queries for reference
4. **System Status:** Check status if queries fail
5. **Service Registry:** View available services before querying

## Troubleshooting

**Issue:** "Service code is required"
**Solution:** Enter a valid service code in Developer mode

**Issue:** "Service not registered"
**Solution:** Register the service first via API or check service code

**Issue:** "Connection Failed"
**Solution:** Ensure backend is running on correct URL

**Issue:** "No documented information found"
**Solution:** Ingest documentation for the service first

## Summary

The unified frontend provides:
✅ Single interface for both use cases
✅ Easy mode switching
✅ Context-aware UI elements
✅ Comprehensive response display
✅ Query history tracking
✅ Service registry integration

Switch modes seamlessly to serve both customer service and developer needs!
