# Claude Quick Reference - Python Dev Learning Web

## 🎯 User Context
- Python expert, web dev learner
- Wants to understand concepts deeply
- May not catch web dev mistakes

## 🧠 Always Remember
1. **Think deeply** before coding
2. **Explain in Python terms**
3. **Use best practices** (user won't know them)
4. **Test everything** with examples
5. **Teach concepts**, don't just code

## 📝 Code Examples Must Have
```javascript
// Always include:
// 1. Python comparison comment
// 2. Explanation of web-specific parts
// 3. Common pitfalls warning
// 4. Best practice approach
```

## ⚡ Quick Conversions

| Python | JavaScript | Notes |
|--------|------------|-------|
| `if not items:` | `if (!items.length)` | Empty arrays are truthy in JS! |
| `for item in items:` | `for (const item of items)` | Use `of` not `in` for arrays |
| `dict.get('key', default)` | `obj.key ?? default` | Nullish coalescing |
| `try/except` | `try/catch` | Different error handling |
| `self` | `this` (use arrow =>)| `this` binding is tricky |

## 🚨 Web Dev Gotchas
1. **Async everywhere** - Most web APIs return Promises
2. **Truthiness differs** - `[]` and `{}` are truthy
3. **No block scope** with `var` - always use `const`/`let`
4. **Event bubbling** - events propagate up the DOM
5. **CORS** - cross-origin requests need setup

## 🧪 Testing Pattern
```python
# Python (pytest)
def test_feature():
    # Arrange
    data = setup_test_data()
    # Act
    result = function_under_test(data)
    # Assert
    assert result == expected
```

```javascript
// JavaScript (Jest)
test('feature works', async () => {
    // Arrange
    const data = setupTestData();
    // Act
    const result = await functionUnderTest(data);
    // Assert
    expect(result).toBe(expected);
});
```

## 📋 Before Every Response
- [ ] Have I explained the web concepts?
- [ ] Did I show Python comparisons?
- [ ] Are there security considerations?
- [ ] Have I included error handling?
- [ ] Are there tests examples?
- [ ] Did I mention common mistakes?

## 🔗 See Also
- Full instructions: `.ai/claude-instructions.md`
- Project context: `PROJECT.md`
- Current tasks: `.ai/tasks/current.yaml`