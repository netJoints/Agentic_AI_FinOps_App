# File Mapping Guide

Copy code from artifacts to these files:

## From "Modular FinOps App Structure" artifact:

### config.py
```python
# Copy the "config.py - Configuration" section
```

### services/__init__.py
```python
# Copy the "services/__init__.py" section
```

### services/financial_data.py
```python
# Copy the "services/financial_data.py" section
```

### services/britive_client.py
```python
# Copy the "services/britive_client.py" section
```

### services/agentcore_client.py
```python
# Copy the "services/agentcore_client.py" section
```

### routes/__init__.py
```python
# Copy the "routes/__init__.py" section
```

### routes/api.py
```python
# Copy the "routes/api.py" section
```

### routes/views.py
```python
# Copy the "routes/views.py" section
```

### app.py
```python
# Copy the "app.py - Main application" section
```

## From "Frontend Files" artifact:

### templates/index.html
```html
<!-- Copy the HTML section -->
```

### static/css/styles.css
```css
/* Copy the CSS section */
```

### static/js/main.js
```javascript
// Copy the JavaScript section
```

## Quick Copy Commands

```bash
# After creating files with setup.sh, use your editor to copy each section
# Or use this approach:

# 1. Copy each code block from the artifacts
# 2. Paste into the corresponding file
# 3. Save all files

# Verify structure
tree finops_app/

# Install and run
cd finops_app
pip install -r requirements.txt
python app.py
```
